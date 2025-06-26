from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import uuid
from django.http import Http404


from .models import (
    Forum, Discussion, Reply, Notification, LearningAnalytics,
    ActivityLog, MediaContent, Announcement, SupportTicket
)
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from courses.serializers import CourseListSerializer

from .serializers import (
    ForumSerializer, DiscussionSerializer, DiscussionDetailSerializer,
    DiscussionCreateSerializer, ReplySerializer, ReplyCreateSerializer,
    NotificationSerializer, NotificationUpdateSerializer,
    LearningAnalyticsSerializer, ActivityLogSerializer,
    MediaContentSerializer, MediaContentUploadSerializer,
    AnnouncementSerializer, AnnouncementCreateSerializer,
    SupportTicketSerializer, SupportTicketCreateSerializer,
    SupportTicketUpdateSerializer, StudentDashboardSerializer,
    TeacherDashboardSerializer, ManagerDashboardSerializer
)
from .filters import DiscussionFilter, NotificationFilter, ActivityLogFilter
from accounts.permissions import (
    IsOwnerOrReadOnly, IsModeratorOrUp, IsManagerOrAdmin, IsVerifiedUser
)
from .utils import send_notification, track_activity, increment_view_count



def get_object_by_uuid(model, uuid_value):
    """Safely get object by UUID with proper error handling"""
    try:
        validate_uuid(uuid_value)
        return get_object_or_404(model, uuid=uuid_value)
    except ValidationError:
        raise Http404("Invalid UUID format")



# Forums
class ForumListView(generics.ListAPIView):
    """List forums"""
    queryset = Forum.objects.filter(is_active=True).order_by('-created_at', 'id')  # Add explicit ordering
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'course'
        ).annotate(
            discussions_count=Count('discussions')
        ).order_by('-created_at', 'id')  # Ensure ordering is maintained

class ForumDetailView(generics.RetrieveAPIView):
    """Get forum details"""
    queryset = Forum.objects.filter(is_active=True)
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

# Discussions
class DiscussionListCreateView(generics.ListCreateAPIView):
    """List and create discussions"""
    queryset = Discussion.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = DiscussionFilter
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'forum', 'author'
        ).prefetch_related('replies').order_by('-is_pinned', '-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DiscussionCreateSerializer
        return DiscussionSerializer
    
    def perform_create(self, serializer):
        discussion = serializer.save(author=self.request.user)
        
        # Notify course instructor for questions
        if discussion.discussion_type == 'question':
            course = discussion.forum.course
            send_notification(
                course.instructor,
                'forum_reply',
                f'New question in {course.title}',
                f'{self.request.user.get_full_name()} asked: {discussion.title}',
                course=course,
                discussion=discussion
            )

class DiscussionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete discussion"""
    queryset = Discussion.objects.all()
    serializer_class = DiscussionDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_object(self):
        """Override to add UUID validation"""
        uuid_value = self.kwargs.get('uuid')
        return validate_and_get_object(Discussion, uuid_value)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        discussion = self.get_object()
        increment_view_count(discussion)
        serializer = self.get_serializer(discussion)
        return Response(serializer.data)

class DiscussionPinView(APIView):
    """Pin/unpin discussion"""
    permission_classes = [IsAuthenticated, IsModeratorOrUp]
    
    def post(self, request, uuid):
        discussion = validate_and_get_object(Discussion, uuid)  # Use safe validation
        discussion.is_pinned = not discussion.is_pinned
        discussion.save()
        
        return Response({
            'is_pinned': discussion.is_pinned,
            'message': f'Discussion {"pinned" if discussion.is_pinned else "unpinned"}'
        })


class DiscussionLockView(APIView):
    """Lock/unlock discussion"""
    permission_classes = [IsAuthenticated, IsModeratorOrUp]
    
    def post(self, request, uuid):
        discussion = validate_and_get_object(Discussion, uuid)  # Use safe validation
        discussion.is_locked = not discussion.is_locked
        discussion.save()
        
        return Response({
            'is_locked': discussion.is_locked,
            'message': f'Discussion {"locked" if discussion.is_locked else "unlocked"}'
        })

class DiscussionResolveView(APIView):
    """Mark discussion as resolved"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        discussion = validate_and_get_object(Discussion, uuid)  # Use safe validation
        
        if discussion.author != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only discussion author can mark as resolved'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        discussion.is_resolved = True
        discussion.save()
        
        return Response({'message': 'Discussion marked as resolved'})
# Replies
class ReplyListCreateView(generics.ListCreateAPIView):
    """List and create replies"""
    queryset = Reply.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        discussion_uuid = self.request.query_params.get('discussion')
        queryset = super().get_queryset().select_related(
            'discussion', 'author', 'parent'
        ).prefetch_related('children')
        
        if discussion_uuid:
            queryset = queryset.filter(discussion__uuid=discussion_uuid)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReplyCreateSerializer
        return ReplySerializer
    
    def perform_create(self, serializer):
        reply = serializer.save(author=self.request.user)
        
        # Notify discussion author
        if reply.discussion.author != self.request.user:
            send_notification(
                reply.discussion.author,
                'forum_reply',
                f'New reply to your discussion',
                f'{self.request.user.get_full_name()} replied to: {reply.discussion.title}',
                discussion=reply.discussion
            )
        
        # Track activity
        track_activity(
            self.request.user,
            'forum_reply',
            course=reply.discussion.forum.course
        )

class ReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete reply"""
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uuid'

class ReplyUpvoteView(APIView):
    """Upvote reply"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        reply = get_object_or_404(Reply, uuid=uuid)
        
        # Simple upvote implementation
        reply.upvotes += 1
        reply.save()
        
        return Response({'upvotes': reply.upvotes})

class ReplyMarkSolutionView(APIView):
    """Mark reply as solution"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        reply = get_object_or_404(Reply, uuid=uuid)
        discussion = reply.discussion
        
        if discussion.author != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only discussion author can mark solution'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Remove previous solution
        Reply.objects.filter(
            discussion=discussion,
            is_solution=True
        ).update(is_solution=False)
        
        # Mark new solution
        reply.is_solution = True
        reply.save()
        
        # Mark discussion as resolved
        discussion.is_resolved = True
        discussion.save()
        
        return Response({'message': 'Reply marked as solution'})

# Notifications
class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('course', 'lesson', 'discussion')

class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """Get and update notification"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationUpdateSerializer
        return NotificationSerializer

class NotificationMarkAllReadView(APIView):
    """Mark all notifications as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated} notifications marked as read'
        })

class NotificationUnreadCountView(APIView):
    """Get unread notification count"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})

# Activity Logs
class ActivityLogListView(generics.ListAPIView):
    """List activity logs"""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ActivityLogFilter
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.role == 'manager':
            return super().get_queryset()
        
        return ActivityLog.objects.filter(user=user)

# Media Content
class MediaContentListCreateView(generics.ListCreateAPIView):
    """List and upload media content"""
    queryset = MediaContent.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MediaContentUploadSerializer
        return MediaContentSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsModeratorOrUp()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class MediaContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete media content"""
    queryset = MediaContent.objects.all()
    serializer_class = MediaContentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsModeratorOrUp()]
        return super().get_permissions()

# Announcements
class AnnouncementListCreateView(generics.ListCreateAPIView):
    """List and create announcements"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Announcement.objects.filter(is_active=True)
        now = timezone.now()
        
        # Filter by display time
        queryset = queryset.filter(
            Q(show_from__isnull=True) | Q(show_from__lte=now),
            Q(show_until__isnull=True) | Q(show_until__gte=now)
        )
        
        # Filter by user role
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(target_roles__contains=[]) | Q(target_roles__contains=[user.role])
            )
        
        return queryset.select_related('author', 'course')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AnnouncementCreateSerializer
        return AnnouncementSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAdmin()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete announcement"""
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAdmin()]
        return super().get_permissions()

# Support Tickets
class SupportTicketListCreateView(generics.ListCreateAPIView):
    """List and create support tickets"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.role in ['manager', 'moderator']:
            return SupportTicket.objects.all()
        
        return SupportTicket.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SupportTicketCreateSerializer
        return SupportTicketSerializer
    
    def perform_create(self, serializer):
        ticket = serializer.save(user=self.request.user)
        
        # Notify support team
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        managers = User.objects.filter(
            Q(is_staff=True) | Q(role='manager')
        )
        
        for manager in managers:
            send_notification(
                manager,
                'system',
                f'New support ticket: {ticket.subject}',
                f'Priority: {ticket.get_priority_display()}',
            )

class SupportTicketDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update support ticket"""
    queryset = SupportTicket.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SupportTicketUpdateSerializer
        return SupportTicketSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.role in ['manager', 'moderator']:
            return super().get_queryset()
        
        return SupportTicket.objects.filter(user=user)

# Dashboard
class DashboardView(APIView):
    """User dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role == 'student':
            return self.get_student_dashboard(user)
        elif user.role == 'teacher':
            return self.get_teacher_dashboard(user)
        elif user.role in ['manager', 'admin'] or user.is_staff:
            return self.get_manager_dashboard(user)
        
        return Response({'error': 'Invalid user role'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_student_dashboard(self, user):
        from courses.models import Enrollment, Certificate, QuizAttempt
        from courses.serializers import CourseListSerializer
        
        enrollments = Enrollment.objects.filter(student=user)
        
        data = {
            'enrolled_courses': enrollments.filter(is_active=True).count(),
            'completed_courses': enrollments.filter(status='completed').count(),
            'in_progress_courses': enrollments.filter(status='in_progress').count(),
            'total_certificates': Certificate.objects.filter(student=user).count(),
            'total_study_hours': user.profile.total_study_hours,
            'average_score': QuizAttempt.objects.filter(
                student=user
            ).aggregate(avg_score=Avg('score'))['avg_score'] or 0,
            'recent_activities': ActivityLogSerializer(
                ActivityLog.objects.filter(user=user).order_by('-created_at')[:10],
                many=True
            ).data,
            'upcoming_lessons': []
        }
        
        return Response(StudentDashboardSerializer(data).data)
    
    
    def get_teacher_dashboard(self, user):
        from courses.models import Course, Enrollment, CourseReview
        from courses.serializers import CourseReviewSerializer
    
        courses = Course.objects.filter(instructor=user)
    
        data = {
            'total_courses': courses.count(),
            'published_courses': courses.filter(status='published').count(),
            'total_students': Enrollment.objects.filter(
                course__instructor=user,
                is_active=True
            ).values('student').distinct().count(),
            'active_students': Enrollment.objects.filter(
                course__instructor=user,
                last_accessed__gte=timezone.now() - timedelta(days=7)
            ).values('student').distinct().count(),
            'average_rating': courses.aggregate(
                avg_rating=Avg('reviews__rating')
            )['avg_rating'] or 0,
            'recent_reviews': CourseReviewSerializer(
                CourseReview.objects.filter(
                    course__instructor=user
                ).order_by('-created_at')[:5],
                many=True
            ).data,
            'pending_questions': Discussion.objects.filter(
                forum__course__instructor=user,
                discussion_type='question',
                is_resolved=False
            ).count(),
            'course_analytics': []
        }
        
        return Response(TeacherDashboardSerializer(data).data)


    def get_manager_dashboard(self, user):

        User = get_user_model()
        
        data = {
            'total_users': User.objects.filter(is_active=True).count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
            'active_users_today': ActivityLog.objects.filter(
                created_at__date=timezone.now().date()
            ).values('user').distinct().count(),
            'revenue_this_month': 0,
            'popular_courses': CourseListSerializer(
                Course.objects.filter(
                    status='published'
                ).annotate(
                    enrollment_count=Count('enrollments')
                ).order_by('-enrollment_count')[:5],
                many=True
            ).data,
            'user_growth': [],
            'system_health': {
                'database_status': 'healthy',
                'redis_status': 'healthy',
                'storage_usage': '45%'
            }
        }
        
        return Response(ManagerDashboardSerializer(data).data)
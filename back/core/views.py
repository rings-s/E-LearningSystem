# back/core/views.py - Complete version with all views
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg, Sum, Prefetch
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import (
    Forum, Discussion, Reply, Notification, LearningAnalytics,
    ActivityLog, MediaContent, Announcement, SupportTicket
)
from courses.models import Course, Enrollment, QuizAttempt, LessonProgress
from .serializers import (
    ForumSerializer, DiscussionSerializer, ReplySerializer,
    NotificationSerializer, LearningAnalyticsSerializer, ActivityLogSerializer,
    MediaContentSerializer, AnnouncementSerializer, SupportTicketSerializer
)
from .filters import DiscussionFilter, NotificationFilter, ActivityLogFilter
from accounts.permissions import IsOwnerOrReadOnly, IsModeratorOrUp, IsManagerOrAdmin, IsTeacherOrAdmin
from .utils import (
    send_notification, track_activity, increment_view_count, 
    validate_and_get_object, format_api_response
)
from .services import AnalyticsService


User = get_user_model()

# Forums
class ForumListView(generics.ListAPIView):
    """GET /api/core/forums/ - List all forums"""
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Forum.objects.filter(is_active=True).select_related(
            'course'
        ).annotate(
            discussions_count=Count('discussions')
        ).order_by('-created_at', 'id')

class ForumDetailView(generics.RetrieveAPIView):
    """GET /api/core/forums/{uuid}/ - Get forum details"""
    queryset = Forum.objects.filter(is_active=True).select_related('course')
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

# Discussions
class DiscussionListCreateView(generics.ListCreateAPIView):
    """
    GET /api/core/discussions/ - List discussions
    POST /api/core/discussions/ - Create discussion
    """
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DiscussionFilter
    
    def get_queryset(self):
        return Discussion.objects.select_related(
            'forum', 'author'
        ).prefetch_related('replies').order_by('-is_pinned', '-created_at', 'id')
    
    def perform_create(self, serializer):
        discussion = serializer.save()
        
        # Notify course instructor for questions
        if discussion.discussion_type == 'question':
            course = discussion.forum.course
            send_notification(
                course.instructor, 'forum_reply',
                f'New question in {course.title}',
                f'{self.request.user.get_full_name()} asked: {discussion.title}',
                course=course, discussion=discussion
            )

class DiscussionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/core/discussions/{uuid}/ - Get discussion details
    PUT/PATCH /api/core/discussions/{uuid}/ - Update discussion
    DELETE /api/core/discussions/{uuid}/ - Delete discussion
    """
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        return Discussion.objects.select_related('forum', 'author').prefetch_related(
            Prefetch('replies', queryset=Reply.objects.select_related('author').order_by('created_at'))
        )
    
    def get_object(self):
        uuid_value = self.kwargs.get('uuid')
        return validate_and_get_object(Discussion, uuid_value, queryset=self.get_queryset())
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        discussion = self.get_object()
        increment_view_count(discussion)
        serializer = self.get_serializer(discussion)
        return Response(serializer.data)

# Discussion Actions
class DiscussionPinView(APIView):
    """POST /api/core/discussions/{uuid}/pin/ - Pin/unpin discussion"""
    permission_classes = [IsAuthenticated, IsModeratorOrUp]
    
    def post(self, request, uuid):
        discussion = validate_and_get_object(Discussion, uuid)
        discussion.is_pinned = not discussion.is_pinned
        discussion.save()
        
        return format_api_response(
            data={'is_pinned': discussion.is_pinned},
            message=f'Discussion {"pinned" if discussion.is_pinned else "unpinned"}'
        )

class DiscussionLockView(APIView):
    """POST /api/core/discussions/{uuid}/lock/ - Lock/unlock discussion"""
    permission_classes = [IsAuthenticated, IsModeratorOrUp]
    
    def post(self, request, uuid):
        discussion = validate_and_get_object(Discussion, uuid)
        discussion.is_locked = not discussion.is_locked
        discussion.save()
        
        return format_api_response(
            data={'is_locked': discussion.is_locked},
            message=f'Discussion {"locked" if discussion.is_locked else "unlocked"}'
        )

class DiscussionResolveView(APIView):
    """POST /api/core/discussions/{uuid}/resolve/ - Mark as resolved"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        discussion = validate_and_get_object(Discussion, uuid)
        
        if discussion.author != request.user and not request.user.is_staff:
            return format_api_response(
                errors={'permission': ['Only discussion author can mark as resolved']},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        discussion.is_resolved = True
        discussion.save()
        
        return format_api_response(message='Discussion marked as resolved')

# Replies
class ReplyListCreateView(generics.ListCreateAPIView):
    """
    GET /api/core/replies/ - List replies
    POST /api/core/replies/ - Create reply
    """
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        discussion_uuid = self.request.query_params.get('discussion')
        queryset = Reply.objects.select_related('discussion', 'author', 'parent')
        
        if discussion_uuid:
            queryset = queryset.filter(discussion__uuid=discussion_uuid)
        
        return queryset.order_by('created_at', 'id')
    
    def perform_create(self, serializer):
        reply = serializer.save()
        
        # Notify discussion author
        if reply.discussion.author != self.request.user:
            send_notification(
                reply.discussion.author, 'forum_reply',
                'New reply to your discussion',
                f'{self.request.user.get_full_name()} replied to: {reply.discussion.title}',
                discussion=reply.discussion
            )
        
        track_activity(
            self.request.user, 'forum_reply',
            course=reply.discussion.forum.course
        )

class ReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/core/replies/{uuid}/ - Get reply details
    PUT/PATCH /api/core/replies/{uuid}/ - Update reply
    DELETE /api/core/replies/{uuid}/ - Delete reply
    """
    queryset = Reply.objects.select_related('discussion', 'author')
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uuid'

# Reply Actions
class ReplyUpvoteView(APIView):
    """POST /api/core/replies/{uuid}/upvote/ - Upvote reply"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        reply = validate_and_get_object(Reply, uuid)
        reply.upvotes += 1
        reply.save()
        
        return format_api_response(
            data={'upvotes': reply.upvotes},
            message='Reply upvoted'
        )

class ReplyMarkSolutionView(APIView):
    """POST /api/core/replies/{uuid}/mark-solution/ - Mark as solution"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        reply = validate_and_get_object(Reply, uuid)
        discussion = reply.discussion
        
        if discussion.author != request.user and not request.user.is_staff:
            return format_api_response(
                errors={'permission': ['Only discussion author can mark solution']},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Remove previous solution
        Reply.objects.filter(discussion=discussion, is_solution=True).update(is_solution=False)
        
        # Mark new solution
        reply.is_solution = True
        reply.save()
        
        # Mark discussion as resolved
        discussion.is_resolved = True
        discussion.save()
        
        return format_api_response(message='Reply marked as solution')

# Notifications
class NotificationListView(generics.ListAPIView):
    """GET /api/core/notifications/ - List user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('course', 'lesson', 'discussion').order_by('-created_at', 'id')

class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/core/notifications/{uuid}/ - Get notification details
    PUT/PATCH /api/core/notifications/{uuid}/ - Update notification
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

# Notification Actions
class NotificationMarkAllReadView(APIView):
    """POST /api/core/notifications/mark-all-read/ - Mark all as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return format_api_response(
            data={'updated_count': updated},
            message=f'{updated} notifications marked as read'
        )

class NotificationUnreadCountView(APIView):
    """GET /api/core/notifications/unread-count/ - Get unread count"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        
        return format_api_response(data={'unread_count': count})

# Activity Logs
class ActivityLogListView(generics.ListAPIView):
    """GET /api/core/activities/ - List activity logs"""
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ActivityLogFilter
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.role == 'manager':
            return ActivityLog.objects.select_related('user', 'course', 'lesson').order_by('-created_at', 'id')
        
        return ActivityLog.objects.filter(user=user).select_related('course', 'lesson').order_by('-created_at', 'id')

# Media Content
class MediaContentListCreateView(generics.ListCreateAPIView):
    """
    GET /api/core/media/ - List media content
    POST /api/core/media/ - Upload media content
    """
    serializer_class = MediaContentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MediaContent.objects.select_related('uploaded_by', 'course', 'lesson').order_by('-created_at', 'id')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsModeratorOrUp()]
        return super().get_permissions()

class MediaContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/core/media/{uuid}/ - Get media details
    PUT/PATCH /api/core/media/{uuid}/ - Update media
    DELETE /api/core/media/{uuid}/ - Delete media
    """
    queryset = MediaContent.objects.select_related('uploaded_by', 'course', 'lesson')
    serializer_class = MediaContentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsModeratorOrUp()]
        return super().get_permissions()

# Announcements
class AnnouncementListCreateView(generics.ListCreateAPIView):
    """
    GET /api/core/announcements/ - List announcements
    POST /api/core/announcements/ - Create announcement
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Announcement.objects.filter(is_active=True).select_related('author', 'course')
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
        
        return queryset.order_by('-is_pinned', '-created_at', 'id')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAdmin()]
        return super().get_permissions()

class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/core/announcements/{uuid}/ - Get announcement details
    PUT/PATCH /api/core/announcements/{uuid}/ - Update announcement
    DELETE /api/core/announcements/{uuid}/ - Delete announcement
    """
    queryset = Announcement.objects.select_related('author', 'course')
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAdmin()]
        return super().get_permissions()

# Support Tickets
class SupportTicketListCreateView(generics.ListCreateAPIView):
    """
    GET /api/core/support-tickets/ - List support tickets
    POST /api/core/support-tickets/ - Create support ticket
    """
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.role in ['manager', 'moderator']:
            return SupportTicket.objects.select_related('user', 'assigned_to', 'course').order_by('-created_at', 'id')
        
        return SupportTicket.objects.filter(user=user).select_related('assigned_to', 'course').order_by('-created_at', 'id')
    
    def perform_create(self, serializer):
        ticket = serializer.save()
        
        # Notify support team
        managers = User.objects.filter(Q(is_staff=True) | Q(role='manager'))
        
        for manager in managers:
            send_notification(
                manager, 'system',
                f'New support ticket: {ticket.subject}',
                f'Priority: {ticket.get_priority_display()}',
            )

class SupportTicketDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/core/support-tickets/{uuid}/ - Get ticket details
    PUT/PATCH /api/core/support-tickets/{uuid}/ - Update ticket
    """
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.role in ['manager', 'moderator']:
            return SupportTicket.objects.select_related('user', 'assigned_to', 'course')
        
        return SupportTicket.objects.filter(user=user).select_related('assigned_to', 'course')

# Analytics Views
class StudentAnalyticsView(APIView):
    """GET /api/core/student-analytics/ - Student analytics dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get basic metrics
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        
        # Study streak
        today = timezone.now().date()
        streak_days = 0
        for i in range(30):
            check_date = today - timedelta(days=i)
            has_activity = ActivityLog.objects.filter(
                user=user, created_at__date=check_date
            ).exists()
            if has_activity:
                streak_days += 1
            else:
                break
        
        # Recent quiz performance
        recent_quizzes = QuizAttempt.objects.filter(
            student=user, completed_at__isnull=False
        ).order_by('-completed_at')[:10]
        
        return format_api_response(data={
            'summary': {
                'total_courses': enrollments.count(),
                'completed_courses': enrollments.filter(status='completed').count(),
                'average_progress': float(enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0),
                'learning_streak': streak_days,
                'total_quizzes': recent_quizzes.count(),
                'avg_quiz_score': float(recent_quizzes.aggregate(avg=Avg('score'))['avg'] or 0)
            },
            'recent_activity': list(ActivityLog.objects.filter(
                user=user
            ).order_by('-created_at')[:5].values(
                'activity_type', 'created_at', 'course__title'
            ))
        })

class TeacherAnalyticsView(APIView):
    """GET /api/core/teacher-analytics/ - Teacher analytics dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'teacher' and not user.is_staff:
            return format_api_response(
                errors={'permission': ['Teacher access only']},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        courses = Course.objects.filter(instructor=user)
        total_enrollments = Enrollment.objects.filter(course__instructor=user, is_active=True)
        
        return format_api_response(data={
            'summary': {
                'total_courses': courses.count(),
                'published_courses': courses.filter(status='published').count(),
                'total_students': total_enrollments.values('student').distinct().count(),
                'avg_course_rating': float(courses.aggregate(avg=Avg('reviews__rating'))['avg'] or 0),
                'pending_questions': Discussion.objects.filter(
                    forum__course__instructor=user,
                    discussion_type='question',
                    is_resolved=False
                ).count()
            },
            'course_performance': [{
                'course_title': course.title,
                'students': course.enrollments.filter(is_active=True).count(),
                'avg_progress': float(course.enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0),
                'rating': float(course.reviews.aggregate(avg=Avg('rating'))['avg'] or 0)
            } for course in courses.select_related().prefetch_related('enrollments', 'reviews')]
        })

class PlatformAnalyticsView(APIView):
    """GET /api/core/platform-analytics/ - Platform-wide analytics"""
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]
    
    def get(self, request):
        # Basic platform stats
        total_users = User.objects.filter(is_active=True).count()
        month_ago = timezone.now() - timedelta(days=30)
        active_users = ActivityLog.objects.filter(
            created_at__gte=month_ago
        ).values('user').distinct().count()
        
        return format_api_response(data={
            'platform_health': {
                'total_users': total_users,
                'active_users_30d': active_users,
                'user_engagement_rate': round((active_users / max(total_users, 1)) * 100, 1),
                'total_courses': Course.objects.count(),
                'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
                'open_tickets': SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()
            },
            'user_distribution': [{
                'role': role.title(),
                'count': User.objects.filter(role=role, is_active=True).count()
            } for role, _ in User.ROLE_CHOICES]
        })

# Dashboard Views
class DashboardView(APIView):
    """GET /api/core/dashboard/ - Main dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role == 'student':
            return self._student_dashboard(user)
        elif user.role == 'teacher':
            return self._teacher_dashboard(user)
        elif user.role in ['manager', 'admin'] or user.is_staff:
            return self._manager_dashboard(user)
        
        return format_api_response(
            errors={'role': ['Invalid user role']},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def _student_dashboard(self, user):
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        recent_activities = ActivityLog.objects.filter(user=user).order_by('-created_at')[:5]
        
        return format_api_response(data={
            'role': 'student',
            'enrolled_courses': enrollments.count(),
            'completed_courses': enrollments.filter(status='completed').count(),
            'average_progress': float(enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0),
            'recent_activities': list(recent_activities.values('activity_type', 'created_at', 'course__title'))
        })
    
    def _teacher_dashboard(self, user):
        courses = Course.objects.filter(instructor=user)
        
        return format_api_response(data={
            'role': 'teacher',
            'total_courses': courses.count(),
            'published_courses': courses.filter(status='published').count(),
            'total_students': Enrollment.objects.filter(
                course__instructor=user, is_active=True
            ).values('student').distinct().count(),
            'pending_questions': Discussion.objects.filter(
                forum__course__instructor=user,
                discussion_type='question',
                is_resolved=False
            ).count()
        })
    
    def _manager_dashboard(self, user):
        return format_api_response(data={
            'role': 'manager',
            'total_users': User.objects.filter(is_active=True).count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
            'open_tickets': SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()
        })

class DashboardSummaryView(APIView):
    """GET /api/core/dashboard/summary/ - Dashboard summary for managers"""
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get(self, request):
        # Date range for recent activity
        seven_days_ago = timezone.now() - timedelta(days=7)

        # Platform-Wide Statistics
        total_users = User.objects.count()
        courses_by_status = Course.objects.values('status').annotate(count=Count('id'))
        total_enrollments = Enrollment.objects.count()
        active_tickets = SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()

        # Recent Activity (Last 7 Days)
        new_users = User.objects.filter(date_joined__gte=seven_days_ago).count()
        new_enrollments = Enrollment.objects.filter(enrolled_at__gte=seven_days_ago).count()
        completed_courses = Enrollment.objects.filter(completed_at__gte=seven_days_ago).count()
        new_discussions = Discussion.objects.filter(created_at__gte=seven_days_ago).count()

        # Key Engagement Metrics (Recent 5)
        recent_courses = Course.objects.order_by('-published_at')[:5]
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_tickets = SupportTicket.objects.order_by('-created_at')[:5]

        response_data = {
            'platform_stats': {
                'total_users': total_users,
                'total_courses': {
                    'published': next((item['count'] for item in courses_by_status if item['status'] == 'published'), 0),
                    'draft': next((item['count'] for item in courses_by_status if item['status'] == 'draft'), 0),
                    'archived': next((item['count'] for item in courses_by_status if item['status'] == 'archived'), 0),
                },
                'total_enrollments': total_enrollments,
                'active_tickets': active_tickets,
            },
            'recent_activity': {
                'new_users_7_days': new_users,
                'new_enrollments_7_days': new_enrollments,
                'completed_courses_7_days': completed_courses,
                'new_discussions_7_days': new_discussions,
            },
            'engagement_metrics': {
                'recent_courses': [
                    {'title': c.title, 'published_at': c.published_at} for c in recent_courses if c.published_at
                ],
                'recent_users': [
                    {'email': u.email, 'date_joined': u.date_joined} for u in recent_users
                ],
                'recent_tickets': [
                    {'subject': t.subject, 'status': t.status, 'created_at': t.created_at} for t in recent_tickets
                ],
            }
        }
        
        return format_api_response(data=response_data)






from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import (
    Forum, Discussion, Reply, Notification, LearningAnalytics,
    ActivityLog, MediaContent, Announcement, SupportTicket
)
from courses.models import Course, Enrollment, QuizAttempt, LessonProgress
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
from .utils import (
    send_notification, track_activity, increment_view_count, 
    validate_and_get_object
)

User = get_user_model()

# =============================================================================
# FORUM VIEWS
# =============================================================================

class ForumListView(generics.ListAPIView):
    """List all active forums"""
    queryset = Forum.objects.filter(is_active=True).order_by('-created_at', 'id')
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'course'
        ).annotate(
            discussions_count=Count('discussions')
        ).order_by('-created_at', 'id')

class ForumDetailView(generics.RetrieveAPIView):
    """Get forum details"""
    queryset = Forum.objects.filter(is_active=True)
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

# =============================================================================
# DISCUSSION VIEWS
# =============================================================================

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
        discussion = validate_and_get_object(Discussion, uuid)
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
        discussion = validate_and_get_object(Discussion, uuid)
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
        discussion = validate_and_get_object(Discussion, uuid)
        
        if discussion.author != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only discussion author can mark as resolved'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        discussion.is_resolved = True
        discussion.save()
        
        return Response({'message': 'Discussion marked as resolved'})

# =============================================================================
# REPLY VIEWS
# =============================================================================

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

# =============================================================================
# NOTIFICATION VIEWS
# =============================================================================

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

# =============================================================================
# ACTIVITY LOG VIEWS
# =============================================================================

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

# =============================================================================
# MEDIA CONTENT VIEWS
# =============================================================================

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

# =============================================================================
# ANNOUNCEMENT VIEWS
# =============================================================================

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

# =============================================================================
# SUPPORT TICKET VIEWS
# =============================================================================

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

# =============================================================================
# ANALYTICS VIEWS - SIMPLIFIED FOR E-LEARNING
# =============================================================================

class StudentAnalyticsView(APIView):
    """Complete student analytics dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'student':
            return Response({'error': 'Student access only'}, status=403)
        
        # Get student enrollments
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        
        # Course progress data
        course_progress = []
        for enrollment in enrollments:
            course_progress.append({
                'course_id': str(enrollment.course.uuid),
                'course_title': enrollment.course.title,
                'progress': float(enrollment.progress_percentage),
                'status': enrollment.status,
                'enrolled_date': enrollment.enrolled_at.date().isoformat(),
                'instructor': enrollment.course.instructor.get_full_name()
            })
        
        # Learning streak calculation
        today = timezone.now().date()
        streak_days = 0
        for i in range(30):
            check_date = today - timedelta(days=i)
            has_activity = ActivityLog.objects.filter(
                user=user,
                created_at__date=check_date
            ).exists()
            if has_activity:
                streak_days += 1
            else:
                break
        
        # Study time last 30 days
        last_30_days = timezone.now() - timedelta(days=30)
        daily_study = []
        for i in range(30):
            day = (timezone.now() - timedelta(days=i)).date()
            
            time_spent = LessonProgress.objects.filter(
                enrollment__student=user,
                started_at__date=day
            ).aggregate(
                total=Sum('time_spent_seconds')
            )['total'] or 0
            
            daily_study.append({
                'date': day.isoformat(),
                'minutes': round(time_spent / 60, 1)
            })
        
        daily_study.reverse()
        
        # Recent quiz performance
        recent_quizzes = QuizAttempt.objects.filter(
            student=user,
            completed_at__isnull=False
        ).order_by('-completed_at')[:10]
        
        quiz_performance = []
        for attempt in recent_quizzes:
            quiz_performance.append({
                'quiz_title': attempt.quiz.title,
                'course': attempt.quiz.course.title,
                'score': float(attempt.score) if attempt.score else 0,
                'passed': attempt.passed,
                'date': attempt.completed_at.date().isoformat()
            })
        
        # Subject performance
        subject_performance = recent_quizzes.values(
            'quiz__course__category__name'
        ).annotate(
            avg_score=Avg('score'),
            total_attempts=Count('id'),
            passed_count=Count('id', filter=Q(passed=True))
        ).order_by('-avg_score')
        
        subject_data = []
        for subject in subject_performance:
            if subject['quiz__course__category__name']:
                subject_data.append({
                    'subject': subject['quiz__course__category__name'],
                    'avg_score': round(float(subject['avg_score'] or 0), 1),
                    'success_rate': round(
                        (subject['passed_count'] / subject['total_attempts'] * 100) 
                        if subject['total_attempts'] > 0 else 0, 1
                    )
                })
        
        # Generate chart data
        charts = {
            'course_progress': {
                'type': 'bar',
                'title': 'Course Progress',
                'data': {
                    'labels': [course['course_title'][:20] + '...' if len(course['course_title']) > 20 
                              else course['course_title'] for course in course_progress],
                    'datasets': [{
                        'label': 'Progress %',
                        'data': [course['progress'] for course in course_progress],
                        'backgroundColor': [
                            '#10B981' if course['progress'] >= 80 else
                            '#F59E0B' if course['progress'] >= 50 else
                            '#EF4444' for course in course_progress
                        ]
                    }]
                }
            },
            'study_time_trend': {
                'type': 'line',
                'title': 'Daily Study Time (Last 30 Days)',
                'data': {
                    'labels': [day['date'][-5:] for day in daily_study],  # Show MM-DD
                    'datasets': [{
                        'label': 'Minutes',
                        'data': [day['minutes'] for day in daily_study],
                        'borderColor': '#3B82F6',
                        'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                        'fill': True
                    }]
                }
            },
            'quiz_performance': {
                'type': 'line',
                'title': 'Recent Quiz Scores',
                'data': {
                    'labels': [quiz['quiz_title'][:15] + '...' if len(quiz['quiz_title']) > 15 
                              else quiz['quiz_title'] for quiz in quiz_performance],
                    'datasets': [{
                        'label': 'Score %',
                        'data': [quiz['score'] for quiz in quiz_performance],
                        'borderColor': '#8B5CF6',
                        'backgroundColor': [
                            '#10B981' if quiz['passed'] else '#EF4444' 
                            for quiz in quiz_performance
                        ]
                    }]
                }
            }
        }
        
        # Summary metrics
        total_courses = enrollments.count()
        avg_progress = enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
        total_study_time = sum(day['minutes'] for day in daily_study)
        
        return Response({
            'summary': {
                'total_courses': total_courses,
                'completed_courses': enrollments.filter(status='completed').count(),
                'in_progress_courses': enrollments.filter(status='in_progress').count(),
                'average_progress': round(avg_progress, 1),
                'study_hours_30d': round(total_study_time / 60, 1),
                'learning_streak': streak_days
            },
            'performance': {
                'total_quizzes': recent_quizzes.count(),
                'avg_quiz_score': recent_quizzes.aggregate(avg=Avg('score'))['avg'] or 0,
                'quiz_pass_rate': recent_quizzes.filter(passed=True).count() / max(recent_quizzes.count(), 1) * 100
            },
            'charts': charts,
            'subject_performance': subject_data
        })

class TeacherAnalyticsView(APIView):
    """Complete teacher analytics dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'teacher' and not user.is_staff:
            return Response({'error': 'Teacher access only'}, status=403)
        
        # Get teacher courses
        courses = Course.objects.filter(instructor=user)
        
        # Course performance data
        course_stats = []
        for course in courses:
            enrollments = course.enrollments.filter(is_active=True)
            
            # Calculate engagement score
            completion_rate = enrollments.filter(status='completed').count() / max(enrollments.count(), 1)
            avg_progress = enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
            forum_activity = Discussion.objects.filter(forum__course=course).count()
            quiz_participation = QuizAttempt.objects.filter(quiz__course=course).count()
            
            engagement = (
                completion_rate * 40 +
                (avg_progress / 100) * 30 +
                min(forum_activity / max(enrollments.count(), 1), 1) * 20 +
                min(quiz_participation / max(enrollments.count(), 1), 1) * 10
            ) * 100
            
            course_stats.append({
                'course_id': str(course.uuid),
                'title': course.title,
                'total_students': enrollments.count(),
                'completed_students': enrollments.filter(status='completed').count(),
                'avg_progress': round(avg_progress, 1),
                'avg_rating': course.reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
                'engagement_score': round(engagement, 1)
            })
        
        # Student activity analysis
        total_enrollments = Enrollment.objects.filter(
            course__instructor=user,
            is_active=True
        )
        
        week_ago = timezone.now() - timedelta(days=7)
        active_students = total_enrollments.filter(
            last_accessed__gte=week_ago
        ).count()
        
        # Progress distribution
        progress_distribution = {
            'not_started': total_enrollments.filter(progress_percentage=0).count(),
            'in_progress': total_enrollments.filter(
                progress_percentage__gt=0, 
                progress_percentage__lt=100
            ).count(),
            'completed': total_enrollments.filter(progress_percentage=100).count()
        }
        
        # Generate charts
        charts = {
            'course_performance': {
                'type': 'scatter',
                'title': 'Course Performance Overview',
                'data': {
                    'datasets': [{
                        'label': 'Courses',
                        'data': [{
                            'x': course['total_students'],
                            'y': course['avg_progress'],
                            'label': course['title'][:20]
                        } for course in course_stats],
                        'backgroundColor': '#3B82F6'
                    }]
                }
            },
            'student_progress': {
                'type': 'doughnut',
                'title': 'Student Progress Distribution',
                'data': {
                    'labels': ['Not Started', 'In Progress', 'Completed'],
                    'datasets': [{
                        'data': [
                            progress_distribution['not_started'],
                            progress_distribution['in_progress'],
                            progress_distribution['completed']
                        ],
                        'backgroundColor': ['#EF4444', '#F59E0B', '#10B981']
                    }]
                }
            }
        }
        
        return Response({
            'summary': {
                'total_courses': courses.count(),
                'published_courses': courses.filter(status='published').count(),
                'total_students': total_enrollments.values('student').distinct().count(),
                'active_students_7d': active_students,
                'avg_course_rating': courses.aggregate(avg=Avg('reviews__rating'))['avg'] or 0
            },
            'course_performance': course_stats,
            'student_activity': {
                'total_students': total_enrollments.count(),
                'active_students_7d': active_students,
                'progress_distribution': progress_distribution
            },
            'charts': charts
        })

class PlatformAnalyticsView(APIView):
    """Platform-wide analytics for managers"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role not in ['manager', 'admin'] and not user.is_staff:
            return Response({'error': 'Manager access only'}, status=403)
        
        # Platform overview
        total_users = User.objects.filter(is_active=True).count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.filter(is_active=True).count()
        
        # User growth (last 6 months)
        user_growth = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            new_users = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count()
            
            user_growth.append({
                'month': month_start.strftime('%b %Y'),
                'new_users': new_users
            })
        
        user_growth.reverse()
        
        # Course category distribution
        category_stats = Course.objects.values(
            'category__name'
        ).annotate(
            course_count=Count('id'),
            total_enrollments=Count('enrollments', filter=Q(enrollments__is_active=True))
        ).order_by('-course_count')
        
        category_data = []
        for cat in category_stats:
            if cat['category__name']:
                category_data.append({
                    'category': cat['category__name'],
                    'courses': cat['course_count'],
                    'enrollments': cat['total_enrollments']
                })
        
        # User role distribution
        user_roles = []
        for role, _ in User.ROLE_CHOICES:
            count = User.objects.filter(role=role, is_active=True).count()
            user_roles.append({
                'role': role.title(),
                'count': count
            })
        
        # Generate charts
        charts = {
            'user_growth': {
                'type': 'bar',
                'title': 'User Growth (Last 6 Months)',
                'data': {
                    'labels': [month['month'] for month in user_growth],
                    'datasets': [{
                        'label': 'New Users',
                        'data': [month['new_users'] for month in user_growth],
                        'backgroundColor': '#10B981'
                    }]
                }
            },
            'category_distribution': {
                'type': 'doughnut',
                'title': 'Courses by Category',
                'data': {
                    'labels': [cat['category'] for cat in category_data],
                    'datasets': [{
                        'data': [cat['courses'] for cat in category_data],
                        'backgroundColor': ['#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#10B981']
                    }]
                }
            },
            'user_roles': {
                'type': 'bar',
                'title': 'Users by Role',
                'data': {
                    'labels': [role['role'] for role in user_roles],
                    'datasets': [{
                        'label': 'Users',
                        'data': [role['count'] for role in user_roles],
                        'backgroundColor': '#8B5CF6'
                    }]
                }
            }
        }
        
        # Active users
        month_ago = timezone.now() - timedelta(days=30)
        active_users = ActivityLog.objects.filter(
            created_at__gte=month_ago
        ).values('user').distinct().count()
        
        return Response({
            'platform_health': {
                'total_users': total_users,
                'active_users_30d': active_users,
                'user_engagement_rate': round((active_users / max(total_users, 1)) * 100, 1),
                'total_courses': total_courses,
                'published_courses': Course.objects.filter(status='published').count(),
                'total_enrollments': total_enrollments
            },
            'growth_metrics': user_growth,
            'category_insights': category_data,
            'user_distribution': user_roles,
            'charts': charts
        })

# =============================================================================
# DASHBOARD VIEW - MAIN ENTRY POINT
# =============================================================================

class DashboardView(APIView):
    """Main dashboard routing based on user role"""
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
        """Simple student dashboard overview"""
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        
        # Recent activities
        recent_activities = ActivityLog.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        activities_data = []
        for activity in recent_activities:
            activities_data.append({
                'activity': activity.get_activity_type_display(),
                'course': activity.course.title if activity.course else 'General',
                'date': activity.created_at.date().isoformat(),
                'time': activity.created_at.time().strftime('%H:%M')
            })
        
        return Response({
            'role': 'student',
            'enrolled_courses': enrollments.count(),
            'completed_courses': enrollments.filter(status='completed').count(),
            'in_progress_courses': enrollments.filter(status='in_progress').count(),
            'average_progress': enrollments.aggregate(
                avg=Avg('progress_percentage')
            )['avg'] or 0,
            'recent_activities': activities_data
        })
    
    def get_teacher_dashboard(self, user):
        """Simple teacher dashboard overview"""
        courses = Course.objects.filter(instructor=user)
        
        return Response({
            'role': 'teacher',
            'total_courses': courses.count(),
            'published_courses': courses.filter(status='published').count(),
            'total_students': Enrollment.objects.filter(
                course__instructor=user,
                is_active=True
            ).values('student').distinct().count(),
            'pending_questions': Discussion.objects.filter(
                forum__course__instructor=user,
                discussion_type='question',
                is_resolved=False
            ).count(),
            'average_rating': courses.aggregate(
                avg_rating=Avg('reviews__rating')
            )['avg_rating'] or 0
        })
    
    def get_manager_dashboard(self, user):
        """Simple manager dashboard overview"""
        return Response({
            'role': 'manager',
            'total_users': User.objects.filter(is_active=True).count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
            'active_users_today': ActivityLog.objects.filter(
                created_at__date=timezone.now().date()
            ).values('user').distinct().count(),
            'open_tickets': SupportTicket.objects.filter(
                status__in=['open', 'in_progress']
            ).count()
        })
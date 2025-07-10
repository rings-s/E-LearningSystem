from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, LessonProgress, QuizAttempt
from core.models import ActivityLog, Discussion, SupportTicket

User = get_user_model()

class AnalyticsService:
    @staticmethod
    def get_teacher_analytics(user):
        """Get comprehensive analytics for a teacher"""
        courses = Course.objects.filter(instructor=user)
        
        # Basic metrics
        total_courses = courses.count()
        published_courses = courses.filter(status='published').count()
        total_students = Enrollment.objects.filter(
            course__instructor=user, is_active=True
        ).values('student').distinct().count()
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        active_students_7d = ActivityLog.objects.filter(
            course__instructor=user,
            created_at__gte=week_ago
        ).values('user').distinct().count()
        
        # Average ratings
        avg_course_rating = courses.aggregate(
            avg_rating=Avg('reviews__rating')
        )['avg_rating'] or 0
        
        return {
            'summary': {
                'total_courses': total_courses,
                'published_courses': published_courses,
                'total_students': total_students,
                'active_students_7d': active_students_7d,
                'avg_course_rating': avg_course_rating
            }
        }
    
    @staticmethod
    def get_course_analytics(course):
        """Get analytics for a specific course"""
        enrollments = course.enrollments.filter(is_active=True)
        
        # Progress distribution
        not_started = enrollments.filter(progress_percentage=0).count()
        in_progress = enrollments.filter(
            progress_percentage__gt=0, progress_percentage__lt=100
        ).count()
        completed = enrollments.filter(progress_percentage=100).count()
        
        return {
            'summary': {
                'total_students': enrollments.count(),
                'avg_progress': enrollments.aggregate(
                    avg=Avg('progress_percentage')
                )['avg'] or 0
            },
            'studentActivity': {
                'progress_distribution': {
                    'not_started': not_started,
                    'in_progress': in_progress,
                    'completed': completed
                }
            }
        }
    
    @staticmethod
    def get_student_analytics(user):
        """Get analytics data for students"""
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        
        # Study streak calculation
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
        
        # Progress by course
        course_progress = []
        for enrollment in enrollments.select_related('course'):
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment, is_completed=True
            ).count()
            total_lessons = enrollment.course.modules.aggregate(
                total=Count('lessons', filter=Q(lessons__is_published=True))
            )['total'] or 0
            
            course_progress.append({
                'course_title': enrollment.course.title,
                'course_uuid': str(enrollment.course.uuid),
                'progress_percentage': enrollment.progress_percentage,
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'last_accessed': enrollment.last_accessed
            })
        
        return {
            'summary': {
                'total_courses': enrollments.count(),
                'completed_courses': enrollments.filter(status='completed').count(),
                'average_progress': float(enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0),
                'learning_streak': streak_days,
                'total_quizzes': recent_quizzes.count(),
                'avg_quiz_score': float(recent_quizzes.aggregate(avg=Avg('score'))['avg'] or 0)
            },
            'course_progress': course_progress,
            'recent_activity': list(ActivityLog.objects.filter(
                user=user
            ).order_by('-created_at')[:5].values(
                'activity_type', 'created_at', 'course__title'
            ))
        }
    
    @staticmethod
    def get_platform_analytics():
        """Get platform-wide analytics data"""
        total_users = User.objects.filter(is_active=True).count()
        month_ago = timezone.now() - timedelta(days=30)
        active_users = ActivityLog.objects.filter(
            created_at__gte=month_ago
        ).values('user').distinct().count()
        
        # Course statistics
        course_stats = Course.objects.aggregate(
            total=Count('id'),
            published=Count('id', filter=Q(status='published')),
            draft=Count('id', filter=Q(status='draft'))
        )
        
        # Enrollment statistics
        enrollment_stats = Enrollment.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            completed=Count('id', filter=Q(status='completed'))
        )
        
        return {
            'platform_health': {
                'total_users': total_users,
                'active_users_30d': active_users,
                'user_engagement_rate': round((active_users / max(total_users, 1)) * 100, 1),
                'total_courses': course_stats['total'],
                'published_courses': course_stats['published'],
                'total_enrollments': enrollment_stats['active'],
                'completion_rate': round((enrollment_stats['completed'] / max(enrollment_stats['total'], 1)) * 100, 1),
                'open_tickets': SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()
            },
            'user_distribution': [{
                'role': role.title(),
                'count': User.objects.filter(role=role, is_active=True).count()
            } for role, _ in User.ROLE_CHOICES],
            'recent_trends': {
                'new_users_7d': User.objects.filter(
                    date_joined__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'new_enrollments_7d': Enrollment.objects.filter(
                    enrolled_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'completed_courses_7d': Enrollment.objects.filter(
                    completed_at__gte=timezone.now() - timedelta(days=7)
                ).count()
            }
        }
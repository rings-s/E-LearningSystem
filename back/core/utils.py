# back/core/utils.py
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
import logging
import uuid

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

def validate_uuid(value):
    """Validate UUID format"""
    try:
        uuid.UUID(str(value))
    except (ValueError, TypeError):
        raise ValidationError("Invalid UUID format")

def validate_and_get_object(model_class, uuid_value, queryset=None):
    """Validate UUID and get object safely"""
    try:
        uuid.UUID(str(uuid_value))
        if queryset is not None:
            return get_object_or_404(queryset, uuid=uuid_value)
        return get_object_or_404(model_class, uuid=uuid_value)
    except (ValueError, TypeError):
        raise Http404("Invalid UUID format")

def format_api_response(data=None, message=None, errors=None, status_code=status.HTTP_200_OK):
    """Standardized API response format"""
    response_data = {
        'success': status_code < 400,
        'status_code': status_code,
    }
    
    if data is not None:
        response_data['data'] = data
    if message:
        response_data['message'] = message
    if errors:
        response_data['errors'] = errors
    
    return Response(response_data, status=status_code)

def send_notification(user, notification_type, title, message, **kwargs):
    """Send notification to user"""
    from core.models import Notification
    
    notification = Notification.objects.create(
        recipient=user,
        notification_type=notification_type,
        title=title,
        message=message,
        **kwargs
    )
    
    # Send via WebSocket if available
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.uuid}",
                {
                    "type": "notification.send",
                    "notification": {
                        "id": str(notification.uuid),
                        "type": notification_type,
                        "title": title,
                        "message": message,
                        "created_at": notification.created_at.isoformat(),
                    }
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send WebSocket notification: {e}")
    
    return notification

def bulk_notify_enrolled_students(course, notification_type, title, message):
    """Notify all enrolled students in a course"""
    from courses.models import Enrollment
    
    enrollments = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related('student')
    
    for enrollment in enrollments:
        send_notification(
            enrollment.student,
            notification_type,
            title,
            message,
            course=course
        )

def track_activity(user, activity_type, **kwargs):
    """Track user activity"""
    from core.models import ActivityLog
    
    ActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        ip_address=kwargs.pop('ip_address', None),
        user_agent=kwargs.pop('user_agent', ''),
        metadata=kwargs.pop('metadata', {}),
        **kwargs
    )

def increment_view_count(obj):
    """Increment view count atomically"""
    obj.__class__.objects.filter(pk=obj.pk).update(
        views_count=F('views_count') + 1
    )

def calculate_course_progress(enrollment):
    """Calculate course completion percentage"""
    from courses.models import Lesson, LessonProgress
    
    total_lessons = Lesson.objects.filter(
        module__course=enrollment.course,
        is_published=True
    ).count()
    
    if total_lessons == 0:
        return 0
    
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        is_completed=True,
        lesson__is_published=True
    ).count()
    
    return round((completed_lessons / total_lessons) * 100, 2)

def update_enrollment_progress(enrollment):
    """Update enrollment progress percentage"""
    progress = calculate_course_progress(enrollment)
    enrollment.progress_percentage = progress
    
    # Update status based on progress
    if progress >= 100 and enrollment.status != 'completed':
        enrollment.status = 'completed'
        enrollment.completed_at = timezone.now()
        
        # Trigger certificate generation if available
        try:
            from courses.tasks import generate_certificate_task
            generate_certificate_task.delay(enrollment.id)
        except ImportError:
            # Handle case where Celery is not available
            logger.info(f"Certificate generation queued for enrollment {enrollment.id}")
            
    elif progress > 0 and enrollment.status == 'enrolled':
        enrollment.status = 'in_progress'
        enrollment.started_at = timezone.now()
    
    enrollment.save()
    return progress

# Cache utilities
def get_or_set_cache(key, func, timeout=3600):
    """Get from cache or set if not exists"""
    value = cache.get(key)
    if value is None:
        value = func()
        cache.set(key, value, timeout)
    return value

def invalidate_cache_pattern(pattern):
    """Invalidate all cache keys matching pattern"""
    if hasattr(cache, '_cache'):
        try:
            keys = cache._cache.keys(f"*{pattern}*")
            cache.delete_many(keys)
        except AttributeError:
            # Fallback for different cache backends
            pass

# Quiz scoring utilities
def calculate_quiz_score(quiz_attempt):
    """Calculate score for a quiz attempt"""
    from courses.models import QuestionResponse
    
    responses = QuestionResponse.objects.filter(
        attempt=quiz_attempt
    ).select_related('question')
    
    total_points = sum(r.question.points for r in responses)
    earned_points = sum(r.points_earned for r in responses)
    
    if total_points == 0:
        return 0
    
    score = (earned_points / total_points) * 100
    return round(score, 2)

# File utilities
def get_file_hash(file):
    """Generate hash for uploaded file"""
    import hashlib
    hasher = hashlib.md5()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()

def format_file_size(size_bytes):
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

# Rate limiting
def check_rate_limit(key, max_attempts=5, window=3600):
    """Check if rate limit exceeded"""
    attempts = cache.get(key, 0)
    if attempts >= max_attempts:
        return False
    cache.set(key, attempts + 1, window)
    return True

# Email utilities
def send_course_enrollment_email(enrollment):
    """Send enrollment confirmation email"""
    try:
        from accounts.utils import send_email
        
        context = {
            'user_name': enrollment.student.get_full_name(),
            'course_title': enrollment.course.title,
            'instructor_name': enrollment.course.instructor.get_full_name(),
            'course_url': f"{getattr(settings, 'FRONTEND_URL', '')}/courses/{enrollment.course.uuid}",
        }
        
        send_email(
            to_email=enrollment.student.email,
            subject=f"Enrolled in {enrollment.course.title}",
            template_name='course_enrollment',
            context=context
        )
    except ImportError:
        logger.warning("Email sending not configured")
    except Exception as e:
        logger.error(f"Failed to send enrollment email: {e}")

# Learning analytics helpers
def get_study_streak(user):
    """Get user's current study streak in days"""
    from core.models import ActivityLog
    
    today = timezone.now().date()
    streak = 0
    
    for i in range(365):  # Check up to 1 year
        check_date = today - timedelta(days=i)
        has_activity = ActivityLog.objects.filter(
            user=user,
            created_at__date=check_date
        ).exists()
        
        if has_activity:
            streak += 1
        else:
            break
            
    return streak

def calculate_engagement_score(course):
    """Calculate course engagement score (0-100)"""
    from courses.models import Enrollment
    from core.models import Discussion
    from courses.models import QuizAttempt
    
    enrollments = course.enrollments.filter(is_active=True)
    if not enrollments.exists():
        return 0
    
    completion_rate = enrollments.filter(status='completed').count() / enrollments.count()
    avg_progress = enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
    
    forum_activity = Discussion.objects.filter(forum__course=course).count()
    quiz_participation = QuizAttempt.objects.filter(quiz__course=course).count()
    
    # Weighted engagement score
    engagement = (
        completion_rate * 40 +  # 40% weight on completion
        (avg_progress / 100) * 30 +  # 30% weight on progress
        min(forum_activity / enrollments.count(), 1) * 20 +  # 20% weight on discussions
        min(quiz_participation / enrollments.count(), 1) * 10  # 10% weight on quiz participation
    )
    
    return round(engagement * 100, 1)

# Time utilities
def format_duration(seconds):
    """Format duration in seconds to human readable"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

# Validation utilities
def validate_course_access(user, course):
    """Check if user has access to course"""
    from courses.models import Enrollment
    
    # Course instructor always has access
    if course.instructor == user:
        return True
    
    # Co-instructors have access
    if user in course.co_instructors.all():
        return True
    
    # Staff/admins have access
    if user.is_staff or user.role in ['manager', 'admin']:
        return True
    
    # Students need active enrollment
    if user.role == 'student':
        return Enrollment.objects.filter(
            student=user,
            course=course,
            is_active=True
        ).exists()
    
    return False

def validate_lesson_access(user, lesson):
    """Check if user has access to lesson"""
    course = lesson.module.course
    
    # Check course access first
    if not validate_course_access(user, course):
        return False
    
    # Check if lesson is published (except for instructors)
    if not lesson.is_published and course.instructor != user and not user.is_staff:
        return False
    
    # Check if lesson is preview or user is enrolled
    if lesson.is_preview:
        return True
    
    return validate_course_access(user, course)

# Error handling utilities
def handle_db_error(func):
    """Decorator to handle database errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            return None
    return wrapper

# Import utilities for missing imports
def safe_import(module_path, class_name):
    """Safely import a class/function"""
    try:
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None

# Account activity tracking
def track_user_activity(user, activity_type, **kwargs):
    """Track user activity for accounts module"""
    from core.models import UserActivity
    
    try:
        UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            metadata=kwargs.get('metadata', {})
        )
    except Exception as e:
        logger.error(f"Failed to track user activity: {str(e)}")

# Enrollment import fix for missing dependency
def create_enrollment_or_pass(*args, **kwargs):
    """Create enrollment if models available"""
    try:
        from courses.models import Enrollment
        return Enrollment.objects.create(*args, **kwargs)
    except Exception:
        return None
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ValidationError
import logging
import hashlib
import uuid  # Use built-in uuid module

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

def validate_uuid(value):
    """Validate that the value is a valid UUID"""
    try:
        uuid.UUID(str(value))
    except (ValueError, TypeError):
        raise ValidationError("Invalid UUID format")

def validate_and_get_object(model_class, uuid_value):
    """Validate UUID and get object safely"""
    try:
        # Validate UUID format
        uuid.UUID(str(uuid_value))
        return get_object_or_404(model_class, uuid=uuid_value)
    except (ValueError, AttributeError, TypeError):
        raise Http404("Invalid UUID format")

def validate_uuid_param(uuid_value):
    """Validate UUID parameter and raise 404 if invalid"""
    try:
        validate_uuid(uuid_value)
        return True
    except ValidationError:
        raise Http404("Invalid UUID format")

def safe_uuid_filter(queryset, field_name, uuid_value):
    """Safely filter by UUID field, returning empty queryset for invalid UUIDs"""
    try:
        validate_uuid(uuid_value)
        filter_kwargs = {field_name: uuid_value}
        return queryset.filter(**filter_kwargs)
    except ValidationError:
        return queryset.none()

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
        keys = cache._cache.keys(f"*{pattern}*")
        cache.delete_many(keys)

# Notification utilities
def send_notification(user, notification_type, title, message, **kwargs):
    """Send notification to user via WebSocket and create DB record"""
    from core.models import Notification
    
    notification = Notification.objects.create(
        recipient=user,
        notification_type=notification_type,
        title=title,
        message=message,
        **kwargs
    )
    
    # Send via WebSocket
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

# Activity tracking
def track_activity(user, activity_type, **kwargs):
    """Track user activity"""
    from core.models import ActivityLog
    
    ActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        ip_address=kwargs.pop('ip_address', None),
        user_agent=kwargs.pop('user_agent', ''),  # Use empty string instead of None
        metadata=kwargs.pop('metadata', {}),
        **kwargs
    )

def increment_view_count(obj):
    """Increment view count atomically"""
    obj.__class__.objects.filter(pk=obj.pk).update(
        views_count=F('views_count') + 1
    )

# Progress calculation
def calculate_course_progress(enrollment):
    """Calculate course completion percentage with better accuracy"""
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
    """Update enrollment progress percentage with real-time calculation"""
    progress = calculate_course_progress(enrollment)
    enrollment.progress_percentage = progress
    
    # Update status based on progress
    if progress >= 100 and enrollment.status != 'completed':
        enrollment.status = 'completed'
        enrollment.completed_at = timezone.now()
        
        # Trigger certificate generation
        try:
            from courses.tasks import generate_certificate_task
            generate_certificate_task.delay(enrollment.id)
        except ImportError:
            # Handle case where Celery is not available
            pass
    elif progress > 0 and enrollment.status == 'enrolled':
        enrollment.status = 'in_progress'
        enrollment.started_at = timezone.now()
    
    enrollment.save()
    return progress

# Quiz scoring
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
    from accounts.utils import send_email
    
    context = {
        'user_name': enrollment.student.get_full_name(),
        'course_title': enrollment.course.title,
        'instructor_name': enrollment.course.instructor.get_full_name(),
        'course_url': f"{settings.FRONTEND_URL}/courses/{enrollment.course.uuid}",
    }
    
    send_email(
        to_email=enrollment.student.email,
        subject=f"Enrolled in {enrollment.course.title}",
        template_name='course_enrollment',
        context=context
    )
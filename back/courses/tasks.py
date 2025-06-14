from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_certificate_task(enrollment_id):
    """Generate certificate for completed course"""
    from courses.models import Enrollment, Certificate
    
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        
        # Generate certificate logic here
        certificate = Certificate.objects.create(
            student=enrollment.student,
            course=enrollment.course,
            enrollment=enrollment,
            completion_date=enrollment.completed_at,
            final_score=enrollment.progress_percentage
        )
        
        # Send email notification
        from accounts.utils import send_certificate_email
        send_certificate_email(
            email=enrollment.student.email,
            user_name=enrollment.student.get_full_name(),
            course_title=enrollment.course.title,
            certificate_url=f"{settings.FRONTEND_URL}/certificates/{certificate.uuid}",
            certificate_number=certificate.certificate_number
        )
        
        logger.info(f"Certificate generated for enrollment {enrollment_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate certificate for enrollment {enrollment_id}: {str(e)}")
        raise

@shared_task
def send_course_reminder_emails():
    """Send reminder emails for inactive students"""
    from courses.models import Enrollment
    from django.utils import timezone
    from datetime import timedelta
    
    # Find students who haven't accessed course in 7 days
    inactive_date = timezone.now() - timedelta(days=7)
    
    inactive_enrollments = Enrollment.objects.filter(
        status='in_progress',
        last_accessed__lt=inactive_date,
        is_active=True
    ).select_related('student', 'course')
    
    for enrollment in inactive_enrollments:
        # Send reminder email
        send_mail(
            subject=f"Continue your learning journey: {enrollment.course.title}",
            message=f"Hi {enrollment.student.first_name}, we miss you! Continue your course to achieve your goals.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[enrollment.student.email],
            fail_silently=True
        )
    
    logger.info(f"Sent {inactive_enrollments.count()} reminder emails")
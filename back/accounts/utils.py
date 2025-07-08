# back/accounts/utils.py - Add activity tracking function
"""Email handling, response formatting, and rate limiting utilities."""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
from typing import Dict, Any, Optional, Union
import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

# Rate limiting configuration
RATE_LIMITS = {
    'verification': {'max_attempts': 3, 'lockout_seconds': 1800},
    'reset': {'max_attempts': 3, 'lockout_seconds': 1800},
    'enrollment': {'max_attempts': 5, 'lockout_seconds': 300},
    'quiz': {'max_attempts': 10, 'lockout_seconds': 600},
    'default': {'max_attempts': 5, 'lockout_seconds': 900}
}

def track_user_activity(user, activity_type, **kwargs):
    """Track user activity for security purposes"""
    try:
        from core.models import UserActivity
        
        UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            metadata=kwargs.get('metadata', {})
        )
    except Exception as e:
        logger.error(f"Failed to track user activity: {str(e)}")

def track_login_attempt(user, ip_address, success=True):
    """Track login attempts for security monitoring"""
    activity_type = 'login_success' if success else 'login_failed'
    track_user_activity(user, activity_type, ip_address=ip_address)
    
    if success:
        security_logger.info(f"Successful login: {user.email} from {ip_address}")
    else:
        security_logger.warning(f"Failed login attempt: {user.email} from {ip_address}")

class EmailRateLimitExceeded(Exception):
    """Exception raised when email action exceeds rate limit."""
    def __init__(self, wait_minutes=None):
        self.wait_minutes = wait_minutes
        message = f"Too many attempts. Please wait {wait_minutes} minutes before trying again." if wait_minutes else "Too many attempts. Please try again later."
        super().__init__(message)

def create_response(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    error: Optional[Union[str, Dict[str, Any]]] = None,
    error_code: Optional[str] = None,
    status_code: int = status.HTTP_200_OK
) -> Response:
    """Create standardized API response."""
    response_data = {"status": "error" if error else "success"}

    if data is not None:
        response_data["data"] = data
    if message:
        response_data["message"] = message
    if error:
        if isinstance(error, dict) and any(isinstance(v, list) for v in error.values()):
            response_data["error"] = error
        else:
            response_data["error"] = {"message": error}
            if error_code:
                response_data["error"]["code"] = error_code

    return Response(response_data, status=status_code)

def check_rate_limit(identifier: str, action_type: str) -> None:
    """Check if action exceeds rate limit."""
    if not identifier:
        logger.warning(f"Empty identifier for rate limit check: {action_type}")
        return

    limits = RATE_LIMITS.get(action_type, RATE_LIMITS['default'])
    max_attempts = limits['max_attempts']
    lockout_time = limits['lockout_seconds']

    cache_key = f"rate_limit_{action_type}_{identifier.lower().replace('@', '_at_').replace('.', '_dot_')}"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= max_attempts:
        wait_minutes = lockout_time // 60
        logger.warning(f"Rate limit exceeded: {action_type} by {identifier}. Attempts: {attempts}/{max_attempts}")
        raise EmailRateLimitExceeded(wait_minutes=wait_minutes)

    cache.set(cache_key, attempts + 1, timeout=lockout_time)

def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    action_type: str = 'default',
    check_limits: bool = True,
    fail_silently: bool = False
) -> bool:
    """Send an email using Django templates with rate limiting."""
    if not to_email:
        logger.error(f"Attempted to send email with empty recipient: {subject}")
        return False

    if check_limits:
        try:
            check_rate_limit(to_email, action_type)
        except EmailRateLimitExceeded as e:
            logger.warning(f"Rate limit hit: {action_type} to {to_email}")
            raise e

    company_name = getattr(settings, 'COMPANY_NAME', '244SCHOOL')
    default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@244school.com')
    frontend_url = getattr(settings, 'FRONTEND_URL', '').rstrip('/')

    context.update({
        'company_name': company_name,
        'frontend_url': frontend_url,
        'current_year': timezone.now().year,
    })

    full_subject = f"[{company_name}] {subject}"

    try:
        html_template = f'emails/{template_name}.html'
        try:
            html_message = render_to_string(html_template, context)
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in {html_template}: {str(e)}")
            if not fail_silently:
                raise
            return False

        try:
            txt_template = f'emails/{template_name}.txt'
            plain_message = render_to_string(txt_template, context)
        except (TemplateDoesNotExist, TemplateSyntaxError):
            plain_message = strip_tags(html_message)

        if settings.DEBUG and 'console' in getattr(settings, 'EMAIL_BACKEND', ''):
            logger.info(f"\n{'='*40}\nEMAIL TO: {to_email}\nSUBJECT: {full_subject}\nTEMPLATE: {template_name}\n{'='*40}")
            if settings.DEBUG and action_type in ['verification', 'reset']:
                code = context.get('verification_code') or context.get('reset_code')
                if code:
                    logger.info(f"DEBUG - {action_type.upper()} CODE: {code}")
            return True

        send_mail(
            subject=full_subject,
            message=plain_message,
            html_message=html_message,
            from_email=default_from_email,
            recipient_list=[to_email],
            fail_silently=fail_silently
        )
        logger.info(f"Email sent: {subject} to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send {action_type} email to {to_email}: {str(e)}", exc_info=True)
        if not fail_silently:
            raise
        return False

def send_verification_email(email: str, verification_code: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Send verification code email."""
    ctx = context or {}
    ctx['verification_code'] = verification_code
    ctx['expiry_hours'] = RATE_LIMITS['verification']['lockout_seconds'] // 3600

    if settings.FRONTEND_URL:
        verify_path = getattr(settings, 'EMAIL_VERIFY_PATH', '/verify-email')
        ctx['verification_url'] = f"{settings.FRONTEND_URL.rstrip('/')}{verify_path}?email={email}&code={verification_code}"

    check_limits = not settings.DEBUG

    send_email(
        to_email=email,
        subject="Verify Your Email Address",
        template_name='verification_email',
        context=ctx,
        action_type='verification',
        check_limits=check_limits
    )

def send_password_reset_email(email: str, reset_code: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Send password reset code email."""
    ctx = context or {}
    ctx['reset_code'] = reset_code
    ctx['expiry_hours'] = RATE_LIMITS['reset']['lockout_seconds'] // 3600

    if settings.FRONTEND_URL:
        reset_path = getattr(settings, 'PASSWORD_RESET_PATH', '/reset-password')
        ctx['reset_url'] = f"{settings.FRONTEND_URL.rstrip('/')}{reset_path}?email={email}&code={reset_code}"

    send_email(
        to_email=email,
        subject="Reset Your Password",
        template_name='password_reset',
        context=ctx,
        action_type='reset'
    )
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

# Rate limiting configuration
RATE_LIMITS = {
    'verification': {'max_attempts': 3, 'lockout_seconds': 1800},  # 30 min
    'reset': {'max_attempts': 3, 'lockout_seconds': 1800},         # 30 min
    'enrollment': {'max_attempts': 5, 'lockout_seconds': 300},      # 5 min
    'quiz': {'max_attempts': 10, 'lockout_seconds': 600},          # 10 min
    'default': {'max_attempts': 5, 'lockout_seconds': 900}         # 15 min
}


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
            # It's a validation error dictionary
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

    # Get limits for action type
    limits = RATE_LIMITS.get(action_type, RATE_LIMITS['default'])
    max_attempts = limits['max_attempts']
    lockout_time = limits['lockout_seconds']

    # Normalize cache key
    cache_key = f"rate_limit_{action_type}_{identifier.lower().replace('@', '_at_').replace('.', '_dot_')}"

    # Check current attempts
    attempts = cache.get(cache_key, 0)
    if attempts >= max_attempts:
        # Fixed for Django 4.1.5's LocMemCache that doesn't have ttl method
        wait_minutes = lockout_time // 60
        logger.warning(f"Rate limit exceeded: {action_type} by {identifier}. Attempts: {attempts}/{max_attempts}")
        raise EmailRateLimitExceeded(wait_minutes=wait_minutes)

    # Increment attempts
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
    """
    Send an email using Django templates with rate limiting.
    """
    if not to_email:
        logger.error(f"Attempted to send email with empty recipient: {subject}")
        return False

    # Rate limiting
    if check_limits:
        try:
            check_rate_limit(to_email, action_type)
        except EmailRateLimitExceeded as e:
            logger.warning(f"Rate limit hit: {action_type} to {to_email}")
            raise e

    # Add common context data
    company_name = getattr(settings, 'COMPANY_NAME', 'E-Learning Platform')
    default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    frontend_url = getattr(settings, 'FRONTEND_URL', '').rstrip('/')

    context.update({
        'company_name': company_name,
        'frontend_url': frontend_url,
        'current_year': timezone.now().year,
    })

    # Format subject with company name
    full_subject = f"[{company_name}] {subject}"

    try:
        # Render email templates with better error handling
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
            # Fallback to HTML stripped of tags
            plain_message = strip_tags(html_message)

        # Debug mode console output
        if settings.DEBUG and 'console' in getattr(settings, 'EMAIL_BACKEND', ''):
            logger.info(f"\n{'='*40}\nEMAIL TO: {to_email}\nSUBJECT: {full_subject}\nTEMPLATE: {template_name}\n{'='*40}")
            # Log verification/reset codes only in debug
            if settings.DEBUG and action_type in ['verification', 'reset']:
                code = context.get('verification_code') or context.get('reset_code')
                if code:
                    logger.info(f"DEBUG - {action_type.upper()} CODE: {code}")
            return True

        # Send actual email
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

# Specific email functions with preset templates and contexts
def send_verification_email(email: str, verification_code: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Send verification code email."""
    ctx = context or {}
    ctx['verification_code'] = verification_code
    ctx['expiry_hours'] = RATE_LIMITS['verification']['lockout_seconds'] // 3600

    if settings.FRONTEND_URL:
        verify_path = getattr(settings, 'EMAIL_VERIFY_PATH', '/verify-email')
        ctx['verification_url'] = f"{settings.FRONTEND_URL.rstrip('/')}{verify_path}/{verification_code}"

    # Skip rate limiting in development
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
        ctx['reset_url'] = f"{settings.FRONTEND_URL.rstrip('/')}{reset_path}/{reset_code}"

    send_email(
        to_email=email,
        subject="Reset Your Password",
        template_name='password_reset',
        context=ctx,
        action_type='reset'
    )


def send_login_alert_email(email: str, ip_address: Optional[str] = None, location: Optional[str] = None,
                          device_info: Optional[str] = None, login_time=None) -> None:
    """Send alert for new device/location login."""
    send_email(
        to_email=email,
        subject="Security Alert: New Login Detected",
        template_name='login_alert',
        context={
            'ip_address': ip_address or 'Unknown',
            'location': location or 'Unknown location',
            'device_info': device_info or 'Unknown device',
            'login_time': login_time or timezone.now(),
        },
        action_type='notification',
        check_limits=False,
        fail_silently=True
    )


def send_welcome_email(email: str, user_name: str) -> None:
    """Send welcome email after successful verification."""
    send_email(
        to_email=email,
        subject="Welcome to Our Learning Platform!",
        template_name='welcome_email',
        context={
            'user_name': user_name,
        },
        action_type='notification',
        check_limits=False,
        fail_silently=True
    )


def send_course_enrollment_email(email: str, user_name: str, course_title: str, 
                                instructor_name: str, course_url: str) -> None:
    """Send course enrollment confirmation."""
    send_email(
        to_email=email,
        subject=f"Enrolled in {course_title}",
        template_name='course_enrollment',
        context={
            'user_name': user_name,
            'course_title': course_title,
            'instructor_name': instructor_name,
            'course_url': course_url,
        },
        action_type='enrollment',
        check_limits=True,
        fail_silently=True
    )


def send_certificate_email(email: str, user_name: str, course_title: str, 
                          certificate_url: str, certificate_number: str) -> None:
    """Send certificate earned notification."""
    send_email(
        to_email=email,
        subject=f"Certificate Earned: {course_title}",
        template_name='certificate_earned',
        context={
            'user_name': user_name,
            'course_title': course_title,
            'certificate_url': certificate_url,
            'certificate_number': certificate_number,
        },
        action_type='notification',
        check_limits=False,
        fail_silently=True
    )


# Simple debug request decorator
def debug_request(view_func):
    """Log request details in debug mode."""
    from functools import wraps
    import json

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)

        if settings.DEBUG:
            try:
                # Basic request info
                logger.debug(f"DEBUG: {request.method} {request.path}")

                # Request body for non-GET requests
                if request.method not in ['GET', 'HEAD'] and hasattr(request, 'body') and request.body:
                    content_type = request.META.get('CONTENT_TYPE', '').lower()
                    if 'application/json' in content_type:
                        try:
                            body = json.loads(request.body)
                            # Mask sensitive data
                            if isinstance(body, dict):
                                for k in body:
                                    if any(s in k.lower() for s in ['password', 'token', 'key', 'secret']):
                                        body[k] = '[REDACTED]'
                            logger.debug(f"BODY: {json.dumps(body)[:500]}")
                        except:
                            pass
            except:
                pass

        return response
    return wrapper
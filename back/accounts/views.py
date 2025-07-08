# back/accounts/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.signals import user_logged_out

from .models import UserProfile
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer, 
    UserProfileSerializer,
    UserProfileUpdateSerializer, 
    UserBriefSerializer, 
    PasswordChangeSerializer,
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer
)
from .permissions import IsOwnerOrReadOnly
from .utils import (
    send_verification_email, 
    send_password_reset_email,
    create_response,
    track_user_activity
)
import logging

logger = logging.getLogger('accounts')
security_logger = logging.getLogger('security')
User = get_user_model()

class LoginRateThrottle(UserRateThrottle):
    scope = 'login'

class PasswordResetRateThrottle(AnonRateThrottle):
    scope = 'password_reset'

class RegistrationRateThrottle(AnonRateThrottle):
    scope = 'registration'

# Authentication Views
class LoginView(TokenObtainPairView):
    """Enhanced login view with security features"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user_data = response.data.get('user', {})
            email = user_data.get('email')
            
            if email:
                try:
                    # Track login activity
                    user = User.objects.get(email=email)
                    track_user_activity(
                        user, 
                        'login',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT')
                    )
                    
                    # Update last login
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                except Exception as e:
                    logger.error(f"Login tracking error: {str(e)}")
                    # Don't fail login for tracking errors
        
        return response

class RegisterView(generics.CreateAPIView):
    """Enhanced registration view with security features"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = serializer.save()
            
            # Generate and send verification code
            verification_code = user.generate_verification_code()
            send_verification_email(user.email, verification_code, {
                'user_name': f"{user.first_name} {user.last_name}",
                'login_url': f"{request.build_absolute_uri('/')[:-1]}/login"
            })
            
            # Log registration
            security_logger.info(
                f"New user registered: {user.email} from {request.META.get('REMOTE_ADDR')}"
            )
            
            return create_response(
                data={'email': user.email},
                message='Registration successful. Please check your email for verification.',
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return create_response(
                error="Registration failed. Please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class VerifyEmailView(APIView):
    """Enhanced email verification with security logging"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = EmailVerificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            code = serializer.validated_data['verification_code']
            
            user = get_object_or_404(User, email=email)
            
            if user.is_verified:
                return create_response(
                    message='Email already verified',
                    status_code=status.HTTP_200_OK
                )
            
            if user.verify_account(code):
                # Generate tokens for immediate login
                refresh = RefreshToken.for_user(user)
                
                # Log verification
                security_logger.info(f"Email verified for user: {email}")
                
                return create_response(
                    data={
                        'tokens': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        },
                        'user': UserBriefSerializer(user).data
                    },
                    message='Email verified successfully',
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                error='Invalid or expired verification code',
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return create_response(
                error="Verification failed. Please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class ResendVerificationView(APIView):
    """Resend verification email with rate limiting"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return create_response(
                    error='Email is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            user = get_object_or_404(User, email=email)
            
            if user.is_verified:
                return create_response(
                    message='Email already verified',
                    status_code=status.HTTP_200_OK
                )
            
            # Check rate limiting
            cache_key = f"resend_verification_{email}"
            last_sent = cache.get(cache_key)
            
            if last_sent:
                return create_response(
                    error='Verification email was sent recently. Please wait before requesting another.',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Generate new code and send email
            verification_code = user.generate_verification_code()
            send_verification_email(user.email, verification_code, {
                'user_name': f"{user.first_name} {user.last_name}",
                'login_url': f"{request.build_absolute_uri('/')[:-1]}/login"
            })
            
            # Set rate limit (5 minutes)
            cache.set(cache_key, timezone.now(), timeout=300)
            
            return create_response(
                message='Verification email sent',
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Resend verification error: {str(e)}")
            return create_response(
                error="Failed to send verification email. Please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class PasswordResetRequestView(APIView):
    """Password reset request with enhanced security"""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    
    def post(self, request):
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                reset_code = user.generate_reset_code()
                send_password_reset_email(user.email, reset_code, {
                    'user_name': f"{user.first_name} {user.last_name}",
                    'reset_url': f"{request.build_absolute_uri('/')[:-1]}/reset-password?email={email}&code={reset_code}"
                })
                
                security_logger.info(f"Password reset requested for: {email}")
                
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                pass
            
            return create_response(
                message='If an account exists with this email, password reset instructions have been sent',
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            return create_response(
                error="Failed to process password reset. Please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class PasswordResetConfirmView(APIView):
    """Confirm password reset with enhanced validation"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = PasswordResetConfirmSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['new_password']
            
            user = get_object_or_404(User, email=email)
            
            if user.reset_password(reset_code, new_password):
                # Generate new tokens
                refresh = RefreshToken.for_user(user)
                
                # Log password reset
                security_logger.info(f"Password reset completed for: {email}")
                
                return create_response(
                    data={
                        'tokens': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }
                    },
                    message='Password reset successfully',
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                error='Invalid or expired reset code',
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Password reset confirm error: {str(e)}")
            return create_response(
                error="Failed to reset password. Please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(APIView):
    """Change password for authenticated users"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = PasswordChangeSerializer(
                data=request.data, 
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Generate new tokens
            refresh = RefreshToken.for_user(user)
            
            # Log password change
            security_logger.info(f"Password changed for user: {user.email}")
            
            return create_response(
                data={
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                },
                message='Password changed successfully',
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return create_response(
                error="Failed to change password. Please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class LogoutView(APIView):
    """Enhanced logout with token blacklisting"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Send logout signal
            user_logged_out.send(
                sender=request.user.__class__, 
                request=request, 
                user=request.user
            )
            
            # Log logout
            security_logger.info(f"User logged out: {request.user.email}")
            
            return create_response(
                message='Logged out successfully',
                status_code=status.HTTP_200_OK
            )
            
        except TokenError:
            pass  # Token already invalid/blacklisted
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
        
        return create_response(
            message='Logged out successfully',
            status_code=status.HTTP_200_OK
        )

# User Management Views
class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get and update current user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

class UserListView(generics.ListAPIView):
    """List users with filtering and search"""
    queryset = User.objects.filter(is_active=True, is_verified=True)
    serializer_class = UserBriefSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True, is_verified=True)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.select_related('profile')

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete user"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uuid'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

class UploadAvatarView(APIView):
    """Upload user avatar"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            if 'avatar' not in request.FILES:
                return create_response(
                    error='No avatar file provided',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            user = request.user
            user.avatar = request.FILES['avatar']
            user.save()
            
            return create_response(
                data=UserBriefSerializer(user, context={'request': request}).data,
                message='Avatar uploaded successfully',
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Avatar upload error: {str(e)}")
            return create_response(
                error="Failed to upload avatar. Please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, UserBriefSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .permissions import IsOwnerOrReadOnly
from .utils import send_verification_email, send_password_reset_email
from core.utils import track_activity

User = get_user_model()

# User Management
class UserListView(generics.ListAPIView):
    """List all users"""
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
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uuid'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserSerializer

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

# Authentication
class RegisterView(generics.CreateAPIView):
    """User registration"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate verification code and send email
        verification_code = user.generate_verification_code()
        send_verification_email(user.email, verification_code)
        
        return Response({
            'message': 'Registration successful. Please check your email for verification.',
            'email': user.email
        }, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    """Email verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('verification_code')
        
        user = get_object_or_404(User, email=email)
        
        if user.is_verified:
            return Response({'message': 'Email already verified'})
        
        if user.verify_account(code):
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Email verified successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': UserSerializer(user, context={'request': request}).data
            })
        
        return Response(
            {'error': 'Invalid or expired verification code'},
            status=status.HTTP_400_BAD_REQUEST
        )

class ResendVerificationView(APIView):
    """Resend verification email"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        
        if user.is_verified:
            return Response({'message': 'Email already verified'})
        
        verification_code = user.generate_verification_code()
        send_verification_email(user.email, verification_code)
        
        return Response({'message': 'Verification email sent'})

class LoginView(TokenObtainPairView):
    """Custom login view with additional user data"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            email = request.data.get('email', request.data.get('username'))
            user = User.objects.get(email=email)
            
            # Track login
            track_activity(
                user, 
                'login',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            # Add user data to response
            response.data['user'] = UserSerializer(user, context={'request': request}).data
        
        return response

class ChangePasswordView(APIView):
    """Change password for authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Generate new tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Password changed successfully',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

class PasswordResetRequestView(generics.GenericAPIView):
    """Request password reset"""
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            reset_code = user.generate_reset_code()
            send_password_reset_email(user.email, reset_code)
        except User.DoesNotExist:
            pass  # Don't reveal if email exists
        
        return Response({
            'message': 'If an account exists with this email, password reset instructions have been sent'
        })

class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirm password reset"""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(User, email=serializer.validated_data['email'])
        
        if user.reset_password(
            serializer.validated_data['reset_code'],
            serializer.validated_data['new_password']
        ):
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Password reset successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        
        return Response(
            {'error': 'Invalid or expired reset code'},
            status=status.HTTP_400_BAD_REQUEST
        )

class UploadAvatarView(APIView):
    """Upload user avatar"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save()
        
        return Response(UserSerializer(user, context={'request': request}).data)
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserListView, UserDetailView, CurrentUserView,
    RegisterView, LoginView, VerifyEmailView, ResendVerificationView,
    ChangePasswordView, PasswordResetRequestView, PasswordResetConfirmView,
    UploadAvatarView
)

app_name = 'accounts'

urlpatterns = [
    # User management
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<uuid:uuid>/', UserDetailView.as_view(), name='user-detail'),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('users/me/avatar/', UploadAvatarView.as_view(), name='upload-avatar'),
    
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
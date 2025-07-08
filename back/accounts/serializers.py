# back/accounts/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in
from .models import UserProfile
from .utils import track_login_attempt
from django.db import transaction
import logging

logger = logging.getLogger('accounts')
security_logger = logging.getLogger('security')
User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Enhanced token serializer with security logging and validation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        if 'username' in self.fields:
            del self.fields['username']  # Remove username field if it exists
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else None
        
        # Simple authentication without lockout
        
        # Authenticate user
        user = authenticate(request=request, email=email, password=password)
        
        if user is None:
            security_logger.warning(
                f"Failed login attempt for {email} from {ip_address}"
            )
            raise serializers.ValidationError(_('Invalid email or password.'))
        
        if not user.is_active:
            security_logger.warning(
                f"Login attempt for inactive user {email} from {ip_address}"
            )
            raise serializers.ValidationError(_('User account is disabled.'))
        
        if not user.is_verified:
            raise serializers.ValidationError(
                _('Email address is not verified. Please check your email.')
            )
        
        # Login successful
        
        # Log successful login
        security_logger.info(f"Successful login for {email} from {ip_address}")
        track_login_attempt(user, ip_address, success=True)
        
        # Call parent validation
        attrs['email'] = email
        attrs['username'] = email  # Use email as username for parent class
        data = super().validate(attrs)
        
        # Add user data to response
        refresh = self.get_token(user)
        data['user'] = UserBriefSerializer(user).data
        
        # Send login signal
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'uuid', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'avatar', 'role', 'is_verified',
            'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'uuid', 'email', 'is_verified', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_profile(self, obj):
        try:
            return {
                'bio': obj.profile.bio,
                'education_level': obj.profile.education_level,
                'institution': obj.profile.institution,
                'field_of_study': obj.profile.field_of_study,
                'learning_goals': obj.profile.learning_goals,
                'preferred_language': obj.profile.preferred_language,
                'time_zone': obj.profile.time_zone,
            }
        except UserProfile.DoesNotExist:
            return {}

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'email', 'password', 'confirm_password', 'first_name', 
            'last_name', 'phone_number', 'date_of_birth', 'role'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.pop('confirm_password', None):
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        logger.info(f"New user registered: {user.email}")
        return user

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    # User fields
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    # Profile fields
    bio = serializers.CharField(source='profile.bio', required=False, allow_blank=True)
    education_level = serializers.CharField(source='profile.education_level', required=False, allow_blank=True)
    institution = serializers.CharField(source='profile.institution', required=False, allow_blank=True)
    field_of_study = serializers.CharField(source='profile.field_of_study', required=False, allow_blank=True)
    learning_goals = serializers.CharField(source='profile.learning_goals', required=False, allow_blank=True)
    preferred_language = serializers.CharField(source='profile.preferred_language', required=False)
    time_zone = serializers.CharField(source='profile.time_zone', required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 'avatar',
            'bio', 'education_level', 'institution', 'field_of_study',
            'learning_goals', 'preferred_language', 'time_zone',
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = {}
        user_data = {}

        # Separate user and profile data
        for field_name, value in validated_data.items():
            if 'profile.' in str(self.fields.get(field_name).source):
                profile_field = self.fields.get(field_name).source.split('.')[-1]
                profile_data[profile_field] = value
            else:
                user_data[field_name] = value

        # Update user fields
        for attr, value in user_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        logger.info(f"User profile updated: {instance.email}")
        return instance

class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'uuid', 'email', 'full_name', 'role', 'role_display', 'avatar']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, 
        write_only=True, 
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("New passwords do not match.")})
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Current password is incorrect."))
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists for security
            pass
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    reset_code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(
        required=True, 
        write_only=True, 
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True, min_length=6, max_length=6)
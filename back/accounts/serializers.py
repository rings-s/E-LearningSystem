from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import UserProfile
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
            'groups': {'read_only': True},
            'user_permissions': {'read_only': True},
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.pop('confirm_password', None):
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        logger.info(f"User '{user.email}' created successfully")
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
    teaching_experience = serializers.IntegerField(source='profile.teaching_experience', required=False, allow_null=True)
    expertise_areas = serializers.CharField(source='profile.expertise_areas', required=False, allow_blank=True)
    certifications = serializers.CharField(source='profile.certifications', required=False, allow_blank=True)
    learning_goals = serializers.CharField(source='profile.learning_goals', required=False, allow_blank=True)
    preferred_language = serializers.CharField(source='profile.preferred_language', required=False)
    time_zone = serializers.CharField(source='profile.time_zone', required=False)
    address = serializers.CharField(source='profile.address', required=False, allow_blank=True)
    city = serializers.CharField(source='profile.city', required=False, allow_blank=True)
    state = serializers.CharField(source='profile.state', required=False, allow_blank=True)
    postal_code = serializers.CharField(source='profile.postal_code', required=False, allow_blank=True)
    country = serializers.CharField(source='profile.country', required=False, allow_blank=True)
    linkedin_url = serializers.URLField(source='profile.linkedin_url', required=False, allow_blank=True)
    github_url = serializers.URLField(source='profile.github_url', required=False, allow_blank=True)
    website_url = serializers.URLField(source='profile.website_url', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 'avatar',
            'bio', 'education_level', 'institution', 'field_of_study',
            'teaching_experience', 'expertise_areas', 'certifications',
            'learning_goals', 'preferred_language', 'time_zone',
            'address', 'city', 'state', 'postal_code', 'country',
            'linkedin_url', 'github_url', 'website_url',
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
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

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
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("New passwords do not match.")})
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    reset_code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        return attrs
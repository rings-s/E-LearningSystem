# back/core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import (
    Forum, Discussion, Reply, Notification, LearningAnalytics,
    ActivityLog, MediaContent, Announcement, SupportTicket
)

User = get_user_model()

# Forum Serializer
class ForumSerializer(serializers.ModelSerializer):
    # Computed fields for better frontend integration
    course_title = serializers.CharField(source='course.title', read_only=True)
    discussions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Forum
        fields = '__all__'
    
    def get_discussions_count(self, obj):
        return obj.discussions.count()

# Discussion Serializer
class DiscussionSerializer(serializers.ModelSerializer):
    # Computed fields
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    author_role = serializers.CharField(source='author.get_role_display', read_only=True)
    replies_count = serializers.SerializerMethodField()
    latest_reply = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = '__all__'
        extra_kwargs = {
            'author': {'read_only': True},
            'views_count': {'read_only': True},
        }
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def get_latest_reply(self, obj):
        latest = obj.replies.order_by('-created_at').first()
        if latest:
            return {
                'author_name': latest.author.get_full_name(),
                'created_at': latest.created_at,
                'preview': latest.content[:100] + '...' if len(latest.content) > 100 else latest.content
            }
        return None
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

# Reply Serializer
class ReplySerializer(serializers.ModelSerializer):
    # Computed fields
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    author_role = serializers.CharField(source='author.get_role_display', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Reply
        fields = '__all__'
        extra_kwargs = {
            'author': {'read_only': True},
            'upvotes': {'read_only': True},
            'is_instructor_reply': {'read_only': True},
        }
    
    def get_children(self, obj):
        return ReplySerializer(obj.children.all(), many=True, context=self.context).data
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        
        # Set instructor reply flag
        if user.role in ['teacher', 'moderator', 'manager'] or user.is_staff:
            validated_data['is_instructor_reply'] = True
            
        return super().create(validated_data)

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    # Computed fields
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        extra_kwargs = {
            'recipient': {'read_only': True},
            'email_sent': {'read_only': True},
            'email_sent_at': {'read_only': True},
        }

# Learning Analytics Serializer
class LearningAnalyticsSerializer(serializers.ModelSerializer):
    # Computed fields
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    completion_percentage = serializers.DecimalField(
        source='enrollment.progress_percentage', 
        max_digits=5, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = LearningAnalytics
        fields = '__all__'
        extra_kwargs = {
            'last_activity': {'read_only': True},
        }

# Activity Log Serializer
class ActivityLogSerializer(serializers.ModelSerializer):
    # Computed fields
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    
    class Meta:
        model = ActivityLog
        fields = '__all__'

# Media Content Serializer
class MediaContentSerializer(serializers.ModelSerializer):
    # Computed fields
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaContent
        fields = '__all__'
        extra_kwargs = {
            'uploaded_by': {'read_only': True},
            'usage_count': {'read_only': True},
            'file_size': {'read_only': True},
            'mime_type': {'read_only': True},
        }
    
    def get_file_size_mb(self, obj):
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['uploaded_by'] = user
        
        file_obj = validated_data.get('file')
        if file_obj:
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = file_obj.content_type
            
        return super().create(validated_data)

# Announcement Serializer
class AnnouncementSerializer(serializers.ModelSerializer):
    # Computed fields
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'
        extra_kwargs = {
            'author': {'read_only': True},
        }
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

# Support Ticket Serializer
class SupportTicketSerializer(serializers.ModelSerializer):
    # Computed fields
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    
    class Meta:
        model = SupportTicket
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'ticket_number': {'read_only': True},
            'resolved_at': {'read_only': True},
        }
    
    def validate_subject(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Subject must be at least 5 characters long")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError("Description must be at least 20 characters long")
        return value.strip()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
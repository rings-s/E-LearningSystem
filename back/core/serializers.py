from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import (
    Forum, Discussion, Reply, Notification, LearningAnalytics,
    ActivityLog, MediaContent, Announcement, SupportTicket
)

User = get_user_model()

# Discussion Forum
class ForumSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    discussions_count = serializers.IntegerField(source='discussions.count', read_only=True)
    
    class Meta:
        model = Forum
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class ReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    author_role = serializers.CharField(source='author.get_role_display', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Reply
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'edited_at', 'upvotes', 'is_instructor_reply']
    
    def get_children(self, obj):
        return ReplySerializer(obj.children.all(), many=True, context=self.context).data

class DiscussionSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    author_role = serializers.CharField(source='author.get_role_display', read_only=True)
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    latest_reply = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'views_count']
    
    def get_latest_reply(self, obj):
        latest = obj.replies.order_by('-created_at').first()
        if latest:
            return {
                'author_name': latest.author.get_full_name(),
                'created_at': latest.created_at,
                'preview': latest.content[:100] + '...' if len(latest.content) > 100 else latest.content
            }
        return None

class DiscussionDetailSerializer(DiscussionSerializer):
    replies = ReplySerializer(many=True, read_only=True)
    
    class Meta:
        model = Discussion
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'views_count']

class DiscussionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['forum', 'title', 'content', 'discussion_type']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class ReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['discussion', 'content', 'parent']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        user = self.context['request'].user
        if user.role in ['teacher', 'moderator', 'manager'] or user.is_staff:
            validated_data['is_instructor_reply'] = True
        return super().create(validated_data)

# Notifications
class NotificationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'email_sent', 'email_sent_at']

class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']

# Analytics
class LearningAnalyticsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    completion_percentage = serializers.DecimalField(
        source='enrollment.progress_percentage', 
        max_digits=5, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = LearningAnalytics
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'last_activity']

class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True, allow_null=True)
    
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at']

# Media Content
class MediaContentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaContent
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'usage_count', 'file_size', 'mime_type']
    
    def get_file_size_mb(self, obj):
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None

class MediaContentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaContent
        fields = ['title', 'description', 'content_type', 'file', 'course', 'lesson']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        file_obj = validated_data.get('file')
        if file_obj:
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = file_obj.content_type
        return super().create(validated_data)

# Announcements
class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'announcement_type', 'course', 
            'target_roles', 'is_pinned', 'show_from', 'show_until'
        ]
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

# Support
class SupportTicketSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    
    class Meta:
        model = SupportTicket
        fields = '__all__'
        read_only_fields = ['uuid', 'ticket_number', 'created_at', 'updated_at', 'resolved_at']

class SupportTicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'description', 'priority', 'course']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SupportTicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'assigned_to']

# Dashboard Serializers
class StudentDashboardSerializer(serializers.Serializer):
    enrolled_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    in_progress_courses = serializers.IntegerField()
    total_certificates = serializers.IntegerField()
    total_study_hours = serializers.IntegerField()
    average_score = serializers.FloatField()
    recent_activities = ActivityLogSerializer(many=True)
    upcoming_lessons = serializers.ListField()

class TeacherDashboardSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    published_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    average_rating = serializers.FloatField()
    recent_reviews = serializers.ListField()
    pending_questions = serializers.IntegerField()
    course_analytics = serializers.ListField()

class ManagerDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    revenue_this_month = serializers.DecimalField(max_digits=10, decimal_places=2)
    popular_courses = serializers.ListField()
    user_growth = serializers.ListField()
    system_health = serializers.DictField()
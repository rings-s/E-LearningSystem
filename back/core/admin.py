from django.contrib import admin
from .models import (
    Forum, Discussion, Reply, Notification, LearningAnalytics, 
    ActivityLog, MediaContent, Announcement, SupportTicket
)

# Inline classes

class DiscussionInline(admin.StackedInline):
    model = Discussion
    extra = 1
    fields = ('author', 'title', 'discussion_type', 'is_pinned', 'is_locked')
    raw_id_fields = ('author',)

class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 1
    fields = ('author', 'content', 'is_solution', 'is_instructor_reply')
    raw_id_fields = ('author',)

# ModelAdmin classes

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'is_active', 'is_moderated', 'created_at')
    list_filter = ('is_active', 'is_moderated')
    search_fields = ('name', 'course__title')
    inlines = [DiscussionInline]
    autocomplete_fields = ('course',)

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'forum', 'author', 'discussion_type', 'is_resolved', 'created_at')
    list_filter = ('discussion_type', 'is_pinned', 'is_locked', 'is_resolved', 'forum__course')
    search_fields = ('title', 'content', 'author__email', 'forum__name')
    inlines = [ReplyInline]
    raw_id_fields = ('author', 'forum')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'discussion', 'is_solution', 'created_at')
    list_filter = ('is_solution', 'is_instructor_reply', 'discussion__forum__course')
    search_fields = ('content', 'author__email', 'discussion__title')
    raw_id_fields = ('author', 'discussion', 'parent')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__email', 'title', 'message')
    raw_id_fields = ('recipient', 'course', 'lesson', 'discussion')
    readonly_fields = ('created_at', 'read_at', 'email_sent_at')

@admin.register(LearningAnalytics)
class LearningAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'last_activity')
    search_fields = ('user__email', 'course__title')
    autocomplete_fields = ('user', 'course', 'enrollment')
    readonly_fields = ('created_at', 'updated_at', 'last_activity')

    def progress_percentage(self, obj):
        return f"{obj.enrollment.progress_percentage} %"
    progress_percentage.short_description = 'Progress'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'created_at', 'ip_address')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('created_at',)

@admin.register(MediaContent)
class MediaContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'file_size', 'uploaded_by', 'created_at')
    list_filter = ('content_type',)
    search_fields = ('title', 'description', 'uploaded_by__email')
    readonly_fields = ('file_size', 'mime_type', 'created_at', 'updated_at')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'is_active', 'is_pinned', 'show_from', 'show_until')
    list_filter = ('announcement_type', 'is_active', 'is_pinned')
    search_fields = ('title', 'content')
    raw_id_fields = ('author', 'course')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'subject', 'user', 'status', 'priority', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'assigned_to')
    search_fields = ('ticket_number', 'subject', 'description', 'user__email')
    raw_id_fields = ('user', 'assigned_to', 'course')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'resolved_at')
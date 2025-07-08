# back/core/models.py - Fixed imports
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import uuid

# Fix for JSONField import based on Django version
try:
    from django.db.models import JSONField
except ImportError:
    # Fallback for older Django versions
    from django.contrib.postgres.fields import JSONField


User = get_user_model()

# Discussion Forum
class Forum(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    course = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='forum')
    
    name = models.CharField(max_length=200, verbose_name=_('Forum Name'))
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    is_moderated = models.BooleanField(default=False)
    
    rules = models.TextField(blank=True, verbose_name=_('Forum Rules'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')
        ordering = ['-created_at', 'id']  # Add this line

    def __str__(self):
        return f"Forum: {self.course.title}"

class Discussion(models.Model):
    DISCUSSION_TYPE_CHOICES = [
        ('question', _('Question')),
        ('discussion', _('Discussion')),
        ('announcement', _('Announcement')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='discussions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    
    discussion_type = models.CharField(max_length=20, choices=DISCUSSION_TYPE_CHOICES, default='discussion')
    
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Discussion')
        verbose_name_plural = _('Discussions')
        ordering = ['-is_pinned', '-created_at', 'id']  # Add explicit ordering with tiebreaker


    def __str__(self):
        return self.title

class Reply(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_replies')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    
    content = models.TextField(verbose_name=_('Reply Content'))
    
    is_solution = models.BooleanField(default=False)
    is_instructor_reply = models.BooleanField(default=False)
    
    upvotes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Reply')
        verbose_name_plural = _('Replies')
        ordering = ['created_at', 'id']  # Add this line


    def __str__(self):
        return f"Reply to: {self.discussion.title} by {self.author.email}"

# Notifications
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('enrollment', _('New Enrollment')),
        ('course_update', _('Course Update')),
        ('lesson_available', _('New Lesson Available')),
        ('assignment_due', _('Assignment Due')),
        ('quiz_result', _('Quiz Result')),
        ('certificate_ready', _('Certificate Ready')),
        ('forum_reply', _('Forum Reply')),
        ('announcement', _('Announcement')),
        ('system', _('System Notification')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    message = models.TextField(verbose_name=_('Message'))
    
    # Related objects
    course = models.ForeignKey('courses.Course', null=True, blank=True, on_delete=models.CASCADE)
    lesson = models.ForeignKey('courses.Lesson', null=True, blank=True, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion, null=True, blank=True, on_delete=models.CASCADE)
    
    # Action URL
    action_url = models.CharField(max_length=500, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Email notification
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at', 'id']  # Add explicit tiebreaker
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]


    def __str__(self):
        return f"{self.notification_type} - {self.recipient.email} - {self.title}"

# Analytics
class LearningAnalytics(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_analytics')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='analytics')
    enrollment = models.ForeignKey('courses.Enrollment', on_delete=models.CASCADE, related_name='analytics')
    
    # Time tracking
    total_time_spent_seconds = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Progress metrics
    lessons_completed = models.PositiveIntegerField(default=0)
    quizzes_attempted = models.PositiveIntegerField(default=0)
    quizzes_passed = models.PositiveIntegerField(default=0)
    assignments_submitted = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_quiz_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    highest_quiz_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Engagement metrics
    forum_posts = models.PositiveIntegerField(default=0)
    forum_replies = models.PositiveIntegerField(default=0)
    resources_accessed = models.PositiveIntegerField(default=0)
    
    # Learning path
    learning_path_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Learning Analytics')
        verbose_name_plural = _('Learning Analytics')
        unique_together = ['user', 'course']

    def __str__(self):
        return f"Analytics: {self.user.email} - {self.course.title}"

class ActivityLog(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('course_view', _('Course Viewed')),
        ('lesson_start', _('Lesson Started')),
        ('lesson_complete', _('Lesson Completed')),
        ('quiz_start', _('Quiz Started')),
        ('quiz_submit', _('Quiz Submitted')),
        ('resource_download', _('Resource Downloaded')),
        ('forum_post', _('Forum Post Created')),
        ('forum_reply', _('Forum Reply Posted')),
        ('assignment_submit', _('Assignment Submitted')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    
    # Related objects
    course = models.ForeignKey('courses.Course', null=True, blank=True, on_delete=models.CASCADE)
    lesson = models.ForeignKey('courses.Lesson', null=True, blank=True, on_delete=models.CASCADE)
    quiz = models.ForeignKey('courses.Quiz', null=True, blank=True, on_delete=models.CASCADE)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    # Request info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Activity Log')
        verbose_name_plural = _('Activity Logs')
        ordering = ['-created_at', 'id']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"

# Content Management
class MediaContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', _('Video')),
        ('audio', _('Audio')),
        ('image', _('Image')),
        ('document', _('Document')),
        ('presentation', _('Presentation')),
        ('archive', _('Archive')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True)
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    
    file = models.FileField(upload_to='content/media/', validators=[
        FileExtensionValidator(allowed_extensions=[
            'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm',  # Video
            'mp3', 'wav', 'ogg', 'm4a',  # Audio
            'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp',  # Image
            'pdf', 'doc', 'docx', 'txt', 'odt',  # Document
            'ppt', 'pptx', 'odp',  # Presentation
            'zip', 'rar', '7z', 'tar', 'gz',  # Archive
        ])
    ])
    
    file_size = models.PositiveBigIntegerField(verbose_name=_('File Size (bytes)'))
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Video/Audio specific
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Image specific
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Relationships
    course = models.ForeignKey('courses.Course', null=True, blank=True, on_delete=models.CASCADE, related_name='media_contents')
    lesson = models.ForeignKey('courses.Lesson', null=True, blank=True, on_delete=models.CASCADE, related_name='media_contents')
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Media Content')
        verbose_name_plural = _('Media Contents')
        ordering = ['-created_at', 'id']

    def __str__(self):
        return f"{self.title} ({self.content_type})"

# Announcements
class Announcement(models.Model):
    ANNOUNCEMENT_TYPE_CHOICES = [
        ('general', _('General')),
        ('course', _('Course Specific')),
        ('system', _('System')),
        ('maintenance', _('Maintenance')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPE_CHOICES, default='general')
    
    # Target audience
    course = models.ForeignKey('courses.Course', null=True, blank=True, on_delete=models.CASCADE, related_name='announcements')
    target_roles = models.JSONField(default=list, blank=True)  # ['student', 'teacher', etc.]
    
    # Display settings
    is_active = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    show_from = models.DateTimeField(null=True, blank=True)
    show_until = models.DateTimeField(null=True, blank=True)
    
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_pinned', '-created_at', 'id']

    def __str__(self):
        return self.title

# Support/Help
class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    description = models.TextField(verbose_name=_('Description'))
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Related to
    course = models.ForeignKey('courses.Course', null=True, blank=True, on_delete=models.SET_NULL)
    
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tickets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Support Ticket')
        verbose_name_plural = _('Support Tickets')
        ordering = ['-created_at', 'id']

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import datetime
            prefix = "TKT"
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.ticket_number = f"{prefix}-{timestamp}"
        super().save(*args, **kwargs)

# User Activity (for accounts tracking)
class UserActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('login', _('User Login')),
        ('login_success', _('Successful Login')),
        ('login_failed', _('Failed Login')),
        ('logout', _('User Logout')),
        ('profile_update', _('Profile Update')),
        ('password_change', _('Password Change')),
        ('email_verification', _('Email Verification')),
        ('password_reset', _('Password Reset')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    
    # Request info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-created_at', 'id']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"
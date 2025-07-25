# Generated by Django 5.2 on 2025-06-13 16:58

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('content', models.TextField(verbose_name='Content')),
                ('announcement_type', models.CharField(choices=[('general', 'General'), ('course', 'Course Specific'), ('system', 'System'), ('maintenance', 'Maintenance')], default='general', max_length=20)),
                ('target_roles', models.JSONField(blank=True, default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('is_pinned', models.BooleanField(default=False)),
                ('show_from', models.DateTimeField(blank=True, null=True)),
                ('show_until', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='courses.course')),
            ],
            options={
                'verbose_name': 'Announcement',
                'verbose_name_plural': 'Announcements',
                'ordering': ['-is_pinned', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=200, verbose_name='Forum Name')),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_moderated', models.BooleanField(default=False)),
                ('rules', models.TextField(blank=True, verbose_name='Forum Rules')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='forum', to='courses.course')),
            ],
            options={
                'verbose_name': 'Forum',
                'verbose_name_plural': 'Forums',
            },
        ),
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('content', models.TextField(verbose_name='Content')),
                ('discussion_type', models.CharField(choices=[('question', 'Question'), ('discussion', 'Discussion'), ('announcement', 'Announcement')], default='discussion', max_length=20)),
                ('is_pinned', models.BooleanField(default=False)),
                ('is_locked', models.BooleanField(default=False)),
                ('is_resolved', models.BooleanField(default=False)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussions', to=settings.AUTH_USER_MODEL)),
                ('forum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussions', to='core.forum')),
            ],
            options={
                'verbose_name': 'Discussion',
                'verbose_name_plural': 'Discussions',
                'ordering': ['-is_pinned', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MediaContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('description', models.TextField(blank=True)),
                ('content_type', models.CharField(choices=[('video', 'Video'), ('audio', 'Audio'), ('image', 'Image'), ('document', 'Document'), ('presentation', 'Presentation'), ('archive', 'Archive')], max_length=20)),
                ('file', models.FileField(upload_to='content/media/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mp3', 'wav', 'ogg', 'm4a', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'pdf', 'doc', 'docx', 'txt', 'odt', 'ppt', 'pptx', 'odp', 'zip', 'rar', '7z', 'tar', 'gz'])])),
                ('file_size', models.PositiveBigIntegerField(verbose_name='File Size (bytes)')),
                ('mime_type', models.CharField(blank=True, max_length=100)),
                ('duration_seconds', models.PositiveIntegerField(blank=True, null=True)),
                ('width', models.PositiveIntegerField(blank=True, null=True)),
                ('height', models.PositiveIntegerField(blank=True, null=True)),
                ('usage_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='media_contents', to='courses.course')),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='media_contents', to='courses.lesson')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Media Content',
                'verbose_name_plural': 'Media Contents',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('content', models.TextField(verbose_name='Reply Content')),
                ('is_solution', models.BooleanField(default=False)),
                ('is_instructor_reply', models.BooleanField(default=False)),
                ('upvotes', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('edited_at', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussion_replies', to=settings.AUTH_USER_MODEL)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='core.discussion')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.reply')),
            ],
            options={
                'verbose_name': 'Reply',
                'verbose_name_plural': 'Replies',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('ticket_number', models.CharField(editable=False, max_length=20, unique=True)),
                ('subject', models.CharField(max_length=200, verbose_name='Subject')),
                ('description', models.TextField(verbose_name='Description')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed')], default='open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_tickets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Support Ticket',
                'verbose_name_plural': 'Support Tickets',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('activity_type', models.CharField(choices=[('course_view', 'Course Viewed'), ('lesson_start', 'Lesson Started'), ('lesson_complete', 'Lesson Completed'), ('quiz_start', 'Quiz Started'), ('quiz_submit', 'Quiz Submitted'), ('resource_download', 'Resource Downloaded'), ('forum_post', 'Forum Post Created'), ('forum_reply', 'Forum Reply Posted'), ('assignment_submit', 'Assignment Submitted')], max_length=30)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.lesson')),
                ('quiz', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Activity Log',
                'verbose_name_plural': 'Activity Logs',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'created_at'], name='core_activi_user_id_599332_idx'), models.Index(fields=['activity_type', 'created_at'], name='core_activi_activit_e5ffd8_idx')],
            },
        ),
        migrations.CreateModel(
            name='LearningAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('total_time_spent_seconds', models.PositiveIntegerField(default=0)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('lessons_completed', models.PositiveIntegerField(default=0)),
                ('quizzes_attempted', models.PositiveIntegerField(default=0)),
                ('quizzes_passed', models.PositiveIntegerField(default=0)),
                ('assignments_submitted', models.PositiveIntegerField(default=0)),
                ('average_quiz_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('highest_quiz_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('forum_posts', models.PositiveIntegerField(default=0)),
                ('forum_replies', models.PositiveIntegerField(default=0)),
                ('resources_accessed', models.PositiveIntegerField(default=0)),
                ('learning_path_data', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='courses.course')),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='courses.enrollment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_analytics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Learning Analytics',
                'verbose_name_plural': 'Learning Analytics',
                'unique_together': {('user', 'course')},
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('notification_type', models.CharField(choices=[('enrollment', 'New Enrollment'), ('course_update', 'Course Update'), ('lesson_available', 'New Lesson Available'), ('assignment_due', 'Assignment Due'), ('quiz_result', 'Quiz Result'), ('certificate_ready', 'Certificate Ready'), ('forum_reply', 'Forum Reply'), ('announcement', 'Announcement'), ('system', 'System Notification')], max_length=30)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('message', models.TextField(verbose_name='Message')),
                ('action_url', models.CharField(blank=True, max_length=500)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('discussion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.discussion')),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.lesson')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['recipient', 'is_read'], name='core_notifi_recipie_aeffaf_idx'), models.Index(fields=['created_at'], name='core_notifi_created_d0c445_idx')],
            },
        ),
    ]

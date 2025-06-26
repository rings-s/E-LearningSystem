from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django import forms
import csv
import datetime
from .models import (
    Category, Tag, Course, Enrollment, Module, Lesson, LessonProgress, Resource,
    Quiz, Question, Answer, QuizAttempt, QuestionResponse, Certificate, CourseReview
)

# Custom Admin Mixins
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields if field.name != 'uuid']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}_export_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)

        return response

    export_as_csv.short_description = _("Export Selected as CSV")

# Resource Inline
class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1
    fields = ('title', 'resource_type', 'file', 'url', 'order', 'is_required')

# Answer Inline
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2
    fields = ('answer_text', 'is_correct', 'order', 'feedback')

# Question Inline
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('question_text', 'question_type', 'points', 'order', 'is_required', 'explanation')
    inlines = [AnswerInline]

# Lesson Inline
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    fields = ('title', 'slug', 'content_type', 'video_url', 'video_duration', 'text_content', 
              'file_attachment', 'order', 'is_preview', 'is_published', 'requires_submission', 'points')
    prepopulated_fields = {'slug': ('title',)}

# Quiz Inline
class QuizInline(admin.StackedInline):
    model = Quiz
    extra = 1
    fields = ('title', 'quiz_type', 'passing_score', 'max_attempts', 'time_limit_minutes', 
              'randomize_questions', 'is_published')

# Module Inline
class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    fields = ('title', 'description', 'order', 'is_published')
    inlines = [LessonInline]

# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Hierarchy'), {
            'fields': ('parent', 'icon', 'order')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, _("Selected categories activated"))
    make_active.short_description = _("Activate selected categories")

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, _("Selected categories deactivated"))
    make_inactive.short_description = _("Deactivate selected categories")

# Tag Admin
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# Course Admin
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        published_at = cleaned_data.get('published_at')
        if status == 'published' and not published_at:
            cleaned_data['published_at'] = datetime.datetime.now()
        return cleaned_data

class CourseAdmin(admin.ModelAdmin, ExportCsvMixin):
    form = CourseForm
    list_display = ('title', 'instructor', 'category', 'level', 'status', 'is_featured', 
                    'enrolled_students_count', 'average_rating', 'views_count', 'created_at')
    
    list_filter = ('status', 'level', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'description', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('co_instructors', 'tags')
    inlines = [ModuleInline, QuizInline]
    actions = ['publish_courses', 'archive_courses', 'export_as_csv']
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'views_count')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        (_('Organization'), {
            'fields': ('category', 'tags')
        }),
        (_('Instructors'), {
            'fields': ('instructor', 'co_instructors')
        }),
        (_('Content Details'), {
            'fields': ('level', 'language', 'duration_hours', 'prerequisites', 'learning_outcomes')
        }),
        (_('Media'), {
            'fields': ('thumbnail', 'preview_video')
        }),
        (_('Settings'), {
            'fields': ('status', 'is_featured', 'enrollment_limit', 'certificate_template')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'published_at')
        }),
    )

    def publish_courses(self, request, queryset):
        for course in queryset:
            course.publish()
        self.message_user(request, _("Selected courses published"))
    publish_courses.short_description = _("Publish selected courses")

    def archive_courses(self, request, queryset):
        queryset.update(status='archived')
        self.message_user(request, _("Selected courses archived"))
    archive_courses.short_description = _("Archive selected courses")

# Module Admin
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published', 'created_at')
    list_filter = ('is_published', 'course', 'created_at')
    search_fields = ('title', 'description')
    inlines = [LessonInline]
    list_editable = ('order', 'is_published')

# Enrollment Admin
class EnrollmentAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('student', 'course', 'status', 'progress_percentage', 'enrolled_at', 
                    'certificate_issued')
    list_filter = ('status', 'is_active', 'certificate_issued', 'enrolled_at')
    search_fields = ('student__email', 'course__title')
    actions = ['issue_certificates', 'export_as_csv']
    readonly_fields = ('enrolled_at', 'started_at', 'completed_at', 'certificate_issued_at')

    def issue_certificates(self, request, queryset):
        for enrollment in queryset.filter(status='completed', certificate_issued=False):
            Certificate.objects.create(
                student=enrollment.student,
                course=enrollment.course,
                enrollment=enrollment,
                completion_date=datetime.date.today(),
                final_score=85.00  # Example score
            )
            enrollment.certificate_issued = True
            enrollment.certificate_issued_at = datetime.datetime.now()
            enrollment.save()
        self.message_user(request, _("Certificates issued for selected enrollments"))
    issue_certificates.short_description = _("Issue certificates for selected enrollments")

# Lesson Admin
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'content_type', 'is_published', 'is_preview', 'order')
    list_filter = ('content_type', 'is_published', 'is_preview', 'module__course')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ResourceInline, QuizInline]

# LessonProgress Admin
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'time_spent_seconds', 'started_at')
    list_filter = ('is_completed', 'started_at')
    search_fields = ('enrollment__student__email', 'lesson__title')
    readonly_fields = ('started_at', 'completed_at')

# Resource Admin
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'resource_type', 'is_required', 'order')
    list_filter = ('resource_type', 'is_required')
    search_fields = ('title', 'description')

# Quiz Admin
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'quiz_type', 'is_published', 'passing_score')
    list_filter = ('quiz_type', 'is_published', 'course')
    search_fields = ('title', 'instructions')
    inlines = [QuestionInline]

# Question Admin
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz__course')
    search_fields = ('question_text',)
    inlines = [AnswerInline]

    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = _('Question Text')

# Answer Admin
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_text_short', 'question', 'is_correct', 'order')
    list_filter = ('is_correct',)
    search_fields = ('answer_text',)

    def answer_text_short(self, obj):
        return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
    answer_text_short.short_description = _('Answer Text')

# QuizAttempt Admin
class QuizAttemptAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('student', 'quiz', 'score', 'passed', 'attempt_number', 'started_at')
    list_filter = ('passed', 'quiz__course', 'started_at')
    search_fields = ('student__email', 'quiz__title')
    actions = ['export_as_csv']
    readonly_fields = ('started_at', 'completed_at')

# QuestionResponse Admin
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'points_earned', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('question__question_text',)
    readonly_fields = ('answered_at',)

# Certificate Admin
class CertificateAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('certificate_number', 'student', 'course', 'issue_date', 'is_valid', 'view_verification')
    list_filter = ('is_valid', 'issue_date')
    search_fields = ('certificate_number', 'student__email', 'course__title')
    actions = ['invalidate_certificates', 'export_as_csv']
    readonly_fields = ('created_at', 'updated_at', 'issue_date', 'qr_code')

    def view_verification(self, obj):
        if obj.verification_url:
            return format_html('<a href="{}" target="_blank">Verify</a>', obj.verification_url)
        return '-'
    view_verification.short_description = _('Verification URL')

    def invalidate_certificates(self, request, queryset):
        queryset.update(is_valid=False)
        self.message_user(request, _("Selected certificates invalidated"))
    invalidate_certificates.short_description = _("Invalidate selected certificates")

# CourseReview Admin
class CourseReviewAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('course', 'student', 'rating', 'comment_short', 'is_verified', 'helpful_count')
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('comment', 'student__email', 'course__title')
    actions = ['verify_reviews', 'export_as_csv']
    readonly_fields = ('created_at', 'updated_at')

    def comment_short(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_short.short_description = _('Comment')

    def verify_reviews(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, _("Selected reviews verified"))
    verify_reviews.short_description = _("Verify selected reviews")

# Register Models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonProgress, LessonProgressAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(QuestionResponse, QuestionResponseAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(CourseReview, CourseReviewAdmin)
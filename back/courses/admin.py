
from django.contrib import admin
from .models import (
    Category, Tag, Course, Enrollment, Module, Lesson, LessonProgress, 
    Resource, Quiz, Question, Answer, QuizAttempt, QuestionResponse, 
    Certificate, CourseReview, CourseFavorite, Assignment, AssignmentSubmission
)

# Inline classes for better management in the admin panel

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    prepopulated_fields = {'slug': ('title',)}

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

class CoInstructorInline(admin.TabularInline):
    model = Course.co_instructors.through
    verbose_name = "Co-instructor"
    verbose_name_plural = "Co-instructors"
    extra = 1

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2

# ModelAdmin classes

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'level', 'status', 'is_featured', 'published_at')
    list_filter = ('status', 'level', 'is_featured', 'category', 'instructor')
    search_fields = ('title', 'description', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline, CoInstructorInline]
    autocomplete_fields = ('instructor', 'category')
    filter_horizontal = ('tags', 'co_instructors')
    readonly_fields = ('published_at', 'views_count')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'instructor', 'description', 'short_description')
        }),
        ('Details', {
            'fields': ('category', 'tags', 'level', 'language', 'duration_hours', 'prerequisites', 'learning_outcomes')
        }),
        ('Media', {
            'fields': ('thumbnail', 'preview_video')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'enrollment_limit', 'published_at')
        }),
        ('Certificate', {
            'fields': ('certificate_template',)
        }),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'enrolled_at', 'completed_at', 'progress_percentage')
    list_filter = ('status', 'course', 'student')
    search_fields = ('student__email', 'course__title')
    autocomplete_fields = ('student', 'course')
    readonly_fields = ('enrolled_at',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published')
    list_filter = ('course', 'is_published')
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]
    ordering = ('course', 'order')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'content_type', 'order', 'is_published')
    list_filter = ('module__course', 'content_type', 'is_published')
    search_fields = ('title', 'description', 'module__title')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('module', 'order')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at', 'time_spent_seconds')
    list_filter = ('is_completed', 'lesson__module__course')
    search_fields = ('enrollment__student__email', 'lesson__title')
    autocomplete_fields = ('enrollment', 'lesson')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'resource_type', 'order')
    list_filter = ('resource_type', 'lesson__module__course')
    search_fields = ('title', 'description')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'quiz_type', 'is_published', 'passing_score')
    list_filter = ('quiz_type', 'is_published', 'course')
    search_fields = ('title', 'instructions', 'course__title')
    inlines = [QuestionInline]
    autocomplete_fields = ('course', 'lesson', 'module')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz__course')
    search_fields = ('question_text', 'quiz__title')
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz__course')
    search_fields = ('answer_text', 'question__question_text')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'attempt_number', 'score', 'passed', 'completed_at')
    list_filter = ('passed', 'quiz__course', 'student')
    search_fields = ('student__email', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at')

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'points_earned')
    list_filter = ('is_correct', 'question__quiz__course')
    search_fields = ('attempt__student__email', 'question__question_text')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student', 'course', 'issue_date', 'is_valid')
    list_filter = ('is_valid', 'course')
    search_fields = ('certificate_number', 'student__email', 'course__title')
    readonly_fields = ('issue_date', 'created_at', 'updated_at', 'pdf_file', 'qr_code')
    autocomplete_fields = ('student', 'course', 'enrollment')

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating', 'created_at', 'is_verified')
    list_filter = ('rating', 'is_verified', 'course')
    search_fields = ('student__email', 'course__title', 'comment')

@admin.register(CourseFavorite)
class CourseFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    search_fields = ('user__email', 'course__title')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'due_date', 'max_points')
    list_filter = ('lesson__module__course',)
    search_fields = ('title', 'description')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submission_date', 'grade', 'status')
    list_filter = ('status', 'assignment__lesson__module__course')
    search_fields = ('student__email', 'assignment__title')
    readonly_fields = ('submission_date',)

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from django.template.loader import render_to_string
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

User = get_user_model()

# Category and Tags
class Category(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200, unique=True, verbose_name=_('Category Name'))
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Icon Class'))
    order = models.IntegerField(default=0, verbose_name=_('Display Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name', 'id']

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# Course Management
class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200, verbose_name=_('Course Title'))
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name=_('Description'))
    short_description = models.CharField(max_length=255, verbose_name=_('Short Description'))
    
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='teaching_courses')
    co_instructors = models.ManyToManyField(User, blank=True, related_name='co_teaching_courses')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    tags = models.ManyToManyField(Tag, blank=True, related_name='courses')
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Views Count'))

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    language = models.CharField(max_length=10, default='en', verbose_name=_('Language'))
    
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True)
    preview_video = models.URLField(blank=True, verbose_name=_('Preview Video URL'))
    
    duration_hours = models.PositiveIntegerField(default=0, verbose_name=_('Estimated Duration (hours)'))
    
    prerequisites = models.TextField(blank=True, verbose_name=_('Prerequisites'))
    learning_outcomes = models.TextField(verbose_name=_('Learning Outcomes'))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, verbose_name=_('Featured Course'))
    
    enrollment_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Enrollment Limit'))
    
    # Certificate template
    certificate_template = models.TextField(blank=True, verbose_name=_('Certificate HTML Template'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-created_at', 'id']

    def __str__(self):
        return self.title

    def publish(self):
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()

    @property
    def enrolled_students_count(self):
        return self.enrollments.filter(is_active=True).count()

    def get_average_rating(self):
        """Calculate average rating from reviews"""
        # Use annotated value if available, otherwise calculate
        if hasattr(self, 'avg_rating') and self.avg_rating is not None:
            return self.avg_rating
        from django.db.models import Avg
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('enrolled', _('Enrolled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('dropped', _('Dropped')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                             validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    is_active = models.BooleanField(default=True)
    
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"

# Module and Lessons
class Module(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200, verbose_name=_('Module Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    is_published = models.BooleanField(default=True, verbose_name=_('Is Published'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Module')
        verbose_name_plural = _('Modules')
        ordering = ['course', 'order', 'id']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', _('Video')),
        ('text', _('Text')),
        ('pdf', _('PDF')),
        ('slides', _('Slides')),
        ('interactive', _('Interactive')),
        ('assignment', _('Assignment')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200, verbose_name=_('Lesson Title'))
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='video')
    
    # Content fields
    video_url = models.URLField(blank=True, verbose_name=_('Video URL'))
    video_duration = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Video Duration (seconds)'))
    text_content = models.TextField(blank=True, verbose_name=_('Text Content'))
    file_attachment = models.FileField(upload_to='lessons/attachments/', null=True, blank=True)
    
    # Meta
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    estimated_time_minutes = models.PositiveIntegerField(default=10, verbose_name=_('Estimated Time (minutes)'))
    
    is_preview = models.BooleanField(default=False, verbose_name=_('Available for Preview'))
    is_published = models.BooleanField(default=True, verbose_name=_('Is Published'))
    
    # Requirements
    requires_submission = models.BooleanField(default=False, verbose_name=_('Requires Submission'))
    points = models.PositiveIntegerField(default=0, verbose_name=_('Points'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['module', 'order']
        unique_together = ['module', 'slug']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

class LessonProgress(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_position = models.PositiveIntegerField(default=0, verbose_name=_('Last Position (seconds)'))
    
    is_completed = models.BooleanField(default=False)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    notes = models.TextField(blank=True, verbose_name=_('Student Notes'))

    class Meta:
        verbose_name = _('Lesson Progress')
        verbose_name_plural = _('Lesson Progress Records')
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.lesson.title}"

class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('document', _('Document')),
        ('link', _('External Link')),
        ('download', _('Downloadable File')),
        ('code', _('Code Sample')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200, verbose_name=_('Resource Title'))
    description = models.TextField(blank=True)
    
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, default='document')
    
    file = models.FileField(upload_to='lessons/resources/', null=True, blank=True)
    url = models.URLField(blank=True, verbose_name=_('External URL'))
    
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Lesson Resource')
        verbose_name_plural = _('Lesson Resources')
        ordering = ['lesson', 'order']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

# Quizzes and Assessments
class Quiz(models.Model):
    QUIZ_TYPE_CHOICES = [
        ('practice', _('Practice Quiz')),
        ('graded', _('Graded Quiz')),
        ('final', _('Final Exam')),
        ('survey', _('Survey')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    
    title = models.CharField(max_length=200, verbose_name=_('Quiz Title'))
    instructions = models.TextField(blank=True, verbose_name=_('Instructions'))
    
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, default='practice')
    
    passing_score = models.PositiveIntegerField(default=60, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_attempts = models.PositiveIntegerField(default=3, verbose_name=_('Maximum Attempts'))
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Time Limit (minutes)'))
    
    randomize_questions = models.BooleanField(default=True)
    randomize_answers = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['course', 'created_at', 'id']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', _('Multiple Choice')),
        ('true_false', _('True/False')),
        ('short_answer', _('Short Answer')),
        ('essay', _('Essay')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    
    question_text = models.TextField(verbose_name=_('Question'))
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    
    explanation = models.TextField(blank=True, verbose_name=_('Explanation'))
    
    points = models.PositiveIntegerField(default=1, verbose_name=_('Points'))
    order = models.PositiveIntegerField(default=0)
    
    is_required = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['quiz', 'order', 'id']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.question_text[:50]}..."

class Answer(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    
    answer_text = models.TextField(verbose_name=_('Answer'))
    is_correct = models.BooleanField(default=False, verbose_name=_('Is Correct'))
    
    order = models.PositiveIntegerField(default=0)
    
    feedback = models.TextField(blank=True, verbose_name=_('Answer Feedback'))

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        ordering = ['question', 'order']

    def __str__(self):
        return f"{self.question} - {self.answer_text[:50]}..."

class QuizAttempt(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_attempts')
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    attempt_number = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _('Quiz Attempt')
        verbose_name_plural = _('Quiz Attempts')
        ordering = ['-started_at', 'id']

    def __str__(self):
        return f"{self.student.email} - {self.quiz.title} - Attempt {self.attempt_number}"

class QuestionResponse(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # For multiple choice, true/false
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    
    # For short answer, essay
    text_response = models.TextField(blank=True)
    
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_correct = models.BooleanField(null=True, blank=True)
    
    feedback = models.TextField(blank=True)
    
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Question Response')
        verbose_name_plural = _('Question Responses')
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"{self.attempt} - {self.question}"

# Certificates
class Certificate(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    certificate_number = models.CharField(max_length=50, unique=True, editable=False)
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    
    # Certificate details
    issue_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Completion details
    completion_date = models.DateField()
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Generated files
    pdf_file = models.FileField(upload_to='certificates/pdfs/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='certificates/qrcodes/', null=True, blank=True)
    
    # Verification
    verification_url = models.URLField(blank=True)
    is_valid = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
        ordering = ['-issue_date', 'id']  # Add explicit tiebreaker


    def __str__(self):
        return f"{self.certificate_number} - {self.student.email} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_certificate_number(self):
        import datetime
        prefix = "CERT"
        year = datetime.datetime.now().year
        random_part = uuid.uuid4().hex[:6].upper()
        return f"{prefix}-{year}-{random_part}"

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        verification_data = f"{self.verification_url or self.uuid}"
        qr.add_data(verification_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        file_name = f"qr_{self.uuid}.png"
        self.qr_code.save(file_name, File(buffer), save=False)

# Reviews
class CourseReview(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_verified = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Course Review')
        verbose_name_plural = _('Course Reviews')
        unique_together = ['course', 'student']
        ordering = ['-created_at', 'id']  # Add explicit tiebreaker


    def __str__(self):
        return f"{self.course.title} - {self.student.email} ({self.rating}★)"


# Favorites
class CourseFavorite(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_courses')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Course Favorite')
        verbose_name_plural = _('Course Favorites')
        unique_together = ['course', 'user']
        ordering = ['-created_at', 'id']

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

# Assignments
class Assignment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    
    title = models.CharField(max_length=200, verbose_name=_('Assignment Title'))
    description = models.TextField(verbose_name=_('Description'))
    
    due_date = models.DateTimeField()
    max_points = models.PositiveIntegerField(default=100)
    
    # Allowed file types
    allowed_file_extensions = models.CharField(max_length=200, blank=True, help_text=_("Comma-separated list of extensions, e.g., 'pdf,docx,zip'"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        ordering = ['lesson', 'due_date']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', _('Submitted')),
        ('graded', _('Graded')),
        ('late', _('Late')),
        ('resubmitted', _('Resubmitted')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='assignment_submissions')
    
    submission_date = models.DateTimeField(auto_now_add=True)
    
    file = models.FileField(upload_to='assignments/submissions/', null=True, blank=True)
    text_submission = models.TextField(blank=True)
    
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Assignment Submission')
        verbose_name_plural = _('Assignment Submissions')
        unique_together = ['assignment', 'student']
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.assignment.title} - {self.student.email}"
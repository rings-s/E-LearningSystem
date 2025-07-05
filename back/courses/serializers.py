from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Tag, Course, Enrollment, Module, Lesson, LessonProgress,
    Resource, Quiz, Question, Answer, QuizAttempt, QuestionResponse,
    Certificate, CourseReview
)

User = get_user_model()

# Category and Tags
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

# Course Management
class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    enrolled_count = serializers.IntegerField(source='enrolled_students_count', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'

class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()
    co_instructors = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    modules = serializers.SerializerMethodField()
    enrolled_count = serializers.IntegerField(source='enrolled_students_count', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(source='reviews.count', read_only=True)
    reviews = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
    
    def get_instructor(self, obj):
        from accounts.serializers import UserBriefSerializer
        return UserBriefSerializer(obj.instructor).data
    
    def get_co_instructors(self, obj):
        from accounts.serializers import UserBriefSerializer
        return UserBriefSerializer(obj.co_instructors.all(), many=True).data
    
    def get_modules(self, obj):
        return ModuleSerializer(obj.modules.filter(is_published=True), many=True).data
    
    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_verified=True).order_by('-created_at')
        return CourseReviewSerializer(reviews, many=True).data
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(student=request.user, is_active=True).exists()
        return False



class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'published_at']
    
    def create(self, validated_data):
        # Handle tags
        tags_data = validated_data.pop('tags', [])
        
        # Create course
        course = Course.objects.create(**validated_data)
        
        # Handle tag creation/assignment
        for tag_name in tags_data:
            if tag_name.strip():  # Only create non-empty tags
                tag, created = Tag.objects.get_or_create(
                    name=tag_name.strip(),
                    defaults={'slug': tag_name.strip().lower().replace(' ', '-')}
                )
                course.tags.add(tag)
        
        return course
    
    def update(self, instance, validated_data):
        # Handle tags
        tags_data = validated_data.pop('tags', None)
        
        # Update course fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                if tag_name.strip():  # Only create non-empty tags
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name.strip(),
                        defaults={'slug': tag_name.strip().lower().replace(' ', '-')}
                    )
                    instance.tags.add(tag)
        
        return instance



# Enrollment
class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    student = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = ['uuid', 'enrolled_at', 'certificate_issued', 'certificate_issued_at']
    
    def get_student(self, obj):
        from accounts.serializers import UserBriefSerializer
        return UserBriefSerializer(obj.student).data

class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['course']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

# Modules and Lessons
class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_lessons(self, obj):
        lessons = obj.lessons.filter(is_published=True)
        return LessonListSerializer(lessons, many=True, context=self.context).data

class LessonListSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = '__all__'
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                student=request.user,
                course=obj.module.course,
                is_active=True
            ).first()
            if enrollment:
                return LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson=obj,
                    is_completed=True
                ).exists()
        return False

class LessonDetailSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    resources = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = '__all__'
    
    def get_resources(self, obj):
        return ResourceSerializer(obj.resources.all(), many=True).data
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                student=request.user,
                course=obj.module.course,
                is_active=True
            ).first()
            if enrollment:
                progress = LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson=obj
                ).first()
                if progress:
                    return LessonProgressSerializer(progress).data
        return None

class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = '__all__'
        read_only_fields = ['uuid', 'started_at']

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at']

# Quizzes
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)
    
    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = '__all__'
        read_only_fields = ['uuid', 'started_at', 'score', 'passed']

class QuestionResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = QuestionResponse
        fields = '__all__'
        read_only_fields = ['uuid', 'answered_at', 'points_earned', 'is_correct']

class QuizSubmissionSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    responses = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

# Certificates
class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = [
            'uuid', 'certificate_number', 'issue_date', 'pdf_file', 
            'qr_code', 'verification_url', 'created_at', 'updated_at'
        ]

# Reviews
class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_avatar = serializers.ImageField(source='student.avatar', read_only=True)
    
    class Meta:
        model = CourseReview
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'helpful_count']

class CourseReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = ['course', 'rating', 'comment']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from .models import (
    Category, Tag, Course, Enrollment, Module, Lesson, LessonProgress,
    Resource, Quiz, Question, Answer, QuizAttempt, QuestionResponse,
    Certificate, CourseReview
)

User = get_user_model()

# Simple Tag Serializer
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

# Category Serializer with depth control
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_subcategories(self, obj):
        # Simple depth control to prevent infinite recursion
        context = self.context
        current_depth = context.get('current_depth', 0)
        if current_depth >= 2:  # Max 2 levels deep
            return []
        
        subcategories = obj.subcategories.filter(is_active=True)
        if subcategories.exists():
            new_context = context.copy()
            new_context['current_depth'] = current_depth + 1
            return CategorySerializer(subcategories, many=True, context=new_context).data
        return []

# Course Serializer - Single serializer for all operations
class CourseSerializer(serializers.ModelSerializer):
    # Write-only field for tag creation
    tags_input = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    # Read-only computed fields
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'instructor': {'read_only': True},
            'views_count': {'read_only': True},
            'published_at': {'read_only': True},
        }
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 50:
            raise serializers.ValidationError("Description must be at least 50 characters")
        return value.strip()
    
    def validate(self, data):
        # Auto-generate slug if not provided
        if not data.get('slug') and data.get('title'):
            data['slug'] = self._generate_slug(data['title'])
        return data
    
    def _generate_slug(self, title):
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        instance = getattr(self, 'instance', None)
        
        while Course.objects.filter(slug=slug).exclude(
            id=instance.id if instance else None
        ).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
    
    def _handle_tags(self, course, tags_data):
        if tags_data:
            course.tags.clear()
            for tag_name in tags_data:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'slug': slugify(tag_name)}
                    )
                    course.tags.add(tag)
    
    def get_average_rating(self, obj):
        """Get average rating from annotation or calculate it"""
        if hasattr(obj, 'avg_rating') and obj.avg_rating is not None:
            return obj.avg_rating
        return obj.get_average_rating()  # Falls back to method
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags_input', [])
        course = Course.objects.create(**validated_data)
        self._handle_tags(course, tags_data)
        return course
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags_input', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data is not None:
            self._handle_tags(instance, tags_data)
        return instance

# Enrollment Serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
        extra_kwargs = {
            'student': {'read_only': True},
            'enrolled_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

# Module Serializer
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

# Lesson Serializer
class LessonSerializer(serializers.ModelSerializer):
    # Computed fields for user progress
    is_completed = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = '__all__'
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Use prefetched data if available
            if hasattr(obj, 'user_progress_data'):
                return obj.user_progress_data.is_completed if obj.user_progress_data else False
        return False
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if hasattr(obj, 'user_progress_data') and obj.user_progress_data:
                progress = obj.user_progress_data
                return {
                    'is_completed': progress.is_completed,
                    'last_position': progress.last_position,
                    'time_spent_seconds': progress.time_spent_seconds,
                    'completed_at': progress.completed_at
                }
        return None

# Lesson Progress Serializer
class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = '__all__'

# Resource Serializer
class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

# Quiz Serializer
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

# Question Serializer
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

# Answer Serializer
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

# Quiz Attempt Serializer
class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = '__all__'
        extra_kwargs = {
            'student': {'read_only': True},
            'started_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

# Question Response Serializer
class QuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionResponse
        fields = '__all__'

# Quiz Submission Serializer (for handling quiz submissions)
class QuizSubmissionSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    responses = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )

# Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
        extra_kwargs = {
            'certificate_number': {'read_only': True},
            'pdf_file': {'read_only': True},
            'qr_code': {'read_only': True},
        }

# Course Review Serializer
class CourseReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = '__all__'
        extra_kwargs = {
            'student': {'read_only': True},
            'helpful_count': {'read_only': True},
        }
    
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
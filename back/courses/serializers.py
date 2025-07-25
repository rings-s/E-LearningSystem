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
    enrollment_count = serializers.IntegerField(read_only=True)  # Frontend expects this field name
    enrolled_students = serializers.SerializerMethodField()  # For unique student counting
    avg_rating = serializers.FloatField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    # Course detail page specific fields
    instructor = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    
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
    
    def get_enrolled_students(self, obj):
        """Return enrolled students for unique counting in dashboard"""
        # Only include for teacher's own courses and when requested
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        
        # Check if this is for dashboard (teacher viewing their own courses)
        if request.user == obj.instructor:
            enrollments = obj.enrollments.filter(is_active=True).select_related('student')
            return [
                {
                    'id': enrollment.student.id,
                    'uuid': str(enrollment.student.uuid) if hasattr(enrollment.student, 'uuid') else str(enrollment.student.id),
                    'name': enrollment.student.get_full_name() if hasattr(enrollment.student, 'get_full_name') else str(enrollment.student)
                }
                for enrollment in enrollments
            ]
        return []
    
    def get_instructor(self, obj):
        """Return detailed instructor information for course detail page"""
        if obj.instructor:
            return {
                'id': obj.instructor.id,
                'full_name': obj.instructor.get_full_name() if hasattr(obj.instructor, 'get_full_name') else str(obj.instructor),
                'avatar': obj.instructor.avatar.url if hasattr(obj.instructor, 'avatar') and obj.instructor.avatar else None,
                'bio': getattr(obj.instructor, 'bio', ''),
                'role': getattr(obj.instructor, 'role', 'teacher')
            }
        return None
    
    def get_modules(self, obj):
        """Return course modules with lessons for curriculum tab"""
        try:
            if hasattr(obj, 'modules'):
                modules = obj.modules.filter(is_published=True).order_by('order')
                result = []
                
                for module in modules:
                    lessons = module.lessons.filter(is_published=True).order_by('order')
                    
                    result.append({
                        'id': module.id,
                        'uuid': str(module.uuid),
                        'title': module.title,
                        'description': module.description,
                        'order': module.order,
                        'lessons': [
                            {
                                'id': lesson.id,
                                'uuid': str(lesson.uuid),
                                'title': lesson.title,
                                'description': lesson.description,
                                'estimated_time_minutes': lesson.estimated_time_minutes,
                                'content_type': lesson.content_type,
                                'order': lesson.order,
                                'is_preview': lesson.is_preview,
                                'is_completed': False  # Will be calculated based on user progress
                            }
                            for lesson in lessons
                        ]
                    })
                
                return result
        except Exception as e:
            print(f"Error in get_modules: {e}")
            
        return []
    
    def get_total_lessons(self, obj):
        """Return total number of lessons across all modules"""
        if hasattr(obj, 'modules'):
            return sum(
                module.lessons.filter(is_published=True).count()
                for module in obj.modules.filter(is_published=True)
            )
        return 0
    
    def get_reviews(self, obj):
        """Return course reviews for reviews tab"""
        if hasattr(obj, 'reviews'):
            reviews = obj.reviews.filter(is_verified=True).select_related('student').order_by('-created_at')[:10]
            return [
                {
                    'id': review.id,
                    'student_name': review.student.get_full_name() if hasattr(review.student, 'get_full_name') else str(review.student),
                    'student_avatar': review.student.avatar.url if hasattr(review.student, 'avatar') and review.student.avatar else None,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
                for review in reviews
            ]
        return []
    
    def get_is_enrolled(self, obj):
        """Check if current user is enrolled in this course"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(student=request.user, is_active=True).exists()
        return False
    
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
    lessons = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = '__all__'
    
    def get_lessons(self, obj):
        # Use prefetched lessons if available
        if hasattr(obj, 'lessons'):
            lessons = obj.lessons.filter(is_published=True).order_by('order')
            return LessonSerializer(lessons, many=True, context=self.context).data
        return []

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
                progress_data = obj.user_progress_data
                # Handle both single object and list cases
                if isinstance(progress_data, list):
                    progress_data = progress_data[0] if progress_data else None
                return progress_data.is_completed if progress_data else False
        return False
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if hasattr(obj, 'user_progress_data') and obj.user_progress_data:
                progress_data = obj.user_progress_data
                # Handle both single object and list cases
                if isinstance(progress_data, list):
                    progress_data = progress_data[0] if progress_data else None
                
                if progress_data:
                    return {
                        'is_completed': progress_data.is_completed,
                        'last_position': progress_data.last_position,
                        'time_spent_seconds': progress_data.time_spent_seconds,
                        'completed_at': progress_data.completed_at
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
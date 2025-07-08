from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q, Prefetch
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
import logging

logger = logging.getLogger(__name__)

from .models import (
    Category, Course, Enrollment, Module, Lesson, LessonProgress,
    Resource, Quiz, Question, Answer, QuizAttempt, QuestionResponse,
    Certificate, CourseReview, CourseFavorite
)
from .serializers import (
    CategorySerializer, CourseSerializer, EnrollmentSerializer,
    ModuleSerializer, LessonSerializer, LessonProgressSerializer,
    ResourceSerializer, QuizSerializer, QuizAttemptSerializer,
    QuizSubmissionSerializer, CertificateSerializer, CourseReviewSerializer
)
from .filters import CourseFilter, LessonFilter, QuizFilter
from accounts.permissions import (
    IsTeacherOrAdmin, IsCourseInstructor, IsEnrolledStudent,
    IsVerifiedUser, CanCreateCourse, IsOwnerOrReadOnly
)
from core.utils import (
    send_notification, bulk_notify_enrolled_students,
    track_activity, increment_view_count, update_enrollment_progress,
    validate_and_get_object, format_api_response
)

# Categories
class CategoryListView(generics.ListAPIView):
    """GET /api/categories/ - List all categories"""
    queryset = Category.objects.filter(is_active=True).select_related('parent').prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class CategoryDetailView(generics.RetrieveAPIView):
    """GET /api/categories/{slug}/ - Get category details"""
    queryset = Category.objects.filter(is_active=True).select_related('parent').prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

# Courses
class CourseListCreateView(generics.ListCreateAPIView):
    """
    GET /api/courses/ - List courses
    POST /api/courses/ - Create course
    """
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter
    
    def get_queryset(self):
        try:
            # Start with basic Course queryset
            queryset = Course.objects.all()
            
            # Add select_related for performance with error handling
            try:
                queryset = queryset.select_related('instructor', 'category')
            except Exception as e:
                print(f"Warning: Could not add select_related - {e}")
                pass
            
            # Add prefetch_related with error handling  
            try:
                queryset = queryset.prefetch_related('tags', 'co_instructors')
            except Exception as e:
                print(f"Warning: Could not add prefetch_related - {e}")
                pass
            
            # Add annotations with error handling
            try:
                queryset = queryset.annotate(
                    enrolled_count=Count('enrollments', filter=Q(enrollments__is_active=True)),
                    avg_rating=Avg('reviews__rating', filter=Q(reviews__is_verified=True))
                )
            except Exception as e:
                print(f"Warning: Could not add annotations - {e}")
                pass
            
            # Filter logic
            my_courses = self.request.query_params.get('my_courses', 'false').lower() == 'true'
            
            if my_courses and self.request.user.is_authenticated:
                queryset = queryset.filter(instructor=self.request.user)
            else:
                # Public browsing - only published courses
                queryset = queryset.filter(status='published')
            
            return queryset.order_by('-created_at', 'id')
            
        except Exception as e:
            print(f"Error in get_queryset: {e}")
            # Fallback to basic queryset
            return Course.objects.filter(status='published').order_by('-created_at', 'id')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), CanCreateCourse()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/courses/{uuid}/ - Get course details
    PUT/PATCH /api/courses/{uuid}/ - Update course
    DELETE /api/courses/{uuid}/ - Delete course
    """
    serializer_class = CourseSerializer
    lookup_field = 'uuid'
    
    def get_queryset(self):
        try:
            queryset = Course.objects.select_related(
                'instructor', 'category'
            ).prefetch_related(
                'tags', 'co_instructors',
                Prefetch(
                    'modules',
                    queryset=Module.objects.filter(is_published=True).prefetch_related(
                        Prefetch(
                            'lessons',
                            queryset=Lesson.objects.filter(is_published=True)
                        )
                    )
                ),
                Prefetch(
                    'reviews',
                    queryset=CourseReview.objects.filter(is_verified=True)
                    .select_related('student').order_by('-created_at')[:10]
                )
            ).annotate(
                enrolled_count=Count('enrollments', filter=Q(enrollments__is_active=True)),
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_verified=True))
            )
            
            # Add user-specific data if authenticated
            user = getattr(self.request, 'user', None)
            if user and user.is_authenticated:
                queryset = queryset.prefetch_related(
                    Prefetch(
                        'enrollments',
                        queryset=Enrollment.objects.filter(student=user, is_active=True),
                        to_attr='user_enrollment'
                    )
                )
            
            return queryset
        except Exception as e:
            logger.error(f"Error in CourseDetailView queryset: {e}")
            # Fallback to simple queryset
            return Course.objects.all()
    
    def get_object(self):
        uuid_value = self.kwargs.get('uuid')
        return validate_and_get_object(Course, uuid_value, queryset=self.get_queryset())
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [AllowAny()]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        increment_view_count(instance)
        
        if request.user.is_authenticated:
            track_activity(
                request.user, 'course_view', course=instance,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Course Actions
class CourseEnrollView(APIView):
    """POST /api/courses/{uuid}/enroll/ - Enroll in course"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def post(self, request, uuid):
        try:
            course = validate_and_get_object(Course, uuid)
            
            if course.status != 'published':
                return format_api_response(
                    errors={'course': ['Course is not available for enrollment']},
                    message='This course is not currently available',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Check enrollment limit
            if course.enrollment_limit:
                current_count = course.enrollments.filter(is_active=True).count()
                if current_count >= course.enrollment_limit:
                    return format_api_response(
                        errors={'enrollment': ['Course enrollment limit reached']},
                        message='Sorry, this course has reached its enrollment limit',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            enrollment, created = Enrollment.objects.get_or_create(
                student=request.user, course=course,
                defaults={'status': 'enrolled'}
            )
            
            if not created and enrollment.is_active:
                return format_api_response(
                    data=EnrollmentSerializer(enrollment, context={'request': request}).data,
                    message='You are already enrolled in this course',
                    status_code=status.HTTP_200_OK
                )
            
            if not created:
                enrollment.is_active = True
                enrollment.status = 'enrolled'
                enrollment.save()
            
            send_notification(
                request.user, 'enrollment',
                f'Enrolled in {course.title}',
                f'You have successfully enrolled in {course.title}',
                course=course
            )
            
            track_activity(request.user, 'course_enrollment', course=course)
            
            return format_api_response(
                data=EnrollmentSerializer(enrollment, context={'request': request}).data,
                message=f'Successfully enrolled in {course.title}',
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return format_api_response(
                errors={'general': ['An unexpected error occurred']},
                message='Unable to process enrollment at this time',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CoursePublishView(APIView):
    """POST /api/courses/{uuid}/publish/ - Publish course"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    
    def post(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        self.check_object_permissions(request, course)
        
        course.publish()
        
        bulk_notify_enrolled_students(
            course, 'course_update',
            f'{course.title} is now published',
            'The course you enrolled in is now available'
        )
        
        return format_api_response(
            message='Course published successfully',
            status_code=status.HTTP_200_OK
        )

class CourseAnalyticsView(APIView):
    """GET /api/courses/{uuid}/analytics/ - Get course analytics"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    
    def get(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        self.check_object_permissions(request, course)
        
        analytics = {
            'total_enrollments': course.enrollments.count(),
            'active_students': course.enrollments.filter(is_active=True).count(),
            'completed_students': course.enrollments.filter(status='completed').count(),
            'average_progress': float(course.enrollments.aggregate(
                avg_progress=Avg('progress_percentage')
            )['avg_progress'] or 0),
            'average_rating': float(course.reviews.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0),
            'total_reviews': course.reviews.count(),
        }
        
        return format_api_response(data=analytics)

class CourseImageUploadView(APIView):
    """POST /api/courses/{uuid}/upload-image/ - Upload course thumbnail"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        self.check_object_permissions(request, course)
        
        image = request.FILES.get('thumbnail')
        if not image:
            return format_api_response(
                errors={'image': ['No image file provided']},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate image
        if image.size > 10 * 1024 * 1024:  # 10MB limit
            return format_api_response(
                errors={'image': ['Image file too large. Maximum size is 10MB']},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not image.content_type.startswith('image/'):
            return format_api_response(
                errors={'image': ['File must be an image']},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        course.thumbnail = image
        course.save()
        
        return format_api_response(
            data={'thumbnail_url': course.thumbnail.url},
            message='Image uploaded successfully'
        )

# Course Favorites
class CourseFavoriteCheckView(APIView):
    """GET /api/courses/{uuid}/is-favorite/ - Check if course is favorite"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        is_favorite = CourseFavorite.objects.filter(course=course, user=request.user).exists()
        return format_api_response(data={'is_favorite': is_favorite})

class CourseFavoriteAddView(APIView):
    """POST /api/courses/{uuid}/add-to-favorites/ - Add to favorites"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        favorite, created = CourseFavorite.objects.get_or_create(course=course, user=request.user)
        
        if created:
            return format_api_response(
                message='Course added to favorites',
                status_code=status.HTTP_201_CREATED
            )
        return format_api_response(message='Course already in favorites')

class CourseFavoriteRemoveView(APIView):
    """DELETE /api/courses/{uuid}/remove-from-favorites/ - Remove from favorites"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        deleted_count, _ = CourseFavorite.objects.filter(course=course, user=request.user).delete()
        
        if deleted_count > 0:
            return format_api_response(message='Course removed from favorites')
        return format_api_response(
            message='Course not in favorites',
            status_code=status.HTTP_404_NOT_FOUND
        )

# Lessons
class CourseLessonListCreateView(generics.ListCreateAPIView):
    """
    GET /api/courses/{course_uuid}/lessons/ - List lessons
    POST /api/courses/{course_uuid}/lessons/ - Create lesson
    """
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        course_uuid = self.kwargs['course_uuid']
        course = validate_and_get_object(Course, course_uuid)
        
        queryset = Lesson.objects.filter(
            module__course=course, is_published=True
        ).select_related('module').prefetch_related('resources')
        
        # Add user progress data if authenticated
        user = self.request.user
        if user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                student=user, course=course, is_active=True
            ).first()
            
            if enrollment:
                queryset = queryset.prefetch_related(
                    Prefetch(
                        'progress_records',
                        queryset=LessonProgress.objects.filter(enrollment=enrollment),
                        to_attr='user_progress_data'
                    )
                )
        
        return queryset.order_by('module__order', 'order')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]

class CourseLessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/courses/{course_uuid}/lessons/{uuid}/ - Get lesson details
    PUT/PATCH /api/courses/{course_uuid}/lessons/{uuid}/ - Update lesson
    DELETE /api/courses/{course_uuid}/lessons/{uuid}/ - Delete lesson
    """
    serializer_class = LessonSerializer
    lookup_field = 'uuid'
    
    def get_queryset(self):
        course_uuid = self.kwargs['course_uuid']
        course = validate_and_get_object(Course, course_uuid)
        return Lesson.objects.filter(module__course=course).select_related('module').prefetch_related('resources')
    
    def get_object(self):
        uuid_value = self.kwargs.get('uuid')
        return validate_and_get_object(Lesson, uuid_value, queryset=self.get_queryset())
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]
    
    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        course_uuid = self.kwargs['course_uuid']
        
        # Track lesson access and update progress
        enrollment = Enrollment.objects.filter(
            student=request.user, course__uuid=course_uuid, is_active=True
        ).first()
        
        if enrollment:
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment, lesson=lesson
            )
            
            if created:
                track_activity(
                    request.user, 'lesson_start',
                    lesson=lesson, course=lesson.module.course
                )
            
            enrollment.last_accessed = timezone.now()
            enrollment.save()
        
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

class LessonFileUploadView(APIView):
    """POST /api/courses/{course_uuid}/lessons/{uuid}/upload/ - Upload lesson file"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        if lesson.module.course != course:
            return format_api_response(
                errors={'lesson': ['Lesson does not belong to this course']},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES.get('file')
        if not file:
            return format_api_response(
                errors={'file': ['No file provided']},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            return format_api_response(
                errors={'file': ['File too large. Maximum size is 50MB']},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        lesson.file_attachment = file
        lesson.save()
        
        return format_api_response(
            data={'file_url': lesson.file_attachment.url},
            message='File uploaded successfully'
        )

class LessonCompleteView(APIView):
    """POST /api/courses/{course_uuid}/lessons/{uuid}/complete/ - Mark lesson complete"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        enrollment = get_object_or_404(
            Enrollment, student=request.user, course=course, is_active=True
        )
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            
            update_enrollment_progress(enrollment)
            track_activity(request.user, 'lesson_complete', lesson=lesson, course=course)
        
        return format_api_response(
            data={
                'progress_percentage': enrollment.progress_percentage,
                'course_completed': enrollment.progress_percentage >= 100
            },
            message='Lesson completed successfully'
        )

class LessonNotesView(APIView):
    """
    GET /api/courses/{course_uuid}/lessons/{uuid}/notes/ - Get notes
    POST /api/courses/{course_uuid}/lessons/{uuid}/notes/ - Save notes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        enrollment = get_object_or_404(
            Enrollment, student=request.user, course=course, is_active=True
        )
        
        progress = LessonProgress.objects.filter(enrollment=enrollment, lesson=lesson).first()
        notes = progress.notes if progress else ''
        
        return format_api_response(
            data={'notes': notes, 'lesson_uuid': str(lesson.uuid)}
        )
    
    def post(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        enrollment = get_object_or_404(
            Enrollment, student=request.user, course=course, is_active=True
        )
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        
        notes = request.data.get('notes', '')
        progress.notes = notes
        progress.save()
        
        return format_api_response(
            data={'notes': progress.notes},
            message='Notes saved successfully'
        )

# Enrollments
class EnrollmentListView(generics.ListAPIView):
    """GET /api/enrollments/ - List user enrollments"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            return Enrollment.objects.filter(student=user).select_related('course', 'course__instructor')
        elif user.role == 'teacher':
            return Enrollment.objects.filter(course__instructor=user).select_related('course', 'student')
        elif user.is_staff:
            return Enrollment.objects.all().select_related('course', 'student')
        
        return Enrollment.objects.none()

class MyEnrollmentsView(generics.ListAPIView):
    """GET /api/enrollments/my-courses/ - Get user's enrolled courses"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user, is_active=True
        ).select_related('course', 'course__instructor')

# Modules
class ModuleListCreateView(generics.ListCreateAPIView):
    """
    GET /api/modules/ - List modules
    POST /api/modules/ - Create module
    """
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        course_uuid = self.request.query_params.get('course')
        queryset = Module.objects.select_related('course').prefetch_related(
            Prefetch(
                'lessons',
                queryset=Lesson.objects.filter(is_published=True)
            )
        )
        
        if course_uuid:
            queryset = queryset.filter(course__uuid=course_uuid)
        
        return queryset.order_by('course', 'order')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]

class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/modules/{uuid}/ - Get module details
    PUT/PATCH /api/modules/{uuid}/ - Update module
    DELETE /api/modules/{uuid}/ - Delete module
    """
    queryset = Module.objects.select_related('course').prefetch_related('lessons')
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]

# Reviews
class CourseReviewListCreateView(generics.ListCreateAPIView):
    """
    GET /api/reviews/ - List course reviews
    POST /api/reviews/ - Create course review
    """
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        course_uuid = self.request.query_params.get('course')
        queryset = CourseReview.objects.filter(is_verified=True).select_related('course', 'student')
        
        if course_uuid:
            queryset = queryset.filter(course__uuid=course_uuid)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        # Check if user completed the course
        get_object_or_404(
            Enrollment, student=self.request.user,
            course=course, status='completed'
        )
        serializer.save()

class CourseReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/reviews/{uuid}/ - Get review details
    PUT/PATCH /api/reviews/{uuid}/ - Update review
    DELETE /api/reviews/{uuid}/ - Delete review
    """
    queryset = CourseReview.objects.select_related('course', 'student')
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uuid'

# Certificates
class CertificateListView(generics.ListAPIView):
    """GET /api/certificates/ - List certificates"""
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            return Certificate.objects.filter(student=user).select_related('course')
        elif user.role == 'teacher':
            return Certificate.objects.filter(course__instructor=user).select_related('course', 'student')
        elif user.is_staff:
            return Certificate.objects.all().select_related('course', 'student')
        
        return Certificate.objects.none()

class CertificateDetailView(generics.RetrieveAPIView):
    """GET /api/certificates/{uuid}/ - Get certificate details"""
    queryset = Certificate.objects.select_related('course', 'student')
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

class CertificateVerifyView(APIView):
    """GET /api/certificates/{uuid}/verify/ - Verify certificate"""
    permission_classes = [AllowAny]
    
    def get(self, request, uuid):
        certificate = validate_and_get_object(Certificate, uuid)
        
        return format_api_response(data={
            'valid': certificate.is_valid,
            'certificate_number': certificate.certificate_number,
            'student_name': certificate.student.get_full_name(),
            'course_title': certificate.course.title,
            'issue_date': certificate.issue_date,
            'completion_date': certificate.completion_date,
        })
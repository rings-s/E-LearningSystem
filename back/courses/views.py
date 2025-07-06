from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import (
    Category, Course, Enrollment, Module, Lesson, LessonProgress,
    Resource, Quiz, Question, Answer, QuizAttempt, QuestionResponse,
    Certificate, CourseReview, CourseFavorite
)
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateUpdateSerializer, EnrollmentSerializer, EnrollmentCreateSerializer,
    ModuleSerializer, LessonListSerializer, LessonDetailSerializer,
    LessonProgressSerializer, ResourceSerializer, QuizSerializer,
    QuizAttemptSerializer, QuizSubmissionSerializer, CertificateSerializer,
    CourseReviewSerializer, CourseReviewCreateSerializer
)
from .filters import CourseFilter, LessonFilter, QuizFilter
from accounts.permissions import (
    IsTeacherOrAdmin, IsCourseInstructor, IsEnrolledStudent,
    IsVerifiedUser, CanCreateCourse, IsOwnerOrReadOnly
)
from core.utils import (
    send_notification, bulk_notify_enrolled_students,
    track_activity, increment_view_count, update_enrollment_progress,
    validate_and_get_object
)

# Categories
class CategoryListView(generics.ListAPIView):
    """GET /api/categories/ - List all categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('subcategories')

class CategoryDetailView(generics.RetrieveAPIView):
    """GET /api/categories/{slug}/ - Get category details"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

# Courses
class CourseListCreateView(generics.ListCreateAPIView):
    """
    GET /api/courses/ - List courses
    POST /api/courses/ - Create course
    """
    queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Check if user wants their own courses (for teachers/instructors)
        my_courses = self.request.query_params.get('my_courses', 'false').lower() == 'true'
        
        if self.request.method == 'GET':
            if my_courses and self.request.user.is_authenticated:
                # For teachers viewing their own courses - include all statuses
                queryset = queryset.filter(instructor=self.request.user)
            else:
                # For public course browsing - only published courses
                queryset = queryset.filter(status='published')
        
        return queryset.select_related(
            'instructor', 'category'
        ).prefetch_related(
            'tags', 'co_instructors'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            enrolled_count=Count('enrollments', filter=Q(enrollments__is_active=True))
        ).order_by('-created_at', 'id')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseListSerializer
    
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
    queryset = Course.objects.all()
    lookup_field = 'uuid'
    
    def get_object(self):
        uuid_value = self.kwargs.get('uuid')
        return validate_and_get_object(Course, uuid_value)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseCreateUpdateSerializer
        return CourseDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [AllowAny()]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        increment_view_count(instance)
        
        if request.user.is_authenticated:
            track_activity(
                request.user,
                'course_view',
                course=instance,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CourseEnrollView(APIView):
    """POST /api/courses/{uuid}/enroll/ - Enroll in course"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def post(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        
        # Check enrollment limit
        if course.enrollment_limit:
            current_count = course.enrollments.filter(is_active=True).count()
            if current_count >= course.enrollment_limit:
                return Response(
                    {'error': 'Course enrollment limit reached'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'status': 'enrolled'}
        )
        
        if not created and enrollment.is_active:
            return Response(
                {'error': 'Already enrolled in this course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not created:
            enrollment.is_active = True
            enrollment.status = 'enrolled'
            enrollment.save()
        
        # Send notification and track activity
        send_notification(
            request.user,
            'enrollment',
            f'Enrolled in {course.title}',
            f'You have successfully enrolled in {course.title}',
            course=course
        )
        
        track_activity(request.user, 'course_enrollment', course=course)
        
        serializer = EnrollmentSerializer(enrollment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CoursePublishView(APIView):
    """POST /api/courses/{uuid}/publish/ - Publish course"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    
    def post(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        self.check_object_permissions(request, course)
        
        course.publish()
        
        bulk_notify_enrolled_students(
            course,
            'course_update',
            f'{course.title} is now published',
            'The course you enrolled in is now available'
        )
        
        return Response({'message': 'Course published successfully'})

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
        
        return Response(analytics)

# Course Image Upload
class CourseImageUploadView(APIView):
    """POST /api/courses/{uuid}/upload-image/ - Upload course thumbnail"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        self.check_object_permissions(request, course)
        
        image = request.FILES.get('thumbnail')
        if not image:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate image
        if image.size > 10 * 1024 * 1024:  # 10MB limit
            return Response(
                {'error': 'Image file too large. Maximum size is 10MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not image.content_type.startswith('image/'):
            return Response(
                {'error': 'File must be an image'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course.thumbnail = image
        course.save()
        
        return Response({
            'message': 'Image uploaded successfully',
            'thumbnail_url': course.thumbnail.url if course.thumbnail else None
        })

# Lessons under Course
class CourseLessonListCreateView(generics.ListCreateAPIView):
    """
    GET /api/courses/{course_uuid}/lessons/ - List lessons in course
    POST /api/courses/{course_uuid}/lessons/ - Create lesson in course
    """
    serializer_class = LessonListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        course_uuid = self.kwargs['course_uuid']
        course = validate_and_get_object(Course, course_uuid)
        
        return Lesson.objects.filter(
            module__course=course,
            is_published=True
        ).select_related('module').prefetch_related('resources').order_by('module__order', 'order')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonDetailSerializer
        return LessonListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]
    
    def perform_create(self, serializer):
        course_uuid = self.kwargs['course_uuid']
        module_uuid = self.request.data.get('module')
        
        course = validate_and_get_object(Course, course_uuid)
        module = validate_and_get_object(Module, module_uuid)
        
        # Verify module belongs to course
        if module.course != course:
            raise ValidationError("Module does not belong to this course")
        
        # Check permissions
        if course.instructor != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You don't have permission to add lessons to this course")
        
        # Set the next order number
        max_order = module.lessons.aggregate(models.Max('order'))['order__max'] or 0
        serializer.save(order=max_order + 1)

class CourseLessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/courses/{course_uuid}/lessons/{uuid}/ - Get lesson details
    PUT/PATCH /api/courses/{course_uuid}/lessons/{uuid}/ - Update lesson
    DELETE /api/courses/{course_uuid}/lessons/{uuid}/ - Delete lesson
    """
    serializer_class = LessonDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        course_uuid = self.kwargs['course_uuid']
        course = validate_and_get_object(Course, course_uuid)
        return Lesson.objects.filter(module__course=course)
    
    def get_object(self):
        uuid_value = self.kwargs.get('uuid')
        return validate_and_get_object(Lesson, uuid_value)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]
    
    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        course_uuid = self.kwargs['course_uuid']
        
        # Track lesson start and update progress
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course__uuid=course_uuid,
            is_active=True
        ).first()
        
        if enrollment:
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            
            if created:
                track_activity(
                    request.user,
                    'lesson_start',
                    lesson=lesson,
                    course=lesson.module.course
                )
            
            # Update last accessed
            enrollment.last_accessed = timezone.now()
            enrollment.save()
        
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

# Lesson File Upload
class LessonFileUploadView(APIView):
    """POST /api/courses/{course_uuid}/lessons/{uuid}/upload/ - Upload lesson file"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        # Verify lesson belongs to course
        if lesson.module.course != course:
            return Response(
                {'error': 'Lesson does not belong to this course'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        if course.instructor != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to upload files for this lesson")
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (50MB limit)
        if file.size > 50 * 1024 * 1024:
            return Response(
                {'error': 'File too large. Maximum size is 50MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the file
        lesson.file_attachment = file
        lesson.save()
        
        return Response({
            'message': 'File uploaded successfully',
            'file_url': lesson.file_attachment.url if lesson.file_attachment else None
        })

# Lesson Completion
class LessonCompleteView(APIView):
    """POST /api/courses/{course_uuid}/lessons/{uuid}/complete/ - Mark lesson as complete"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=course,
            is_active=True
        )
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            
            # Update enrollment progress
            new_progress = update_enrollment_progress(enrollment)
            
            # Track activity
            track_activity(
                request.user,
                'lesson_complete',
                lesson=lesson,
                course=course
            )
        
        return Response({
            'message': 'Lesson completed successfully',
            'progress_percentage': enrollment.progress_percentage,
            'course_completed': enrollment.progress_percentage >= 100
        })

# Lesson Notes
class LessonNotesView(APIView):
    """
    GET /api/courses/{course_uuid}/lessons/{uuid}/notes/ - Get lesson notes
    POST /api/courses/{course_uuid}/lessons/{uuid}/notes/ - Save lesson notes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=course,
            is_active=True
        )
        
        progress = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson=lesson
        ).first()
        
        notes = progress.notes if progress else ''
        
        return Response({
            'notes': notes,
            'lesson_uuid': str(lesson.uuid)
        })
    
    def post(self, request, course_uuid, uuid):
        lesson = validate_and_get_object(Lesson, uuid)
        course = validate_and_get_object(Course, course_uuid)
        
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=course,
            is_active=True
        )
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        notes = request.data.get('notes', '')
        progress.notes = notes
        progress.save()
        
        return Response({
            'message': 'Notes saved successfully',
            'notes': progress.notes
        })

# Enrollments
class EnrollmentListView(generics.ListAPIView):
    """GET /api/enrollments/ - List user enrollments"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            return Enrollment.objects.filter(student=user)
        elif user.role == 'teacher':
            return Enrollment.objects.filter(course__instructor=user)
        elif user.is_staff:
            return Enrollment.objects.all()
        
        return Enrollment.objects.none()

class MyEnrollmentsView(generics.ListAPIView):
    """GET /api/enrollments/my-courses/ - Get user's enrolled courses"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user,
            is_active=True
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
        queryset = Module.objects.all()
        
        if course_uuid:
            queryset = queryset.filter(course__uuid=course_uuid)
        
        return queryset.prefetch_related(
            Prefetch(
                'lessons',
                queryset=Lesson.objects.filter(is_published=True)
            )
        )
    
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
    queryset = Module.objects.all()
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
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        course_uuid = self.request.query_params.get('course')
        queryset = CourseReview.objects.filter(is_verified=True)
        
        if course_uuid:
            queryset = queryset.filter(course__uuid=course_uuid)
        
        return queryset.select_related('course', 'student')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseReviewCreateSerializer
        return CourseReviewSerializer
    
    def perform_create(self, serializer):
        # Check if user completed the course
        course = serializer.validated_data['course']
        enrollment = get_object_or_404(
            Enrollment,
            student=self.request.user,
            course=course,
            status='completed'
        )
        
        serializer.save(student=self.request.user)

class CourseReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/reviews/{uuid}/ - Get review details
    PUT/PATCH /api/reviews/{uuid}/ - Update review
    DELETE /api/reviews/{uuid}/ - Delete review
    """
    queryset = CourseReview.objects.all()
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
            return Certificate.objects.filter(student=user)
        elif user.role == 'teacher':
            return Certificate.objects.filter(course__instructor=user)
        elif user.is_staff:
            return Certificate.objects.all()
        
        return Certificate.objects.none()

class CertificateDetailView(generics.RetrieveAPIView):
    """GET /api/certificates/{uuid}/ - Get certificate details"""
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

class CertificateVerifyView(APIView):
    """GET /api/certificates/{uuid}/verify/ - Verify certificate authenticity"""
    permission_classes = [AllowAny]
    
    def get(self, request, uuid):
        certificate = validate_and_get_object(Certificate, uuid)
        
        return Response({
            'valid': certificate.is_valid,
            'certificate_number': certificate.certificate_number,
            'student_name': certificate.student.get_full_name(),
            'course_title': certificate.course.title,
            'issue_date': certificate.issue_date,
            'completion_date': certificate.completion_date,
        })


# Course Favorites
class CourseFavoriteCheckView(APIView):
    """GET /api/courses/{uuid}/is-favorite/ - Check if course is in user's favorites"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        is_favorite = CourseFavorite.objects.filter(course=course, user=request.user).exists()
        return Response({'is_favorite': is_favorite})


class CourseFavoriteAddView(APIView):
    """POST /api/courses/{uuid}/add-to-favorites/ - Add course to user's favorites"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        favorite, created = CourseFavorite.objects.get_or_create(
            course=course, 
            user=request.user
        )
        if created:
            return Response({'message': 'Course added to favorites'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Course already in favorites'}, status=status.HTTP_200_OK)


class CourseFavoriteRemoveView(APIView):
    """DELETE /api/courses/{uuid}/remove-from-favorites/ - Remove course from user's favorites"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, uuid):
        course = validate_and_get_object(Course, uuid)
        deleted_count, _ = CourseFavorite.objects.filter(course=course, user=request.user).delete()
        if deleted_count > 0:
            return Response({'message': 'Course removed from favorites'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Course not in favorites'}, status=status.HTTP_404_NOT_FOUND)
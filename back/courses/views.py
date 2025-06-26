from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q, Prefetch
from django.utils import timezone

from .models import (
    Category, Course, Enrollment, Module, Lesson, LessonProgress,
    Resource, Quiz, Question, Answer, QuizAttempt, QuestionResponse,
    Certificate, CourseReview
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
    track_activity, increment_view_count, update_enrollment_progress
)

# Categories
class CategoryListView(generics.ListAPIView):
    """List all categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('subcategories')

class CategoryDetailView(generics.RetrieveAPIView):
    """Get category details"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

# Courses
class CourseListCreateView(generics.ListCreateAPIView):
    """List and create courses"""
    queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.method == 'GET':
            queryset = queryset.filter(status='published')
        
        # Ensure explicit ordering to fix pagination warning
        queryset = queryset.select_related(
            'instructor', 'category'
        ).prefetch_related(
            'tags', 'co_instructors'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            enrolled_count=Count('enrollments', filter=Q(enrollments__is_active=True))
        ).order_by('-created_at', 'id')  # Add explicit ordering with tiebreaker
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsVerifiedUser(), CanCreateCourse()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete course"""
    queryset = Course.objects.all()
    lookup_field = 'uuid'
    
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
    """Enroll in a course"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def post(self, request, uuid):
        course = get_object_or_404(Course, uuid=uuid)
        
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
        
        # Send notification
        send_notification(
            request.user,
            'enrollment',
            f'Enrolled in {course.title}',
            f'You have successfully enrolled in {course.title}',
            course=course
        )
        
        # Track activity
        track_activity(
            request.user,
            'course_enrollment',
            course=course
        )
        
        serializer = EnrollmentSerializer(enrollment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CoursePublishView(APIView):
    """Publish a course"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    
    def post(self, request, uuid):
        course = get_object_or_404(Course, uuid=uuid)
        self.check_object_permissions(request, course)
        
        course.publish()
        
        # Notify enrolled students
        bulk_notify_enrolled_students(
            course,
            'course_update',
            f'{course.title} is now published',
            'The course you enrolled in is now available'
        )
        
        return Response({'message': 'Course published successfully'})

class CourseAnalyticsView(APIView):
    """Get course analytics"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    
    def get(self, request, uuid):
        course = get_object_or_404(Course, uuid=uuid)
        self.check_object_permissions(request, course)
        
        analytics = {
            'total_enrollments': course.enrollments.count(),
            'active_students': course.enrollments.filter(is_active=True).count(),
            'completed_students': course.enrollments.filter(status='completed').count(),
            'average_progress': course.enrollments.aggregate(
                avg_progress=Avg('progress_percentage')
            )['avg_progress'] or 0,
            'average_rating': course.reviews.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
            'total_reviews': course.reviews.count(),
        }
        
        return Response(analytics)

# Enrollments
class EnrollmentListView(generics.ListAPIView):
    """List user enrollments"""
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

class EnrollmentDetailView(generics.RetrieveAPIView):
    """Get enrollment details"""
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

class MyCoursesView(generics.ListAPIView):
    """Get user's enrolled courses"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user,
            is_active=True
        ).select_related('course', 'course__instructor')

# Modules
class ModuleListCreateView(generics.ListCreateAPIView):
    """List and create modules"""
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
    """Retrieve, update or delete module"""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]

# Lessons
class LessonListCreateView(generics.ListCreateAPIView):
    """List and create lessons"""
    queryset = Lesson.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonFilter
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'module', 'module__course'
        ).prefetch_related('resources')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LessonListSerializer
        return LessonDetailSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]

class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete lesson"""
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]
    
    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        
        # Track lesson start
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=lesson.module.course,
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
        
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

class LessonCompleteView(APIView):
    """Mark lesson as completed"""
    permission_classes = [IsAuthenticated, IsEnrolledStudent]
    
    def post(self, request, uuid):
        lesson = get_object_or_404(Lesson, uuid=uuid)
        
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=lesson.module.course,
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
            update_enrollment_progress(enrollment)
            
            # Track activity
            track_activity(
                request.user,
                'lesson_complete',
                lesson=lesson,
                course=lesson.module.course
            )
            
            # Send notification if course completed
            if enrollment.progress_percentage >= 100:
                send_notification(
                    request.user,
                    'course_completed',
                    f'Congratulations! You completed {enrollment.course.title}',
                    'You have successfully completed all lessons in the course',
                    course=enrollment.course
                )
        
        return Response({'message': 'Lesson marked as completed'})

# Quizzes
class QuizListCreateView(generics.ListCreateAPIView):
    """List and create quizzes"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuizFilter
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'questions__answers'
        ).select_related('course')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]

class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete quiz"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsCourseInstructor()]
        return [IsAuthenticated(), IsEnrolledStudent()]

class QuizStartAttemptView(APIView):
    """Start quiz attempt"""
    permission_classes = [IsAuthenticated, IsEnrolledStudent]
    
    def post(self, request, uuid):
        quiz = get_object_or_404(Quiz, uuid=uuid)
        
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=quiz.course,
            is_active=True
        )
        
        # Check max attempts
        attempts_count = QuizAttempt.objects.filter(
            quiz=quiz,
            student=request.user
        ).count()
        
        if quiz.max_attempts and attempts_count >= quiz.max_attempts:
            return Response(
                {'error': 'Maximum attempts reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            enrollment=enrollment,
            attempt_number=attempts_count + 1
        )
        
        track_activity(
            request.user,
            'quiz_start',
            quiz=quiz,
            course=quiz.course
        )
        
        serializer = QuizAttemptSerializer(attempt, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuizSubmitView(APIView):
    """Submit quiz answers"""
    permission_classes = [IsAuthenticated, IsEnrolledStudent]
    
    def post(self, request, uuid):
        quiz = get_object_or_404(Quiz, uuid=uuid)
        serializer = QuizSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get active attempt
        attempt = QuizAttempt.objects.filter(
            quiz=quiz,
            student=request.user,
            completed_at__isnull=True
        ).first()
        
        if not attempt:
            return Response(
                {'error': 'No active quiz attempt found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process responses
        total_score = 0
        total_points = 0
        
        for response_data in serializer.validated_data['responses']:
            question = get_object_or_404(Question, uuid=response_data['question_id'])
            total_points += question.points
            
            response = QuestionResponse.objects.create(
                attempt=attempt,
                question=question
            )
            
            if question.question_type in ['multiple_choice', 'true_false']:
                answer = get_object_or_404(Answer, uuid=response_data['answer_id'])
                response.selected_answer = answer
                response.is_correct = answer.is_correct
                if answer.is_correct:
                    response.points_earned = question.points
                    total_score += question.points
            else:
                response.text_response = response_data.get('text_response', '')
                # Manual grading required for other types
            
            response.save()
        
        # Complete attempt
        attempt.completed_at = timezone.now()
        attempt.score = (total_score / total_points * 100) if total_points > 0 else 0
        attempt.passed = attempt.score >= quiz.passing_score
        attempt.save()
        
        # Track activity
        track_activity(
            request.user,
            'quiz_submit',
            quiz=quiz,
            course=quiz.course,
            metadata={'score': float(attempt.score)}
        )
        
        # Send notification
        send_notification(
            request.user,
            'quiz_result',
            f'Quiz completed: {quiz.title}',
            f'You scored {attempt.score:.1f}% - {"Passed" if attempt.passed else "Failed"}',
            course=quiz.course
        )
        
        return Response({
            'score': attempt.score,
            'passed': attempt.passed,
            'message': 'Quiz submitted successfully'
        })

# Certificates
class CertificateListView(generics.ListAPIView):
    """List certificates"""
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
    """Get certificate details"""
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

class CertificateVerifyView(APIView):
    """Verify certificate authenticity"""
    permission_classes = [AllowAny]
    
    def get(self, request, uuid):
        certificate = get_object_or_404(Certificate, uuid=uuid)
        
        return Response({
            'valid': certificate.is_valid,
            'certificate_number': certificate.certificate_number,
            'student_name': certificate.student.get_full_name(),
            'course_title': certificate.course.title,
            'issue_date': certificate.issue_date,
            'completion_date': certificate.completion_date,
        })

# Reviews
class CourseReviewListCreateView(generics.ListCreateAPIView):
    """List and create course reviews"""
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
    """Retrieve, update or delete review"""
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uuid'
# back/courses/urls.py - Add categories endpoint
from django.urls import path

from .views import (
    CategoryListView, CategoryDetailView,
    CourseListCreateView, CourseDetailView, CourseEnrollView,
    CoursePublishView, CourseAnalyticsView,
    EnrollmentListView, EnrollmentDetailView, MyCoursesView,
    ModuleListCreateView, ModuleDetailView,
    LessonListCreateView, LessonDetailView, LessonCompleteView,
    QuizListCreateView, QuizDetailView, QuizStartAttemptView, QuizSubmitView,
    CertificateListView, CertificateDetailView, CertificateVerifyView,
    CourseReviewListCreateView, CourseReviewDetailView
)

app_name = 'courses'

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Courses
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<uuid:uuid>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<uuid:uuid>/enroll/', CourseEnrollView.as_view(), name='course-enroll'),
    path('courses/<uuid:uuid>/publish/', CoursePublishView.as_view(), name='course-publish'),
    path('courses/<uuid:uuid>/analytics/', CourseAnalyticsView.as_view(), name='course-analytics'),
    
    # Enrollments
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment-list'),
    path('enrollments/<uuid:uuid>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),
    path('enrollments/my-courses/', MyCoursesView.as_view(), name='my-courses'),
    
    # Modules
    path('modules/', ModuleListCreateView.as_view(), name='module-list'),
    path('modules/<uuid:uuid>/', ModuleDetailView.as_view(), name='module-detail'),
    
    # Lessons
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('lessons/<uuid:uuid>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<uuid:uuid>/complete/', LessonCompleteView.as_view(), name='lesson-complete'),
    
    # Quizzes
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list'),
    path('quizzes/<uuid:uuid>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<uuid:uuid>/start/', QuizStartAttemptView.as_view(), name='quiz-start'),
    path('quizzes/<uuid:uuid>/submit/', QuizSubmitView.as_view(), name='quiz-submit'),
    
    # Certificates
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<uuid:uuid>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificates/<uuid:uuid>/verify/', CertificateVerifyView.as_view(), name='certificate-verify'),
    
    # Reviews
    path('reviews/', CourseReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<uuid:uuid>/', CourseReviewDetailView.as_view(), name='review-detail'),
]
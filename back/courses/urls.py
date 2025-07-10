from django.urls import path
from .views import (
    # Categories
    CategoryListView, CategoryDetailView,
    
    # Courses - Main CRUD
    CourseListCreateView, CourseDetailView,
    
    # Course Actions
    CourseEnrollView, CoursePublishView, CourseAnalyticsView, CourseImageUploadView,
    CourseFavoriteCheckView, CourseFavoriteAddView, CourseFavoriteRemoveView,
    
    # Lessons under Course
    CourseLessonListCreateView, CourseLessonDetailView, LessonFileUploadView,
    LessonCompleteView, LessonNotesView,
    
    # Enrollments
    EnrollmentListView, MyEnrollmentsView,
    
    # Modules
    ModuleListCreateView, ModuleDetailView,
    
    # Reviews
    CourseReviewListCreateView, CourseReviewDetailView,
    
    TeacherCoursesView, TeacherStudentsView,
    # Certificates
    CertificateListView, CertificateDetailView, CertificateVerifyView,
)

app_name = 'courses'

urlpatterns = [
    # ===== CATEGORIES =====
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # ===== COURSES - MAIN CRUD =====
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<uuid:uuid>/', CourseDetailView.as_view(), name='course-detail'),
    
    # ===== COURSE ACTIONS =====
    # Enrollment
    path('courses/<uuid:uuid>/enroll/', CourseEnrollView.as_view(), name='course-enroll'),
    
    # Publishing & Management
    path('courses/<uuid:uuid>/publish/', CoursePublishView.as_view(), name='course-publish'),
    path('courses/<uuid:uuid>/analytics/', CourseAnalyticsView.as_view(), name='course-analytics'),
    
    # File Upload
    path('courses/<uuid:uuid>/upload-image/', CourseImageUploadView.as_view(), name='course-image-upload'),
    
    # Favorites
    path('courses/<uuid:uuid>/is-favorite/', CourseFavoriteCheckView.as_view(), name='course-is-favorite'),
    path('courses/<uuid:uuid>/add-to-favorites/', CourseFavoriteAddView.as_view(), name='course-add-favorite'),
    path('courses/<uuid:uuid>/remove-from-favorites/', CourseFavoriteRemoveView.as_view(), name='course-remove-favorite'),
    
    # ===== LESSONS UNDER COURSE =====
    path('courses/<uuid:course_uuid>/lessons/', CourseLessonListCreateView.as_view(), name='course-lessons'),
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/', CourseLessonDetailView.as_view(), name='course-lesson-detail'),
    
    # Lesson Actions
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/upload/', LessonFileUploadView.as_view(), name='lesson-file-upload'),
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/complete/', LessonCompleteView.as_view(), name='lesson-complete'),
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/notes/', LessonNotesView.as_view(), name='lesson-notes'),
    

    path('courses/teacher/', TeacherCoursesView.as_view(), name='teacher-courses'),
    path('courses/teacher/students/', TeacherStudentsView.as_view(), name='teacher-students'),
    
    # ===== ENROLLMENTS =====
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment-list'),
    path('enrollments/my-courses/', MyEnrollmentsView.as_view(), name='my-courses'),
    
    # ===== MODULES =====
    path('modules/', ModuleListCreateView.as_view(), name='module-list-create'),
    path('modules/<uuid:uuid>/', ModuleDetailView.as_view(), name='module-detail'),
    
    # ===== REVIEWS =====
    path('reviews/', CourseReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<uuid:uuid>/', CourseReviewDetailView.as_view(), name='review-detail'),
    
    # ===== CERTIFICATES =====
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<uuid:uuid>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificates/<uuid:uuid>/verify/', CertificateVerifyView.as_view(), name='certificate-verify'),
]

# Alternative URL patterns for different API versions or organization
# (Uncomment if you want to use them)

# API v1 patterns (more RESTful grouping)
"""
v1_patterns = [
    # Categories
    path('v1/categories/', CategoryListView.as_view()),
    path('v1/categories/<slug:slug>/', CategoryDetailView.as_view()),
    
    # Courses
    path('v1/courses/', CourseListCreateView.as_view()),
    path('v1/courses/<uuid:uuid>/', CourseDetailView.as_view()),
    path('v1/courses/<uuid:uuid>/enroll/', CourseEnrollView.as_view()),
    path('v1/courses/<uuid:uuid>/publish/', CoursePublishView.as_view()),
    
    # Nested resources
    path('v1/courses/<uuid:course_uuid>/lessons/', CourseLessonListCreateView.as_view()),
    path('v1/courses/<uuid:course_uuid>/lessons/<uuid:uuid>/', CourseLessonDetailView.as_view()),
    
    # User-specific endpoints
    path('v1/my/enrollments/', MyEnrollmentsView.as_view()),
    path('v1/my/certificates/', CertificateListView.as_view()),
]
"""

# Flat URL structure (if you prefer non-nested URLs)
"""
flat_patterns = [
    # Main resources
    path('categories/', CategoryListView.as_view()),
    path('courses/', CourseListCreateView.as_view()),
    path('lessons/', CourseLessonListCreateView.as_view()),  # Would need view modification
    path('modules/', ModuleListCreateView.as_view()),
    path('enrollments/', EnrollmentListView.as_view()),
    path('reviews/', CourseReviewListCreateView.as_view()),
    path('certificates/', CertificateListView.as_view()),
    
    # Detail views
    path('categories/<slug:slug>/', CategoryDetailView.as_view()),
    path('courses/<uuid:uuid>/', CourseDetailView.as_view()),
    path('lessons/<uuid:uuid>/', CourseLessonDetailView.as_view()),  # Would need view modification
    path('modules/<uuid:uuid>/', ModuleDetailView.as_view()),
    path('reviews/<uuid:uuid>/', CourseReviewDetailView.as_view()),
    path('certificates/<uuid:uuid>/', CertificateDetailView.as_view()),
    
    # Actions
    path('courses/<uuid:uuid>/enroll/', CourseEnrollView.as_view()),
    path('lessons/<uuid:uuid>/complete/', LessonCompleteView.as_view()),  # Would need view modification
    path('certificates/<uuid:uuid>/verify/', CertificateVerifyView.as_view()),
]
"""
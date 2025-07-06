from django.urls import path

from .views import (
    CategoryListView, CategoryDetailView,
    CourseListCreateView, CourseDetailView, CourseEnrollView,
    CoursePublishView, CourseAnalyticsView, CourseImageUploadView,
    CourseFavoriteCheckView, CourseFavoriteAddView, CourseFavoriteRemoveView,
    CourseLessonListCreateView, CourseLessonDetailView, LessonFileUploadView,
    LessonCompleteView, LessonNotesView,
    EnrollmentListView, MyEnrollmentsView,
    ModuleListCreateView, ModuleDetailView,
    CertificateListView, CertificateDetailView, CertificateVerifyView,
    CourseReviewListCreateView, CourseReviewDetailView
)

app_name = 'courses'

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Courses - Main CRUD
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<uuid:uuid>/', CourseDetailView.as_view(), name='course-detail'),
    
    # Course Actions
    path('courses/<uuid:uuid>/enroll/', CourseEnrollView.as_view(), name='course-enroll'),
    path('courses/<uuid:uuid>/publish/', CoursePublishView.as_view(), name='course-publish'),
    path('courses/<uuid:uuid>/analytics/', CourseAnalyticsView.as_view(), name='course-analytics'),
    path('courses/<uuid:uuid>/upload-image/', CourseImageUploadView.as_view(), name='course-image-upload'),
    path('courses/<uuid:uuid>/is-favorite/', CourseFavoriteCheckView.as_view(), name='course-is-favorite'),
    path('courses/<uuid:uuid>/add-to-favorites/', CourseFavoriteAddView.as_view(), name='course-add-favorite'),
    path('courses/<uuid:uuid>/remove-from-favorites/', CourseFavoriteRemoveView.as_view(), name='course-remove-favorite'),
    
    # Lessons under Course
    path('courses/<uuid:course_uuid>/lessons/', CourseLessonListCreateView.as_view(), name='course-lessons'),
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/', CourseLessonDetailView.as_view(), name='course-lesson-detail'),
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/upload/', LessonFileUploadView.as_view(), name='lesson-file-upload'),
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/complete/', LessonCompleteView.as_view(), name='lesson-complete'),
    path('courses/<uuid:course_uuid>/lessons/<uuid:uuid>/notes/', LessonNotesView.as_view(), name='lesson-notes'),
    
    # Enrollments
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment-list'),
    path('enrollments/my-courses/', MyEnrollmentsView.as_view(), name='my-courses'),
    
    # Modules
    path('modules/', ModuleListCreateView.as_view(), name='module-list-create'),
    path('modules/<uuid:uuid>/', ModuleDetailView.as_view(), name='module-detail'),
    
    # Certificates
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<uuid:uuid>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificates/<uuid:uuid>/verify/', CertificateVerifyView.as_view(), name='certificate-verify'),
    
    # Reviews
    path('reviews/', CourseReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<uuid:uuid>/', CourseReviewDetailView.as_view(), name='review-detail'),
]
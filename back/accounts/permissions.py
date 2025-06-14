from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.translation import gettext_lazy as _

class IsOwnerOrReadOnly(BasePermission):
    """Object owner can edit, others can only read"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)

class IsTeacherOrAdmin(BasePermission):
    """Only teachers, moderators, managers, or admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.role in ['teacher', 'moderator', 'manager']
        )

class IsCourseInstructor(BasePermission):
    """Only course instructor or co-instructors"""
    def has_object_permission(self, request, view, obj):
        course = obj if hasattr(obj, 'instructor') else getattr(obj, 'course', None)
        if not course:
            return False
        return (
            course.instructor == request.user or 
            request.user in course.co_instructors.all() or
            request.user.is_staff
        )

class IsEnrolledStudent(BasePermission):
    """Only enrolled students can access course content"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        course = getattr(obj, 'course', obj)
        if hasattr(obj, 'module'):
            course = obj.module.course
        return course.enrollments.filter(student=request.user, is_active=True).exists()

class IsManagerOrAdmin(BasePermission):
    """Only managers or admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.role == 'manager'
        )

class IsVerifiedUser(BasePermission):
    """Only verified users"""
    message = _('Email verification required.')
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified

class IsModeratorOrUp(BasePermission):
    """Moderators, managers, or admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.role in ['moderator', 'manager']
        )

class CanCreateCourse(BasePermission):
    """Teachers and above can create courses"""
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated and (
                request.user.is_staff or 
                request.user.role in ['teacher', 'manager']
            )
        return True
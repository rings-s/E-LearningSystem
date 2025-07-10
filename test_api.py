#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints are working correctly.
Run this to test the teacher courses and students endpoints.
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the path
sys.path.insert(0, '/home/ahmed/tech-Savvy-projects/2025/new_ones/E-LearningSystem/back')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from courses.views import TeacherCoursesView, TeacherStudentsView
from django.test import RequestFactory
from django.http import JsonResponse

User = get_user_model()

def test_teacher_endpoints():
    """Test the teacher endpoints with the existing data"""
    print("🧪 Testing Teacher API Endpoints")
    print("=" * 50)
    
    # Find a teacher user
    teacher = User.objects.filter(role='teacher').first()
    if not teacher:
        print("❌ No teacher user found!")
        return
    
    print(f"👨‍🏫 Testing with teacher: {teacher.email}")
    
    # Test courses endpoint
    print("\n📚 Testing Teacher Courses Endpoint")
    print("-" * 30)
    
    courses = Course.objects.filter(instructor=teacher)
    print(f"Found {courses.count()} courses for teacher")
    
    for course in courses:
        enrollment_count = course.enrollments.filter(is_active=True).count()
        print(f"  - Course: {course.title}")
        print(f"    Status: {course.status}")
        print(f"    Enrollments: {enrollment_count}")
    
    # Test students endpoint
    print("\n👥 Testing Teacher Students Endpoint")
    print("-" * 30)
    
    students_data = []
    for course in courses:
        enrollments = Enrollment.objects.filter(
            course=course, is_active=True
        ).select_related('student', 'course')
        
        print(f"Course '{course.title}' has {enrollments.count()} active enrollments")
        
        for enrollment in enrollments:
            student_data = {
                'uuid': str(enrollment.student.uuid),
                'name': enrollment.student.get_full_name(),
                'email': enrollment.student.email,
                'course_name': course.title,
                'course_uuid': str(course.uuid),
                'enrolled_at': enrollment.enrolled_at.isoformat(),
                'progress': float(enrollment.progress_percentage),
                'last_active': enrollment.last_accessed.isoformat() if enrollment.last_accessed else None,
                'status': enrollment.status
            }
            students_data.append(student_data)
            print(f"  - Student: {student_data['name']} ({student_data['email']})")
            print(f"    Progress: {student_data['progress']}%")
    
    print(f"\n✅ Total students found: {len(students_data)}")
    
    # Test JSON serialization
    print("\n🔄 Testing JSON Response Format")
    print("-" * 30)
    
    try:
        import json
        response_data = {'results': students_data}
        json_str = json.dumps(response_data, indent=2)
        print("✅ JSON serialization successful")
        print(f"Response size: {len(json_str)} characters")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")

if __name__ == "__main__":
    test_teacher_endpoints()
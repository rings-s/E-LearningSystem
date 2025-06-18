import pandas as pd
import numpy as np
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any
from courses.models import Course, Enrollment, Quiz, QuizAttempt, Lesson, LessonProgress
from core.models import ActivityLog, Discussion, Reply
from accounts.models import CustomUser as User

class AnalyticsDataProcessor:
    """Process data for analytics visualizations"""
    
    @staticmethod
    def get_student_progress_data(user: User) -> List[Dict]:
        """Get progress data for all student's enrolled courses"""
        enrollments = Enrollment.objects.filter(
            student=user,
            is_active=True
        ).select_related('course')
        
        progress_data = []
        for enrollment in enrollments:
            progress_data.append({
                'course_title': enrollment.course.title,
                'progress_percentage': float(enrollment.progress_percentage),
                'status': enrollment.status,
                'enrolled_date': enrollment.enrolled_at.isoformat(),
                'last_accessed': enrollment.last_accessed.isoformat() if enrollment.last_accessed else None
            })
        
        return progress_data
    
    @staticmethod
    def get_learning_activity_heatmap_data(user: User, days: int = 30) -> List[Dict]:
        """Get activity data for heatmap visualization"""
        start_date = timezone.now() - timedelta(days=days)
        
        activities = ActivityLog.objects.filter(
            user=user,
            created_at__gte=start_date
        ).values('created_at')
        
        # Process into hourly buckets
        heatmap_data = []
        for activity in activities:
            created_at = activity['created_at']
            heatmap_data.append({
                'day_of_week': created_at.strftime('%A'),
                'hour': created_at.hour,
                'activity_count': 1
            })
        
        # Aggregate data
        df = pd.DataFrame(heatmap_data)
        if not df.empty:
            aggregated = df.groupby(['day_of_week', 'hour']).size().reset_index(name='activity_count')
            return aggregated.to_dict('records')
        
        return []
    
    @staticmethod
    def get_quiz_performance_data(user: User, course_id: str = None) -> List[Dict]:
        """Get quiz performance data over time"""
        query = QuizAttempt.objects.filter(
            student=user,
            completed_at__isnull=False
        ).select_related('quiz')
        
        if course_id:
            query = query.filter(quiz__course__uuid=course_id)
        
        performance_data = []
        for attempt in query.order_by('completed_at'):
            performance_data.append({
                'date': attempt.completed_at.date().isoformat(),
                'score': float(attempt.score) if attempt.score else 0,
                'quiz_title': attempt.quiz.title,
                'passed': attempt.passed
            })
        
        return performance_data
    
    @staticmethod
    def get_course_completion_funnel_data(course_id: str) -> List[Dict]:
        """Get funnel data for course completion stages"""
        enrollments = Enrollment.objects.filter(course__uuid=course_id)
        
        total = enrollments.count()
        started = enrollments.filter(started_at__isnull=False).count()
        progress_25 = enrollments.filter(progress_percentage__gte=25).count()
        progress_50 = enrollments.filter(progress_percentage__gte=50).count()
        progress_75 = enrollments.filter(progress_percentage__gte=75).count()
        completed = enrollments.filter(status='completed').count()
        
        return [
            {'stage': 'Enrolled', 'count': total},
            {'stage': 'Started', 'count': started},
            {'stage': '25% Complete', 'count': progress_25},
            {'stage': '50% Complete', 'count': progress_50},
            {'stage': '75% Complete', 'count': progress_75},
            {'stage': 'Completed', 'count': completed}
        ]
    
    @staticmethod
    def get_engagement_metrics(course_id: str = None) -> Dict:
        """Get overall engagement metrics"""
        base_query = ActivityLog.objects.all()
        if course_id:
            base_query = base_query.filter(course__uuid=course_id)
        
        # Calculate metrics
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Discussion participation
        total_users = User.objects.filter(is_active=True).count()
        active_discussers = Discussion.objects.filter(
            created_at__gte=last_30_days
        ).values('author').distinct().count()
        
        viewers = ActivityLog.objects.filter(
            activity_type='course_view',
            created_at__gte=last_30_days
        ).values('user').distinct().count()
        
        # Average session duration (simulated for now)
        avg_session = 45  # This would be calculated from actual session data
        
        return {
            'discussion_participation': {
                'active': active_discussers,
                'viewers': viewers - active_discussers,
                'none': total_users - viewers
            },
            'avg_session_duration': avg_session
        }
    
    @staticmethod
    def get_teacher_analytics_data(teacher: User) -> Dict:
        """Get analytics data for teacher dashboard"""
        courses = Course.objects.filter(instructor=teacher)
        
        # Get top students
        top_students_query = QuizAttempt.objects.filter(
            quiz__course__instructor=teacher,
            completed_at__isnull=False
        ).values('student__email', 'student__first_name', 'student__last_name').annotate(
            avg_score=Avg('score'),
            total_quizzes=Count('id')
        ).order_by('-avg_score')[:5]
        
        top_students = []
        for student in top_students_query:
            top_students.append({
                'name': f"{student['student__first_name']} {student['student__last_name']}",
                'avg_score': float(student['avg_score'] or 0),
                'courses': student['total_quizzes']
            })
        
        # Progress distribution
        progress_data = []
        for course in courses:
            enrollments = course.enrollments.filter(is_active=True)
            for enrollment in enrollments:
                progress_data.append({
                    'course': course.title,
                    'progress': float(enrollment.progress_percentage)
                })
        
        # Quiz success rates
        quiz_data = Quiz.objects.filter(
            course__instructor=teacher
        ).annotate(
            attempts_count=Count('attempts'),
            pass_count=Count('attempts', filter=Q(attempts__passed=True))
        )
        
        quiz_names = []
        success_rates = []
        for quiz in quiz_data:
            if quiz.attempts_count > 0:
                quiz_names.append(quiz.title)
                success_rates.append(
                    (quiz.pass_count / quiz.attempts_count) * 100
                )
        
        return {
            'top_students': top_students,
            'progress_distribution': progress_data,
            'quiz_names': quiz_names,
            'quiz_success_rates': success_rates
        }
    
    @staticmethod
    def get_course_analytics_data(course_id: str) -> Dict:
        """Get detailed analytics for a specific course"""
        course = Course.objects.get(uuid=course_id)
        
        # Module completion rates
        modules = []
        for module in course.modules.all():
            total_lessons = module.lessons.count()
            if total_lessons > 0:
                completed_lessons = LessonProgress.objects.filter(
                    lesson__module=module,
                    is_completed=True
                ).count()
                
                modules.append({
                    'name': module.title,
                    'completion_rate': (completed_lessons / total_lessons) * 100
                })
        
        # Quiz scores over time
        quiz_attempts = QuizAttempt.objects.filter(
            quiz__course=course,
            completed_at__isnull=False
        ).values('completed_at').annotate(
            avg_score=Avg('score')
        ).order_by('completed_at')
        
        quiz_dates = []
        avg_scores = []
        for attempt in quiz_attempts:
            quiz_dates.append(attempt['completed_at'].date().isoformat())
            avg_scores.append(float(attempt['avg_score'] or 0))
        
        # Time spent distribution (simulated)
        time_spent = np.random.lognormal(3.5, 0.8, 200)
        
        # Satisfaction score
        avg_rating = course.reviews.aggregate(Avg('rating'))['rating__avg'] or 4.0
        
        return {
            'start_date': course.created_at,
            'modules': modules,
            'quiz_dates': quiz_dates,
            'avg_quiz_scores': avg_scores,
            'time_spent_distribution': time_spent.tolist(),
            'satisfaction_score': float(avg_rating)
        }
    
    @staticmethod
    def get_platform_overview_data() -> Dict:
        """Get platform-wide analytics data"""
        # Categories and course distribution
        categories = Course.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        category_names = [c['category__name'] for c in categories]
        course_counts = [c['count'] for c in categories]
        
        # Popular courses
        popular_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:5]
        
        popular_courses_data = []
        for course in popular_courses:
            popular_courses_data.append({
                'title': course.title,
                'enrollments': course.enrollment_count
            })
        
        # Completion rates by level
        completion_by_level = {}
        for level, _ in Course.LEVEL_CHOICES:
            enrollments = Enrollment.objects.filter(
                course__level=level
            )
            total = enrollments.count()
            completed = enrollments.filter(status='completed').count()
            
            if total > 0:
                completion_by_level[level] = (completed / total) * 100
            else:
                completion_by_level[level] = 0
        
        # Support ticket status
        from core.models import SupportTicket
        ticket_status = SupportTicket.objects.values('status').annotate(
            count=Count('id')
        )
        
        ticket_data = {}
        for status in ticket_status:
            ticket_data[status['status']] = status['count']
        
        # System health (simulated)
        health_score = 92  # This would be calculated from real metrics
        
        return {
            'categories': category_names,
            'course_counts': course_counts,
            'popular_courses': popular_courses_data,
            'completion_by_level': [
                completion_by_level.get('beginner', 0),
                completion_by_level.get('intermediate', 0),
                completion_by_level.get('advanced', 0)
            ],
            'ticket_status': ticket_data,
            'health_score': health_score
        }
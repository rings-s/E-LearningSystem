from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta, date
from typing import Dict, List, Any
from courses.models import Course, Enrollment, Quiz, QuizAttempt, Lesson, LessonProgress
from core.models import ActivityLog, Discussion
from accounts.models import CustomUser as User

class ELearningAnalytics:
    """Simple, focused analytics for e-learning platform"""
    
    @staticmethod
    def get_student_progress_overview(user: User) -> Dict[str, Any]:
        """Get comprehensive student progress data"""
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        
        # Course progress data
        course_progress = []
        for enrollment in enrollments:
            course_progress.append({
                'course_id': str(enrollment.course.uuid),
                'course_title': enrollment.course.title,
                'progress': float(enrollment.progress_percentage),
                'status': enrollment.status,
                'enrolled_date': enrollment.enrolled_at.date().isoformat(),
                'estimated_completion': enrollment.course.duration_hours,
                'instructor': enrollment.course.instructor.get_full_name()
            })
        
        # Learning streak (days with activity)
        today = timezone.now().date()
        streak_days = 0
        for i in range(30):  # Check last 30 days
            check_date = today - timedelta(days=i)
            has_activity = ActivityLog.objects.filter(
                user=user,
                created_at__date=check_date
            ).exists()
            if has_activity:
                streak_days += 1
            else:
                break
        
        # Study time analysis
        study_time_data = ELearningAnalytics._get_study_time_breakdown(user)
        
        return {
            'courses': course_progress,
            'streak_days': streak_days,
            'study_time': study_time_data,
            'summary': {
                'total_courses': enrollments.count(),
                'completed': enrollments.filter(status='completed').count(),
                'in_progress': enrollments.filter(status='in_progress').count(),
                'avg_progress': enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
            }
        }
    
    @staticmethod
    def get_student_performance_metrics(user: User) -> Dict[str, Any]:
        """Get student quiz and assessment performance"""
        quiz_attempts = QuizAttempt.objects.filter(
            student=user,
            completed_at__isnull=False
        ).order_by('-completed_at')
        
        # Performance trend (last 10 quizzes)
        performance_trend = []
        for attempt in quiz_attempts[:10]:
            performance_trend.append({
                'quiz_title': attempt.quiz.title,
                'course': attempt.quiz.course.title,
                'score': float(attempt.score) if attempt.score else 0,
                'passed': attempt.passed,
                'date': attempt.completed_at.date().isoformat(),
                'attempt_number': attempt.attempt_number
            })
        
        # Subject performance breakdown
        subject_performance = quiz_attempts.values(
            'quiz__course__category__name'
        ).annotate(
            avg_score=Avg('score'),
            total_attempts=Count('id'),
            passed_count=Count('id', filter=Q(passed=True))
        ).order_by('-avg_score')
        
        subject_data = []
        for subject in subject_performance:
            if subject['quiz__course__category__name']:
                subject_data.append({
                    'subject': subject['quiz__course__category__name'],
                    'avg_score': round(float(subject['avg_score'] or 0), 1),
                    'success_rate': round(
                        (subject['passed_count'] / subject['total_attempts'] * 100) 
                        if subject['total_attempts'] > 0 else 0, 1
                    ),
                    'total_quizzes': subject['total_attempts']
                })
        
        return {
            'performance_trend': performance_trend,
            'subject_performance': subject_data,
            'overall_stats': {
                'total_quizzes': quiz_attempts.count(),
                'avg_score': quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0,
                'pass_rate': quiz_attempts.filter(passed=True).count() / max(quiz_attempts.count(), 1) * 100
            }
        }
    
    @staticmethod
    def get_teacher_course_analytics(teacher: User) -> Dict[str, Any]:
        """Get comprehensive teacher analytics"""
        courses = Course.objects.filter(instructor=teacher)
        
        # Course performance overview
        course_stats = []
        for course in courses:
            enrollments = course.enrollments.filter(is_active=True)
            
            course_stats.append({
                'course_id': str(course.uuid),
                'title': course.title,
                'total_students': enrollments.count(),
                'completed_students': enrollments.filter(status='completed').count(),
                'avg_progress': enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0,
                'avg_rating': course.reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
                'total_reviews': course.reviews.count(),
                'engagement_score': ELearningAnalytics._calculate_engagement_score(course)
            })
        
        # Student activity analysis
        student_activity = ELearningAnalytics._get_teacher_student_activity(teacher)
        
        # Discussion engagement
        discussion_stats = Discussion.objects.filter(
            forum__course__instructor=teacher
        ).aggregate(
            total_discussions=Count('id'),
            resolved_questions=Count('id', filter=Q(discussion_type='question', is_resolved=True)),
            total_questions=Count('id', filter=Q(discussion_type='question'))
        )
        
        return {
            'course_performance': course_stats,
            'student_activity': student_activity,
            'discussion_engagement': {
                'total_discussions': discussion_stats['total_discussions'],
                'question_resolution_rate': round(
                    (discussion_stats['resolved_questions'] / max(discussion_stats['total_questions'], 1)) * 100, 1
                )
            }
        }
    
    @staticmethod
    def get_platform_overview() -> Dict[str, Any]:
        """Get platform-wide analytics for managers"""
        
        # User growth (last 6 months)
        user_growth = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            new_users = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count()
            
            user_growth.append({
                'month': month_start.strftime('%b %Y'),
                'new_users': new_users
            })
        
        user_growth.reverse()
        
        # Course category distribution
        category_stats = Course.objects.values(
            'category__name'
        ).annotate(
            course_count=Count('id'),
            total_enrollments=Count('enrollments', filter=Q(enrollments__is_active=True))
        ).order_by('-course_count')
        
        category_data = []
        for cat in category_stats:
            if cat['category__name']:
                category_data.append({
                    'category': cat['category__name'],
                    'courses': cat['course_count'],
                    'enrollments': cat['total_enrollments']
                })
        
        # Platform health metrics
        total_users = User.objects.filter(is_active=True).count()
        active_users = ActivityLog.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('user').distinct().count()
        
        return {
            'user_growth': user_growth,
            'category_distribution': category_data,
            'platform_health': {
                'total_users': total_users,
                'active_users_30d': active_users,
                'user_engagement_rate': round((active_users / max(total_users, 1)) * 100, 1),
                'total_courses': Course.objects.count(),
                'published_courses': Course.objects.filter(status='published').count(),
                'total_enrollments': Enrollment.objects.filter(is_active=True).count()
            }
        }
    
    # Helper methods
    @staticmethod
    def _get_study_time_breakdown(user: User) -> Dict[str, Any]:
        """Get detailed study time analysis"""
        last_30_days = timezone.now() - timedelta(days=30)
        
        # Daily study time for last 30 days
        daily_study = []
        for i in range(30):
            day = (timezone.now() - timedelta(days=i)).date()
            
            time_spent = LessonProgress.objects.filter(
                enrollment__student=user,
                started_at__date=day
            ).aggregate(
                total=Sum('time_spent_seconds')
            )['total'] or 0
            
            daily_study.append({
                'date': day.isoformat(),
                'minutes': round(time_spent / 60, 1)
            })
        
        daily_study.reverse()
        
        # Weekly average
        total_minutes = sum(day['minutes'] for day in daily_study)
        weekly_avg = total_minutes / 4  # 30 days ≈ 4 weeks
        
        return {
            'daily_breakdown': daily_study,
            'weekly_average': round(weekly_avg, 1),
            'total_hours_30d': round(total_minutes / 60, 1)
        }
    
    @staticmethod
    def _calculate_engagement_score(course: Course) -> float:
        """Calculate course engagement score (0-100)"""
        enrollments = course.enrollments.filter(is_active=True)
        if not enrollments.exists():
            return 0
        
        # Factors: completion rate, avg progress, forum activity, quiz participation
        completion_rate = enrollments.filter(status='completed').count() / enrollments.count()
        avg_progress = enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
        
        forum_activity = Discussion.objects.filter(forum__course=course).count()
        quiz_participation = QuizAttempt.objects.filter(quiz__course=course).count()
        
        # Weighted score
        engagement = (
            completion_rate * 40 +  # 40% weight on completion
            (avg_progress / 100) * 30 +  # 30% weight on progress
            min(forum_activity / enrollments.count(), 1) * 20 +  # 20% weight on discussions
            min(quiz_participation / enrollments.count(), 1) * 10  # 10% weight on quiz participation
        )
        
        return round(engagement * 100, 1)
    
    @staticmethod
    def _get_teacher_student_activity(teacher: User) -> Dict[str, Any]:
        """Get student activity data for teacher's courses"""
        enrollments = Enrollment.objects.filter(
            course__instructor=teacher,
            is_active=True
        )
        
        # Active students (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        active_students = enrollments.filter(
            last_accessed__gte=week_ago
        ).count()
        
        # Students by progress level
        progress_distribution = {
            'not_started': enrollments.filter(progress_percentage=0).count(),
            'in_progress': enrollments.filter(
                progress_percentage__gt=0, 
                progress_percentage__lt=100
            ).count(),
            'completed': enrollments.filter(progress_percentage=100).count()
        }
        
        return {
            'total_students': enrollments.count(),
            'active_students_7d': active_students,
            'progress_distribution': progress_distribution
        }
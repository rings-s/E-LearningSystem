# Simple data processing utilities
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any

class LearningMetrics:
    """Simple learning metrics calculator"""
    
    @staticmethod
    def calculate_engagement_score(course) -> float:
        """Calculate course engagement score (0-100)"""
        enrollments = course.enrollments.filter(is_active=True)
        if not enrollments.exists():
            return 0
        
        completion_rate = enrollments.filter(status='completed').count() / enrollments.count()
        avg_progress = enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
        
        return round((completion_rate * 50 + (avg_progress / 100) * 50) * 100, 1)
    
    @staticmethod
    def get_study_streak(user) -> int:
        """Get user's current study streak in days"""
        from core.models import ActivityLog
        
        today = timezone.now().date()
        streak = 0
        
        for i in range(365):  # Check up to 1 year
            check_date = today - timedelta(days=i)
            has_activity = ActivityLog.objects.filter(
                user=user,
                created_at__date=check_date
            ).exists()
            
            if has_activity:
                streak += 1
            else:
                break
                
        return streak
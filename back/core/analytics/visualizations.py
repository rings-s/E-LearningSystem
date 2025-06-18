from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .charts import LearningAnalyticsCharts
from .data_processors import AnalyticsDataProcessor

class StudentAnalyticsDashboard(LoginRequiredMixin, APIView):
    """Student analytics dashboard endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get all necessary data
        progress_data = AnalyticsDataProcessor.get_student_progress_data(user)
        activity_data = AnalyticsDataProcessor.get_learning_activity_heatmap_data(user)
        quiz_data = AnalyticsDataProcessor.get_quiz_performance_data(user)
        
        # Generate charts
        charts = {
            'progress_chart': LearningAnalyticsCharts.create_student_progress_chart(progress_data),
            'activity_heatmap': LearningAnalyticsCharts.create_learning_activity_heatmap(activity_data),
            'quiz_performance': LearningAnalyticsCharts.create_quiz_performance_chart(quiz_data)
        }
        
        # Additional metrics
        metrics = {
            'total_courses': len(progress_data),
            'completed_courses': sum(1 for p in progress_data if p['status'] == 'completed'),
            'average_progress': sum(p['progress_percentage'] for p in progress_data) / len(progress_data) if progress_data else 0,
            'total_study_hours': user.profile.total_study_hours
        }
        
        return Response({
            'charts': charts,
            'metrics': metrics
        })

class TeacherAnalyticsDashboard(LoginRequiredMixin, APIView):
    """Teacher analytics dashboard endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'teacher' and not user.is_staff:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Get teacher analytics data
        teacher_data = AnalyticsDataProcessor.get_teacher_analytics_data(user)
        
        # Generate dashboard
        dashboard = LearningAnalyticsCharts.create_teacher_analytics_dashboard(teacher_data)
        
        return Response({
            'dashboard': dashboard,
            'summary': {
                'total_students': len(teacher_data.get('progress_distribution', [])),
                'average_completion': sum(p['progress'] for p in teacher_data.get('progress_distribution', [])) / len(teacher_data.get('progress_distribution', [])) if teacher_data.get('progress_distribution') else 0
            }
        })

class CourseAnalyticsView(LoginRequiredMixin, APIView):
    """Course-specific analytics endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_uuid):
        # Check permissions
        from courses.models import Course
        try:
            course = Course.objects.get(uuid=course_uuid)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
        
        # Check if user has access
        if not (course.instructor == request.user or request.user.is_staff):
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Get course analytics
        course_data = AnalyticsDataProcessor.get_course_analytics_data(course_uuid)
        funnel_data = AnalyticsDataProcessor.get_course_completion_funnel_data(course_uuid)
        engagement_metrics = AnalyticsDataProcessor.get_engagement_metrics(course_uuid)
        
        # Generate charts
        charts = {
            'course_report': LearningAnalyticsCharts.create_course_analytics_report(course_data),
            'completion_funnel': LearningAnalyticsCharts.create_course_completion_funnel(funnel_data),
            'engagement_dashboard': LearningAnalyticsCharts.create_engagement_metrics_dashboard(engagement_metrics)
        }
        
        return Response({
            'course': {
                'title': course.title,
                'uuid': str(course.uuid)
            },
            'charts': charts
        })

class PlatformAnalyticsView(LoginRequiredMixin, APIView):
    """Platform-wide analytics for managers"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role not in ['manager', 'admin'] and not user.is_staff:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Get platform data
        platform_data = AnalyticsDataProcessor.get_platform_overview_data()
        
        # Generate dashboard
        dashboard = LearningAnalyticsCharts.create_platform_overview_dashboard(platform_data)
        
        return Response({
            'dashboard': dashboard,
            'last_updated': timezone.now().isoformat()
        })

class ExportAnalyticsView(LoginRequiredMixin, APIView):
    """Export analytics data in various formats"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        export_type = request.data.get('type', 'pdf')
        chart_data = request.data.get('chart_data')
        
        if export_type == 'pdf':
            # Generate PDF report
            pass
        elif export_type == 'excel':
            # Generate Excel report
            pass
        elif export_type == 'png':
            # Export chart as image
            pass
        
        return Response({'message': 'Export functionality to be implemented'})
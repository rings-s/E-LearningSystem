import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from typing import Dict, List, Any, Optional

class LearningAnalyticsCharts:
    """Generate interactive charts for e-learning analytics"""
    
    # Color scheme for consistency
    COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'success': '#48bb78',
        'warning': '#f6ad55',
        'danger': '#fc8181',
        'info': '#4299e1',
        'light': '#e2e8f0',
        'dark': '#2d3748'
    }
    
    CHART_TEMPLATE = {
        'layout': {
            'font': {'family': 'Arial, sans-serif'},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
            'showlegend': True,
            'hovermode': 'x unified'
        }
    }

    @staticmethod
    def create_student_progress_chart(enrollments_data: List[Dict]) -> str:
        """Create a progress chart for student courses"""
        df = pd.DataFrame(enrollments_data)
        
        fig = go.Figure()
        
        # Add progress bars
        fig.add_trace(go.Bar(
            x=df['course_title'],
            y=df['progress_percentage'],
            text=df['progress_percentage'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
            marker=dict(
                color=df['progress_percentage'],
                colorscale=[
                    [0, LearningAnalyticsCharts.COLORS['danger']],
                    [0.5, LearningAnalyticsCharts.COLORS['warning']],
                    [1, LearningAnalyticsCharts.COLORS['success']]
                ],
                showscale=True,
                colorbar=dict(title="Progress %")
            ),
            hovertemplate='<b>%{x}</b><br>Progress: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Course Progress Overview",
            xaxis_title="Courses",
            yaxis_title="Progress (%)",
            yaxis_range=[0, 100],
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()

    @staticmethod
    def create_learning_activity_heatmap(activity_data: List[Dict]) -> str:
        """Create a heatmap showing learning activity patterns"""
        df = pd.DataFrame(activity_data)
        
        # Create pivot table for heatmap
        heatmap_data = df.pivot_table(
            values='activity_count',
            index='hour',
            columns='day_of_week',
            aggfunc='sum',
            fill_value=0
        )
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = [f'{h:02d}:00' for h in range(24)]
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=days,
            y=hours,
            colorscale='Viridis',
            hovertemplate='Day: %{x}<br>Time: %{y}<br>Activities: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Learning Activity Heatmap",
            xaxis_title="Day of Week",
            yaxis_title="Hour of Day",
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()

    @staticmethod
    def create_quiz_performance_chart(quiz_data: List[Dict]) -> str:
        """Create a chart showing quiz performance over time"""
        df = pd.DataFrame(quiz_data)
        
        fig = go.Figure()
        
        # Add score line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['score'],
            mode='lines+markers',
            name='Quiz Scores',
            line=dict(color=LearningAnalyticsCharts.COLORS['primary'], width=3),
            marker=dict(size=8),
            hovertemplate='Date: %{x}<br>Score: %{y:.1f}%<extra></extra>'
        ))
        
        # Add average line
        avg_score = df['score'].mean()
        fig.add_hline(
            y=avg_score,
            line_dash="dash",
            line_color=LearningAnalyticsCharts.COLORS['secondary'],
            annotation_text=f"Average: {avg_score:.1f}%"
        )
        
        # Add passing score line
        fig.add_hline(
            y=60,
            line_dash="dot",
            line_color=LearningAnalyticsCharts.COLORS['warning'],
            annotation_text="Passing Score: 60%"
        )
        
        fig.update_layout(
            title="Quiz Performance Over Time",
            xaxis_title="Date",
            yaxis_title="Score (%)",
            yaxis_range=[0, 100],
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()

    @staticmethod
    def create_course_completion_funnel(funnel_data: List[Dict]) -> str:
        """Create a funnel chart for course completion stages"""
        stages = ['Enrolled', 'Started', '25% Complete', '50% Complete', '75% Complete', 'Completed']
        values = [d['count'] for d in funnel_data]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker=dict(
                color=[
                    LearningAnalyticsCharts.COLORS['info'],
                    LearningAnalyticsCharts.COLORS['primary'],
                    LearningAnalyticsCharts.COLORS['secondary'],
                    LearningAnalyticsCharts.COLORS['warning'],
                    LearningAnalyticsCharts.COLORS['success'],
                    LearningAnalyticsCharts.COLORS['success']
                ]
            ),
            connector=dict(line=dict(color="rgb(63, 63, 63)", width=3))
        ))
        
        fig.update_layout(
            title="Course Completion Funnel",
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()

    @staticmethod
    def create_engagement_metrics_dashboard(metrics: Dict) -> str:
        """Create a comprehensive engagement metrics dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Active Users', 'Content Engagement', 
                          'Discussion Participation', 'Average Session Duration'),
            specs=[[{'type': 'scatter'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'indicator'}]]
        )
        
        # Daily Active Users
        dates = pd.date_range(end=timezone.now(), periods=30, freq='D')
        active_users = np.random.poisson(150, 30) + np.arange(30) * 2
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=active_users,
                mode='lines+markers',
                name='Active Users',
                line=dict(color=LearningAnalyticsCharts.COLORS['primary'])
            ),
            row=1, col=1
        )
        
        # Content Engagement
        content_types = ['Videos', 'Documents', 'Quizzes', 'Discussions']
        engagement_counts = [450, 320, 280, 190]
        
        fig.add_trace(
            go.Bar(
                x=content_types,
                y=engagement_counts,
                marker_color=[
                    LearningAnalyticsCharts.COLORS['primary'],
                    LearningAnalyticsCharts.COLORS['secondary'],
                    LearningAnalyticsCharts.COLORS['warning'],
                    LearningAnalyticsCharts.COLORS['info']
                ]
            ),
            row=1, col=2
        )
        
        # Discussion Participation
        participation_data = metrics.get('discussion_participation', {})
        
        fig.add_trace(
            go.Pie(
                labels=['Active Participants', 'Viewers Only', 'No Participation'],
                values=[
                    participation_data.get('active', 35),
                    participation_data.get('viewers', 45),
                    participation_data.get('none', 20)
                ],
                marker_colors=[
                    LearningAnalyticsCharts.COLORS['success'],
                    LearningAnalyticsCharts.COLORS['warning'],
                    LearningAnalyticsCharts.COLORS['light']
                ]
            ),
            row=2, col=1
        )
        
        # Average Session Duration
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=metrics.get('avg_session_duration', 45),
                delta={'reference': 40},
                gauge={
                    'axis': {'range': [None, 120]},
                    'bar': {'color': LearningAnalyticsCharts.COLORS['primary']},
                    'steps': [
                        {'range': [0, 30], 'color': LearningAnalyticsCharts.COLORS['light']},
                        {'range': [30, 60], 'color': LearningAnalyticsCharts.COLORS['info']},
                        {'range': [60, 120], 'color': LearningAnalyticsCharts.COLORS['success']}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                },
                title={'text': "Minutes"}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()

    @staticmethod
    def create_teacher_analytics_dashboard(teacher_data: Dict) -> str:
        """Create analytics dashboard for teachers"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Student Enrollment Trend', 'Course Ratings Distribution',
                'Student Progress Distribution', 'Quiz Success Rate',
                'Forum Activity', 'Top Performing Students'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'histogram'}],
                [{'type': 'box'}, {'type': 'bar'}],
                [{'type': 'scatter'}, {'type': 'table'}]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # Student Enrollment Trend
        enrollment_dates = pd.date_range(end=timezone.now(), periods=90, freq='D')
        cumulative_enrollments = np.cumsum(np.random.poisson(3, 90))
        
        fig.add_trace(
            go.Scatter(
                x=enrollment_dates,
                y=cumulative_enrollments,
                mode='lines',
                fill='tozeroy',
                name='Enrollments',
                line=dict(color=LearningAnalyticsCharts.COLORS['primary'])
            ),
            row=1, col=1
        )
        
        # Course Ratings Distribution
        ratings = np.random.normal(4.2, 0.5, 200)
        ratings = np.clip(ratings, 1, 5)
        
        fig.add_trace(
            go.Histogram(
                x=ratings,
                nbinsx=10,
                marker_color=LearningAnalyticsCharts.COLORS['secondary']
            ),
            row=1, col=2
        )
        
        # Student Progress Distribution
        progress_data = teacher_data.get('progress_distribution', [])
        courses = [d['course'] for d in progress_data]
        
        for course in set(courses):
            course_progress = [d['progress'] for d in progress_data if d['course'] == course]
            fig.add_trace(
                go.Box(
                    y=course_progress,
                    name=course,
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8
                ),
                row=2, col=1
            )
        
        # Quiz Success Rate
        quiz_names = teacher_data.get('quiz_names', ['Quiz 1', 'Quiz 2', 'Quiz 3', 'Quiz 4'])
        success_rates = teacher_data.get('quiz_success_rates', [75, 82, 68, 90])
        
        fig.add_trace(
            go.Bar(
                x=quiz_names,
                y=success_rates,
                text=[f'{rate}%' for rate in success_rates],
                textposition='auto',
                marker_color=LearningAnalyticsCharts.COLORS['success']
            ),
            row=2, col=2
        )
        
        # Forum Activity Over Time
        forum_dates = pd.date_range(end=timezone.now(), periods=30, freq='D')
        posts_count = np.random.poisson(10, 30)
        replies_count = np.random.poisson(25, 30)
        
        fig.add_trace(
            go.Scatter(
                x=forum_dates,
                y=posts_count,
                mode='lines+markers',
                name='Posts',
                line=dict(color=LearningAnalyticsCharts.COLORS['primary'])
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=forum_dates,
                y=replies_count,
                mode='lines+markers',
                name='Replies',
                line=dict(color=LearningAnalyticsCharts.COLORS['secondary'])
            ),
            row=3, col=1
        )
        
        # Top Performing Students Table
        top_students = teacher_data.get('top_students', [])
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Rank', 'Student', 'Avg Score', 'Courses'],
                    fill_color=LearningAnalyticsCharts.COLORS['primary'],
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[
                        [i+1 for i in range(len(top_students))],
                        [s['name'] for s in top_students],
                        [f"{s['avg_score']:.1f}%" for s in top_students],
                        [s['courses'] for s in top_students]
                    ],
                    fill_color='lavender',
                    font=dict(size=11)
                )
            ),
            row=3, col=2
        )
        
        fig.update_layout(
            height=1200,
            showlegend=True,
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()

    @staticmethod
    def create_course_analytics_report(course_data: Dict) -> str:
        """Create comprehensive course analytics report"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Enrollment Growth', 'Module Completion Rates', 'Average Quiz Scores',
                'Time Spent Distribution', 'Student Satisfaction', 'Completion Timeline'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'bar'}, {'type': 'scatter'}],
                [{'type': 'violin'}, {'type': 'indicator'}, {'type': 'gantt'}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Enrollment Growth
        dates = pd.date_range(
            start=course_data.get('start_date', timezone.now() - timedelta(days=90)),
            end=timezone.now(),
            freq='W'
        )
        enrollments = np.cumsum(np.random.poisson(5, len(dates)))
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=enrollments,
                mode='lines+markers',
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)',
                line=dict(color=LearningAnalyticsCharts.COLORS['primary'], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Module Completion Rates
        modules = course_data.get('modules', [])
        completion_rates = [m['completion_rate'] for m in modules]
        module_names = [m['name'] for m in modules]
        
        fig.add_trace(
            go.Bar(
                x=module_names,
                y=completion_rates,
                text=[f'{rate:.1f}%' for rate in completion_rates],
                textposition='auto',
                marker=dict(
                    color=completion_rates,
                    colorscale='Viridis',
                    showscale=True
                )
            ),
            row=1, col=2
        )
        
        # Average Quiz Scores
        quiz_dates = course_data.get('quiz_dates', [])
        avg_scores = course_data.get('avg_quiz_scores', [])
        
        fig.add_trace(
            go.Scatter(
                x=quiz_dates,
                y=avg_scores,
                mode='lines+markers',
                name='Avg Score',
                line=dict(color=LearningAnalyticsCharts.COLORS['success'], width=2)
            ),
            row=1, col=3
        )
        
        # Time Spent Distribution
        time_spent_data = course_data.get('time_spent_distribution', 
                                         np.random.lognormal(3.5, 0.8, 200))
        
        fig.add_trace(
            go.Violin(
                y=time_spent_data,
                box_visible=True,
                line_color=LearningAnalyticsCharts.COLORS['secondary'],
                meanline_visible=True,
                fillcolor='rgba(118, 75, 162, 0.5)',
                opacity=0.6,
                name='Time (hours)'
            ),
            row=2, col=1
        )
        
        # Student Satisfaction Score
        satisfaction_score = course_data.get('satisfaction_score', 4.5)
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=satisfaction_score,
                gauge={
                    'axis': {'range': [1, 5]},
                    'bar': {'color': LearningAnalyticsCharts.COLORS['success']},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [1, 2], 'color': LearningAnalyticsCharts.COLORS['danger']},
                        {'range': [2, 3], 'color': LearningAnalyticsCharts.COLORS['warning']},
                        {'range': [3, 4], 'color': LearningAnalyticsCharts.COLORS['info']},
                        {'range': [4, 5], 'color': LearningAnalyticsCharts.COLORS['success']}
                    ],
                },
                number={'suffix': " / 5"},
                title={'text': "Satisfaction Score"}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()

    @staticmethod
    def create_platform_overview_dashboard(platform_data: Dict) -> str:
        """Create platform-wide analytics dashboard for managers"""
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=(
                'Total Users Growth', 'Course Distribution by Category', 'Revenue Trend',
                'User Activity Map', 'Course Completion Rates', 'Platform Health Metrics',
                'Popular Courses', 'User Demographics', 'Support Ticket Status'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'pie'}, {'type': 'scatter'}],
                [{'type': 'geo'}, {'type': 'bar'}, {'type': 'indicator'}],
                [{'type': 'bar'}, {'type': 'sunburst'}, {'type': 'pie'}]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.08
        )
        
        # Total Users Growth
        user_dates = pd.date_range(end=timezone.now(), periods=365, freq='D')
        total_users = np.cumsum(np.random.poisson(10, 365)) + 1000
        
        fig.add_trace(
            go.Scatter(
                x=user_dates,
                y=total_users,
                mode='lines',
                fill='tozeroy',
                name='Total Users',
                line=dict(color=LearningAnalyticsCharts.COLORS['primary'], width=2)
            ),
            row=1, col=1
        )
        
        # Course Distribution by Category
        categories = platform_data.get('categories', 
                                     ['Programming', 'Data Science', 'Business', 'Design', 'Marketing'])
        course_counts = platform_data.get('course_counts', [45, 32, 28, 20, 15])
        
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=course_counts,
                hole=0.4,
                marker_colors=[
                    LearningAnalyticsCharts.COLORS['primary'],
                    LearningAnalyticsCharts.COLORS['secondary'],
                    LearningAnalyticsCharts.COLORS['success'],
                    LearningAnalyticsCharts.COLORS['warning'],
                    LearningAnalyticsCharts.COLORS['info']
                ]
            ),
            row=1, col=2
        )
        
        # Revenue Trend (if applicable)
        revenue_dates = pd.date_range(end=timezone.now(), periods=12, freq='M')
        revenue = np.cumsum(np.random.normal(5000, 1000, 12))
        
        fig.add_trace(
            go.Scatter(
                x=revenue_dates,
                y=revenue,
                mode='lines+markers',
                name='Revenue',
                line=dict(color=LearningAnalyticsCharts.COLORS['success'], width=3),
                fill='tozeroy',
                fillcolor='rgba(72, 187, 120, 0.2)'
            ),
            row=1, col=3
        )
        
        # Course Completion Rates by Level
        levels = ['Beginner', 'Intermediate', 'Advanced']
        completion_rates = platform_data.get('completion_by_level', [65, 55, 70])
        
        fig.add_trace(
            go.Bar(
                x=levels,
                y=completion_rates,
                text=[f'{rate}%' for rate in completion_rates],
                textposition='auto',
                marker_color=[
                    LearningAnalyticsCharts.COLORS['info'],
                    LearningAnalyticsCharts.COLORS['warning'],
                    LearningAnalyticsCharts.COLORS['danger']
                ]
            ),
            row=2, col=2
        )
        
        # Platform Health Metrics
        health_score = platform_data.get('health_score', 92)
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=health_score,
                delta={'reference': 90},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': LearningAnalyticsCharts.COLORS['success']},
                    'steps': [
                        {'range': [0, 50], 'color': LearningAnalyticsCharts.COLORS['danger']},
                        {'range': [50, 80], 'color': LearningAnalyticsCharts.COLORS['warning']},
                        {'range': [80, 100], 'color': LearningAnalyticsCharts.COLORS['success']}
                    ],
                },
                title={'text': "System Health %"}
            ),
            row=2, col=3
        )
        
        # Popular Courses
        popular_courses = platform_data.get('popular_courses', [])[:5]
        
        fig.add_trace(
            go.Bar(
                y=[c['title'] for c in popular_courses],
                x=[c['enrollments'] for c in popular_courses],
                orientation='h',
                marker_color=LearningAnalyticsCharts.COLORS['primary'],
                text=[f"{c['enrollments']} students" for c in popular_courses],
                textposition='auto'
            ),
            row=3, col=1
        )
        
        # Support Ticket Status
        ticket_status = platform_data.get('ticket_status', {
            'Open': 15,
            'In Progress': 25,
            'Resolved': 145,
            'Closed': 89
        })
        
        fig.add_trace(
            go.Pie(
                labels=list(ticket_status.keys()),
                values=list(ticket_status.values()),
                marker_colors=[
                    LearningAnalyticsCharts.COLORS['danger'],
                    LearningAnalyticsCharts.COLORS['warning'],
                    LearningAnalyticsCharts.COLORS['success'],
                    LearningAnalyticsCharts.COLORS['light']
                ]
            ),
            row=3, col=3
        )
        
        fig.update_layout(
            height=1200,
            showlegend=False,
            **LearningAnalyticsCharts.CHART_TEMPLATE['layout']
        )
        
        return fig.to_json()
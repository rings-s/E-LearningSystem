// front/src/lib/services/analytics.service.js - Enhanced integration
import { coreApi } from '../apis/core.js';
import { coursesApi } from '../apis/courses.js';

class AnalyticsService {
	constructor() {
		this.cache = new Map();
		this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
	}

	// Enhanced Student Analytics - Direct backend integration
	async getStudentAnalytics() {
		const cacheKey = 'student_analytics';
		const cached = this.getFromCache(cacheKey);
		if (cached) return cached;

		try {
			// Use the backend analytics endpoint directly
			const response = await coreApi.getStudentAnalytics();
			
			// Process and enhance the backend data
			const analytics = {
				summary: response.summary || {},
				performance: response.performance || {},
				charts: response.charts || {},
				study_time: response.study_time || {},
				subject_performance: response.subject_performance || [],
				insights: this.generateInsights(response, 'student')
			};

			this.setCache(cacheKey, analytics);
			return analytics;
		} catch (error) {
			console.error('Failed to get student analytics:', error);
			console.error('Analytics error details:', {
				message: error.message,
				status: error.status,
				url: error.config?.url
			});
			
			// Only use fallback for network issues, not data errors
			if (error.status >= 500 || error.status === 0 || !error.status) {
				console.warn('Using fallback student analytics due to server/network error');
				return this.getFallbackStudentAnalytics();
			}
			
			// Re-throw for client errors to be handled by the dashboard
			throw error;
		}
	}

	// Enhanced Teacher Analytics
	async getTeacherAnalytics() {
		const cacheKey = 'teacher_analytics';
		const cached = this.getFromCache(cacheKey);
		if (cached) return cached;

		try {
			const response = await coreApi.getTeacherAnalytics();
			
			const analytics = {
				summary: response.summary || {},
				course_performance: response.course_performance || [],
				student_activity: response.student_activity || {},
				charts: response.charts || {},
				engagement_metrics: this.calculateEngagementMetrics(response),
				insights: this.generateInsights(response, 'teacher')
			};

			this.setCache(cacheKey, analytics);
			return analytics;
		} catch (error) {
			console.error('Failed to get teacher analytics:', error);
			console.error('Analytics error details:', {
				message: error.message,
				status: error.status,
				url: error.config?.url
			});
			
			// Only use fallback for network issues, not data errors
			if (error.status >= 500 || error.status === 0 || !error.status) {
				console.warn('Using fallback teacher analytics due to server/network error');
				return this.getFallbackTeacherAnalytics();
			}
			
			// Re-throw for client errors to be handled by the dashboard
			throw error;
		}
	}

	// Platform Analytics for Managers
	async getPlatformAnalytics() {
		const cacheKey = 'platform_analytics';
		const cached = this.getFromCache(cacheKey);
		if (cached) return cached;

		try {
			const response = await coreApi.getPlatformAnalytics();
			
			const analytics = {
				platform_health: response.platform_health || {},
				user_growth: response.growth_metrics || [],
				category_insights: response.category_insights || [],
				charts: response.charts || {},
				trends: this.analyzeTrends(response),
				insights: this.generateInsights(response, 'platform')
			};

			this.setCache(cacheKey, analytics);
			return analytics;
		} catch (error) {
			console.error('Failed to get platform analytics:', error);
			console.error('Analytics error details:', {
				message: error.message,
				status: error.status,
				url: error.config?.url
			});
			
			// Only use fallback for network issues, not data errors
			if (error.status >= 500 || error.status === 0 || !error.status) {
				console.warn('Using fallback platform analytics due to server/network error');
				return this.getFallbackPlatformAnalytics();
			}
			
			// Re-throw for client errors to be handled by the dashboard
			throw error;
		}
	}

	// Enhanced chart generation for student data
	generateStudentCharts(data) {
		return {
			progressChart: {
				type: 'bar',
				title: 'Course Progress',
				data: {
					labels: (data.courses || []).map(c => this.truncateText(c.course_title, 15)),
					datasets: [{
						label: 'Progress %',
						data: (data.courses || []).map(c => c.progress),
						backgroundColor: (data.courses || []).map(c => 
							c.progress >= 80 ? '#10b981' : 
							c.progress >= 50 ? '#f59e0b' : '#3b82f6'
						),
						borderRadius: 6
					}]
				}
			},
			
			studyTimeChart: {
				type: 'line',
				title: 'Daily Study Time',
				data: {
					labels: (data.study_time?.daily_breakdown || []).map(d => 
						new Date(d.date).toLocaleDateString('en', { month: 'short', day: 'numeric' })
					),
					datasets: [{
						label: 'Minutes',
						data: (data.study_time?.daily_breakdown || []).map(d => d.minutes),
						borderColor: '#6366f1',
						backgroundColor: 'rgba(99, 102, 241, 0.1)',
						fill: true,
						tension: 0.4
					}]
				}
			}
		};
	}

	// Enhanced chart generation for teacher data
	generateTeacherCharts(data) {
		return {
			courseEngagement: {
				type: 'doughnut',
				title: 'Student Progress Distribution',
				data: {
					labels: ['Not Started', 'In Progress', 'Completed'],
					datasets: [{
						data: [
							data.student_activity?.progress_distribution?.not_started || 0,
							data.student_activity?.progress_distribution?.in_progress || 0,
							data.student_activity?.progress_distribution?.completed || 0
						],
						backgroundColor: ['#ef4444', '#f59e0b', '#10b981']
					}]
				}
			}
		};
	}

	// Generate actionable insights
	generateInsights(data, userType) {
		const insights = [];

		if (userType === 'student') {
			// Student-specific insights
			if (data.summary?.learning_streak >= 7) {
				insights.push({
					type: 'success',
					title: 'Great Learning Streak!',
					description: `You've maintained a ${data.summary.learning_streak}-day learning streak. Keep it up!`
				});
			}

			if (data.study_time?.weekly_average < 5) {
				insights.push({
					type: 'suggestion',
					title: 'Increase Study Time',
					description: 'Try to study at least 5 hours per week for better progress.'
				});
			}
		} else if (userType === 'teacher') {
			// Teacher-specific insights
			const engagementRate = this.calculateEngagementRate(data);
			
			if (engagementRate < 50) {
				insights.push({
					type: 'warning',
					title: 'Low Student Engagement',
					description: 'Consider adding more interactive content to boost engagement.'
				});
			}

			if (data.course_performance?.some(course => course.avg_progress < 30)) {
				insights.push({
					type: 'suggestion',
					title: 'Course Progress Review',
					description: 'Some courses have low completion rates. Review content difficulty.'
				});
			}
		}

		return insights;
	}

	// Helper methods
	calculateEngagementMetrics(data) {
		const total = data.summary?.total_students || 0;
		const active = data.summary?.active_students_7d || 0;
		const engagementRate = total > 0 ? Math.round((active / total) * 100) : 0;
		
		return {
			engagement_rate: engagementRate,
			total_students: total,
			active_students: active,
			activity_score: this.calculateActivityScore(data)
		};
	}

	calculateEngagementRate(data) {
		const total = data.summary?.total_students || 0;
		const active = data.summary?.active_students_7d || 0;
		if (total === 0) return 0;
		const rate = (active / total) * 100;
		return Math.round(rate) || 0;
	}

	calculateActivityScore(data) {
		// Simple activity score based on various metrics
		const base = 50;
		const engagementBonus = this.calculateEngagementRate(data);
		const ratingBonus = (data.summary?.avg_course_rating || 0) * 10;
		return Math.min(100, Math.round(base + engagementBonus * 0.3 + ratingBonus * 0.2));
	}

	analyzeTrends(data) {
		// Analyze trends in platform data
		const userGrowth = data.growth_metrics || [];
		const categoryInsights = data.category_insights || [];
		
		return {
			user_growth_trend: userGrowth.length > 1 ? 'growing' : 'stable',
			popular_categories: categoryInsights.slice(0, 3).map(cat => cat.category || cat.name),
			platform_health: data.platform_health?.user_engagement_rate > 70 ? 'healthy' : 'needs_attention'
		};
	}

	truncateText(text, maxLength) {
		return text && text.length > maxLength ? text.substring(0, maxLength) + '...' : text || '';
	}

	// Cache management
	getFromCache(key) {
		const cached = this.cache.get(key);
		if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
			return cached.data;
		}
		this.cache.delete(key);
		return null;
	}

	setCache(key, data) {
		this.cache.set(key, {
			data,
			timestamp: Date.now()
		});
	}

	// Fallback data methods remain the same...
	getFallbackStudentAnalytics() {
		return {
			summary: { total_courses: 0, completed_courses: 0, study_hours_30d: 0, learning_streak: 0 },
			performance: { total_quizzes: 0, avg_quiz_score: 0, quiz_pass_rate: 0 },
			charts: { 
				course_progress: { 
					type: 'bar',
					title: 'Course Progress',
					data: { labels: [], datasets: [] } 
				},
				study_time_trend: {
					type: 'line',
					title: 'Daily Study Time',
					data: { labels: [], datasets: [] }
				}
			},
			study_time: { daily_breakdown: [], weekly_average: 0 }
		};
	}

	getFallbackTeacherAnalytics() {
		return {
			summary: { 
				total_courses: 0, 
				published_courses: 0,
				total_students: 0, 
				active_students_7d: 0,
				avg_course_rating: 0 
			},
			course_performance: [],
			student_activity: { 
				total_students: 0,
				progress_distribution: { not_started: 0, in_progress: 0, completed: 0 } 
			},
			charts: { 
				student_progress: { 
					type: 'doughnut',
					title: 'Student Progress Distribution',
					data: { 
						labels: ['Not Started', 'In Progress', 'Completed'], 
						datasets: [{
							data: [0, 0, 0],
							backgroundColor: ['#ef4444', '#f59e0b', '#10b981']
						}]
					} 
				}
			}
		};
	}

	getFallbackPlatformAnalytics() {
		return {
			platform_health: { total_users: 0, active_users_30d: 0, total_courses: 0 },
			user_growth: [],
			category_insights: [],
			charts: {}
		};
	}
}

export const analyticsService = new AnalyticsService();
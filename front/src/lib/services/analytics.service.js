// front/src/lib/services/analytics.service.js
import { coreApi } from '../apis/core.js';
import { coursesApi } from '../apis/courses.js';

class AnalyticsService {
	constructor() {
		this.cache = new Map();
		this.cacheTimeout = 5 * 60 * 1000; // 5 minutes for real-time feel
	}

	// Student Analytics - Integrated with Backend
	async getStudentAnalytics() {
		const cacheKey = 'student_analytics';
		const cached = this.getFromCache(cacheKey);
		if (cached) return cached;

		try {
			// Use the backend analytics endpoint for comprehensive data
			const response = await coreApi.getStudentAnalytics();
			
			// Process the rich analytics data from backend
			const analytics = {
				summary: response.summary || {},
				performance: response.performance || {},
				charts: this.generateStudentCharts(response),
				subjectPerformance: response.subject_performance || [],
				learningStreak: response.summary?.learning_streak || 0,
				studyTime: response.study_time || {},
				goals: this.calculateLearningGoals(response.summary)
			};

			this.setCache(cacheKey, analytics);
			return analytics;
		} catch (error) {
			console.error('Failed to get student analytics:', error);
			return this.getFallbackStudentAnalytics();
		}
	}

	// Teacher Analytics - Enhanced with Backend Data
	async getTeacherAnalytics() {
		const cacheKey = 'teacher_analytics';
		const cached = this.getFromCache(cacheKey);
		if (cached) return cached;

		try {
			const response = await coreApi.getTeacherAnalytics();
			
			const analytics = {
				summary: response.summary || {},
				coursePerformance: response.course_performance || [],
				studentActivity: response.student_activity || {},
				charts: this.generateTeacherCharts(response),
				engagementMetrics: this.calculateEngagementMetrics(response),
				insights: this.generateTeacherInsights(response)
			};

			this.setCache(cacheKey, analytics);
			return analytics;
		} catch (error) {
			console.error('Failed to get teacher analytics:', error);
			return this.getFallbackTeacherAnalytics();
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
				platformHealth: response.platform_health || {},
				userGrowth: response.growth_metrics || [],
				categoryInsights: response.category_insights || [],
				charts: this.generatePlatformCharts(response),
				trends: this.analyzeTrends(response),
				systemHealth: this.calculateSystemHealth(response.platform_health)
			};

			this.setCache(cacheKey, analytics);
			return analytics;
		} catch (error) {
			console.error('Failed to get platform analytics:', error);
			return this.getFallbackPlatformAnalytics();
		}
	}

	// Generate Student Charts from Backend Data
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
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: { legend: { display: false } },
					scales: {
						y: { beginAtZero: true, max: 100 }
					}
				}
			},
			
			studyTimeChart: {
				type: 'line',
				title: 'Daily Study Time (Last 30 Days)',
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
			},

			performanceRadar: {
				type: 'radar',
				title: 'Performance Overview',
				data: {
					labels: (data.subject_performance || []).map(s => s.subject),
					datasets: [{
						label: 'Average Score',
						data: (data.subject_performance || []).map(s => s.avg_score),
						borderColor: '#8b5cf6',
						backgroundColor: 'rgba(139, 92, 246, 0.2)',
						pointBackgroundColor: '#8b5cf6'
					}]
				}
			}
		};
	}

	// Generate Teacher Charts
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
			},

			coursePerformance: {
				type: 'scatter',
				title: 'Course Performance Overview',
				data: {
					datasets: [{
						label: 'Courses',
						data: (data.course_performance || []).map(c => ({
							x: c.total_students,
							y: c.avg_progress,
							label: c.title
						})),
						backgroundColor: '#3b82f6'
					}]
				}
			}
		};
	}

	// Calculate Engagement Metrics
	calculateEngagementMetrics(data) {
		const totalStudents = data.summary?.total_students || 0;
		const activeStudents = data.summary?.active_students_7d || 0;
		
		return {
			activeStudentRate: totalStudents > 0 ? Math.round((activeStudents / totalStudents) * 100) : 0,
			avgCourseRating: data.summary?.avg_course_rating || 0,
			totalCourses: data.summary?.total_courses || 0,
			publishedCourses: data.summary?.published_courses || 0
		};
	}

	// Learning Goals Calculation
	calculateLearningGoals(summary) {
		const weeklyTarget = 10; // 10 hours per week target
		const currentWeekHours = summary?.study_hours_30d ? summary.study_hours_30d / 4 : 0;
		
		return {
			weekly: {
				target: weeklyTarget,
				current: Math.round(currentWeekHours * 10) / 10,
				percentage: Math.min(100, Math.round((currentWeekHours / weeklyTarget) * 100))
			},
			streak: {
				current: summary?.learning_streak || 0,
				target: 7,
				percentage: Math.min(100, Math.round(((summary?.learning_streak || 0) / 7) * 100))
			},
			completion: {
				current: summary?.completed_courses || 0,
				total: summary?.total_courses || 0,
				percentage: summary?.total_courses > 0 ? 
					Math.round((summary.completed_courses / summary.total_courses) * 100) : 0
			}
		};
	}

	// Real-time Progress Tracking
	async trackLessonProgress(lessonId, progressData) {
		try {
			// Send progress update to backend
			await coursesApi.updateLessonProgress(lessonId, progressData);
			
			// Update local analytics cache
			this.invalidateCache('student_analytics');
			
			return { success: true };
		} catch (error) {
			console.error('Failed to track lesson progress:', error);
			return { success: false, error: error.message };
		}
	}

	// Study Session Tracking
	startStudySession(courseId, lessonId) {
		const session = {
			courseId,
			lessonId,
			startTime: Date.now(),
			lastActiveTime: Date.now()
		};
		
		if (typeof window !== 'undefined') {
			localStorage.setItem('current_study_session', JSON.stringify(session));
		}
		
		return session;
	}

	updateStudySession(progressData) {
		if (typeof window === 'undefined') return;
		
		const session = this.getCurrentStudySession();
		if (session) {
			session.lastActiveTime = Date.now();
			session.progress = progressData;
			localStorage.setItem('current_study_session', JSON.stringify(session));
		}
	}

	endStudySession() {
		if (typeof window === 'undefined') return null;
		
		const session = this.getCurrentStudySession();
		if (session) {
			const duration = Date.now() - session.startTime;
			localStorage.removeItem('current_study_session');
			
			// Send session data to backend for analytics
			this.trackStudySession({
				...session,
				duration,
				endTime: Date.now()
			});
			
			return { ...session, duration };
		}
		return null;
	}

	getCurrentStudySession() {
		if (typeof window === 'undefined') return null;
		
		try {
			const session = localStorage.getItem('current_study_session');
			return session ? JSON.parse(session) : null;
		} catch (error) {
			console.error('Failed to get study session:', error);
			return null;
		}
	}

	async trackStudySession(sessionData) {
		try {
			await coreApi.trackStudySession(sessionData);
		} catch (error) {
			console.error('Failed to track study session:', error);
		}
	}

	// Fallback Analytics for Offline Mode
	getFallbackStudentAnalytics() {
		return {
			summary: {
				total_courses: 0,
				completed_courses: 0,
				in_progress_courses: 0,
				average_progress: 0,
				study_hours_30d: 0,
				learning_streak: 0
			},
			performance: {
				total_quizzes: 0,
				avg_quiz_score: 0,
				quiz_pass_rate: 0
			},
			charts: {
				progressChart: { data: { labels: [], datasets: [] } },
				studyTimeChart: { data: { labels: [], datasets: [] } },
				performanceRadar: { data: { labels: [], datasets: [] } }
			},
			subjectPerformance: [],
			studyTime: { daily_breakdown: [], weekly_average: 0 }
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
			coursePerformance: [],
			studentActivity: {
				total_students: 0,
				active_students_7d: 0,
				progress_distribution: { not_started: 0, in_progress: 0, completed: 0 }
			},
			charts: {
				courseEngagement: { data: { labels: [], datasets: [] } },
				coursePerformance: { data: { datasets: [] } }
			}
		};
	}

	getFallbackPlatformAnalytics() {
		return {
			platformHealth: {
				total_users: 0,
				active_users_30d: 0,
				user_engagement_rate: 0,
				total_courses: 0,
				total_enrollments: 0
			},
			userGrowth: [],
			categoryInsights: [],
			charts: {},
			trends: {}
		};
	}

	// Utility Methods
	truncateText(text, maxLength) {
		return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
	}

	// Cache Management
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

	invalidateCache(pattern = null) {
		if (!pattern) {
			this.cache.clear();
		} else {
			for (const key of this.cache.keys()) {
				if (key.includes(pattern)) {
					this.cache.delete(key);
				}
			}
		}
	}
}

export const analyticsService = new AnalyticsService();
// front/src/lib/services/analytics.service.js
import { coreApi } from '../apis/core.js';
import { coursesApi } from '../apis/courses.js';

class AnalyticsService {
	constructor() {
		this.cache = new Map();
		this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
	}

	// Dashboard Analytics
	async getDashboardAnalytics(role) {
		const cacheKey = `dashboard_${role}`;
		const cached = this.getFromCache(cacheKey);
		if (cached) return cached;

		try {
			const analytics = await coreApi.getDashboard();

			// Process and enhance analytics data
			const enhanced = this.enhanceDashboardData(analytics, role);

			this.setCache(cacheKey, enhanced);
			return enhanced;
		} catch (error) {
			console.error('Failed to get dashboard analytics:', error);
			throw error;
		}
	}

	enhanceDashboardData(data, role) {
		if (role === 'student') {
			return this.enhanceStudentDashboard(data);
		} else if (role === 'teacher') {
			return this.enhanceTeacherDashboard(data);
		} else if (role === 'manager' || role === 'admin') {
			return this.enhanceManagerDashboard(data);
		}
		return data;
	}

	enhanceStudentDashboard(data) {
		return {
			...data,
			charts: {
				progressChart: this.generateProgressChartData(data),
				activityChart: this.generateActivityChartData(data.recent_activities),
				performanceChart: this.generatePerformanceChartData(data),
				timeChart: this.generateTimeSpentChartData(data)
			},
			insights: this.generateStudentInsights(data),
			goals: this.calculateLearningGoals(data)
		};
	}

	enhanceTeacherDashboard(data) {
		return {
			...data,
			charts: {
				enrollmentChart: this.generateEnrollmentChartData(data),
				completionChart: this.generateCompletionRateChartData(data),
				engagementChart: this.generateEngagementChartData(data),
				ratingsChart: this.generateRatingsChartData(data)
			},
			insights: this.generateTeacherInsights(data),
			topPerformers: this.identifyTopPerformers(data)
		};
	}

	enhanceManagerDashboard(data) {
		return {
			...data,
			charts: {
				userGrowthChart: this.generateUserGrowthChartData(data),
				revenueChart: this.generateRevenueChartData(data),
				coursePopularityChart: this.generateCoursePopularityChartData(data),
				systemHealthChart: this.generateSystemHealthChartData(data)
			},
			insights: this.generateManagerInsights(data),
			trends: this.analyzeTrends(data)
		};
	}

	// Chart Data Generators
	generateProgressChartData(data) {
		const courses = data.active_courses || [];

		return {
			type: 'bar',
			data: {
				labels: courses.map((c) => this.truncateLabel(c.title, 20)),
				datasets: [
					{
						label: 'Progress %',
						data: courses.map((c) => c.progress || 0),
						backgroundColor: courses.map((c) =>
							c.progress >= 80 ? '#10b981' : c.progress >= 50 ? '#f59e0b' : '#3b82f6'
						),
						borderRadius: 6
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { display: false },
					tooltip: {
						callbacks: {
							label: (context) => `${context.parsed.y}% completed`
						}
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						max: 100,
						ticks: {
							callback: (value) => `${value}%`
						}
					}
				}
			}
		};
	}

	generateActivityChartData(activities) {
		const last7Days = this.getLast7Days();
		const activityCounts = this.countActivitiesByDay(activities, last7Days);

		return {
			type: 'line',
			data: {
				labels: last7Days.map((d) => this.formatDateLabel(d)),
				datasets: [
					{
						label: 'Activities',
						data: activityCounts,
						borderColor: '#6366f1',
						backgroundColor: 'rgba(99, 102, 241, 0.1)',
						tension: 0.4,
						fill: true
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { display: false }
				},
				scales: {
					y: {
						beginAtZero: true,
						ticks: {
							stepSize: 1
						}
					}
				}
			}
		};
	}

	generatePerformanceChartData(data) {
		const quizScores = data.quiz_scores || [];

		return {
			type: 'radar',
			data: {
				labels: ['Quizzes', 'Assignments', 'Participation', 'Completion', 'Consistency'],
				datasets: [
					{
						label: 'Performance',
						data: [
							data.average_score || 0,
							data.assignment_score || 0,
							data.participation_score || 0,
							data.completion_rate || 0,
							data.consistency_score || 0
						],
						borderColor: '#8b5cf6',
						backgroundColor: 'rgba(139, 92, 246, 0.2)',
						pointBackgroundColor: '#8b5cf6',
						pointBorderColor: '#fff',
						pointHoverBackgroundColor: '#fff',
						pointHoverBorderColor: '#8b5cf6'
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					r: {
						beginAtZero: true,
						max: 100,
						ticks: {
							stepSize: 20
						}
					}
				}
			}
		};
	}

	generateTimeSpentChartData(data) {
		const timeByCategory = data.time_by_category || {};

		return {
			type: 'doughnut',
			data: {
				labels: Object.keys(timeByCategory),
				datasets: [
					{
						data: Object.values(timeByCategory),
						backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
						borderWidth: 0
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						position: 'bottom',
						labels: {
							padding: 15,
							usePointStyle: true
						}
					},
					tooltip: {
						callbacks: {
							label: (context) => {
								const hours = context.parsed;
								return `${context.label}: ${hours}h`;
							}
						}
					}
				}
			}
		};
	}

	generateEnrollmentChartData(data) {
		const enrollmentsByMonth = data.enrollments_by_month || {};
		const months = Object.keys(enrollmentsByMonth).slice(-6);

		return {
			type: 'line',
			data: {
				labels: months,
				datasets: [
					{
						label: 'New Enrollments',
						data: months.map((m) => enrollmentsByMonth[m] || 0),
						borderColor: '#10b981',
						backgroundColor: 'rgba(16, 185, 129, 0.1)',
						tension: 0.4,
						fill: true
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { display: false }
				},
				scales: {
					y: {
						beginAtZero: true
					}
				}
			}
		};
	}

	generateCompletionRateChartData(data) {
		const courses = data.course_analytics || [];

		return {
			type: 'bar',
			data: {
				labels: courses.map((c) => this.truncateLabel(c.title, 20)),
				datasets: [
					{
						label: 'Completion Rate',
						data: courses.map((c) => c.completion_rate || 0),
						backgroundColor: '#6366f1',
						borderRadius: 6
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { display: false },
					tooltip: {
						callbacks: {
							label: (context) => `${context.parsed.y}% completion rate`
						}
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						max: 100,
						ticks: {
							callback: (value) => `${value}%`
						}
					}
				}
			}
		};
	}

	generateEngagementChartData(data) {
		const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
		const engagementData = data.engagement_by_day || {};

		return {
			type: 'heatmap',
			data: {
				labels: {
					x: weekDays,
					y: ['Week 1', 'Week 2', 'Week 3', 'Week 4']
				},
				datasets: [
					{
						label: 'Student Engagement',
						data: this.generateHeatmapData(engagementData),
						backgroundColor: (context) => {
							const value = context.dataset.data[context.dataIndex].v;
							const alpha = value / 100;
							return `rgba(99, 102, 241, ${alpha})`;
						},
						borderWidth: 1,
						borderColor: '#e5e7eb'
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					tooltip: {
						callbacks: {
							label: (context) => `${context.raw.v}% engagement`
						}
					}
				},
				scales: {
					x: { type: 'category' },
					y: { type: 'category' }
				}
			}
		};
	}

	generateRatingsChartData(data) {
		const ratingDistribution = data.rating_distribution || {};

		return {
			type: 'bar',
			data: {
				labels: ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'],
				datasets: [
					{
						label: 'Number of Reviews',
						data: [
							ratingDistribution['5'] || 0,
							ratingDistribution['4'] || 0,
							ratingDistribution['3'] || 0,
							ratingDistribution['2'] || 0,
							ratingDistribution['1'] || 0
						],
						backgroundColor: ['#10b981', '#6366f1', '#f59e0b', '#fb923c', '#ef4444'],
						borderRadius: 6
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				indexAxis: 'y',
				plugins: {
					legend: { display: false }
				},
				scales: {
					x: {
						beginAtZero: true,
						ticks: {
							stepSize: 1
						}
					}
				}
			}
		};
	}

	// Insights Generators
	generateStudentInsights(data) {
		const insights = [];

		// Learning pace insight
		if (data.average_completion_time) {
			const pace = data.average_completion_time > 30 ? 'steady' : 'fast';
			insights.push({
				type: 'pace',
				title: 'Learning Pace',
				message: `You're learning at a ${pace} pace. Keep it up!`,
				icon: '🏃‍♂️'
			});
		}

		// Streak insight
		if (data.current_streak > 0) {
			insights.push({
				type: 'streak',
				title: 'Learning Streak',
				message: `${data.current_streak} day streak! Don't break it!`,
				icon: '🔥'
			});
		}

		// Performance insight
		if (data.average_score > 80) {
			insights.push({
				type: 'performance',
				title: 'Top Performer',
				message: 'Your quiz scores are excellent!',
				icon: '⭐'
			});
		}

		return insights;
	}

	generateTeacherInsights(data) {
		const insights = [];

		// Enrollment trend
		const enrollmentTrend = this.calculateTrend(data.enrollments_by_month);
		insights.push({
			type: 'enrollment',
			title: 'Enrollment Trend',
			message: `Enrollments are ${enrollmentTrend > 0 ? 'increasing' : 'decreasing'} by ${Math.abs(enrollmentTrend)}%`,
			icon: enrollmentTrend > 0 ? '📈' : '📉'
		});

		// Student engagement
		if (data.average_engagement < 50) {
			insights.push({
				type: 'engagement',
				title: 'Engagement Alert',
				message: 'Student engagement is low. Consider adding interactive content.',
				icon: '⚠️'
			});
		}

		// Course rating
		if (data.average_rating > 4.5) {
			insights.push({
				type: 'rating',
				title: 'Highly Rated',
				message: 'Your courses are highly rated by students!',
				icon: '⭐'
			});
		}

		return insights;
	}

	generateManagerInsights(data) {
		const insights = [];

		// User growth
		const userGrowth = this.calculateGrowthRate(data.user_growth);
		insights.push({
			type: 'growth',
			title: 'User Growth',
			message: `Platform growing at ${userGrowth}% monthly`,
			icon: '📊'
		});

		// Revenue insights
		if (data.revenue_trend > 0) {
			insights.push({
				type: 'revenue',
				title: 'Revenue Trend',
				message: `Revenue up ${data.revenue_trend}% this month`,
				icon: '💰'
			});
		}

		// System health
		const healthScore = this.calculateSystemHealth(data.system_health);
		if (healthScore < 80) {
			insights.push({
				type: 'system',
				title: 'System Alert',
				message: 'System performance needs attention',
				icon: '🔧'
			});
		}

		return insights;
	}

	// Helper Methods
	truncateLabel(label, maxLength) {
		return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
	}

	formatDateLabel(date) {
		const d = new Date(date);
		return d.toLocaleDateString('en', { month: 'short', day: 'numeric' });
	}

	getLast7Days() {
		const days = [];
		for (let i = 6; i >= 0; i--) {
			const date = new Date();
			date.setDate(date.getDate() - i);
			days.push(date.toISOString().split('T')[0]);
		}
		return days;
	}

	countActivitiesByDay(activities, days) {
		const counts = new Array(days.length).fill(0);

		activities.forEach((activity) => {
			const activityDate = new Date(activity.created_at).toISOString().split('T')[0];
			const dayIndex = days.indexOf(activityDate);
			if (dayIndex >= 0) {
				counts[dayIndex]++;
			}
		});

		return counts;
	}

	generateHeatmapData(engagementData) {
		const data = [];
		for (let week = 0; week < 4; week++) {
			for (let day = 0; day < 7; day++) {
				data.push({
					x: day,
					y: week,
					v: engagementData[`${week}-${day}`] || Math.random() * 100
				});
			}
		}
		return data;
	}

	calculateTrend(monthlyData) {
		const values = Object.values(monthlyData);
		if (values.length < 2) return 0;

		const recent = values.slice(-3).reduce((a, b) => a + b, 0) / 3;
		const previous = values.slice(-6, -3).reduce((a, b) => a + b, 0) / 3;

		return previous > 0 ? (((recent - previous) / previous) * 100).toFixed(1) : 0;
	}

	calculateGrowthRate(growthData) {
		if (!growthData || growthData.length < 2) return 0;

		const firstMonth = growthData[0].value;
		const lastMonth = growthData[growthData.length - 1].value;

		return (((lastMonth - firstMonth) / firstMonth) * 100).toFixed(1);
	}

	calculateSystemHealth(healthData) {
		const scores = {
			healthy: 100,
			warning: 70,
			critical: 30
		};

		let totalScore = 0;
		let count = 0;

		Object.entries(healthData).forEach(([component, status]) => {
			totalScore += scores[status] || 0;
			count++;
		});

		return count > 0 ? totalScore / count : 100;
	}

	calculateLearningGoals(data) {
		const weeklyGoal = 5; // 5 hours per week
		const currentWeekHours = data.weekly_study_hours || 0;

		return {
			weekly: {
				target: weeklyGoal,
				current: currentWeekHours,
				percentage: ((currentWeekHours / weeklyGoal) * 100).toFixed(0)
			},
			monthly: {
				target: weeklyGoal * 4,
				current: data.monthly_study_hours || 0,
				percentage: (((data.monthly_study_hours || 0) / (weeklyGoal * 4)) * 100).toFixed(0)
			}
		};
	}

	identifyTopPerformers(data) {
		const students = data.student_performance || [];
		return students
			.sort((a, b) => b.score - a.score)
			.slice(0, 5)
			.map((student, index) => ({
				...student,
				rank: index + 1,
				badge: index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🏅'
			}));
	}

	analyzeTrends(data) {
		return {
			userGrowth: this.calculateTrend(data.user_growth_by_month || {}),
			revenueGrowth: this.calculateTrend(data.revenue_by_month || {}),
			engagementTrend: this.calculateTrend(data.engagement_by_month || {}),
			completionTrend: this.calculateTrend(data.completion_by_month || {})
		};
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

	clearCache() {
		this.cache.clear();
	}

	// Export Methods
	async exportAnalytics(type, format = 'csv') {
		const data = await this.getDashboardAnalytics(type);

		if (format === 'csv') {
			return this.exportToCSV(data);
		} else if (format === 'pdf') {
			return this.exportToPDF(data);
		}

		throw new Error(`Unsupported export format: ${format}`);
	}

	exportToCSV(data) {
		// Convert data to CSV format
		const rows = [];

		// Add headers
		rows.push(['Metric', 'Value']);

		// Add data rows
		Object.entries(data).forEach(([key, value]) => {
			if (typeof value === 'object') {
				Object.entries(value).forEach(([subKey, subValue]) => {
					rows.push([`${key} - ${subKey}`, subValue]);
				});
			} else {
				rows.push([key, value]);
			}
		});

		// Convert to CSV string
		const csv = rows.map((row) => row.join(',')).join('\n');

		// Create download
		const blob = new Blob([csv], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `analytics_${new Date().toISOString().split('T')[0]}.csv`;
		a.click();
		URL.revokeObjectURL(url);
	}

	async exportToPDF(data) {
		// This would require a PDF library like jsPDF
		console.log('PDF export not implemented yet');
	}
}

export const analyticsService = new AnalyticsService();
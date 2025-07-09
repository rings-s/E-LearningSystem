<script>
	import { fade, fly } from 'svelte/transition';
	import { isTeacher, isStudent, isAdmin } from '$lib/utils/helpers.js';
	import { formatters } from '$lib/utils/formatters.js';
	
	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import ActivityChart from '$lib/components/charts/ActivityChart.svelte';
	import PerformanceRadar from '$lib/components/charts/PerformanceRadar.svelte';

	export let user;
	export let data = {};
	export let analytics = {};
	export let courses = [];
	export let onAction = () => {};

	// Utility functions - defined first for proper hoisting
	function getUniqueStudentCount(coursesData) {
		if (!coursesData || !Array.isArray(coursesData)) {
			return 0;
		}
		
		// Get unique students across all courses
		const uniqueStudents = new Set();
		
		coursesData.forEach(course => {
			if (course.enrolled_students && Array.isArray(course.enrolled_students)) {
				course.enrolled_students.forEach(student => {
					uniqueStudents.add(student.id || student.uuid);
				});
			}
		});
		
		// Fallback to enrollment count sum if enrolled_students not available
		if (uniqueStudents.size === 0) {
			// Try both field names for compatibility
			return coursesData.reduce((sum, c) => {
				return sum + (c.enrollment_count || c.enrolled_count || 0);
			}, 0);
		}
		
		return uniqueStudents.size;
	}

	// Derived user role
	$: userRole = user?.role || 'student';
	$: userName = user?.name || user?.first_name || user?.username || 'User';

	// Role-based data processing
	$: stats = getStatsForRole(userRole, data, courses);
	$: quickActions = getQuickActionsForRole(userRole);
	$: recentItems = getRecentItemsForRole(userRole, courses, data);

	function getStatsForRole(role, dashboardData, coursesData) {
		if (isTeacher(user)) {
			return {
				primary: {
					title: 'Total Courses',
					value: coursesData.length || 0,
					icon: '📚',
					trend: '+2 this month',
					trendDirection: 'up'
				},
				secondary: [
					{
						title: 'Published Courses',
						value: coursesData.filter(c => c.status === 'published').length || 0,
						icon: '✅',
						trend: '+1 this week',
						trendDirection: 'up'
					},
					{
						title: 'Total Students',
						value: getUniqueStudentCount(coursesData),
						icon: '👥',
						trend: '+12 this month',
						trendDirection: 'up'
					},
					{
						title: 'Average Rating',
						value: coursesData.length > 0 ? 
							(coursesData.reduce((sum, c) => sum + (c.average_rating || 0), 0) / coursesData.length).toFixed(1) : '0.0',
						icon: '⭐',
						trend: '+0.2 this month',
						trendDirection: 'up'
					}
				]
			};
		} else if (isStudent(user)) {
			return {
				primary: {
					title: 'Enrolled Courses',
					value: coursesData.length || 0,
					icon: '🎓',
					trend: '+1 this week',
					trendDirection: 'up'
				},
				secondary: [
					{
						title: 'Completed',
						value: coursesData.filter(c => c.progress === 100).length || 0,
						icon: '✅',
						trend: '+2 this month',
						trendDirection: 'up'
					},
					{
						title: 'In Progress',
						value: coursesData.filter(c => c.progress > 0 && c.progress < 100).length || 0,
						icon: '📖',
						trend: 'Active',
						trendDirection: 'neutral'
					},
					{
						title: 'Study Hours',
						value: dashboardData.total_study_hours || 0,
						icon: '⏱️',
						trend: '+5 this week',
						trendDirection: 'up'
					}
				]
			};
		} else {
			// Admin/Manager stats
			return {
				primary: {
					title: 'Total Users',
					value: dashboardData.total_users || 0,
					icon: '👥',
					trend: '+15 this month',
					trendDirection: 'up'
				},
				secondary: [
					{
						title: 'Active Courses',
						value: dashboardData.total_courses || 0,
						icon: '📚',
						trend: '+3 this week',
						trendDirection: 'up'
					},
					{
						title: 'Total Enrollments',
						value: dashboardData.total_enrollments || 0,
						icon: '🎓',
						trend: '+45 this month',
						trendDirection: 'up'
					},
					{
						title: 'Active Today',
						value: dashboardData.active_users_today || 0,
						icon: '🟢',
						trend: 'Now',
						trendDirection: 'neutral'
					}
				]
			};
		}
	}

	function getQuickActionsForRole(role) {
		if (isTeacher(user)) {
			return [
				{
					title: 'Create New Course',
					description: 'Start building your next course',
					icon: '➕',
					action: 'create_course',
					href: '/teacher/courses/create',
					primary: true
				},
				{
					title: 'Manage Students',
					description: 'View and manage your students',
					icon: '👥',
					action: 'manage_students',
					href: '/teacher/students'
				},
				{
					title: 'View All Courses',
					description: 'Manage your existing courses',
					icon: '📚',
					action: 'view_courses',
					href: '/teacher/courses'
				},
				{
					title: 'Analytics',
					description: 'View performance insights',
					icon: '📊',
					action: 'view_analytics',
					href: '#'
				}
			];
		} else if (isStudent(user)) {
			return [
				{
					title: 'Browse Courses',
					description: 'Discover new learning opportunities',
					icon: '🔍',
					action: 'browse_courses',
					href: '/courses',
					primary: true
				},
				{
					title: 'My Courses',
					description: 'Continue your learning journey',
					icon: '📖',
					action: 'my_courses',
					href: '/my-courses'
				},
				{
					title: 'Certificates',
					description: 'View your achievements',
					icon: '🏆',
					action: 'certificates',
					href: '/certificates'
				},
				{
					title: 'Study Schedule',
					description: 'Plan your learning time',
					icon: '📅',
					action: 'schedule',
					href: '/schedule'
				}
			];
		} else {
			return [
				{
					title: 'Manage Courses',
					description: 'Oversee platform courses',
					icon: '📚',
					action: 'manage_courses',
					href: '/admin/courses',
					primary: true
				},
				{
					title: 'User Management',
					description: 'Manage platform users',
					icon: '👤',
					action: 'manage_users',
					href: '/admin/users'
				},
				{
					title: 'Analytics Dashboard',
					description: 'Platform performance metrics',
					icon: '📊',
					action: 'platform_analytics',
					href: '/admin/analytics'
				},
				{
					title: 'System Settings',
					description: 'Configure platform settings',
					icon: '⚙️',
					action: 'settings',
					href: '/admin/settings'
				}
			];
		}
	}

	function getRecentItemsForRole(role, coursesData, dashboardData) {
		if (isTeacher(user)) {
			return coursesData
				.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
				.slice(0, 5)
				.map(course => ({
					title: course.title,
					description: `${course.enrollment_count || 0} students`,
					status: course.status,
					href: `/teacher/courses/${course.uuid}/manage`,
					thumbnail: course.thumbnail,
					date: course.created_at
				}));
		} else if (isStudent(user)) {
			return coursesData
				.sort((a, b) => new Date(b.last_accessed || b.enrolled_at) - new Date(a.last_accessed || a.enrolled_at))
				.slice(0, 5)
				.map(course => ({
					title: course.title,
					description: `${course.progress || 0}% complete`,
					status: course.progress === 100 ? 'completed' : 'in_progress',
					href: `/my-courses/${course.uuid}/learn`,
					thumbnail: course.thumbnail,
					date: course.last_accessed || course.enrolled_at,
					progress: course.progress
				}));
		} else {
			return dashboardData.recent_activities || [];
		}
	}

	function handleActionClick(action) {
		onAction(action.action);
	}

	// Process analytics data for charts
	function processAnalyticsData(analyticsData, userRole) {
		// Generate robust activity data with proper created_at timestamps for ActivityChart
		const now = new Date();
		const defaultActivity = [];
		
		// Create 14 days of activity data
		for (let i = 13; i >= 0; i--) {
			const date = new Date(now.getTime() - (i * 24 * 60 * 60 * 1000));
			const activityCount = Math.floor(Math.random() * 5) + 1;
			
			for (let j = 0; j < activityCount; j++) {
				const activityTime = new Date(date.getTime() + (j * 3600000)); // Add hours
				defaultActivity.push({
					created_at: activityTime.toISOString(),
					type: 'activity',
					id: `activity-${i}-${j}`,
					title: `Activity ${i}-${j}`,
					user_id: 'user-123'
				});
			}
		}
		
		const defaultPerformance = {
			quizzes: 75,
			assignments: 82,
			participation: 68,
			completion: 90,
			consistency: 85
		};

		// Validate analytics data structure
		let processedActivity = defaultActivity;
		if (analyticsData?.activity && Array.isArray(analyticsData.activity)) {
			processedActivity = analyticsData.activity.filter(activity => {
				return activity && activity.created_at && !isNaN(new Date(activity.created_at).getTime());
			});
			
			// If no valid activities, use default
			if (processedActivity.length === 0) {
				processedActivity = defaultActivity;
			}
		}

		return {
			activity: processedActivity,
			performance: analyticsData?.performance || defaultPerformance
		};
	}

	$: processedAnalytics = processAnalyticsData(analytics, userRole);
</script>

<div class="space-y-8">
	<!-- Welcome Section -->
	<div class="mb-8" in:fade={{ duration: 600 }}>
		<h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
			Welcome back, {userName}!
		</h1>
		<p class="text-gray-600 dark:text-gray-400">
			{#if isTeacher(user)}
				Here's an overview of your teaching activity and course performance.
			{:else if isStudent(user)}
				Continue your learning journey and track your progress.
			{:else}
				Monitor platform performance and manage system operations.
			{/if}
		</p>
	</div>

	<!-- Stats Section -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" in:fly={{ y: 20, delay: 100, duration: 600 }}>
		<!-- Primary Stat -->
		<div class="md:col-span-2 lg:col-span-1">
			<StatsCard
				title={stats.primary.title}
				value={stats.primary.value}
				icon={stats.primary.icon}
				trend={stats.primary.trend}
				trendDirection={stats.primary.trendDirection}
				size="large"
			/>
		</div>

		<!-- Secondary Stats -->
		{#each stats.secondary as stat}
			<StatsCard
				title={stat.title}
				value={stat.value}
				icon={stat.icon}
				trend={stat.trend}
				trendDirection={stat.trendDirection}
			/>
		{/each}
	</div>

	<!-- Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8" in:fly={{ y: 20, delay: 200, duration: 600 }}>
		<!-- Activity Chart -->
		<Card class="p-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
				Weekly Activity
			</h3>
			{#if processedAnalytics?.activity}
				<ActivityChart activities={processedAnalytics.activity} />
			{:else}
				<div class="flex items-center justify-center h-64 text-gray-500">
					<p>No activity data available</p>
				</div>
			{/if}
		</Card>

		<!-- Performance Chart -->
		<Card class="p-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
				Performance Overview
			</h3>
			{#if processedAnalytics?.performance}
				<PerformanceRadar metrics={processedAnalytics.performance} />
			{:else}
				<div class="flex items-center justify-center h-64 text-gray-500">
					<p>No performance data available</p>
				</div>
			{/if}
		</Card>
	</div>

	<!-- Recent Items and Quick Actions -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-8" in:fly={{ y: 20, delay: 300, duration: 600 }}>
		<!-- Recent Items -->
		<Card class="p-6">
			<div class="flex justify-between items-center mb-6">
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
					{#if isTeacher(user)}
						Recent Courses
					{:else if isStudent(user)}
						Continue Learning
					{:else}
						Recent Activity
					{/if}
				</h3>
				{#if recentItems.length > 0}
					<Button
						href={isTeacher(user) ? '/teacher/courses' : isStudent(user) ? '/my-courses' : '/admin'}
						variant="outline"
						size="small"
					>
						View All
					</Button>
				{/if}
			</div>

			{#if recentItems && recentItems.length > 0}
				<div class="space-y-4">
					{#each recentItems as item}
						<div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
							<div class="flex items-center space-x-4">
								{#if item.thumbnail}
									<img 
										src={item.thumbnail} 
										alt={item.title}
										class="w-12 h-12 object-cover rounded-lg"
									/>
								{:else}
									<div class="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
										<span class="text-blue-600 dark:text-blue-400 font-medium">
											{item.title?.charAt(0)?.toUpperCase() || '?'}
										</span>
									</div>
								{/if}
								<div>
									<h4 class="font-medium text-gray-900 dark:text-white">
										{item.title}
									</h4>
									<p class="text-sm text-gray-500 dark:text-gray-400">
										{item.description} • {formatters.relativeTime(item.date)}
									</p>
								</div>
							</div>
							<div class="flex items-center space-x-2">
								{#if item.status}
									<Badge
										variant={item.status === 'published' || item.status === 'completed' ? 'success' : 'warning'}
										size="small"
									>
										{item.status}
									</Badge>
								{/if}
								{#if item.progress !== undefined && isStudent(user)}
									<div class="w-16 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
										<div
											class="bg-blue-600 h-2 rounded-full"
											style="width: {item.progress}%"
										></div>
									</div>
								{/if}
								<Button
									href={item.href}
									variant="ghost"
									size="small"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
									</svg>
								</Button>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="text-center py-8 text-gray-500 dark:text-gray-400">
					<svg class="mx-auto h-16 w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						{#if isTeacher(user)}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						{:else if isStudent(user)}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
						{:else}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
						{/if}
					</svg>
					<p class="text-lg font-medium mb-2">
						{#if isTeacher(user)}
							No courses yet
						{:else if isStudent(user)}
							No enrolled courses
						{:else}
							No recent activity
						{/if}
					</p>
					<p class="mb-4">
						{#if isTeacher(user)}
							Start teaching by creating your first course
						{:else if isStudent(user)}
							Start learning by enrolling in a course
						{:else}
							Platform activity will appear here
						{/if}
					</p>
					{#if isTeacher(user)}
						<Button
							href="/teacher/courses/create"
							variant="primary"
							size="medium"
						>
							Create Your First Course
						</Button>
					{:else if isStudent(user)}
						<Button
							href="/courses"
							variant="primary"
							size="medium"
						>
							Browse Courses
						</Button>
					{/if}
				</div>
			{/if}
		</Card>

		<!-- Quick Actions -->
		<Card class="p-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
				Quick Actions
			</h3>
			
			<div class="space-y-4">
				{#each quickActions as action}
					<Button
						href={action.href}
						onclick={() => handleActionClick(action)}
						variant={action.primary ? 'primary' : 'outline'}
						size="medium"
						fullWidth
						class="justify-start"
					>
						<span class="text-xl mr-3">{action.icon}</span>
						<div class="text-left">
							<div class="font-medium">{action.title}</div>
							<div class="text-sm opacity-75">{action.description}</div>
						</div>
					</Button>
				{/each}
			</div>
		</Card>
	</div>
</div>
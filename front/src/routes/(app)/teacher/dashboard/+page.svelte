<!-- front/src/routes/(app)/teacher/dashboard/+page.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { analyticsService } from '$lib/services/analytics.service.js';
	import { coursesApi } from '$lib/apis/courses.js';
	import { t, locale } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { goto } from '$app/navigation';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';
	import ProgressChart from '$lib/components/charts/ProgressChart.svelte';
	import ActivityChart from '$lib/components/charts/ActivityChart.svelte';

	// State variables
	let loading = $state(true);
	let analytics = $state(null);
	let courses = $state([]);
	let recentActivity = $state([]);
	let error = $state('');
	let refreshing = $state(false);
	let selectedTimeRange = $state('30d');

	// Auto-refresh interval
	let refreshInterval;

	// Time range options
	const timeRanges = [
		{ value: '7d', label: 'Last 7 days' },
		{ value: '30d', label: 'Last 30 days' },
		{ value: '90d', label: 'Last 3 months' },
		{ value: 'all', label: 'All time' }
	];

	// Derived analytics data
	let summary = $derived(() => analytics?.summary || {
		total_courses: 0,
		published_courses: 0,
		total_students: 0,
		active_students_7d: 0,
		avg_course_rating: 0,
		total_revenue: 0
	});

	let engagementMetrics = $derived(() => analytics?.engagementMetrics || {
		activeStudentRate: 0,
		avgCourseRating: 0,
		totalCourses: 0,
		publishedCourses: 0
	});

	let coursePerformance = $derived(() => analytics?.coursePerformance || []);

	let studentActivity = $derived(() => analytics?.studentActivity || {
		progress_distribution: { not_started: 0, in_progress: 0, completed: 0 },
		total_students: 0,
		active_students_7d: 0
	});

	// Chart configurations
	let courseProgressChart = $derived(() => {
		if (!coursePerformance || coursePerformance.length === 0) {
			return {
				labels: [],
				datasets: [{
					label: 'Average Progress',
					data: [],
					backgroundColor: '#3b82f6',
					borderRadius: 6
				}]
			};
		}

		return {
			labels: coursePerformance.map(c => c.title.length > 15 ? c.title.substring(0, 15) + '...' : c.title),
			datasets: [{
				label: 'Average Progress (%)',
				data: coursePerformance.map(c => c.avg_progress || 0),
				backgroundColor: coursePerformance.map(c => {
					const progress = c.avg_progress || 0;
					if (progress >= 80) return '#10b981';
					if (progress >= 50) return '#f59e0b';
					return '#3b82f6';
				}),
				borderRadius: 6,
				barThickness: 20
			}]
		};
	});

	let studentDistributionChart = $derived(() => ({
		labels: ['Not Started', 'In Progress', 'Completed'],
		datasets: [{
			label: 'Students',
			data: [
				studentActivity.progress_distribution?.not_started || 0,
				studentActivity.progress_distribution?.in_progress || 0,
				studentActivity.progress_distribution?.completed || 0
			],
			backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
			borderWidth: 2,
			borderColor: '#ffffff'
		}]
	}));

	onMount(async () => {
		// Check if user is authorized
		if (!$currentUser || ($currentUser.role !== 'teacher' && !$currentUser.is_staff)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: 'You need to be a teacher to access the teacher dashboard'
			});
			goto('/dashboard');
			return;
		}

		await loadDashboardData();
		startAutoRefresh();
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadDashboardData() {
		loading = true;
		error = '';

		try {
			// Load teacher analytics
			const analyticsData = await analyticsService.getTeacherAnalytics();
			analytics = analyticsData;

			// Load teacher's courses
			await loadTeacherCourses();

			// Load recent activity
			await loadRecentActivity();

		} catch (err) {
			console.error('Failed to load dashboard data:', err);
			error = err.message || 'Failed to load dashboard data';
			
			uiStore.showNotification({
				type: 'error',
				title: 'Dashboard Error',
				message: error
			});
		} finally {
			loading = false;
		}
	}

	async function loadTeacherCourses() {
		try {
			const response = await coursesApi.getCourses({ 
				instructor: $currentUser.uuid,
				limit: 10,
				ordering: '-created_at'
			});
			courses = response.results || response || [];
		} catch (err) {
			console.error('Failed to load courses:', err);
			courses = [];
		}
	}

	async function loadRecentActivity() {
		try {
			// This would typically come from a dedicated activity API
			// For now, we'll generate some activity from course data
			recentActivity = courses.slice(0, 5).map(course => ({
				id: course.uuid,
				type: 'course_update',
				title: `Course "${course.title}" updated`,
				description: `Last modified ${formatters.relativeTime(course.updated_at)}`,
				timestamp: course.updated_at,
				metadata: { course_id: course.uuid }
			}));
		} catch (err) {
			console.error('Failed to load recent activity:', err);
			recentActivity = [];
		}
	}

	function startAutoRefresh() {
		// Refresh dashboard every 5 minutes
		refreshInterval = setInterval(async () => {
			if (!refreshing) {
				await refreshDashboard();
			}
		}, 5 * 60 * 1000);
	}

	async function refreshDashboard() {
		refreshing = true;
		try {
			await loadDashboardData();
		} catch (err) {
			console.error('Failed to refresh dashboard:', err);
		} finally {
			refreshing = false;
		}
	}

	async function handleTimeRangeChange(newRange) {
		selectedTimeRange = newRange;
		await loadDashboardData();
	}

	function navigateToCourse(courseId) {
		goto(`/teacher/courses/${courseId}/manage`);
	}

	function navigateToAnalytics(courseId) {
		goto(`/teacher/courses/${courseId}/analytics`);
	}
</script>

<svelte:head>
	<title>Teacher Dashboard | E-Learning Platform</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="container mx-auto max-w-7xl px-4 py-8">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
						Teacher Dashboard
					</h1>
					<p class="text-gray-600 dark:text-gray-400">
						Welcome back, {$currentUser?.first_name || 'Teacher'}! 
						Here's an overview of your teaching activity.
					</p>
				</div>

				<div class="flex flex-col sm:flex-row gap-3">
					<!-- Time Range Selector -->
					<select
						bind:value={selectedTimeRange}
						onchange={(e) => handleTimeRangeChange(e.target.value)}
						class="px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
					>
						{#each timeRanges as range}
							<option value={range.value}>{range.label}</option>
						{/each}
					</select>

					<!-- Action Buttons -->
					<div class="flex gap-2">
						<Button
							onclick={refreshDashboard}
							variant="outline"
							size="medium"
							disabled={refreshing}
							loading={refreshing}
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
							Refresh
						</Button>

						<Button
							href="/courses/create"
							variant="primary"
							size="medium"
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Create Course
						</Button>
					</div>
				</div>
			</div>
		</div>

		<!-- Error State -->
		{#if error}
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Dashboard Error</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={loadDashboardData} variant="primary" size="medium">
					Try Again
				</Button>
			</div>
		{:else if loading}
			<!-- Loading State -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
				{#each Array(4) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="h-4 bg-gray-200 rounded w-1/2 mb-2 dark:bg-gray-700"></div>
							<div class="h-8 bg-gray-200 rounded w-3/4 mb-2 dark:bg-gray-700"></div>
							<div class="h-3 bg-gray-200 rounded w-1/3 dark:bg-gray-700"></div>
						</Card>
					</div>
				{/each}
			</div>
		{:else}
			<!-- Dashboard Content -->
			<div in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<!-- Key Metrics -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
					<StatsCard
						title="Total Courses"
						value={summary.total_courses}
						trend="+2"
						trendDirection="up"
						icon="📚"
						color="blue"
						subtitle="courses created"
					/>
					<StatsCard
						title="Published Courses"
						value={summary.published_courses}
						trend="+1"
						trendDirection="up"
						icon="🚀"
						color="green"
						subtitle="live courses"
					/>
					<StatsCard
						title="Total Students"
						value={summary.total_students}
						trend="+{Math.floor(summary.total_students * 0.1)}"
						trendDirection="up"
						icon="👥"
						color="purple"
						subtitle="enrolled students"
					/>
					<StatsCard
						title="Active Students"
						value={summary.active_students_7d}
						trend="-{Math.floor(summary.active_students_7d * 0.05)}"
						trendDirection="down"
						icon="⚡"
						color="yellow"
						subtitle="last 7 days"
					/>
				</div>

				<!-- Charts Row -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
					<!-- Course Performance Chart -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
							Course Performance
						</h3>
						{#if coursePerformance && coursePerformance.length > 0}
							<ChartWrapper
								type="bar"
								data={courseProgressChart}
								options={{
									responsive: true,
									maintainAspectRatio: false,
									indexAxis: 'y',
									plugins: {
										legend: { display: false },
										tooltip: {
											callbacks: {
												label: (context) => `${context.parsed.x}% avg progress`
											}
										}
									},
									scales: {
										x: {
											beginAtZero: true,
											max: 100,
											ticks: {
												callback: (value) => `${value}%`
											}
										}
									}
								}}
								height="300px"
							/>
						{:else}
							<div class="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
								<div class="text-center">
									<svg class="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
									</svg>
									<p>No course data available</p>
								</div>
							</div>
						{/if}
					</Card>

					<!-- Student Progress Distribution -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
							Student Progress Distribution
						</h3>
						{#if studentActivity.total_students > 0}
							<ChartWrapper
								type="doughnut"
								data={studentDistributionChart}
								options={{
									responsive: true,
									maintainAspectRatio: false,
									plugins: {
										legend: {
											position: 'bottom'
										}
									}
								}}
								height="300px"
							/>
						{:else}
							<div class="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
								<div class="text-center">
									<svg class="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
									</svg>
									<p>No student data available</p>
								</div>
							</div>
						{/if}
					</Card>
				</div>

				<!-- Content Row -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
					<!-- Recent Courses -->
					<Card class="p-6">
						<div class="flex items-center justify-between mb-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
								Your Courses
							</h3>
							<Button
								href="/my-courses"
								variant="outline"
								size="small"
							>
								View All
							</Button>
						</div>

						{#if courses && courses.length > 0}
							<div class="space-y-4">
								{#each courses.slice(0, 5) as course}
									<div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
										<div class="flex items-center space-x-4">
											{#if course.thumbnail}
												<img
													src={course.thumbnail}
													alt={course.title}
													class="w-12 h-12 rounded-lg object-cover"
												/>
											{:else}
												<div class="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
													<svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
													</svg>
												</div>
											{/if}
											<div class="flex-1 min-w-0">
												<h4 class="font-medium text-gray-900 dark:text-white truncate">
													{course.title}
												</h4>
												<div class="flex items-center space-x-3 mt-1">
													<Badge
														variant={course.status === 'published' ? 'success' : course.status === 'draft' ? 'warning' : 'secondary'}
														size="small"
													>
														{course.status}
													</Badge>
													<span class="text-sm text-gray-500 dark:text-gray-400">
														{course.enrollments_count || 0} students
													</span>
												</div>
											</div>
										</div>
										<div class="flex items-center space-x-2">
											<Button
												onclick={() => navigateToAnalytics(course.uuid)}
												variant="ghost"
												size="small"
												title="View Analytics"
											>
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
												</svg>
											</Button>
											<Button
												onclick={() => navigateToCourse(course.uuid)}
												variant="ghost"
												size="small"
												title="Manage Course"
											>
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
												</svg>
											</Button>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="text-center py-8 text-gray-500 dark:text-gray-400">
								<svg class="mx-auto h-16 w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
								</svg>
								<p class="text-lg font-medium mb-2">No courses yet</p>
								<p class="mb-4">Start building your first course to begin teaching</p>
								<Button
									href="/courses/create"
									variant="primary"
									size="medium"
								>
									Create Your First Course
								</Button>
							</div>
						{/if}
					</Card>

					<!-- Activity Feed -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
							Recent Activity
						</h3>

						{#if recentActivity && recentActivity.length > 0}
							<ActivityFeed activities={recentActivity} />
						{:else}
							<div class="text-center py-8 text-gray-500 dark:text-gray-400">
								<svg class="mx-auto h-16 w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
								</svg>
								<p class="text-lg font-medium mb-2">No recent activity</p>
								<p>Your teaching activity will appear here</p>
							</div>
						{/if}
					</Card>
				</div>

				<!-- Quick Actions -->
				<Card class="p-6 mt-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
						Quick Actions
					</h3>
					
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
						<Button
							href="/courses/create"
							variant="outline"
							size="medium"
							class="h-20 flex-col space-y-2"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							<span>Create Course</span>
						</Button>

						<Button
							href="/my-courses"
							variant="outline"
							size="medium"
							class="h-20 flex-col space-y-2"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
							</svg>
							<span>My Courses</span>
						</Button>

						<Button
							href="/teacher/students"
							variant="outline"
							size="medium"
							class="h-20 flex-col space-y-2"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
							<span>Manage Students</span>
						</Button>

						<Button
							href="/teacher/analytics"
							variant="outline"
							size="medium"
							class="h-20 flex-col space-y-2"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
							</svg>
							<span>View Analytics</span>
						</Button>
					</div>
				</Card>
			</div>
		{/if}
	</div>
</div>
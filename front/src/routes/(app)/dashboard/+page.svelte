<!-- front/src/routes/(app)/dashboard/+page.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { analyticsService } from '$lib/services/analytics.service.js';
	import { coreApi } from '$lib/apis/core.js';
	import { coursesApi } from '$lib/apis/courses.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { goto } from '$app/navigation';

	// Core Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	
	// Dashboard Components
	import StudentDashboard from '$lib/components/dashboard/StudentDashboard.svelte';
	import TeacherDashboard from '$lib/components/dashboard/TeacherDashboard.svelte';
	import ManagerDashboard from '$lib/components/dashboard/ManagerDashboard.svelte';
	import DashboardHeader from '$lib/components/dashboard/DashboardHeader.svelte';
	import QuickActions from '$lib/components/dashboard/QuickActions.svelte';

	// State
	let loading = $state(true);
	let error = $state('');
	let dashboardData = $state(null);
	let analyticsData = $state(null);
	let coursesData = $state([]);
	let refreshing = $state(false);
	
	// Auto-refresh
	let refreshInterval;

	// User role and permissions
	const userRole = $derived($currentUser?.role || 'student');
	const userName = $derived($currentUser?.first_name || $currentUser?.username || 'User');
	const isStudent = $derived(userRole === 'student');
	const isTeacher = $derived(userRole === 'teacher');
	const isManager = $derived(userRole === 'manager' || userRole === 'admin' || $currentUser?.is_staff);

	onMount(async () => {
		await loadDashboard();
		startAutoRefresh();
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadDashboard() {
		loading = true;
		error = '';

		try {
			// Load data in parallel for better performance
			const promises = [];
			
			// Load role-specific analytics data
			if (isStudent) {
				promises.push(
					analyticsService.getStudentAnalytics().catch(err => {
						console.error('Failed to load student analytics:', err);
						return analyticsService.getFallbackStudentAnalytics();
					})
				);
				promises.push(
					coursesApi.getMyEnrollments().catch(err => {
						console.error('Failed to load enrollments:', err);
						return [];
					})
				);
			} else if (isTeacher) {
				promises.push(
					analyticsService.getTeacherAnalytics().catch(err => {
						console.error('Failed to load teacher analytics:', err);
						return analyticsService.getFallbackTeacherAnalytics();
					})
				);
				promises.push(
					coursesApi.getMyCourses().catch(err => {
						console.error('Failed to load teacher courses:', err);
						return [];
					})
				);
			} else if (isManager) {
				promises.push(
					analyticsService.getPlatformAnalytics().catch(err => {
						console.error('Failed to load platform analytics:', err);
						return analyticsService.getFallbackPlatformAnalytics();
					})
				);
				promises.push(
					coursesApi.getCourses().catch(err => {
						console.error('Failed to load courses:', err);
						return [];
					})
				);
			}

			// Always load general dashboard data
			promises.push(
				coreApi.getDashboard().catch(err => {
					console.error('Failed to load dashboard data:', err);
					return getFallbackData();
				})
			);

			// Wait for all promises to resolve
			const results = await Promise.allSettled(promises);
			
			// Process results
			if (results.length >= 2) {
				analyticsData = results[0].status === 'fulfilled' ? results[0].value : getFallbackAnalytics();
				const coursesResult = results[1].status === 'fulfilled' ? results[1].value : [];
				coursesData = Array.isArray(coursesResult) ? coursesResult : 
				              Array.isArray(coursesResult?.results) ? coursesResult.results : [];
				dashboardData = results[2]?.status === 'fulfilled' ? 
				               (results[2].value?.data || results[2].value) : getFallbackData();
			}

		} catch (err) {
			console.error('Failed to load dashboard:', err);
			error = err.message || 'Failed to load dashboard data';
			
			// Use fallback data
			dashboardData = getFallbackData();
			analyticsData = getFallbackAnalytics();
			coursesData = [];
		} finally {
			loading = false;
		}
	}

	function startAutoRefresh() {
		// Refresh every 5 minutes for real-time updates
		refreshInterval = setInterval(async () => {
			if (!refreshing) {
				await refreshDashboard();
			}
		}, 5 * 60 * 1000);
	}

	async function refreshDashboard() {
		refreshing = true;
		try {
			await loadDashboard();
		} catch (err) {
			console.error('Failed to refresh dashboard:', err);
		} finally {
			refreshing = false;
		}
	}

	function getFallbackData() {
		if (isStudent) {
			return {
				enrolled_courses: 0,
				completed_courses: 0,
				in_progress_courses: 0,
				total_study_hours: 0,
				learning_streak: 0,
				active_courses: [],
				upcoming_deadlines: [],
				recent_activities: []
			};
		} else if (isTeacher) {
			return {
				total_courses: 0,
				published_courses: 0,
				total_students: 0,
				active_students: 0,
				average_rating: 0,
				course_analytics: [],
				recent_activities: []
			};
		} else {
			return {
				total_users: 0,
				total_courses: 0,
				total_enrollments: 0,
				active_users_today: 0,
				platform_health: {}
			};
		}
	}

	function getFallbackAnalytics() {
		if (isStudent) {
			return analyticsService.getFallbackStudentAnalytics();
		} else if (isTeacher) {
			return analyticsService.getFallbackTeacherAnalytics();
		} else {
			return analyticsService.getFallbackPlatformAnalytics();
		}
	}

	function handleQuickAction(action) {
		switch (action) {
			case 'create_course':
				goto('/courses/create');
				break;
			case 'browse_courses':
				goto('/courses');
				break;
			case 'view_courses':
				goto('/my-courses');
				break;
			case 'view_analytics':
				// Navigate to role-appropriate analytics page
				if (isTeacher && coursesData && coursesData.length > 0) {
					// For teachers with courses, go to first course analytics
					goto(`/teacher/courses/${coursesData[0].uuid}/analytics`);
				} else {
					// For students and managers, show current page analytics (dashboard has built-in analytics)
					console.log('Analytics are displayed on this dashboard page');
				}
				break;
			default:
				console.log('Unknown action:', action);
		}
	}
</script>

<svelte:head>
	<title>Dashboard - E-Learning Platform</title>
</svelte:head>

<!-- Modern Dashboard Layout -->
<div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
	<div class="container mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
		<!-- Dashboard Header -->
		<DashboardHeader 
			{userName} 
			{userRole} 
			{refreshing}
			onRefresh={refreshDashboard}
		/>

		{#if error && !loading}
			<!-- Error State -->
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Dashboard Error</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={loadDashboard} variant="primary" size="medium">
					Try Again
				</Button>
			</div>
		{:else if loading}
			<!-- Loading State -->
			<div class="space-y-6" in:fade={{ duration: 300 }}>
				<!-- Loading Header -->
				<div class="animate-pulse">
					<div class="h-8 bg-gray-200 rounded-lg w-1/3 mb-4 dark:bg-gray-700"></div>
					<div class="h-4 bg-gray-200 rounded w-1/2 dark:bg-gray-700"></div>
				</div>

				<!-- Loading Stats -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
					{#each Array(4) as _}
						<div class="animate-pulse">
							<Card class="p-6">
								<div class="h-4 bg-gray-200 rounded w-1/2 mb-3 dark:bg-gray-700"></div>
								<div class="h-8 bg-gray-200 rounded w-3/4 mb-2 dark:bg-gray-700"></div>
								<div class="h-3 bg-gray-200 rounded w-1/3 dark:bg-gray-700"></div>
							</Card>
						</div>
					{/each}
				</div>

				<!-- Loading Content -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
					{#each Array(2) as _}
						<div class="animate-pulse">
							<Card class="p-6">
								<div class="h-6 bg-gray-200 rounded w-1/3 mb-4 dark:bg-gray-700"></div>
								<div class="h-64 bg-gray-200 rounded dark:bg-gray-700"></div>
							</Card>
						</div>
					{/each}
				</div>
			</div>
		{:else}
			<!-- Role-based Dashboard Content -->
			<div class="space-y-8" in:fly={{ y: 20, duration: 600 }}>
				{#if isStudent}
					<StudentDashboard 
						data={dashboardData} 
						analytics={analyticsData}
						courses={coursesData}
						onAction={handleQuickAction}
					/>
				{:else if isTeacher}
					<TeacherDashboard 
						data={dashboardData} 
						analytics={analyticsData}
						courses={coursesData}
						onAction={handleQuickAction}
					/>
				{:else if isManager}
					<ManagerDashboard 
						data={dashboardData} 
						analytics={analyticsData}
						courses={coursesData}
						onAction={handleQuickAction}
					/>
				{:else}
					<!-- Default/Guest View -->
					<Card class="p-8 text-center">
						<div class="mb-4">
							<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
						</div>
						<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
							Welcome to E-Learning Platform
						</h3>
						<p class="text-gray-600 dark:text-gray-400 mb-6">
							Please complete your profile setup to access your personalized dashboard.
						</p>
						<Button href="/profile" variant="primary" size="medium">
							Complete Profile
						</Button>
					</Card>
				{/if}

				<!-- Universal Quick Actions -->
				<QuickActions 
					{userRole} 
					onAction={handleQuickAction}
				/>
			</div>
		{/if}
	</div>
</div>
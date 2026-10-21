<!-- front/src/routes/(app)/dashboard/+page.svelte -->
<script>
	import { t } from '#lib/i18n/index.js';
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { currentUser, authStore } from '#lib/stores/auth.store.js';
	import { analyticsService } from '#lib/services/analytics.service.js';
	import { coreApi } from '#lib/apis/core.js';
	import { coursesApi } from '#lib/apis/courses.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { formatters } from '#lib/utils/formatters.js';
	import { goto } from '$app/navigation';

	// Core Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import EmptyState from '#lib/components/common/EmptyState.svelte';
	import Skeleton from '#lib/components/common/Skeleton.svelte';

	// Dashboard Components
	import UnifiedDashboard from '#lib/components/dashboard/UnifiedDashboard.svelte';
	import DashboardHeader from '#lib/components/dashboard/DashboardHeader.svelte';

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
	const userName = $derived(
		$currentUser?.first_name || $currentUser?.username || $t('dashboardHome.user')
	);
	const isStudent = $derived(userRole === 'student');
	const isTeacher = $derived(userRole === 'teacher');
	const isManager = $derived(
		userRole === 'manager' || userRole === 'admin' || $currentUser?.is_staff
	);

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
					analyticsService.getStudentAnalytics().catch((err) => {
						console.error('Failed to load student analytics:', err);
						return analyticsService.getFallbackStudentAnalytics();
					})
				);
				promises.push(
					authStore
						.makeAuthenticatedRequest(() => coursesApi.getMyEnrollments())
						.catch((err) => {
							console.error('Failed to load enrollments:', err);
							return [];
						})
				);
			} else if (isTeacher) {
				promises.push(
					analyticsService.getTeacherAnalytics().catch((err) => {
						console.error('Failed to load teacher analytics:', err);
						return analyticsService.getFallbackTeacherAnalytics();
					})
				);
				promises.push(
					coursesApi.getMyCourses().catch((err) => {
						console.error('Failed to load teacher courses:', err);
						return [];
					})
				);
			} else if (isManager) {
				promises.push(
					analyticsService.getPlatformAnalytics().catch((err) => {
						console.error('Failed to load platform analytics:', err);
						return analyticsService.getFallbackPlatformAnalytics();
					})
				);
				promises.push(
					coursesApi.getCourses().catch((err) => {
						console.error('Failed to load courses:', err);
						return [];
					})
				);
			}

			// Wait for all promises to resolve
			const results = await Promise.allSettled(promises);

			// Process results
			if (results.length >= 2) {
				analyticsData =
					results[0].status === 'fulfilled' ? results[0].value : getFallbackAnalytics();
				const coursesResult = results[1].status === 'fulfilled' ? results[1].value : [];
				const courseList = Array.isArray(coursesResult)
					? coursesResult
					: Array.isArray(coursesResult?.results)
						? coursesResult.results
						: [];
				// Student enrollments nest the course; flatten them so the dashboard reads course fields
				coursesData = isStudent
					? courseList.map((e) =>
							e?.course
								? {
										...e.course,
										progress: e.progress_percentage ?? 0,
										enrollment_status: e.status,
										enrolled_at: e.enrolled_at,
										last_accessed: e.last_accessed
									}
								: e
						)
					: courseList;
				dashboardData =
					results[2]?.status === 'fulfilled'
						? results[2].value?.data || results[2].value
						: getFallbackData();
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
		refreshInterval = setInterval(
			async () => {
				if (!refreshing) {
					await refreshDashboard();
				}
			},
			5 * 60 * 1000
		);
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
				goto('/teacher/courses/create');
				break;
			case 'browse_courses':
				goto('/courses');
				break;
			case 'view_courses':
			case 'my_courses':
				goto('/my-courses');
				break;
			case 'manage_students':
				goto('/teacher/students');
				break;
			case 'certificates':
				goto('/certificates');
				break;
			case 'schedule':
				window.location.href = '/schedule'; // page not built yet
				break;
			case 'manage_courses':
				window.location.href = '/admin/courses'; // page not built yet
				break;
			case 'manage_users':
				window.location.href = '/admin/users'; // page not built yet
				break;
			case 'platform_analytics':
				window.location.href = '/admin/analytics'; // page not built yet
				break;
			case 'settings':
				window.location.href = '/admin/settings'; // page not built yet
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
	<title>{$t('dashboardHome.pageTitle')}</title>
</svelte:head>

<div class="space-y-8">
	<DashboardHeader {userName} {userRole} {refreshing} onRefresh={refreshDashboard} />

	{#if error && !loading}
		<EmptyState
			title={$t('dashboardHome.loadError')}
			description={error}
			icon={'<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />'}
		>
			{#snippet actions()}
				<Button onclick={loadDashboard}>{$t('dashboardHome.tryAgain')}</Button>
			{/snippet}
		</EmptyState>
	{:else if loading}
		<div class="space-y-6" aria-busy="true">
			<div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
				{#each Array(4) as _}
					<Card padding="small" class="space-y-3">
						<Skeleton class="h-3 w-1/2" />
						<Skeleton class="h-7 w-2/3" />
						<Skeleton class="h-3 w-1/3" />
					</Card>
				{/each}
			</div>
			<div class="grid gap-6 lg:grid-cols-2">
				{#each Array(2) as _}
					<Card class="space-y-4">
						<Skeleton class="h-5 w-1/3" />
						<Skeleton class="h-56" />
					</Card>
				{/each}
			</div>
		</div>
	{:else if $currentUser}
		<div in:fade={{ duration: 200 }}>
			<UnifiedDashboard
				user={$currentUser}
				data={dashboardData}
				analytics={analyticsData}
				courses={coursesData}
				onAction={handleQuickAction}
			/>
		</div>
	{:else}
		<EmptyState
			title={$t('dashboardHome.profileTitle')}
			description={$t('dashboardHome.profileText')}
		>
			{#snippet actions()}
				<Button href="/profile">{$t('dashboardHome.completeProfile')}</Button>
			{/snippet}
		</EmptyState>
	{/if}
</div>

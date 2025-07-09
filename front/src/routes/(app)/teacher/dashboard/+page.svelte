<script>
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { isTeacher } from '$lib/utils/helpers.js';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import ActivityChart from '$lib/components/charts/ActivityChart.svelte';
	import PerformanceRadar from '$lib/components/charts/PerformanceRadar.svelte';

	// State variables
	let loading = $state(true);
	let error = $state('');
	let stats = $state({
		totalCourses: 0,
		publishedCourses: 0,
		totalStudents: 0,
		totalRevenue: 0,
		avgRating: 0
	});
	let recentCourses = $state([]);
	let recentActivities = $state([]);
	let chartData = $state(null);

	onMount(async () => {
		// Check authorization
		if (!isTeacher($currentUser)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: 'You need to be a teacher to access this page'
			});
			goto('/dashboard');
			return;
		}

		await loadDashboardData();
	});

	async function loadDashboardData() {
		loading = true;
		error = '';

		try {
			// Load teacher's courses
			const coursesResponse = await coursesApi.getTeacherCourses();
			const courses = coursesResponse.results || coursesResponse || [];
			
			// Calculate stats
			stats = {
				totalCourses: courses.length,
				publishedCourses: courses.filter(c => c.status === 'published').length,
				totalStudents: courses.reduce((sum, c) => sum + (c.enrollment_count || 0), 0),
				totalRevenue: 0, // TODO: Implement revenue tracking
				avgRating: courses.length > 0 ? 
					courses.reduce((sum, c) => sum + (c.average_rating || 0), 0) / courses.length : 0
			};

			// Get recent courses (last 5)
			recentCourses = courses
				.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
				.slice(0, 5);

			// Mock chart data (replace with real analytics)
			chartData = generateMockChartData();

		} catch (err) {
			console.error('Failed to load dashboard data:', err);
			error = err.message || 'Failed to load dashboard data';
		} finally {
			loading = false;
		}
	}

	function generateMockChartData() {
		// Mock data - replace with real analytics API
		return {
			activity: {
				labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
				datasets: [{
					label: 'Students Active',
					data: [12, 19, 8, 15, 22, 8, 14],
					borderColor: 'rgb(59, 130, 246)',
					backgroundColor: 'rgba(59, 130, 246, 0.1)'
				}]
			},
			performance: {
				labels: ['Course Quality', 'Student Engagement', 'Completion Rate', 'Rating', 'Feedback'],
				datasets: [{
					label: 'Performance',
					data: [85, 78, 92, 88, 82],
					borderColor: 'rgb(34, 197, 94)',
					backgroundColor: 'rgba(34, 197, 94, 0.2)'
				}]
			}
		};
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
						Welcome back, {$currentUser?.name || 'Teacher'}! Here's an overview of your teaching activity.
					</p>
				</div>

				<div class="flex flex-col sm:flex-row gap-3">
					<Button
						href="/teacher/courses/create"
						variant="primary"
						size="medium"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Create Course
					</Button>
					<Button
						href="/teacher/students"
						variant="outline"
						size="medium"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
						Manage Students
					</Button>
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
							<div class="h-4 bg-gray-200 rounded w-1/2 mb-4 dark:bg-gray-700"></div>
							<div class="h-8 bg-gray-200 rounded w-3/4 dark:bg-gray-700"></div>
						</Card>
					</div>
				{/each}
			</div>
		{:else}
			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<StatsCard
					title="Total Courses"
					value={stats.totalCourses}
					icon="📚"
					trend="+2 this month"
					trendDirection="up"
				/>
				<StatsCard
					title="Published Courses"
					value={stats.publishedCourses}
					icon="✅"
					trend="+1 this week"
					trendDirection="up"
				/>
				<StatsCard
					title="Total Students"
					value={stats.totalStudents}
					icon="👥"
					trend="+12 this month"
					trendDirection="up"
				/>
				<StatsCard
					title="Average Rating"
					value={stats.avgRating.toFixed(1)}
					icon="⭐"
					trend="+0.2 this month"
					trendDirection="up"
				/>
			</div>

			<!-- Charts and Recent Activity -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8" in:fly={{ y: 20, delay: 200, duration: 600 }}>
				<!-- Activity Chart -->
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
						Weekly Activity
					</h3>
					{#if chartData}
						<ActivityChart data={chartData.activity} />
					{/if}
				</Card>

				<!-- Performance Radar -->
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
						Teaching Performance
					</h3>
					{#if chartData}
						<PerformanceRadar data={chartData.performance} />
					{/if}
				</Card>
			</div>

			<!-- Recent Courses -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8" in:fly={{ y: 20, delay: 300, duration: 600 }}>
				<!-- My Courses -->
				<Card class="p-6">
					<div class="flex justify-between items-center mb-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
							Recent Courses
						</h3>
						<Button
							href="/teacher/courses"
							variant="outline"
							size="small"
						>
							View All
						</Button>
					</div>

					{#if recentCourses && recentCourses.length > 0}
						<div class="space-y-4">
							{#each recentCourses as course}
								<div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
									<div class="flex items-center space-x-4">
										{#if course.thumbnail}
											<img 
												src={course.thumbnail} 
												alt={course.title}
												class="w-12 h-12 object-cover rounded-lg"
											/>
										{:else}
											<div class="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
												<span class="text-blue-600 dark:text-blue-400 font-medium">
													{course.title?.charAt(0)?.toUpperCase() || '?'}
												</span>
											</div>
										{/if}
										<div>
											<h4 class="font-medium text-gray-900 dark:text-white">
												{course.title}
											</h4>
											<p class="text-sm text-gray-500 dark:text-gray-400">
												{course.enrollment_count || 0} students • {formatters.date(course.created_at)}
											</p>
										</div>
									</div>
									<div class="flex items-center space-x-2">
										<Badge
											variant={course.status === 'published' ? 'success' : 'warning'}
											size="small"
										>
											{course.status}
										</Badge>
										<Button
											href="/teacher/courses/{course.uuid}/manage"
											variant="ghost"
											size="small"
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
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							<p class="text-lg font-medium mb-2">No courses yet</p>
							<p class="mb-4">Start teaching by creating your first course</p>
							<Button
								href="/teacher/courses/create"
								variant="primary"
								size="medium"
							>
								Create Your First Course
							</Button>
						</div>
					{/if}
				</Card>

				<!-- Quick Actions -->
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
						Quick Actions
					</h3>
					
					<div class="space-y-4">
						<Button
							href="/teacher/courses/create"
							variant="outline"
							size="medium"
							fullWidth
							class="justify-start"
						>
							<svg class="h-5 w-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							<span class="ml-3">Create New Course</span>
						</Button>

						<Button
							href="/teacher/students"
							variant="outline"
							size="medium"
							fullWidth
							class="justify-start"
						>
							<svg class="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
							<span class="ml-3">Manage Students</span>
						</Button>

						<Button
							href="/teacher/courses"
							variant="outline"
							size="medium"
							fullWidth
							class="justify-start"
						>
							<svg class="h-5 w-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							<span class="ml-3">View All Courses</span>
						</Button>

						<Button
							href="/certificates"
							variant="outline"
							size="medium"
							fullWidth
							class="justify-start"
						>
							<svg class="h-5 w-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
							</svg>
							<span class="ml-3">View Certificates</span>
						</Button>
					</div>
				</Card>
			</div>
		{/if}
	</div>
</div>
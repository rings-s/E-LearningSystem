<!-- front/src/lib/components/dashboard/TeacherDashboard.svelte -->
<script>
	import { fade, fly } from 'svelte/transition';
	import { formatters } from '$lib/utils/formatters.js';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';

	let { data, analytics, courses = [], onAction = () => {} } = $props();

	// Derived data from backend analytics
	const summary = $derived(analytics?.summary || {});
	const coursePerformance = $derived(analytics?.course_performance || []);
	const studentActivity = $derived(analytics?.student_activity || {});
	const charts = $derived(analytics?.charts || {});

	// Combine analytics course performance with real courses data
	// Analytics provides engagement metrics, real courses ensure we show all courses
	const combinedCourses = $derived(() => {
		// Always show courses if they exist, even without analytics
		if (courses && courses.length > 0) {
			return courses.map(course => {
				// Find matching analytics data for this course
				const analyticsMatch = coursePerformance.find(p => p.course_id === course.uuid);
				
				return {
					course_id: course.uuid,
					title: course.title,
					total_students: course.enrolled_students_count || 0,
					avg_progress: analyticsMatch?.avg_progress || 0,
					engagement_score: analyticsMatch?.engagement_score || 0,
					avg_rating: course.avg_rating || analyticsMatch?.avg_rating || 0,
					status: course.status,
					created_at: course.created_at,
					updated_at: course.updated_at
				};
			});
		}
		
		// If no courses but we have analytics data, show that
		return coursePerformance || [];
	});

	// Analytics calculations
	const engagementRate = $derived(() => {
		return formatters.safePercent(summary?.active_students_7d || 0, summary?.total_students || 0);
	});

	const completionRate = $derived(() => {
		const dist = studentActivity?.progress_distribution || {};
		const total = (dist.not_started || 0) + (dist.in_progress || 0) + (dist.completed || 0);
		return formatters.safePercent(dist.completed || 0, total);
	});
</script>

<div class="space-y-8">
	<!-- Teacher Metrics -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" in:fly={{ y: 20, duration: 600 }}>
		<StatsCard
			title="Total Courses"
			value={summary?.total_courses || 0}
			trend={summary?.published_courses ? `${summary.published_courses} published` : ''}
			trendDirection="up"
			icon="📚"
			color="blue"
		/>
		<StatsCard
			title="Total Students"
			value={summary?.total_students || 0}
			trend={summary?.active_students_7d ? `${summary.active_students_7d} active` : ''}
			trendDirection="up"
			icon="👥"
			color="green"
		/>
		<StatsCard
			title="Avg. Rating"
			value={(summary?.avg_course_rating || 0).toFixed(1)}
			trend={summary?.avg_course_rating > 4 ? '⭐' : ''}
			trendDirection="up"
			icon="⭐"
			color="yellow"
		/>
		<StatsCard
			title="Engagement"
			value="{engagementRate()}%"
			trend={engagementRate() > 70 ? 'High' : engagementRate() > 40 ? 'Medium' : 'Low'}
			trendDirection={engagementRate() > 70 ? 'up' : 'down'}
			icon="⚡"
			color="purple"
		/>
	</div>

	<!-- Main Content -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
		<!-- Course Performance -->
		<Card class="p-6">
			<div class="flex items-center justify-between mb-6">
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Course Performance</h3>
				<Button onclick={() => onAction('view_analytics')} variant="outline" size="small">
					View Details
				</Button>
			</div>

			{#if combinedCourses && combinedCourses.length > 0}
				<div class="space-y-4">
					{#each combinedCourses.slice(0, 5) as course}
						<div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
							<div class="flex-1 min-w-0">
								<h4 class="font-medium text-gray-900 dark:text-white truncate">
									{course.title}
								</h4>
								<div class="flex items-center space-x-4 mt-1 text-sm text-gray-500 dark:text-gray-400">
									<span>{course.total_students || 0} students</span>
									<span>{formatters.safeRound(course.avg_progress)}% avg progress</span>
									<Badge
										variant={course.engagement_score > 70 ? 'success' : course.engagement_score > 40 ? 'warning' : 'danger'}
										size="small"
									>
										{formatters.safeRound(course.engagement_score)}% engagement
									</Badge>
								</div>
							</div>
							<div class="flex items-center space-x-2 ml-4">
								<Button
									href="/teacher/courses/{course.course_id}/analytics"
									variant="ghost"
									size="small"
									title="View Analytics"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
									</svg>
								</Button>
								<Button
									href="/teacher/courses/{course.course_id}/manage"
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
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
					</svg>
					<p class="text-lg font-medium mb-2">No courses yet</p>
					<p class="mb-4">Create your first course to start teaching</p>
					<Button onclick={() => onAction('create_course')} variant="primary" size="medium">
						Create Course
					</Button>
				</div>
			{/if}
		</Card>

		<!-- Student Progress Distribution -->
		<Card class="p-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
				Student Progress Distribution
			</h3>
			
			{#if studentActivity?.total_students > 0}
				<div class="space-y-4">
					<!-- Chart -->
					{#if charts?.student_progress}
						<ChartWrapper
							type="doughnut"
							data={charts.student_progress.data}
							options={{
								responsive: true,
								maintainAspectRatio: false,
								plugins: {
									legend: { position: 'bottom' }
								}
							}}
							height="250px"
						/>
					{/if}

					<!-- Summary Stats -->
					<div class="grid grid-cols-3 gap-4 mt-6">
						<div class="text-center">
							<div class="text-2xl font-bold text-red-600 dark:text-red-400">
								{studentActivity?.progress_distribution?.not_started || 0}
							</div>
							<div class="text-sm text-gray-600 dark:text-gray-400">Not Started</div>
						</div>
						<div class="text-center">
							<div class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
								{studentActivity?.progress_distribution?.in_progress || 0}
							</div>
							<div class="text-sm text-gray-600 dark:text-gray-400">In Progress</div>
						</div>
						<div class="text-center">
							<div class="text-2xl font-bold text-green-600 dark:text-green-400">
								{studentActivity?.progress_distribution?.completed || 0}
							</div>
							<div class="text-sm text-gray-600 dark:text-gray-400">Completed</div>
						</div>
					</div>
				</div>
			{:else}
				<div class="text-center py-8 text-gray-500 dark:text-gray-400">
					<svg class="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
					<p>No student data available</p>
				</div>
			{/if}
		</Card>
	</div>

	<!-- Quick Course Actions -->
	<Card class="p-6">
		<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
			Quick Actions
		</h3>
		
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<Button
				onclick={() => onAction('create_course')}
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-blue-50 dark:hover:bg-blue-900/20"
			>
				<svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				<span>Create Course</span>
			</Button>

			<Button
				onclick={() => onAction('view_courses')}
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-green-50 dark:hover:bg-green-900/20"
			>
				<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
				</svg>
				<span>My Courses</span>
			</Button>

			<Button
				href="/teacher/students"
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-purple-50 dark:hover:bg-purple-900/20"
			>
				<svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
				</svg>
				<span>Manage Students</span>
			</Button>

			<Button
				onclick={() => onAction('view_analytics')}
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-orange-50 dark:hover:bg-orange-900/20"
			>
				<svg class="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
				</svg>
				<span>View Analytics</span>
			</Button>
		</div>
	</Card>
</div>
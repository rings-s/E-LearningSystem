<!-- front/src/lib/components/dashboard/StudentDashboard.svelte -->
<script>
	import { fade, fly, slide } from 'svelte/transition';
	import { formatters } from '$lib/utils/formatters.js';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';

	let { data, analytics, courses = [], onAction = () => {} } = $props();

	// Derived data from backend analytics
	const summary = $derived(analytics?.summary || {});
	const charts = $derived(analytics?.charts || {});
	const performanceData = $derived(analytics?.performance || {});
	const studyTimeData = $derived(analytics?.study_time || {});

	// Progress calculations
	const totalProgress = $derived(() => {
		if (!summary.total_courses || summary.total_courses === 0) return 0;
		return Math.round((summary.completed_courses / summary.total_courses) * 100);
	});

	const weeklyGoalProgress = $derived(() => {
		const weeklyTarget = 5; // 5 hours per week
		const currentWeekHours = studyTimeData?.weekly_average || 0;
		return Math.min(100, Math.round((currentWeekHours / weeklyTarget) * 100));
	});
</script>

<div class="space-y-8">
	<!-- Key Metrics -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" in:fly={{ y: 20, duration: 600 }}>
		<StatsCard
			title="Enrolled Courses"
			value={summary.total_courses || 0}
			trend={summary.total_courses > 0 ? '+1' : ''}
			trendDirection="up"
			icon="📚"
			color="blue"
		/>
		<StatsCard
			title="Completed"
			value={summary.completed_courses || 0}
			trend={summary.completed_courses > 0 ? `${totalProgress}%` : ''}
			trendDirection="up"
			icon="✅"
			color="green"
		/>
		<StatsCard
			title="Study Hours"
			value={Math.round(summary.study_hours_30d || 0)}
			trend={studyTimeData?.weekly_average ? `+${Math.round(studyTimeData.weekly_average)}h/week` : ''}
			trendDirection="up"
			icon="⏱️"
			color="purple"
		/>
		<StatsCard
			title="Learning Streak"
			value={summary.learning_streak || 0}
			trend={summary.learning_streak > 7 ? '🔥' : ''}
			trendDirection="up"
			icon="📈"
			color="orange"
		/>
	</div>

	<!-- Main Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
		<!-- Continue Learning (2 columns) -->
		<div class="lg:col-span-2 space-y-6">
			{#if data?.active_courses?.length > 0}
				<Card class="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
					<div class="flex items-center justify-between mb-6">
						<div>
							<h3 class="text-xl font-bold text-gray-900 dark:text-white">Continue Learning</h3>
							<p class="text-gray-600 dark:text-gray-400">Pick up where you left off</p>
						</div>
						<Badge variant="primary" class="bg-blue-100 text-blue-700">
							{data.in_progress_courses || 0} active
						</Badge>
					</div>
					
					<div class="space-y-4">
						{#each data.active_courses as course, index}
							<div class="group relative overflow-hidden rounded-xl bg-white dark:bg-gray-800 p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
								<div class="flex items-center justify-between">
									<div class="flex-1 space-y-3">
										<div>
											<h4 class="font-semibold text-gray-900 dark:text-white text-lg group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
												{course.title}
											</h4>
											<p class="text-sm text-gray-500 dark:text-gray-400">
												by {course.instructor}
											</p>
										</div>
										
										<div class="space-y-2">
											<div class="flex items-center justify-between text-sm">
												<span class="text-gray-600 dark:text-gray-400">Progress</span>
												<span class="font-semibold text-gray-900 dark:text-white">{course.progress}%</span>
											</div>
											<CourseProgress progress={course.progress} />
										</div>
										
										<p class="text-xs text-gray-500 dark:text-gray-400">
											Last accessed {formatters.relativeTime(course.last_accessed)}
										</p>
									</div>
									
									<div class="ml-6">
										<Button 
											href="/courses/{course.uuid}/learn" 
											variant="primary" 
											class="shadow-lg hover:shadow-xl transition-all duration-300 group-hover:scale-105"
										>
											Continue
											<svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
											</svg>
										</Button>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</Card>
			{:else}
				<!-- Empty State -->
				<Card class="p-8 text-center bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900">
					<div class="space-y-6">
						<div class="mx-auto w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-2xl flex items-center justify-center">
							<svg class="w-10 h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
							</svg>
						</div>
						<div>
							<h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
								Ready to Start Learning? 🎓
							</h3>
							<p class="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
								Discover courses designed to help you grow and succeed in your learning journey.
							</p>
						</div>
						<Button onclick={() => onAction('browse_courses')} variant="primary" size="large" class="shadow-lg hover:shadow-xl">
							<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							Explore Courses
						</Button>
					</div>
				</Card>
			{/if}

			<!-- Course Progress Chart -->
			{#if charts?.course_progress}
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
						Course Progress
					</h3>
					<ChartWrapper
						type="bar"
						data={charts.course_progress.data}
						options={{
							responsive: true,
							maintainAspectRatio: false,
							plugins: { legend: { display: false } },
							scales: {
								y: { beginAtZero: true, max: 100, title: { display: true, text: 'Progress %' } },
								x: { title: { display: true, text: 'Courses' } }
							}
						}}
						height="300px"
					/>
				</Card>
			{/if}

			<!-- Study Analytics -->
			{#if charts?.study_time_trend}
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
						Study Time Trends
					</h3>
					<ChartWrapper
						type="line"
						data={charts.study_time_trend.data}
						options={{
							responsive: true,
							maintainAspectRatio: false,
							plugins: { legend: { display: false } },
							scales: {
								y: { beginAtZero: true, title: { display: true, text: 'Minutes' } },
								x: { title: { display: true, text: 'Days' } }
							}
						}}
						height="300px"
					/>
				</Card>
			{/if}
		</div>

		<!-- Sidebar -->
		<div class="space-y-6">
			<!-- Weekly Goal -->
			<Card class="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
				<div class="flex items-center space-x-3 mb-4">
					<div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
						<svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
					<div>
						<h4 class="font-semibold text-gray-900 dark:text-white">Weekly Goal</h4>
						<p class="text-sm text-gray-600 dark:text-gray-400">5 hours this week</p>
					</div>
				</div>
				<div class="space-y-2">
					<div class="flex justify-between text-sm">
						<span class="text-gray-600 dark:text-gray-400">Progress</span>
						<span class="font-semibold text-gray-900 dark:text-white">{weeklyGoalProgress}%</span>
					</div>
					<CourseProgress progress={weeklyGoalProgress} variant="success" />
				</div>
			</Card>

			<!-- Upcoming Deadlines -->
			{#if data?.upcoming_deadlines?.length}
				<Card class="p-6">
					<h4 class="font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
						<svg class="w-5 h-5 mr-2 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						Upcoming Deadlines
					</h4>
					<div class="space-y-3">
						{#each data.upcoming_deadlines as deadline}
							<div class="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
								<div>
									<p class="font-medium text-gray-900 dark:text-white text-sm">{deadline.assignment}</p>
									<p class="text-xs text-gray-600 dark:text-gray-400">{deadline.course}</p>
								</div>
								<Badge variant="warning" size="small">
									{formatters.relativeTime(deadline.due)}
								</Badge>
							</div>
						{/each}
					</div>
				</Card>
			{/if}

			<!-- Performance Overview -->
			{#if performanceData?.total_quizzes > 0}
				<Card class="p-6">
					<h4 class="font-semibold text-gray-900 dark:text-white mb-4">Performance</h4>
					<div class="space-y-4">
						<div class="flex items-center justify-between">
							<span class="text-sm text-gray-600 dark:text-gray-400">Quiz Average</span>
							<span class="font-semibold text-gray-900 dark:text-white">
								{Math.round(performanceData.avg_quiz_score || 0)}%
							</span>
						</div>
						<div class="flex items-center justify-between">
							<span class="text-sm text-gray-600 dark:text-gray-400">Pass Rate</span>
							<span class="font-semibold text-gray-900 dark:text-white">
								{Math.round(performanceData.quiz_pass_rate || 0)}%
							</span>
						</div>
						<div class="flex items-center justify-between">
							<span class="text-sm text-gray-600 dark:text-gray-400">Completed Quizzes</span>
							<span class="font-semibold text-gray-900 dark:text-white">
								{performanceData.total_quizzes || 0}
							</span>
						</div>
					</div>
				</Card>
			{/if}
		</div>
	</div>
</div>
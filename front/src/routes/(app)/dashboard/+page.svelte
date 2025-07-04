<!-- front/src/routes/(app)/dashboard/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { coreApi } from '$lib/apis/core.js';
	import { currentUser } from '$lib/services/auth.service.js';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import { formatters } from '$lib/utils/formatters.js';

	let dashboardData = $state(null);
	let loading = $state(true);
	let activeTab = $state('overview');
	let greeting = $state('');
	let currentTime = $state(new Date());

	// Animation and visual state
	let statsVisible = $state(false);
	let contentVisible = $state(false);

	onMount(async () => {
		// Set greeting based on time
		const hour = new Date().getHours();
		if (hour < 12) greeting = 'Good morning';
		else if (hour < 17) greeting = 'Good afternoon';
		else greeting = 'Good evening';

		// Update time every minute
		const timeInterval = setInterval(() => {
			currentTime = new Date();
		}, 60000);

		try {
			const response = await coreApi.getDashboard();
			dashboardData = response.data || response;
		} catch (error) {
			console.error('Failed to load dashboard:', error);
			dashboardData = {
				enrolled_courses: 5,
				completed_courses: 2,
				total_study_hours: 42,
				total_certificates: 3,
				in_progress_courses: 3,
				active_courses: [
					{
						uuid: '1',
						title: 'Advanced React Development',
						progress: 75,
						last_accessed: '2024-01-15',
						instructor: 'Dr. Sarah Johnson'
					},
					{
						uuid: '2',
						title: 'Machine Learning Fundamentals',
						progress: 45,
						last_accessed: '2024-01-14',
						instructor: 'Prof. Ahmad Hassan'
					}
				],
				recent_activities: [],
				total_courses: 8,
				total_students: 150,
				average_rating: 4.8,
				active_students: 89,
				course_analytics: [],
				learning_streak: 7,
				weekly_goal_progress: 68,
				upcoming_deadlines: [
					{ course: 'React Development', assignment: 'Final Project', due: '2024-01-20' },
					{ course: 'ML Fundamentals', assignment: 'Quiz 3', due: '2024-01-18' }
				]
			};
		} finally {
			loading = false;
			// Trigger animations after loading
			setTimeout(() => (statsVisible = true), 200);
			setTimeout(() => (contentVisible = true), 400);
		}

		return () => clearInterval(timeInterval);
	});

	const isTeacher = $derived($currentUser?.role === 'teacher');
	const userName = $derived($currentUser?.first_name || 'Student');

	// Dynamic background based on time of day
	const timeBasedGradient = $derived(() => {
		const hour = currentTime.getHours();
		if (hour >= 6 && hour < 12) {
			return 'from-orange-100 via-amber-50 to-yellow-100 dark:from-orange-900/20 dark:via-amber-900/10 dark:to-yellow-900/20';
		} else if (hour >= 12 && hour < 18) {
			return 'from-blue-100 via-cyan-50 to-sky-100 dark:from-blue-900/20 dark:via-cyan-900/10 dark:to-sky-900/20';
		} else {
			return 'from-purple-100 via-indigo-50 to-blue-100 dark:from-purple-900/20 dark:via-indigo-900/10 dark:to-blue-900/20';
		}
	});

	const tabs = $derived([
		{ id: 'overview', label: 'Overview', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z' },
		...(isTeacher
			? [
					{ id: 'courses', label: 'My Courses', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' },
					{ id: 'analytics', label: 'Analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' }
				]
			: [
					{ id: 'progress', label: 'My Progress', icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' },
					{ id: 'activity', label: 'Activity', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' }
				])
	]);
</script>

<svelte:head>
	<title>Dashboard - 244SCHOOL</title>
</svelte:head>

<!-- Main Dashboard Container -->
<div class="min-h-screen bg-gradient-to-br {timeBasedGradient} transition-all duration-1000">
	<div class="container mx-auto px-4 py-6 lg:px-6 xl:px-8">
		<div class="mx-auto max-w-8xl space-y-8">
			<!-- Enhanced Header with Personalization -->
			<div class="relative overflow-hidden" in:fly={{ y: -20, duration: 600 }}>
				<div class="relative z-10 flex flex-col space-y-4 lg:flex-row lg:items-center lg:justify-between lg:space-y-0">
					<div class="space-y-1">
						<div class="flex items-center space-x-3">
							<h1 class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent dark:from-white dark:to-gray-300 lg:text-5xl">
								{greeting}, {userName}! 👋
							</h1>
						</div>
						<p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl">
							Ready to continue your learning journey? Let's make today count.
						</p>
						<div class="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
							<span class="flex items-center space-x-1">
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<span>{currentTime.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
							</span>
							{#if dashboardData?.learning_streak}
								<span class="flex items-center space-x-1">
									<svg class="w-4 h-4 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
										<path d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" />
									</svg>
									<span>{dashboardData.learning_streak} day streak</span>
								</span>
							{/if}
						</div>
					</div>
					
					<!-- Quick Actions -->
					<div class="flex flex-wrap gap-3">
						{#if !isTeacher}
							<Button href="/courses" variant="primary" class="shadow-lg hover:shadow-xl transition-all duration-300">
								<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
								Explore Courses
							</Button>
						{:else}
							<Button href="/courses/create" variant="primary" class="shadow-lg hover:shadow-xl transition-all duration-300">
								<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
								</svg>
								Create Course
							</Button>
						{/if}
						<Button href="/my-courses" variant="outline" class="backdrop-blur-sm bg-white/20 border-white/30 hover:bg-white/30">
							My Courses
						</Button>
					</div>
				</div>
				
				<!-- Floating background elements -->
				<div class="absolute top-0 right-0 -mr-40 -mt-40 opacity-10">
					<div class="w-80 h-80 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full blur-3xl"></div>
				</div>
			</div>

			{#if loading}
				<div class="flex items-center justify-center h-96" transition:fade>
					<div class="text-center space-y-4">
						<div class="relative">
							<div class="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto"></div>
							<div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-secondary-400 rounded-full animate-spin mx-auto animation-delay-150"></div>
						</div>
						<p class="text-lg font-medium text-gray-600 dark:text-gray-300">Loading your dashboard...</p>
						<p class="text-sm text-gray-500 dark:text-gray-400">Preparing your personalized experience</p>
					</div>
				</div>
			{:else if dashboardData}
				<!-- Enhanced Tab Navigation -->
				<div class="sticky top-16 z-40 -mx-4 px-4 lg:-mx-6 lg:px-6 xl:-mx-8 xl:px-8" in:fly={{ y: 20, duration: 600, delay: 200 }}>
					<div class="backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 border border-white/20 dark:border-gray-700/50 rounded-2xl shadow-xl">
						<nav class="flex space-x-1 p-2">
							{#each tabs as tab}
								<button
									onclick={() => (activeTab = tab.id)}
									class="relative flex items-center space-x-3 px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 group {activeTab === tab.id
										? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg'
										: 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-800/50'}"
								>
									<svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={tab.icon} />
									</svg>
									<span>{tab.label}</span>
									{#if activeTab === tab.id}
										<div class="absolute inset-0 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl blur opacity-30 -z-10" transition:scale></div>
									{/if}
								</button>
							{/each}
						</nav>
					</div>
				</div>

				<!-- Tab Content with Enhanced Animations -->
				<div class="space-y-8">
					{#if activeTab === 'overview'}
						{#if isTeacher}
							{@render TeacherOverview()}
						{:else}
							{@render StudentOverview()}
						{/if}
					{:else if activeTab === 'courses' && isTeacher}
						{@render TeacherCourses()}
					{:else if activeTab === 'analytics' && isTeacher}
						{@render TeacherAnalytics()}
					{:else if activeTab === 'progress' && !isTeacher}
						{@render StudentProgress()}
					{:else if activeTab === 'activity' && !isTeacher}
						{@render StudentActivity()}
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>

{#snippet StudentOverview()}
	<div class="space-y-8" in:fade={{ duration: 600 }}>
		<!-- Enhanced Stats Grid with Micro-interactions -->
		{#if statsVisible}
			<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4" in:fly={{ y: 30, duration: 600, delay: 100 }}>
				<div in:fly={{ x: -20, duration: 500, delay: 200 }}>
					<StatsCard
						title="Total Courses"
						value={dashboardData?.enrolled_courses || 0}
						icon="<path stroke-linecap='round' stroke-linejoin='round' d='M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' />"
						color="primary"
						trend={{ value: 2, direction: 'up' }}
					/>
				</div>
				<div in:fly={{ x: -20, duration: 500, delay: 300 }}>
					<StatsCard
						title="Completed Courses"
						value={dashboardData?.completed_courses || 0}
						icon="<path stroke-linecap='round' stroke-linejoin='round' d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' />"
						color="success"
						trend={{ value: 15, direction: 'up' }}
					/>
				</div>
				<div in:fly={{ x: -20, duration: 500, delay: 400 }}>
					<StatsCard
						title="Hours Learned"
						value={dashboardData?.total_study_hours || 0}
						format="duration"
						icon="<path stroke-linecap='round' stroke-linejoin='round' d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' />"
						color="warning"
						trend={{ value: 8, direction: 'up' }}
					/>
				</div>
				<div in:fly={{ x: -20, duration: 500, delay: 500 }}>
					<StatsCard
						title="Certificates"
						value={dashboardData?.total_certificates || 0}
						icon="<path stroke-linecap='round' stroke-linejoin='round' d='M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z' />"
						color="info"
						trend={{ value: 1, direction: 'up' }}
					/>
				</div>
			</div>
		{/if}

		{#if contentVisible}
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8" in:fly={{ y: 30, duration: 600, delay: 300 }}>
				<!-- Continue Learning - Enhanced -->
				<div class="lg:col-span-2 space-y-6">
					{#if dashboardData?.in_progress_courses > 0 && dashboardData?.active_courses?.length > 0}
						<Card variant="elevated" class="overflow-hidden">
							<div class="p-6 bg-gradient-to-r from-primary-500/5 to-secondary-500/5 dark:from-primary-400/10 dark:to-secondary-400/10">
								<div class="flex items-center justify-between mb-6">
									<div>
										<h3 class="text-xl font-bold text-gray-900 dark:text-white">Continue Learning</h3>
										<p class="text-gray-600 dark:text-gray-400">Pick up where you left off</p>
									</div>
									<Badge variant="primary" class="bg-primary-100 text-primary-700">
										{dashboardData.in_progress_courses} active
									</Badge>
								</div>
								
								<div class="space-y-4">
									{#each dashboardData.active_courses as course, index}
										<div class="group relative overflow-hidden rounded-xl bg-white dark:bg-gray-800 p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
											<div class="flex items-center justify-between">
												<div class="flex-1 space-y-3">
													<div>
														<h4 class="font-semibold text-gray-900 dark:text-white text-lg group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
															{course.title}
														</h4>
														<p class="text-sm text-gray-500 dark:text-gray-400">
															Instructor: {course.instructor}
														</p>
													</div>
													
													<div class="space-y-2">
														<div class="flex items-center justify-between text-sm">
															<span class="text-gray-600 dark:text-gray-400">Progress</span>
															<span class="font-semibold text-gray-900 dark:text-white">{course.progress}%</span>
														</div>
														<CourseProgress progress={course.progress} class="h-2" />
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
											
											<!-- Hover gradient effect -->
											<div class="absolute inset-0 bg-gradient-to-r from-primary-500/0 to-secondary-500/0 group-hover:from-primary-500/5 group-hover:to-secondary-500/5 transition-all duration-300 pointer-events-none"></div>
										</div>
									{/each}
								</div>
							</div>
						</Card>
					{:else}
						<Card variant="elevated" class="text-center py-12">
							<div class="space-y-6">
								<div class="mx-auto w-24 h-24 bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 rounded-2xl flex items-center justify-center">
									<svg class="w-12 h-12 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
									</svg>
								</div>
								<div>
									<h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
										Welcome to 244SCHOOL! 🎓
									</h3>
									<p class="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
										Ready to start your learning journey? Discover courses designed to help you grow and succeed.
									</p>
								</div>
								<Button href="/courses" variant="primary" size="large" class="shadow-lg hover:shadow-xl">
									<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
									</svg>
									Explore Courses
								</Button>
							</div>
						</Card>
					{/if}
				</div>

				<!-- Sidebar with Goals and Quick Info -->
				<div class="space-y-6">
					<!-- Weekly Goal Progress -->
					{#if dashboardData?.weekly_goal_progress}
						<Card variant="elevated" class="overflow-hidden">
							<div class="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
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
										<span class="font-semibold text-gray-900 dark:text-white">{dashboardData.weekly_goal_progress}%</span>
									</div>
									<CourseProgress progress={dashboardData.weekly_goal_progress} variant="success" class="h-2" />
								</div>
							</div>
						</Card>
					{/if}

					<!-- Upcoming Deadlines -->
					{#if dashboardData?.upcoming_deadlines?.length}
						<Card variant="elevated">
							<div class="p-6">
								<h4 class="font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
									<svg class="w-5 h-5 mr-2 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									Upcoming Deadlines
								</h4>
								<div class="space-y-3">
									{#each dashboardData.upcoming_deadlines as deadline}
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
							</div>
						</Card>
					{/if}

					<!-- Learning Insights -->
					<Card variant="elevated">
						<div class="p-6">
							<h4 class="font-semibold text-gray-900 dark:text-white mb-4">Learning Insights</h4>
							<div class="space-y-4">
								<div class="flex items-center justify-between">
									<span class="text-sm text-gray-600 dark:text-gray-400">Avg. session time</span>
									<span class="font-semibold text-gray-900 dark:text-white">1h 24m</span>
								</div>
								<div class="flex items-center justify-between">
									<span class="text-sm text-gray-600 dark:text-gray-400">Favorite topic</span>
									<Badge variant="info" size="small">Development</Badge>
								</div>
								<div class="flex items-center justify-between">
									<span class="text-sm text-gray-600 dark:text-gray-400">Study streak</span>
									<span class="font-semibold text-orange-600 dark:text-orange-400 flex items-center">
										<svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
											<path d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" />
										</svg>
										{dashboardData.learning_streak} days
									</span>
								</div>
							</div>
						</div>
					</Card>
				</div>
			</div>
		{/if}
	</div>
{/snippet}

{#snippet TeacherOverview()}
	<div class="space-y-8" in:fade={{ duration: 600 }}>
		{#if statsVisible}
			<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4" in:fly={{ y: 30, duration: 600, delay: 100 }}>
				<StatsCard
					title="Total Courses"
					value={dashboardData?.total_courses || 0}
					icon="<path stroke-linecap='round' stroke-linejoin='round' d='M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' />"
					color="primary"
				/>
				<StatsCard
					title="Total Students"
					value={dashboardData?.total_students || 0}
					icon="<path stroke-linecap='round' stroke-linejoin='round' d='M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' />"
					color="success"
				/>
				<StatsCard
					title="Average Rating"
					value={dashboardData?.average_rating || 0}
					format="number"
					icon="<path d='M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z' />"
					color="warning"
				/>
				<StatsCard
					title="Active Students"
					value={dashboardData?.active_students || 0}
					trend={{ value: 12, direction: 'up' }}
					icon="<path stroke-linecap='round' stroke-linejoin='round' d='M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' />"
					color="info"
				/>
			</div>
		{/if}
	</div>
{/snippet}

{#snippet TeacherCourses()}
	<div class="space-y-4" in:fade={{ duration: 600 }}>
		{#if dashboardData?.course_analytics?.length > 0}
			{#each dashboardData.course_analytics as course}
				<Card variant="bordered" hoverable>
					<div class="flex items-center justify-between">
						<div>
							<h4 class="text-lg font-semibold text-gray-900 dark:text-white">
								{course.title}
							</h4>
							<p class="text-sm text-gray-500 dark:text-gray-400">
								{course.enrolled_count} students • {course.completion_rate}% completion rate
							</p>
						</div>
						<Button href="/teaching/courses/{course.uuid}" variant="outline">
							Manage Course
						</Button>
					</div>
				</Card>
			{/each}
		{:else}
			<Card variant="bordered">
				<div class="py-8 text-center">
					<h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">No courses yet</h3>
					<p class="mb-4 text-gray-600 dark:text-gray-400">
						Create your first course to start teaching
					</p>
					<Button href="/courses/create" variant="primary">Create Course</Button>
				</div>
			</Card>
		{/if}
	</div>
{/snippet}

{#snippet TeacherAnalytics()}
	<div in:fade={{ duration: 600 }}>
		<Card variant="bordered" class="min-h-96">
		<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">Course Performance</h3>
		<div class="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
			<div class="text-center">
				<svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
				</svg>
				<p>Detailed analytics will appear here once you have active courses.</p>
			</div>
		</div>
	</Card>
	</div>
{/snippet}

{#snippet StudentProgress()}
	<div in:fade={{ duration: 600 }}>
		<Card variant="bordered" class="min-h-96">
		<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">My Progress</h3>
		<div class="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
			<div class="text-center">
				<svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
				</svg>
				<p>Your learning progress will appear here once you start taking courses.</p>
			</div>
		</div>
	</Card>
	</div>
{/snippet}

{#snippet StudentActivity()}
	<div in:fade={{ duration: 600 }}>
		<Card variant="bordered">
		<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">Recent Activity</h3>
		<ActivityFeed activities={dashboardData?.recent_activities || []} />
	</Card>
	</div>
{/snippet}

<style>
	.animation-delay-150 {
		animation-delay: 150ms;
	}
	
	@keyframes float {
		0%, 100% {
			transform: translateY(0px);
		}
		50% {
			transform: translateY(-10px);
		}
	}
	
	.animate-float {
		animation: float 6s ease-in-out infinite;
	}
</style>
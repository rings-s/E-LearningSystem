<!-- front/src/routes/(app)/my-courses/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { coursesApi } from '$lib/apis/courses.js';
	import { t } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { classNames } from '$lib/utils/helpers.js';
	
	// Components
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Input from '$lib/components/common/Input.svelte';

	let enrollments = $state([]);
	let loading = $state(true);
	let searchQuery = $state('');
	let activeFilter = $state('all');

	// Filtered enrollments based on search and filter
	let filteredEnrollments = $derived(() => {
		let filtered = enrollments;
		
		// Apply status filter
		if (activeFilter !== 'all') {
			filtered = filtered.filter(e => e.status === activeFilter);
		}
		
		// Apply search filter
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(e => 
				e.course.title.toLowerCase().includes(query) ||
				e.course.instructor_name?.toLowerCase().includes(query) ||
				e.course.category?.name?.toLowerCase().includes(query)
			);
		}
		
		return filtered;
	});

	// Statistics for the overview cards
	let stats = $derived(() => {
		const total = enrollments.length;
		const completed = enrollments.filter(e => e.status === 'completed').length;
		const inProgress = enrollments.filter(e => e.status === 'in_progress').length;
		const avgProgress = total > 0 
			? Math.round(enrollments.reduce((sum, e) => sum + (e.progress_percentage || 0), 0) / total)
			: 0;
			
		return { total, completed, inProgress, avgProgress };
	});

	// Filter options
	const filterOptions = [
		{ id: 'all', label: 'All Courses', icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z' },
		{ id: 'in_progress', label: 'In Progress', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
		{ id: 'completed', label: 'Completed', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
		{ id: 'enrolled', label: 'Recently Enrolled', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' }
	];

	onMount(async () => {
		await fetchEnrollments();
	});

	const fetchEnrollments = async () => {
		try {
			const response = await coursesApi.getMyEnrollments();
			enrollments = response.results || response;
		} catch (error) {
			console.error('Failed to fetch enrollments:', error);
		} finally {
			loading = false;
		}
	};

	const getStatusConfig = (status) => {
		const configs = {
			enrolled: { color: 'info', label: 'Enrolled', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
			in_progress: { color: 'warning', label: 'In Progress', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
			completed: { color: 'success', label: 'Completed', bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
			dropped: { color: 'danger', label: 'Dropped', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' }
		};
		return configs[status] || configs.enrolled;
	};

	const formatDate = (dateString) => {
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { 
			month: 'short', 
			day: 'numeric', 
			year: 'numeric' 
		});
	};

	const getProgressColor = (progress) => {
		if (progress >= 80) return 'success';
		if (progress >= 50) return 'warning';
		return 'info';
	};
</script>

<svelte:head>
	<title>My Courses - 244SCHOOL</title>
	<meta name="description" content="Track your learning progress and continue your educational journey with 244SCHOOL" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
	<!-- Hero Section -->
	<div class="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600 text-white" in:fade={{ duration: 800 }}>
		<!-- Background Pattern -->
		<div class="absolute inset-0 opacity-10">
			<div class="h-full w-full bg-white bg-opacity-5" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0); background-size: 40px 40px;"></div>
		</div>
		
		<div class="container relative mx-auto px-4 py-16">
			<div class="mx-auto max-w-4xl">
				<div in:fly={{ y: 30, delay: 200, duration: 800 }}>
					<h1 class="mb-4 text-4xl font-bold leading-tight lg:text-5xl">
						My Learning Journey
					</h1>
					<p class="mb-8 text-xl leading-relaxed text-white/90">
						Track your progress, continue where you left off, and achieve your educational goals
					</p>
				</div>

				<!-- Quick Stats -->
				{#if !loading}
					<div class="grid grid-cols-2 gap-4 md:grid-cols-4" in:fly={{ y: 30, delay: 400, duration: 800 }}>
						<div class="rounded-xl bg-white/10 p-4 backdrop-blur-sm">
							<div class="text-2xl font-bold">{stats.total}</div>
							<div class="text-sm text-white/80">Total Courses</div>
						</div>
						<div class="rounded-xl bg-white/10 p-4 backdrop-blur-sm">
							<div class="text-2xl font-bold">{stats.completed}</div>
							<div class="text-sm text-white/80">Completed</div>
						</div>
						<div class="rounded-xl bg-white/10 p-4 backdrop-blur-sm">
							<div class="text-2xl font-bold">{stats.inProgress}</div>
							<div class="text-sm text-white/80">In Progress</div>
						</div>
						<div class="rounded-xl bg-white/10 p-4 backdrop-blur-sm">
							<div class="text-2xl font-bold">{stats.avgProgress}%</div>
							<div class="text-sm text-white/80">Avg Progress</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="container mx-auto px-4 py-12">
		<!-- Controls Section -->
		<div class="mb-8" in:fly={{ y: 20, delay: 600, duration: 600 }}>
			<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-lg dark:bg-gray-800/95">
				<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
					<!-- Search -->
					<div class="flex-1 lg:max-w-md">
						<Input
							type="search"
							placeholder="Search your courses..."
							bind:value={searchQuery}
							class="h-12"
							icon="<path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' />"
						/>
					</div>

					<!-- Filter Tabs -->
					<div class="flex overflow-x-auto">
						<div class="flex space-x-1 rounded-xl bg-gray-100 p-1 dark:bg-gray-800">
							{#each filterOptions as filter}
								<button
									onclick={() => activeFilter = filter.id}
									class={classNames(
										"flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all whitespace-nowrap",
										activeFilter === filter.id
											? "bg-white text-primary-600 shadow-sm dark:bg-gray-700 dark:text-primary-400"
											: "text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
									)}
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={filter.icon} />
									</svg>
									{filter.label}
									{#if filter.id === 'all'}
										<span class="ml-1 rounded-full bg-gray-200 px-2 py-0.5 text-xs dark:bg-gray-600">
											{stats.total}
										</span>
									{:else if filter.id === 'in_progress'}
										<span class="ml-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-800 dark:bg-amber-900/20 dark:text-amber-400">
											{stats.inProgress}
										</span>
									{:else if filter.id === 'completed'}
										<span class="ml-1 rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-800 dark:bg-green-900/20 dark:text-green-400">
											{stats.completed}
										</span>
									{/if}
								</button>
							{/each}
						</div>
					</div>

					<!-- Browse More Button -->
					<div class="flex-shrink-0">
						<Button href="/courses" variant="primary" size="medium">
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Browse More Courses
						</Button>
					</div>
				</div>
			</Card>
		</div>

		<!-- Content Section -->
		{#if loading}
			<!-- Loading State -->
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each Array(6) as _, index}
					<div class="animate-pulse" in:fly={{ y: 20, delay: index * 100, duration: 400 }}>
						<Card variant="bordered">
							<div class="space-y-4">
								<div class="h-48 rounded-xl bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600"></div>
								<div class="space-y-3">
									<div class="h-6 w-3/4 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
									<div class="h-4 w-1/2 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
									<div class="h-4 w-2/3 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
								</div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{:else if enrollments.length === 0}
			<!-- Empty State -->
			<div in:fade={{ duration: 500 }}>
				<Card variant="bordered" class="py-20 text-center shadow-lg">
					<div in:scale={{ duration: 600, start: 0.8 }}>
						<svg class="mx-auto mb-6 h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
						</svg>
						<h3 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">Start Your Learning Journey</h3>
						<p class="mx-auto mb-8 max-w-md text-lg text-gray-600 dark:text-gray-400">
							Discover thousands of courses from world-class instructors and begin building your skills today.
						</p>
						<Button href="/courses" variant="primary" size="large" class="transition-all hover:scale-105">
							<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							Explore Courses
						</Button>
					</div>
				</Card>
			</div>
		{:else if filteredEnrollments.length === 0}
			<!-- No Results State -->
			<div in:fade={{ duration: 500 }}>
				<Card variant="bordered" class="py-16 text-center">
					<svg class="mx-auto mb-6 h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">No courses found</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">
						{searchQuery ? `No courses match "${searchQuery}"` : `No ${activeFilter.replace('_', ' ')} courses found`}
					</p>
					<Button onclick={() => { searchQuery = ''; activeFilter = 'all'; }} variant="outline">
						Clear Filters
					</Button>
				</Card>
			</div>
		{:else}
			<!-- Courses Grid -->
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each filteredEnrollments as enrollment, index}
					{@const statusConfig = getStatusConfig(enrollment.status)}
					<div in:fly={{ y: 30, delay: index * 100, duration: 600 }}>
						<Card variant="bordered" hoverable class="group h-full overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
							<!-- Course Thumbnail -->
							<div class="relative -m-6 mb-6">
								{#if enrollment.course.thumbnail}
									<img
										src={enrollment.course.thumbnail}
										alt={enrollment.course.title}
										class="h-48 w-full object-cover transition-transform duration-300 group-hover:scale-105"
									/>
								{:else}
									<div class="h-48 w-full bg-gradient-to-br from-primary-400 to-primary-600 transition-all duration-300 group-hover:from-primary-500 group-hover:to-primary-700"></div>
								{/if}

								<!-- Status Badge -->
								<div class="absolute top-3 left-3">
									<Badge variant={statusConfig.color} class="shadow-lg backdrop-blur-sm">
										<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											{#if enrollment.status === 'completed'}
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
											{:else if enrollment.status === 'in_progress'}
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
											{:else}
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
											{/if}
										</svg>
										{statusConfig.label}
									</Badge>
								</div>

								<!-- Progress Badge -->
								{#if enrollment.progress_percentage > 0}
									<div class="absolute top-3 right-3">
										<div class="rounded-full bg-black/20 px-3 py-1 text-sm font-medium text-white backdrop-blur-sm">
											{Math.round(enrollment.progress_percentage)}%
										</div>
									</div>
								{/if}
							</div>

							<!-- Course Content -->
							<div class="flex flex-1 flex-col space-y-4">
								<!-- Course Title -->
								<h3 class="text-lg font-bold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2">
									{enrollment.course.title}
								</h3>

								<!-- Course Meta -->
								<div class="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
									<div class="flex items-center gap-1">
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
										</svg>
										<span>{enrollment.course.instructor_name}</span>
									</div>
									{#if enrollment.course.level}
										<Badge variant="outline" size="small">
											{enrollment.course.level}
										</Badge>
									{/if}
								</div>

								<!-- Progress Section -->
								<div class="space-y-3">
									<div>
										<div class="mb-2 flex items-center justify-between text-sm">
											<span class="font-medium text-gray-700 dark:text-gray-300">Progress</span>
											<span class="font-semibold text-gray-900 dark:text-white">
												{Math.round(enrollment.progress_percentage || 0)}%
											</span>
										</div>
										<CourseProgress 
											progress={enrollment.progress_percentage || 0} 
											variant={getProgressColor(enrollment.progress_percentage || 0)}
											size="medium"
										/>
									</div>
								</div>

								<!-- Enrollment Info -->
								<div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
									<span>Enrolled {formatDate(enrollment.enrolled_at)}</span>
									{#if enrollment.last_accessed}
										<span>Last accessed {formatDate(enrollment.last_accessed)}</span>
									{/if}
								</div>

								<!-- Action Buttons -->
								<div class="mt-auto space-y-2">
									<Button 
										href={`/courses/${enrollment.course.uuid}/learn`} 
										variant="primary" 
										fullWidth
										size="medium"
										class="transition-all hover:scale-[1.02]"
									>
										{enrollment.status === 'completed' ? 'Review Course' : 'Continue Learning'}
									</Button>
									
									<div class="flex gap-2">
										<Button 
											href={`/courses/${enrollment.course.uuid}`} 
											variant="outline" 
											size="small"
											class="flex-1"
										>
											<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											Details
										</Button>
										
										<Button 
											href={`/my-courses/${enrollment.course.uuid}/notes`} 
											variant="outline" 
											size="small"
											class="flex-1"
										>
											<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
											</svg>
											Notes
										</Button>
									</div>
								</div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
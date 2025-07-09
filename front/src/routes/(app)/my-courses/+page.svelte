<!-- front/src/routes/(app)/my-courses/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { classNames, debounce } from '$lib/utils/helpers.js';
	
	// Components
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Input from '$lib/components/common/Input.svelte';

	let courses = $state([]);
	let loading = $state(true);
	let searchQuery = $state('');
	let activeFilter = $state('all');
	let viewMode = $state('grid');
	let sortBy = $state('recent');
	let error = $state(null);

	// Convert reactive statements to derived runes
	const userRole = $derived($currentUser?.role || 'student');
	const isTeacher = $derived(userRole === 'teacher');

	// Debounced search function
	const debouncedSearch = debounce((query) => {
		searchQuery = query;
	}, 300);

	// Convert filtered courses to derived
	const filteredCourses = $derived((() => {
		try {
			let filtered = [...courses];

			// Apply status filter
			if (activeFilter !== 'all') {
				if (isTeacher) {
					filtered = filtered.filter(c => c.status === activeFilter);
				} else {
					filtered = filtered.filter(c => c.enrollment?.status === activeFilter);
				}
			}
			
			// Apply search filter
			if (searchQuery.trim()) {
				const query = searchQuery.toLowerCase();
				filtered = filtered.filter(c => {
					const title = c.title?.toLowerCase() || '';
					const instructor = c.instructor_name?.toLowerCase() || '';
					const category = c.category_name?.toLowerCase() || '';
					return title.includes(query) || instructor.includes(query) || category.includes(query);
				});
			}

			// Apply sorting
			filtered.sort((a, b) => {
				switch (sortBy) {
					case 'title':
						return a.title.localeCompare(b.title);
					case 'progress':
						if (isTeacher) return 0;
						return (b.enrollment?.progress_percentage || 0) - (a.enrollment?.progress_percentage || 0);
					case 'status':
						if (isTeacher) return a.status.localeCompare(b.status);
						return (a.enrollment?.status || '').localeCompare(b.enrollment?.status || '');
					case 'recent':
					default:
						const aDate = isTeacher ? a.updated_at : a.enrollment?.enrolled_at;
						const bDate = isTeacher ? b.updated_at : b.enrollment?.enrolled_at;
						return new Date(bDate || 0) - new Date(aDate || 0);
				}
			});
			
			return filtered;
		} catch (err) {
			console.error('Error filtering courses:', err);
			return [];
		}
	})());

	// Convert stats to derived
	const stats = $derived((() => {
		try {
			if (isTeacher) {
				const total = courses.length;
				const published = courses.filter(c => c.status === 'published').length;
				const draft = courses.filter(c => c.status === 'draft').length;
				const totalStudents = courses.reduce((sum, c) => sum + (c.enrolled_students_count || 0), 0);
				
				return { total, published, draft, totalStudents };
			} else {
				const total = courses.length;
				const completed = courses.filter(c => c.enrollment?.status === 'completed').length;
				const inProgress = courses.filter(c => c.enrollment?.status === 'in_progress').length;
				const avgProgress = total > 0 
					? Math.round(courses.reduce((sum, c) => sum + (c.enrollment?.progress_percentage || 0), 0) / total)
					: 0;
					
				return { total, completed, inProgress, avgProgress };
			}
		} catch (err) {
			console.error('Error calculating stats:', err);
			return { total: 0, completed: 0, inProgress: 0, avgProgress: 0 };
		}
	})());

	// Convert filter options to derived
	const filterOptions = $derived((() => {
		if (isTeacher) {
			return [
				{ id: 'all', label: 'All Courses', icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z' },
				{ id: 'published', label: 'Published', icon: 'M5 13l4 4L19 7' },
				{ id: 'draft', label: 'Drafts', icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z' },
				{ id: 'archived', label: 'Archived', icon: 'M5 8l6 6M5 8l6 6m0-6L5 8' }
			];
		} else {
			return [
				{ id: 'all', label: 'All Courses', icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z' },
				{ id: 'in_progress', label: 'In Progress', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
				{ id: 'completed', label: 'Completed', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
				{ id: 'enrolled', label: 'Recently Enrolled', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' }
			];
		}
	})());

	// Convert sort options to derived
	const sortOptions = $derived([
		{ id: 'recent', label: isTeacher ? 'Recently Updated' : 'Recently Enrolled' },
		{ id: 'title', label: 'Title (A-Z)' },
		...(isTeacher ? [] : [{ id: 'progress', label: 'Progress' }]),
		{ id: 'status', label: 'Status' }
	]);

	onMount(async () => {
		await fetchCourses();
	});

	// Fixed: This should be fetchCourses (plural), not fetchCourse (singular)
	const fetchCourses = async () => {
		loading = true;
		error = null;
		
		try {
			console.log('Fetching courses for user:', $currentUser);
			console.log('Is teacher:', isTeacher);
			
			if (isTeacher) {
				// For teachers, get courses they created
				const response = await coursesApi.getMyCourses();
				console.log('Teacher courses response:', response);
				courses = Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : [];
			} else {
				// For students, get their enrollments
				const enrollments = await coursesApi.getMyEnrollments();
				console.log('Student enrollments response:', enrollments);
				courses = Array.isArray(enrollments) ? enrollments.map(e => ({
					...e.course,
					enrollment: e
				})) : [];
			}
			console.log('Final courses:', courses);
		} catch (err) {
			console.error('Failed to fetch courses:', err);
			error = err.message || 'Failed to load courses';
			courses = [];
			
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: 'Failed to load courses. Please try again.'
			});
		} finally {
			loading = false;
		}
	};

	const handleSearchInput = (event) => {
		debouncedSearch(event.target.value);
	};

	const getStatusConfig = (status, isTeacherCourse = false) => {
		if (isTeacherCourse) {
			const configs = {
				published: { color: 'success', label: 'Published', bg: 'bg-green-50', text: 'text-green-700' },
				draft: { color: 'warning', label: 'Draft', bg: 'bg-amber-50', text: 'text-amber-700' },
				archived: { color: 'gray', label: 'Archived', bg: 'bg-gray-50', text: 'text-gray-700' }
			};
			return configs[status] || configs.draft;
		} else {
			const configs = {
				enrolled: { color: 'info', label: 'Enrolled', bg: 'bg-blue-50', text: 'text-blue-700' },
				in_progress: { color: 'warning', label: 'In Progress', bg: 'bg-amber-50', text: 'text-amber-700' },
				completed: { color: 'success', label: 'Completed', bg: 'bg-green-50', text: 'text-green-700' },
				dropped: { color: 'danger', label: 'Dropped', bg: 'bg-red-50', text: 'text-red-700' }
			};
			return configs[status] || configs.enrolled;
		}
	};

	const getProgressColor = (progress) => {
		if (progress >= 80) return 'success';
		if (progress >= 50) return 'warning';
		return 'info';
	};

	const formatDate = (dateString) => {
		if (!dateString) return 'N/A';
		return formatters.date(dateString);
	};

	const getCourseActionUrl = (course) => {
		if (isTeacher) {
			return `/teacher/courses/${course.uuid}/manage`;
		} else {
			return `/courses/${course.uuid}/learn`;
		}
	};

	const getCourseActionLabel = (course) => {
		if (isTeacher) {
			return course.status === 'published' ? 'Manage Course' : 'Edit Course';
		} else {
			return course.enrollment?.status === 'completed' ? 'Review Course' : 'Continue Learning';
		}
	};
</script>

<svelte:head>
	<title>{isTeacher ? 'My Courses - Teaching' : 'My Courses - Learning'} - 244SCHOOL</title>
	<meta name="description" content={isTeacher ? 'Manage your courses and track student progress' : 'Track your learning progress and continue your educational journey'} />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
	<!-- Enhanced Hero Section with Fixed Animated Background -->
	<div class="relative overflow-hidden" in:fade={{ duration: 800 }}>
		<!-- Fixed Animated Background -->
		<div class="absolute inset-0 bg-gradient-to-br from-blue-600 via-blue-700 to-purple-600">
			<!-- Animated geometric pattern -->
			<div class="absolute inset-0 opacity-10">
				<svg class="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
					<defs>
						<pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
							<path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/>
						</pattern>
					</defs>
					<rect width="100%" height="100%" fill="url(#grid)" />
				</svg>
			</div>
			
			<!-- Floating geometric shapes -->
			<div class="absolute inset-0 overflow-hidden">
				{#each Array(6) as _, i}
					<div 
						class="absolute rounded-full bg-white/5 animate-float-gentle"
						style="
							width: {20 + Math.random() * 40}px; 
							height: {20 + Math.random() * 40}px;
							left: {Math.random() * 100}%;
							top: {Math.random() * 100}%;
							animation-delay: {i * 0.8}s;
							animation-duration: {8 + Math.random() * 4}s;
						"
					></div>
				{/each}
			</div>

			<!-- Gradient overlay -->
			<div class="absolute inset-0 bg-gradient-to-r from-black/20 via-transparent to-black/20"></div>
		</div>
		
		<div class="container relative mx-auto px-4 py-20">
			<div class="mx-auto max-w-4xl text-center text-white">
				<div in:fly={{ y: 30, delay: 200, duration: 800 }}>
					<div class="mb-4 inline-flex items-center rounded-full bg-white/10 px-6 py-2 backdrop-blur-sm">
						<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={isTeacher ? "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" : "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"} />
						</svg>
						<span class="text-sm font-medium">{isTeacher ? 'Teaching Dashboard' : 'Learning Dashboard'}</span>
					</div>
					
					<h1 class="mb-6 text-5xl font-bold leading-tight lg:text-6xl">
						{isTeacher ? 'My Teaching Hub' : 'My Learning Journey'}
					</h1>
					<p class="mb-8 text-xl leading-relaxed text-white/90">
						{isTeacher 
							? 'Create, manage, and track your courses. Empower students with quality education.'
							: 'Track your progress, continue where you left off, and achieve your educational goals.'
						}
					</p>
				</div>

				<!-- Enhanced Quick Stats -->
				{#if !loading && !error}
					<div class="grid grid-cols-2 gap-6 md:grid-cols-4" in:fly={{ y: 30, delay: 400, duration: 800 }}>
						<div class="group rounded-2xl bg-white/10 p-6 backdrop-blur-sm transition-all hover:bg-white/15 hover:scale-105">
							<div class="text-3xl font-bold">{stats.total}</div>
							<div class="text-sm text-white/80">{isTeacher ? 'Total Courses' : 'Enrolled Courses'}</div>
						</div>
						<div class="group rounded-2xl bg-white/10 p-6 backdrop-blur-sm transition-all hover:bg-white/15 hover:scale-105">
							<div class="text-3xl font-bold">{isTeacher ? stats.published : stats.completed}</div>
							<div class="text-sm text-white/80">{isTeacher ? 'Published' : 'Completed'}</div>
						</div>
						<div class="group rounded-2xl bg-white/10 p-6 backdrop-blur-sm transition-all hover:bg-white/15 hover:scale-105">
							<div class="text-3xl font-bold">{isTeacher ? stats.draft : stats.inProgress}</div>
							<div class="text-sm text-white/80">{isTeacher ? 'Drafts' : 'In Progress'}</div>
						</div>
						<div class="group rounded-2xl bg-white/10 p-6 backdrop-blur-sm transition-all hover:bg-white/15 hover:scale-105">
							<div class="text-3xl font-bold">{isTeacher ? stats.totalStudents : `${stats.avgProgress}%`}</div>
							<div class="text-sm text-white/80">{isTeacher ? 'Total Students' : 'Avg Progress'}</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="container mx-auto px-4 py-12">
		<!-- Enhanced Controls Section -->
		<div class="mb-8" in:fly={{ y: 20, delay: 600, duration: 600 }}>
			<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-xl dark:bg-gray-800/95">
				<div class="space-y-6">
					<!-- Top Row: Search and Actions -->
					<div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
						<div class="flex-1 lg:max-w-md">
							<Input
								type="search"
								placeholder={`Search ${isTeacher ? 'your courses' : 'enrolled courses'}...`}
								value={searchQuery}
								oninput={handleSearchInput}
								class="h-12"
								icon="<path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' />"
							/>
						</div>

						<div class="flex items-center gap-3">
							<!-- View Mode Toggle -->
							<div class="flex rounded-lg bg-gray-100 p-1 dark:bg-gray-800">
								<button
									onclick={() => viewMode = 'grid'}
									aria-label="Switch to grid view"
									class={classNames(
										"rounded-md px-3 py-2 text-sm font-medium transition-all",
										viewMode === 'grid'
											? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white"
											: "text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
									)}
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
									</svg>
								</button>
								<button
									onclick={() => viewMode = 'list'}
									aria-label="Switch to list view"
									class={classNames(
										"rounded-md px-3 py-2 text-sm font-medium transition-all",
										viewMode === 'list'
											? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white"
											: "text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
									)}
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
									</svg>
								</button>
							</div>

							<!-- Sort Dropdown -->
							<select 
								bind:value={sortBy}
								class="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							>
								{#each sortOptions as option}
									<option value={option.id}>{option.label}</option>
								{/each}
							</select>

							<!-- Create/Browse Button -->
							<Button 
								href={isTeacher ? "/courses/create" : "/courses"} 
								variant="primary" 
								size="medium"
								class="whitespace-nowrap"
							>
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
								</svg>
								{isTeacher ? 'Create Course' : 'Browse Courses'}
							</Button>
						</div>
					</div>

					<!-- Filter Tabs -->
					<div class="flex overflow-x-auto">
						<div class="flex space-x-1 rounded-xl bg-gray-100 p-1 dark:bg-gray-800">
							{#each filterOptions as filter}
								{@const count = filter.id === 'all' ? stats.total : 
								 filter.id === 'published' || filter.id === 'completed' ? (isTeacher ? stats.published : stats.completed) :
								 filter.id === 'draft' || filter.id === 'in_progress' ? (isTeacher ? stats.draft : stats.inProgress) : 0}
								<button
									onclick={() => activeFilter = filter.id}
									class={classNames(
										"flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all whitespace-nowrap",
										activeFilter === filter.id
											? "bg-white text-blue-600 shadow-sm dark:bg-gray-700 dark:text-blue-400"
											: "text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
									)}
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={filter.icon} />
									</svg>
									{filter.label}
									<span class={classNames(
										"ml-1 rounded-full px-2 py-0.5 text-xs",
										activeFilter === filter.id 
											? "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
											: "bg-gray-200 dark:bg-gray-600"
									)}>
										{count}
									</span>
								</button>
							{/each}
						</div>
					</div>
				</div>
			</Card>
		</div>

		<!-- Error State -->
		{#if error}
			<div in:fade={{ duration: 500 }}>
				<Card variant="bordered" class="py-16 text-center shadow-xl">
					<div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/20">
						<svg class="h-8 w-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
					<h3 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">Error Loading Courses</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
					<Button onclick={fetchCourses} variant="primary">
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
						Retry
					</Button>
				</Card>
			</div>
		{:else if loading}
			<!-- Enhanced Loading State -->
			<div class={classNames(
				"grid gap-6",
				viewMode === 'grid' ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" : "grid-cols-1"
			)}>
				{#each Array(6) as _, index}
					<div class="animate-pulse" in:fly={{ y: 20, delay: index * 100, duration: 400 }}>
						<Card variant="bordered" class="overflow-hidden">
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
		{:else if !loading && courses.length === 0}
			<!-- Enhanced Empty State -->
			<div in:fade={{ duration: 500 }}>
				<Card variant="bordered" class="py-20 text-center shadow-xl">
					<div in:scale={{ duration: 600, start: 0.8 }}>
						<div class="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-900 dark:to-blue-800">
							<svg class="h-12 w-12 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={isTeacher ? "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" : "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"} />
							</svg>
						</div>
						<h3 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
							{isTeacher ? 'Start Teaching Today' : 'Start Your Learning Journey'}
						</h3>
						<p class="mx-auto mb-8 max-w-md text-lg text-gray-600 dark:text-gray-400">
							{isTeacher 
								? 'Create your first course and share your knowledge with students around the world.'
								: 'Discover thousands of courses from world-class instructors and begin building your skills today.'
							}
						</p>
						<div class="flex flex-col gap-4 sm:flex-row sm:justify-center">
							<Button 
								href={isTeacher ? "/courses/create" : "/courses"} 
								variant="primary" 
								size="large" 
								class="transition-all hover:scale-105"
							>
								<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
								</svg>
								{isTeacher ? 'Create First Course' : 'Explore Courses'}
							</Button>
							<Button onclick={fetchCourses} variant="outline" size="large">
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
								</svg>
								Refresh
							</Button>
						</div>
					</div>
				</Card>
			</div>
		{:else if filteredCourses.length === 0}
			<!-- No Results State -->
			<div in:fade={{ duration: 500 }}>
				<Card variant="bordered" class="py-16 text-center">
					<div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
						<svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
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
			<!-- Enhanced Courses Display -->
			<div class={classNames(
				"grid gap-6",
				viewMode === 'grid' ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" : "grid-cols-1"
			)}>
				{#each filteredCourses as course, index}
					{@const statusConfig = getStatusConfig(
						isTeacher ? course.status : course.enrollment?.status,
						isTeacher
					)}
					<div in:fly={{ y: 30, delay: index * 100, duration: 600 }}>
						<Card 
							variant="bordered" 
							hoverable 
							class={classNames(
								"group h-full overflow-hidden transition-all duration-300 hover:shadow-2xl hover:-translate-y-2",
								viewMode === 'list' && "flex flex-row"
							)}
						>
							<!-- Course Thumbnail -->
							<div class={classNames(
								"relative",
								viewMode === 'grid' ? "-m-6 mb-6" : "w-64 flex-shrink-0 -m-6 mr-6"
							)}>
								{#if course.thumbnail}
									<img
										src={course.thumbnail}
										alt={course.title}
										class={classNames(
											"object-cover transition-transform duration-300 group-hover:scale-105",
											viewMode === 'grid' ? "h-48 w-full" : "h-full w-full"
										)}
									/>
								{:else}
									<div class={classNames(
										"bg-gradient-to-br from-blue-400 to-blue-600 transition-all duration-300 group-hover:from-blue-500 group-hover:to-blue-700",
										viewMode === 'grid' ? "h-48 w-full" : "h-full w-full"
									)}>
										<div class="flex h-full items-center justify-center">
											<svg class="h-16 w-16 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
											</svg>
										</div>
									</div>
								{/if}

								<!-- Status Badge -->
								<div class="absolute top-3 left-3">
									<Badge variant={statusConfig.color} class="shadow-lg backdrop-blur-sm">
										<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											{#if statusConfig.label === 'Completed' || statusConfig.label === 'Published'}
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
											{:else if statusConfig.label === 'In Progress'}
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
											{:else}
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
											{/if}
										</svg>
										{statusConfig.label}
									</Badge>
								</div>

								<!-- Progress/Stats Badge -->
								{#if isTeacher}
									<div class="absolute top-3 right-3">
										<div class="rounded-full bg-black/20 px-3 py-1 text-sm font-medium text-white backdrop-blur-sm">
											{course.enrolled_students_count || 0} students
										</div>
									</div>
								{:else if course.enrollment?.progress_percentage > 0}
									<div class="absolute top-3 right-3">
										<div class="rounded-full bg-black/20 px-3 py-1 text-sm font-medium text-white backdrop-blur-sm">
											{Math.round(course.enrollment.progress_percentage)}%
										</div>
									</div>
								{/if}
							</div>

							<!-- Course Content -->
							<div class="flex flex-1 flex-col space-y-4 p-6">
								<!-- Course Title -->
								<h3 class="text-lg font-bold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
									{course.title}
								</h3>

								<!-- Course Meta -->
								<div class="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
									<div class="flex items-center gap-1">
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
										</svg>
										<span>{isTeacher ? 'You' : (course.instructor_name || 'Unknown Instructor')}</span>
									</div>
									{#if course.level}
										<Badge variant="outline" size="small">
											{course.level}
										</Badge>
									{/if}
									{#if course.category_name}
										<Badge variant="outline" size="small">
											{course.category_name}
										</Badge>
									{/if}
								</div>

								<!-- Progress Section (Students only) -->
								{#if !isTeacher}
									<div class="space-y-3">
										<div>
											<div class="mb-2 flex items-center justify-between text-sm">
												<span class="font-medium text-gray-700 dark:text-gray-300">Progress</span>
												<span class="font-semibold text-gray-900 dark:text-white">
													{Math.round(course.enrollment?.progress_percentage || 0)}%
												</span>
											</div>
											<CourseProgress 
												progress={course.enrollment?.progress_percentage || 0} 
												variant={getProgressColor(course.enrollment?.progress_percentage || 0)}
												size="medium"
											/>
										</div>
									</div>
								{/if}

								<!-- Teacher Analytics -->
								{#if isTeacher}
									<div class="grid grid-cols-3 gap-4 text-center text-sm">
										<div>
											<div class="font-semibold text-gray-900 dark:text-white">{course.enrolled_students_count || 0}</div>
											<div class="text-gray-500">Students</div>
										</div>
										<div>
											<div class="font-semibold text-gray-900 dark:text-white">{course.average_rating?.toFixed(1) || '0.0'}</div>
											<div class="text-gray-500">Rating</div>
										</div>
										<div>
											<div class="font-semibold text-gray-900 dark:text-white">{formatDate(course.updated_at)}</div>
											<div class="text-gray-500">Updated</div>
										</div>
									</div>
								{:else}
									<!-- Enrollment Info -->
									<div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
										<span>Enrolled {formatDate(course.enrollment?.enrolled_at)}</span>
										{#if course.enrollment?.last_accessed}
											<span>Last accessed {formatDate(course.enrollment.last_accessed)}</span>
										{/if}
									</div>
								{/if}

								<!-- Action Buttons -->
								<div class="mt-auto space-y-2">
									<Button 
										href={getCourseActionUrl(course)} 
										variant="primary" 
										fullWidth
										size="medium"
										class="transition-all hover:scale-[1.02]"
									>
										{getCourseActionLabel(course)}
									</Button>
									
									<div class="flex gap-2">
										<Button 
											href={`/courses/${course.uuid}`} 
											variant="outline" 
											size="small"
											class="flex-1"
										>
											<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											Details
										</Button>
										
										{#if !isTeacher}
											<Button 
												href={`/my-courses/${course.uuid}/notes`} 
												variant="outline" 
												size="small"
												class="flex-1"
											>
												<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
												</svg>
												Notes
											</Button>
										{:else}
											<Button 
												href={`/teacher/courses/${course.uuid}/analytics`} 
												variant="outline" 
												size="small"
												class="flex-1"
											>
												<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
												</svg>
												Analytics
											</Button>
										{/if}
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

<style>
	@keyframes float-gentle {
		0%, 100% {
			transform: translateY(0px) rotate(0deg);
		}
		33% {
			transform: translateY(-20px) rotate(1deg);
		}
		66% {
			transform: translateY(-10px) rotate(-1deg);
		}
	}

	.animate-float-gentle {
		animation: float-gentle 8s ease-in-out infinite;
	}
</style>
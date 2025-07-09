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
	import Input from '$lib/components/common/Input.svelte';
	import CourseCard from '$lib/components/course/CourseCard.svelte';

	// State variables
	let courses = $state([]);
	let filteredCourses = $state([]);
	let loading = $state(true);
	let error = $state('');
	let searchQuery = $state('');
	let selectedStatus = $state('all');
	let sortBy = $state('updated');
	let sortOrder = $state('desc');

	// Pagination
	let currentPage = $state(1);
	let itemsPerPage = $state(12);
	let totalCourses = $state(0);

	// Filter options
	const statusOptions = [
		{ value: 'all', label: 'All Courses' },
		{ value: 'draft', label: 'Draft' },
		{ value: 'published', label: 'Published' },
		{ value: 'archived', label: 'Archived' }
	];

	const sortOptions = [
		{ value: 'updated', label: 'Last Updated' },
		{ value: 'created', label: 'Date Created' },
		{ value: 'title', label: 'Title' },
		{ value: 'students', label: 'Student Count' }
	];

	// Derived states
	let stats = $derived(() => {
		const published = courses.filter(c => c.status === 'published').length;
		const draft = courses.filter(c => c.status === 'draft').length;
		const totalStudents = courses.reduce((sum, c) => sum + (c.enrollment_count || 0), 0);
		const avgRating = courses.length > 0 ? 
			courses.reduce((sum, c) => sum + (c.average_rating || 0), 0) / courses.length : 0;
		
		return {
			total: courses.length,
			published,
			draft,
			totalStudents,
			avgRating
		};
	});

	let paginatedCourses = $derived(() => {
		const start = (currentPage - 1) * itemsPerPage;
		const end = start + itemsPerPage;
		return filteredCourses.slice(start, end);
	});

	let totalPages = $derived(() => Math.ceil(filteredCourses.length / itemsPerPage));

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

		await loadCourses();
	});

	async function loadCourses() {
		loading = true;
		error = '';

		try {
			// For now, use the regular courses API and filter by instructor
			const response = await coursesApi.getCourses();
			const allCourses = response.results || response || [];
			
			// Filter courses by current user (teacher)
			courses = allCourses.filter(course => 
				course.instructor?.uuid === $currentUser.uuid
			);

			totalCourses = courses.length;
			applyFilters();

		} catch (err) {
			console.error('Failed to load courses:', err);
			error = err.message || 'Failed to load courses';
		} finally {
			loading = false;
		}
	}

	function applyFilters() {
		let filtered = [...courses];

		// Filter by status
		if (selectedStatus !== 'all') {
			filtered = filtered.filter(course => course.status === selectedStatus);
		}

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(course => 
				course.title.toLowerCase().includes(query) ||
				course.description?.toLowerCase().includes(query) ||
				course.short_description?.toLowerCase().includes(query)
			);
		}

		// Sort
		filtered.sort((a, b) => {
			let aValue, bValue;
			
			switch (sortBy) {
				case 'updated':
					aValue = new Date(a.updated_at || a.created_at);
					bValue = new Date(b.updated_at || b.created_at);
					break;
				case 'created':
					aValue = new Date(a.created_at);
					bValue = new Date(b.created_at);
					break;
				case 'title':
					aValue = a.title.toLowerCase();
					bValue = b.title.toLowerCase();
					break;
				case 'students':
					aValue = a.enrollment_count || 0;
					bValue = b.enrollment_count || 0;
					break;
				default:
					aValue = new Date(a.updated_at || a.created_at);
					bValue = new Date(b.updated_at || b.created_at);
			}

			if (sortOrder === 'asc') {
				return aValue > bValue ? 1 : -1;
			} else {
				return aValue < bValue ? 1 : -1;
			}
		});

		filteredCourses = filtered;
		currentPage = 1; // Reset to first page when filters change
	}

	function handleSearch() {
		applyFilters();
	}

	function handleFilterChange() {
		applyFilters();
	}

	function toggleSortOrder() {
		sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		applyFilters();
	}

	function goToPage(page) {
		if (page >= 1 && page <= totalPages) {
			currentPage = page;
		}
	}

	async function duplicateCourse(courseId) {
		try {
			// This would need to be implemented in the backend
			uiStore.showNotification({
				type: 'info',
				title: 'Feature Coming Soon',
				message: 'Course duplication will be available soon'
			});
		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: 'Duplication Failed',
				message: err.message || 'Failed to duplicate course'
			});
		}
	}

	async function deleteCourse(courseId) {
		if (!confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
			return;
		}

		try {
			await coursesApi.deleteCourse(courseId);
			courses = courses.filter(c => c.uuid !== courseId);
			applyFilters();

			uiStore.showNotification({
				type: 'success',
				title: 'Course Deleted',
				message: 'Course has been permanently deleted'
			});
		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: 'Delete Failed',
				message: err.message || 'Failed to delete course'
			});
		}
	}
</script>

<svelte:head>
	<title>My Courses | E-Learning Platform</title>
	<meta name="description" content="Manage your courses and track student progress" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="container mx-auto max-w-7xl px-4 py-8">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
				<div>
					<div class="flex items-center gap-4 mb-2">
						<Button
							href="/teacher/dashboard"
							variant="ghost"
							size="medium"
							class="text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
							</svg>
							Back to Dashboard
						</Button>
					</div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
						My Courses
					</h1>
					<p class="text-gray-600 dark:text-gray-400">
						Manage your courses and track student progress
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

			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
				<Card class="p-6">
					<div class="flex items-center">
						<div class="rounded-lg bg-blue-100 p-3 dark:bg-blue-900/30">
							<svg class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Courses</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
						</div>
					</div>
				</Card>

				<Card class="p-6">
					<div class="flex items-center">
						<div class="rounded-lg bg-green-100 p-3 dark:bg-green-900/30">
							<svg class="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">Published</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.published}</p>
						</div>
					</div>
				</Card>

				<Card class="p-6">
					<div class="flex items-center">
						<div class="rounded-lg bg-purple-100 p-3 dark:bg-purple-900/30">
							<svg class="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Students</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalStudents}</p>
						</div>
					</div>
				</Card>

				<Card class="p-6">
					<div class="flex items-center">
						<div class="rounded-lg bg-yellow-100 p-3 dark:bg-yellow-900/30">
							<svg class="h-6 w-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Rating</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.avgRating.toFixed(1)}</p>
						</div>
					</div>
				</Card>
			</div>
		</div>

		<!-- Filters and Search -->
		<Card class="p-6 mb-8" in:fly={{ y: 20, delay: 100, duration: 600 }}>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				<!-- Search -->
				<div class="lg:col-span-2">
					<Input
						label="Search Courses"
						placeholder="Search by title or description"
						bind:value={searchQuery}
						onchange={handleSearch}
						oninput={handleSearch}
					>
						<svg slot="icon" class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
					</Input>
				</div>

				<!-- Status Filter -->
				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						Filter by Status
					</label>
					<select
						bind:value={selectedStatus}
						onchange={handleFilterChange}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
					>
						{#each statusOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Sort -->
				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						Sort by
					</label>
					<div class="flex gap-2">
						<select
							bind:value={sortBy}
							onchange={handleFilterChange}
							class="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
						>
							{#each sortOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
						<Button
							onclick={toggleSortOrder}
							variant="outline"
							size="medium"
							class="px-3"
						>
							<svg 
								class="h-4 w-4 transform {sortOrder === 'desc' ? 'rotate-180' : ''}" 
								fill="none" 
								stroke="currentColor" 
								viewBox="0 0 24 24"
							>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
							</svg>
						</Button>
					</div>
				</div>
			</div>
		</Card>

		<!-- Error State -->
		{#if error}
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Error Loading Courses</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={loadCourses} variant="primary" size="medium">
					Try Again
				</Button>
			</div>
		{:else if loading}
			<!-- Loading State -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each Array(6) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="h-4 bg-gray-200 rounded w-3/4 mb-4 dark:bg-gray-700"></div>
							<div class="space-y-3">
								<div class="h-3 bg-gray-200 rounded w-full dark:bg-gray-700"></div>
								<div class="h-3 bg-gray-200 rounded w-2/3 dark:bg-gray-700"></div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{:else if filteredCourses.length === 0}
			<!-- Empty State -->
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
					{courses.length === 0 ? 'No Courses Yet' : 'No Courses Found'}
				</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">
					{courses.length === 0 
						? 'Start teaching by creating your first course' 
						: 'No courses match your search criteria'}
				</p>
				{#if courses.length === 0}
					<Button
						href="/teacher/courses/create"
						variant="primary"
						size="medium"
					>
						Create Your First Course
					</Button>
				{/if}
			</div>
		{:else}
			<!-- Courses Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8" in:fly={{ y: 20, delay: 200, duration: 600 }}>
				{#each paginatedCourses as course}
					<Card class="overflow-hidden hover:shadow-lg transition-shadow duration-300">
						<div class="aspect-video bg-gray-200 dark:bg-gray-700 relative">
							{#if course.thumbnail}
								<img 
									src={course.thumbnail} 
									alt={course.title}
									class="w-full h-full object-cover"
								/>
							{:else}
								<div class="w-full h-full flex items-center justify-center">
									<svg class="h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
									</svg>
								</div>
							{/if}
							<div class="absolute top-4 right-4">
								<Badge
									variant={course.status === 'published' ? 'success' : course.status === 'draft' ? 'warning' : 'secondary'}
									size="small"
								>
									{course.status}
								</Badge>
							</div>
						</div>

						<div class="p-6">
							<div class="mb-4">
								<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
									{course.title}
								</h3>
								<p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
									{course.short_description || course.description}
								</p>
							</div>

							<div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
								<div class="flex items-center">
									<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
									</svg>
									{course.enrollment_count || 0} students
								</div>
								<span>{formatters.relativeTime(course.updated_at || course.created_at)}</span>
							</div>

							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-2">
									<Button
										href="/teacher/courses/{course.uuid}/manage"
										variant="outline"
										size="small"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
										</svg>
										Edit
									</Button>
									<Button
										href="/teacher/courses/{course.uuid}/analytics"
										variant="outline"
										size="small"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
										</svg>
										Analytics
									</Button>
								</div>

								<div class="flex items-center space-x-1">
									<Button
										onclick={() => duplicateCourse(course.uuid)}
										variant="ghost"
										size="small"
										class="text-gray-400 hover:text-gray-600"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
										</svg>
									</Button>
									<Button
										onclick={() => deleteCourse(course.uuid)}
										variant="ghost"
										size="small"
										class="text-red-400 hover:text-red-600"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
										</svg>
									</Button>
								</div>
							</div>
						</div>
					</Card>
				{/each}
			</div>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-2">
						<Button
							onclick={() => goToPage(currentPage - 1)}
							disabled={currentPage === 1}
							variant="outline"
							size="small"
						>
							Previous
						</Button>
						
						{#each Array(Math.min(5, totalPages)) as _, i}
							{@const page = i + 1}
							<Button
								onclick={() => goToPage(page)}
								variant={currentPage === page ? 'primary' : 'outline'}
								size="small"
							>
								{page}
							</Button>
						{/each}
						
						<Button
							onclick={() => goToPage(currentPage + 1)}
							disabled={currentPage === totalPages}
							variant="outline"
							size="small"
						>
							Next
						</Button>
					</div>
					
					<p class="text-sm text-gray-500 dark:text-gray-400">
						Showing {Math.min((currentPage - 1) * itemsPerPage + 1, filteredCourses.length)} - {Math.min(currentPage * itemsPerPage, filteredCourses.length)} of {filteredCourses.length} courses
					</p>
				</div>
			{/if}
		{/if}
	</div>
</div>
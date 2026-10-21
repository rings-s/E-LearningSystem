<script>
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '#lib/apis/courses.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t, locale } from '#lib/i18n/index.js';
	import { formatters } from '#lib/utils/formatters.js';
	import { isTeacher } from '#lib/utils/helpers.js';

	// Components
	import CourseCover from '#lib/components/course/CourseCover.svelte';
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import Input from '#lib/components/common/Input.svelte';
	import CourseCard from '#lib/components/course/CourseCard.svelte';

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
	const statusOptions = $derived([
		{ value: 'all', label: $t('teacher.allCourses') },
		{ value: 'draft', label: $t('teacher.draft') },
		{ value: 'published', label: $t('teacher.published') },
		{ value: 'archived', label: $t('teacher.archived') }
	]);

	const sortOptions = $derived([
		{ value: 'updated', label: $t('teacher.lastUpdated') },
		{ value: 'created', label: $t('teacher.dateCreated') },
		{ value: 'title', label: $t('teacher.titleSort') },
		{ value: 'students', label: $t('teacher.studentCount') }
	]);

	// Derived states
	let stats = $derived.by(() => {
		const published = courses.filter((c) => c.status === 'published').length;
		const draft = courses.filter((c) => c.status === 'draft').length;
		const totalStudents = courses.reduce((sum, c) => sum + (c.enrollment_count || 0), 0);
		const avgRating =
			courses.length > 0
				? courses.reduce((sum, c) => sum + (c.average_rating || 0), 0) / courses.length
				: 0;

		return {
			total: courses.length,
			published,
			draft,
			totalStudents,
			avgRating
		};
	});

	let paginatedCourses = $derived.by(() => {
		const start = (currentPage - 1) * itemsPerPage;
		const end = start + itemsPerPage;
		return filteredCourses.slice(start, end);
	});

	let totalPages = $derived.by(() => Math.ceil(filteredCourses.length / itemsPerPage));

	onMount(async () => {
		// Check authorization
		if (!$currentUser) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: $t('teacher.mustLogin')
			});
			goto('/login');
			return;
		}

		if (!isTeacher($currentUser)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: $t('teacher.mustBeTeacherRole', { role: $currentUser?.role || '-' })
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
			console.log('🔍 [FRONTEND] Calling getTeacherCourses...');
			const response = await coursesApi.getTeacherCourses();

			console.log('📦 [FRONTEND] Raw API response:', response);
			console.log('📦 [FRONTEND] Response type:', typeof response);
			console.log('📦 [FRONTEND] Is array:', Array.isArray(response));
			console.log('📦 [FRONTEND] Response length:', response?.length);

			if (response && typeof response === 'object' && !Array.isArray(response)) {
				console.log('📦 [FRONTEND] Response keys:', Object.keys(response));
				if (response.results) {
					console.log('📦 [FRONTEND] Results array:', response.results);
					console.log('📦 [FRONTEND] Results length:', response.results.length);
				}
			}

			// Process the response more robustly
			if (Array.isArray(response)) {
				courses = response;
			} else if (response?.results && Array.isArray(response.results)) {
				courses = response.results;
			} else if (response?.data && Array.isArray(response.data)) {
				courses = response.data;
			} else if (response && typeof response === 'object') {
				// If we get a single course object, wrap it in an array
				courses = [response];
			} else {
				console.warn('📦 [FRONTEND] Unexpected response format, setting empty array');
				courses = [];
			}

			totalCourses = courses.length;

			console.log('✅ [FRONTEND] Final courses array:', courses);
			console.log('✅ [FRONTEND] Courses count:', totalCourses);

			applyFilters();
		} catch (err) {
			console.error('❌ [COURSES] Failed to load courses:', err);

			// Provide specific error messages based on error type
			if (err.message?.includes('403') || err.message?.includes('Forbidden')) {
				error = $t('teacher.mustBeTeacherContact');
			} else if (err.message?.includes('401') || err.message?.includes('Unauthorized')) {
				error = $t('teacher.sessionExpiredMsg');
			} else {
				error = err.message || $t('teacher.loadCoursesFailed');
			}
		} finally {
			loading = false;
		}
	}
	function applyFilters() {
		let filtered = [...courses];

		// Filter by status
		if (selectedStatus !== 'all') {
			filtered = filtered.filter((course) => course.status === selectedStatus);
		}

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(
				(course) =>
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
				title: $t('teacher.comingSoon'),
				message: $t('teacher.duplicationSoon')
			});
		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: $t('teacher.duplicationFailed'),
				message: err.message || $t('teacher.duplicationFailedMsg')
			});
		}
	}

	async function deleteCourse(courseId) {
		if (!confirm($t('teacher.deleteConfirm'))) {
			return;
		}

		try {
			await coursesApi.deleteCourse(courseId);
			courses = courses.filter((c) => c.uuid !== courseId);
			applyFilters();

			uiStore.showNotification({
				type: 'success',
				title: $t('teacher.courseDeleted'),
				message: $t('teacher.courseDeletedMsg')
			});
		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: $t('teacher.deleteFailed'),
				message: err.message || $t('teacher.deleteFailedMsg')
			});
		}
	}
</script>

<svelte:head>
	<title>{$t('teacher.coursesPageTitle')}</title>
	<meta name="description" content={$t('teacher.manageCoursesDesc')} />
</svelte:head>

<div>
	<div>
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
				<div>
					<div class="mb-2 flex items-center gap-4">
						<Button
							href="/dashboard"
							variant="ghost"
							size="medium"
							class="hover:text-primary-600 dark:hover:text-primary-400 text-gray-600 dark:text-gray-400"
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 19l-7-7 7-7"
								/>
							</svg>
							{$t('teacher.backToDashboard')}
						</Button>
					</div>
					<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
						{$t('teacher.myCourses')}
					</h1>
					<p class="text-gray-600 dark:text-gray-400">
						{$t('teacher.manageCoursesDesc')}
					</p>
				</div>

				<div class="flex flex-col gap-3 sm:flex-row">
					<Button href="/teacher/courses/create" variant="primary" size="medium">
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4v16m8-8H4"
							/>
						</svg>
						{$t('teacher.createCourse')}
					</Button>
					<Button href="/teacher/students" variant="outline" size="medium">
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
							/>
						</svg>
						{$t('teacher.manageStudents')}
					</Button>
				</div>
			</div>

			<!-- Stats Cards -->
			<div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				<Card class="p-6">
					<div class="flex items-center">
						<div class="bg-primary-100 dark:bg-primary-900/30 rounded-lg p-3">
							<svg
								class="text-primary-600 dark:text-primary-400 h-6 w-6"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
								/>
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
								{$t('teacher.totalCourses')}
							</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
						</div>
					</div>
				</Card>

				<Card class="p-6">
					<div class="flex items-center">
						<div class="rounded-lg bg-green-100 p-3 dark:bg-green-900/30">
							<svg
								class="h-6 w-6 text-green-600 dark:text-green-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
								{$t('teacher.published')}
							</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.published}</p>
						</div>
					</div>
				</Card>

				<Card class="p-6">
					<div class="flex items-center">
						<div class="bg-secondary-100 dark:bg-secondary-900/30 rounded-lg p-3">
							<svg
								class="text-secondary-600 dark:text-secondary-400 h-6 w-6"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
								/>
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
								{$t('teacher.totalStudents')}
							</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalStudents}</p>
						</div>
					</div>
				</Card>

				<Card class="p-6">
					<div class="flex items-center">
						<div class="rounded-lg bg-yellow-100 p-3 dark:bg-yellow-900/30">
							<svg
								class="h-6 w-6 text-yellow-600 dark:text-yellow-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
								/>
							</svg>
						</div>
						<div class="ml-4">
							<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
								{$t('teacher.avgRating')}
							</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white">
								{(stats.avgRating || 0).toFixed(1)}
							</p>
						</div>
					</div>
				</Card>
			</div>
		</div>

		<!-- Filters and Search -->
		<div in:fly={{ y: 20, delay: 100, duration: 600 }}>
			<Card class="mb-8 p-6">
				<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
					<!-- Search -->
					<div class="lg:col-span-2">
						<Input
							label={$t('teacher.searchCourses')}
							placeholder={$t('teacher.searchCoursesPlaceholder')}
							bind:value={searchQuery}
							onchange={handleSearch}
							oninput={handleSearch}
						>
							<svg
								slot="icon"
								class="h-4 w-4 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
								/>
							</svg>
						</Input>
					</div>

					<!-- Status Filter -->
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('teacher.filterByStatus')}
						</label>
						<select
							bind:value={selectedStatus}
							onchange={handleFilterChange}
							class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
						>
							{#each statusOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>

					<!-- Sort -->
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('teacher.sortBy')}
						</label>
						<div class="flex gap-2">
							<select
								bind:value={sortBy}
								onchange={handleFilterChange}
								class="focus:border-primary-500 focus:ring-primary-500 flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
							>
								{#each sortOptions as option}
									<option value={option.value}>{option.label}</option>
								{/each}
							</select>
							<Button onclick={toggleSortOrder} variant="outline" size="medium" class="px-3">
								<svg
									class="h-4 w-4 {sortOrder === 'desc' ? 'rotate-180' : ''}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M7 11l5-5m0 0l5 5m-5-5v12"
									/>
								</svg>
							</Button>
						</div>
					</div>
				</div>
			</Card>
		</div>

		<!-- Error State -->
		{#if error}
			<div class="py-12 text-center" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					{#if error.includes('teacher') || error.includes('403')}
						<svg
							class="mx-auto h-16 w-16 text-yellow-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
							/>
						</svg>
					{:else if error.includes('session') || error.includes('401')}
						<svg
							class="text-primary-400 mx-auto h-16 w-16"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/>
						</svg>
					{:else}
						<svg
							class="mx-auto h-16 w-16 text-red-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					{/if}
				</div>
				<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
					{#if error.includes('teacher') || error.includes('403')}
						{$t('teacher.accessRestricted')}
					{:else if error.includes('session') || error.includes('401')}
						{$t('teacher.sessionExpired')}
					{:else}
						{$t('teacher.errorLoadingCourses')}
					{/if}
				</h3>
				<p class="mx-auto mb-6 max-w-md text-gray-600 dark:text-gray-400">{error}</p>

				<div class="flex flex-col justify-center gap-3 sm:flex-row">
					{#if error.includes('session') || error.includes('401')}
						<Button href="/auth/login" variant="primary" size="medium"
							>{$t('teacher.logInAgain')}</Button
						>
					{:else if error.includes('teacher') || error.includes('403')}
						<Button href="/dashboard" variant="outline" size="medium"
							>{$t('teacher.backToDashboard')}</Button
						>
						<Button href="/profile" variant="primary" size="medium"
							>{$t('teacher.checkProfile')}</Button
						>
					{:else}
						<Button onclick={loadCourses} variant="primary" size="medium"
							>{$t('teacher.tryAgain')}</Button
						>
						<Button href="/dashboard" variant="outline" size="medium"
							>{$t('teacher.backToDashboard')}</Button
						>
					{/if}
				</div>
			</div>
		{:else if loading}
			<!-- Loading State -->
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each Array(6) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="mb-4 h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="space-y-3">
								<div class="h-3 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-3 w-2/3 rounded bg-gray-200 dark:bg-gray-700"></div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{:else if filteredCourses.length === 0}
			<!-- Empty State -->
			<div class="py-12 text-center" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg
						class="mx-auto h-16 w-16 text-gray-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						/>
					</svg>
				</div>
				<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
					{courses.length === 0 ? $t('teacher.noCoursesYet') : $t('teacher.noCoursesFound')}
				</h3>
				<p class="mb-6 text-gray-600 dark:text-gray-400">
					{courses.length === 0 ? $t('teacher.startTeaching') : $t('teacher.noCoursesMatch')}
				</p>
				{#if courses.length === 0}
					<Button href="/teacher/courses/create" variant="primary" size="medium">
						{$t('teacher.createFirstCourse')}
					</Button>
				{/if}
			</div>
		{:else}
			<!-- Courses Grid -->
			<div
				class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
				in:fly={{ y: 20, delay: 200, duration: 600 }}
			>
				{#each paginatedCourses as course}
					<Card padding="none" class="overflow-hidden hover:shadow-lg">
						<div class="relative aspect-video bg-gray-100 dark:bg-white/5">
							<CourseCover {course} />
							<div class="absolute end-3 top-3">
								<Badge
									variant={course.status === 'published'
										? 'success'
										: course.status === 'draft'
											? 'warning'
											: 'secondary'}
									size="small"
								>
									{course.status}
								</Badge>
							</div>
						</div>

						<div class="p-6">
							<div class="mb-4">
								<h3 class="mb-2 line-clamp-2 text-lg font-semibold text-gray-900 dark:text-white">
									{course.title}
								</h3>
								<p class="line-clamp-3 text-sm text-gray-600 dark:text-gray-400">
									{course.short_description || course.description}
								</p>
							</div>

							<div
								class="mb-4 flex items-center justify-between text-sm text-gray-500 dark:text-gray-400"
							>
								<div class="flex items-center">
									<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
										/>
									</svg>
									{course.enrollment_count || 0} students
								</div>
								<span
									>{formatters.relativeTime(course.updated_at || course.created_at, $locale)}</span
								>
							</div>

							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-2">
									<Button
										href="/teacher/courses/{course.uuid}/manage"
										variant="outline"
										size="small"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
											/>
										</svg>
										{$t('teacher.edit')}
									</Button>
									<Button
										href="/teacher/courses/{course.uuid}/analytics"
										variant="outline"
										size="small"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
											/>
										</svg>
										{$t('teacher.analytics')}
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
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
											/>
										</svg>
									</Button>
									<Button
										onclick={() => deleteCourse(course.uuid)}
										variant="ghost"
										size="small"
										class="text-red-400 hover:text-red-600"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
											/>
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
							{$t('teacher.previous')}
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
							{$t('teacher.next')}
						</Button>
					</div>

					<p class="text-sm text-gray-500 dark:text-gray-400">
						{$t('teacher.showingOf', {
							from: Math.min((currentPage - 1) * itemsPerPage + 1, filteredCourses.length),
							to: Math.min(currentPage * itemsPerPage, filteredCourses.length),
							total: filteredCourses.length
						})}
					</p>
				</div>
			{/if}
		{/if}
	</div>
</div>

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
	import Select from '$lib/components/common/Select.svelte';

	// State variables
	let loading = $state(true);
	let error = $state('');
	let students = $state([]);
	let courses = $state([]);
	let filteredStudents = $state([]);
	let selectedCourse = $state('all');
	let searchQuery = $state('');
	let sortBy = $state('name');
	let sortOrder = $state('asc');

	// Pagination
	let currentPage = $state(1);
	let itemsPerPage = $state(20);
	let totalStudents = $state(0);

	const sortOptions = [
		{ value: 'name', label: 'Name' },
		{ value: 'enrolled_at', label: 'Enrollment Date' },
		{ value: 'last_active', label: 'Last Active' },
		{ value: 'progress', label: 'Progress' }
	];

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

		await loadData();
	});

	async function loadData() {
		loading = true;
		error = '';

		try {
			// Load teacher's courses
			const coursesResponse = await coursesApi.getTeacherCourses();
			courses = coursesResponse.results || coursesResponse || [];

			// Load all students from teacher's courses
			const allStudents = [];
			for (const course of courses) {
				try {
					const studentsResponse = await coursesApi.getCourseStudents(course.uuid);
					const courseStudents = (studentsResponse.results || studentsResponse || []).map(student => ({
						...student,
						courseName: course.title,
						courseUuid: course.uuid,
						courseSlug: course.slug
					}));
					allStudents.push(...courseStudents);
				} catch (err) {
					console.warn(`Failed to load students for course ${course.title}:`, err);
				}
			}

			// Remove duplicates and combine enrollments
			const studentsMap = new Map();
			allStudents.forEach(student => {
				const key = student.email || student.uuid;
				if (studentsMap.has(key)) {
					const existing = studentsMap.get(key);
					existing.courses = existing.courses || [];
					existing.courses.push({
						name: student.courseName,
						uuid: student.courseUuid,
						slug: student.courseSlug,
						enrolled_at: student.enrolled_at,
						progress: student.progress,
						last_active: student.last_active
					});
				} else {
					studentsMap.set(key, {
						...student,
						courses: [{
							name: student.courseName,
							uuid: student.courseUuid,
							slug: student.courseSlug,
							enrolled_at: student.enrolled_at,
							progress: student.progress,
							last_active: student.last_active
						}]
					});
				}
			});

			students = Array.from(studentsMap.values());
			totalStudents = students.length;
			applyFilters();

		} catch (err) {
			console.error('Failed to load students data:', err);
			error = err.message || 'Failed to load students data';
		} finally {
			loading = false;
		}
	}

	function applyFilters() {
		let filtered = [...students];

		// Filter by course
		if (selectedCourse !== 'all') {
			filtered = filtered.filter(student => 
				student.courses.some(course => course.uuid === selectedCourse)
			);
		}

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase().trim();
			filtered = filtered.filter(student => 
				student.name?.toLowerCase().includes(query) ||
				student.email?.toLowerCase().includes(query) ||
				student.courses.some(course => course.name?.toLowerCase().includes(query))
			);
		}

		// Sort
		filtered.sort((a, b) => {
			let aValue, bValue;
			
			switch (sortBy) {
				case 'name':
					aValue = a.name || '';
					bValue = b.name || '';
					break;
				case 'enrolled_at':
					aValue = new Date(a.courses[0]?.enrolled_at || 0);
					bValue = new Date(b.courses[0]?.enrolled_at || 0);
					break;
				case 'last_active':
					aValue = new Date(a.last_active || 0);
					bValue = new Date(b.last_active || 0);
					break;
				case 'progress':
					aValue = a.courses.reduce((sum, c) => sum + (c.progress || 0), 0) / a.courses.length;
					bValue = b.courses.reduce((sum, c) => sum + (c.progress || 0), 0) / b.courses.length;
					break;
				default:
					aValue = a.name || '';
					bValue = b.name || '';
			}

			if (sortOrder === 'asc') {
				return aValue > bValue ? 1 : -1;
			} else {
				return aValue < bValue ? 1 : -1;
			}
		});

		filteredStudents = filtered;
	}

	function handleSearch() {
		currentPage = 1;
		applyFilters();
	}

	function handleCourseFilter() {
		currentPage = 1;
		applyFilters();
	}

	function handleSort() {
		applyFilters();
	}

	function toggleSortOrder() {
		sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		handleSort();
	}

	// Pagination helpers
	let paginatedStudents = $derived(() => {
		const start = (currentPage - 1) * itemsPerPage;
		const end = start + itemsPerPage;
		return filteredStudents.slice(start, end);
	});

	let totalPages = $derived(() => Math.ceil(filteredStudents.length / itemsPerPage));

	function goToPage(page) {
		if (page >= 1 && page <= totalPages) {
			currentPage = page;
		}
	}

	function getStudentAverageProgress(student) {
		if (!student.courses || student.courses.length === 0) return 0;
		return Math.round(
			student.courses.reduce((sum, course) => sum + (course.progress || 0), 0) / student.courses.length
		);
	}
</script>

<svelte:head>
	<title>Student Management | E-Learning Platform</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="container mx-auto max-w-7xl px-4 py-8">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
				<div>
					<div class="flex items-center gap-4 mb-2">
						<Button
							href="/dashboard"
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
						Student Management
					</h1>
					<p class="text-gray-600 dark:text-gray-400">
						Manage and track students across all your courses
					</p>
				</div>

				<div class="flex flex-col sm:flex-row gap-3">
					<Button
						href="/teacher/courses"
						variant="outline"
						size="medium"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						View Courses
					</Button>
				</div>
			</div>
		</div>

		<!-- Filters and Search -->
		<Card class="p-6 mb-8" in:fly={{ y: 20, delay: 100, duration: 600 }}>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				<!-- Search -->
				<div class="lg:col-span-2">
					<Input
						label="Search Students"
						placeholder="Search by name, email, or course"
						bind:value={searchQuery}
						onchange={handleSearch}
						oninput={handleSearch}
					>
						<svg slot="icon" class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
					</Input>
				</div>

				<!-- Course Filter -->
				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						Filter by Course
					</label>
					<select
						bind:value={selectedCourse}
						onchange={handleCourseFilter}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
					>
						<option value="all">All Courses</option>
						{#each courses as course}
							<option value={course.uuid}>{course.title}</option>
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
							onchange={handleSort}
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
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Error Loading Students</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={loadData} variant="primary" size="medium">
					Try Again
				</Button>
			</div>
		{:else if loading}
			<!-- Loading State -->
			<Card class="p-6">
				<div class="space-y-4">
					{#each Array(5) as _}
						<div class="animate-pulse flex items-center space-x-4">
							<div class="rounded-full bg-gray-200 h-12 w-12 dark:bg-gray-700"></div>
							<div class="flex-1 space-y-2">
								<div class="h-4 bg-gray-200 rounded w-1/4 dark:bg-gray-700"></div>
								<div class="h-3 bg-gray-200 rounded w-1/2 dark:bg-gray-700"></div>
							</div>
						</div>
					{/each}
				</div>
			</Card>
		{:else if filteredStudents.length === 0}
			<!-- Empty State -->
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No Students Found</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">
					{searchQuery ? 'No students match your search criteria.' : 'No students have enrolled in your courses yet.'}
				</p>
				{#if !searchQuery}
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
			<!-- Students Table -->
			<Card class="overflow-hidden" in:fly={{ y: 20, delay: 200, duration: 600 }}>
				<div class="px-6 py-4 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
					<div class="flex justify-between items-center">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
							Students ({filteredStudents.length})
						</h3>
						<p class="text-sm text-gray-500 dark:text-gray-400">
							Showing {Math.min((currentPage - 1) * itemsPerPage + 1, filteredStudents.length)} - {Math.min(currentPage * itemsPerPage, filteredStudents.length)} of {filteredStudents.length}
						</p>
					</div>
				</div>

				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
						<thead class="bg-gray-50 dark:bg-gray-800">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									Student
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									Courses
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									Average Progress
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									Last Active
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									Actions
								</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
							{#each paginatedStudents as student}
								<tr class="hover:bg-gray-50 dark:hover:bg-gray-800">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="flex items-center">
											<div class="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
												<span class="text-blue-600 dark:text-blue-400 font-medium">
													{student.name?.charAt(0)?.toUpperCase() || '?'}
												</span>
											</div>
											<div class="ml-4">
												<div class="text-sm font-medium text-gray-900 dark:text-white">
													{student.name || 'Anonymous Student'}
												</div>
												<div class="text-sm text-gray-500 dark:text-gray-400">
													{student.email || 'No email'}
												</div>
											</div>
										</div>
									</td>
									<td class="px-6 py-4">
										<div class="space-y-1">
											{#each student.courses as course}
												<div class="flex items-center justify-between">
													<span class="text-sm text-gray-900 dark:text-white">
														{course.name}
													</span>
													<Badge variant="secondary" size="small">
														{course.progress || 0}%
													</Badge>
												</div>
											{/each}
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="flex items-center">
											<div class="w-16 bg-gray-200 rounded-full h-2 mr-3 dark:bg-gray-700">
												<div
													class="bg-blue-600 h-2 rounded-full"
													style="width: {getStudentAverageProgress(student)}%"
												></div>
											</div>
											<span class="text-sm text-gray-900 dark:text-white">
												{getStudentAverageProgress(student)}%
											</span>
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
										{formatters.relativeTime(student.last_active)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
										<div class="flex items-center space-x-2">
											{#if student.courses.length === 1}
												<Button
													href="/teacher/courses/{student.courses[0].uuid}/analytics"
													variant="outline"
													size="small"
												>
													View Details
												</Button>
											{:else}
												<select
													onchange={(e) => goto(`/teacher/courses/${e.target.value}/analytics`)}
													class="text-sm border border-gray-300 rounded px-2 py-1 dark:border-gray-600 dark:bg-gray-800"
												>
													<option value="">View Course</option>
													{#each student.courses as course}
														<option value={course.uuid}>{course.name}</option>
													{/each}
												</select>
											{/if}
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Pagination -->
				{#if totalPages > 1}
					<div class="px-6 py-4 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
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
								Page {currentPage} of {totalPages}
							</p>
						</div>
					</div>
				{/if}
			</Card>
		{/if}
	</div>
</div>
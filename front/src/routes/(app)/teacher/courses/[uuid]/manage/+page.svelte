<!-- front/src/routes/(app)/teacher/courses/[uuid]/manage/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t, locale } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { debounce } from '$lib/utils/helpers.js';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Tabs from '$lib/components/common/Tabs.svelte';

	// Route params
	let courseId = $page.params.uuid;

	// State variables
	let course = $state(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let selectedTab = $state('general');
	let showDeleteModal = $state(false);
	let showPublishModal = $state(false);

	// Form data
	let courseData = $state({
		title: '',
		slug: '',
		short_description: '',
		description: '',
		category: '',
		level: 'beginner',
		language: 'en',
		duration_hours: 1,
		prerequisites: '',
		learning_outcomes: '',
		status: 'draft',
		is_featured: false,
		enrollment_limit: null
	});

	let categories = $state([]);
	let modules = $state([]);
	let students = $state([]);
	let validationErrors = $state({});

	// Image upload
	let thumbnailFile = $state(null);
	let thumbnailPreview = $state(null);
	let uploading = $state(false);

	// Tab configuration
	const tabs = [
		{ id: 'general', label: 'General', icon: '⚙️' },
		{ id: 'content', label: 'Content', icon: '📚' },
		{ id: 'students', label: 'Students', icon: '👥' },
		{ id: 'settings', label: 'Settings', icon: '🔧' },
		{ id: 'analytics', label: 'Analytics', icon: '📊' }
	];

	// Derived states
	let canPublish = $derived(() => {
		return course?.status === 'draft' && 
			   course?.title?.trim() && 
			   course?.description?.trim() && 
			   modules.length > 0;
	});

	let canUnpublish = $derived(() => {
		return course?.status === 'published';
	});

	let enrollmentCount = $derived(() => students.length);

	onMount(async () => {
		// Check authorization
		if (!$currentUser || ($currentUser.role !== 'teacher' && !$currentUser.is_staff)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: 'You need to be a teacher to manage courses'
			});
			goto('/my-courses');
			return;
		}

		await loadCourse();
		await loadCategories();
		await loadModules();
		await loadStudents();
	});

	async function loadCourse() {
		loading = true;
		error = '';

		try {
			const response = await coursesApi.getCourse(courseId);
			course = response;

			// Verify user is the instructor
			if (course.instructor?.uuid !== $currentUser.uuid && !$currentUser.is_staff) {
				throw new Error('You are not authorized to manage this course');
			}

			// Populate form data
			courseData = {
				title: course.title || '',
				slug: course.slug || '',
				short_description: course.short_description || '',
				description: course.description || '',
				category: course.category?.uuid || '',
				level: course.level || 'beginner',
				language: course.language || 'en',
				duration_hours: course.duration_hours || 1,
				prerequisites: course.prerequisites || '',
				learning_outcomes: course.learning_outcomes || '',
				status: course.status || 'draft',
				is_featured: course.is_featured || false,
				enrollment_limit: course.enrollment_limit || null
			};

			if (course.thumbnail) {
				thumbnailPreview = course.thumbnail;
			}

		} catch (err) {
			console.error('Failed to load course:', err);
			error = err.message || 'Failed to load course';
			
			if (err.message.includes('not authorized')) {
				goto('/my-courses');
			}
		} finally {
			loading = false;
		}
	}

	async function loadCategories() {
		try {
			const response = await coursesApi.getCategories();
			categories = response.results || response || [];
		} catch (err) {
			console.error('Failed to load categories:', err);
			categories = [];
		}
	}

	async function loadModules() {
		try {
			const response = await coursesApi.getModules(courseId);
			modules = response.results || response || [];
		} catch (err) {
			console.error('Failed to load modules:', err);
			modules = [];
		}
	}

	async function loadStudents() {
		try {
			const response = await coursesApi.getCourseStudents(courseId);
			students = response.results || response || [];
		} catch (err) {
			console.error('Failed to load students:', err);
			students = [];
		}
	}

	function validateForm() {
		const errors = {};

		if (!courseData.title?.trim()) {
			errors.title = $t('course.titleRequired');
		}
		if (!courseData.short_description?.trim()) {
			errors.short_description = $t('course.shortDescriptionRequired');
		}
		if (!courseData.description?.trim()) {
			errors.description = $t('course.fullDescriptionRequired');
		}
		if (courseData.short_description?.length > 255) {
			errors.short_description = $t('course.shortDescriptionTooLong');
		}
		if (courseData.duration_hours < 1) {
			errors.duration_hours = $t('course.durationMinimum');
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	}

	async function saveCourse() {
		if (!validateForm()) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.validationError'),
				message: $t('course.fixErrorsBeforeContinuing')
			});
			return;
		}

		saving = true;
		try {
			// Prepare update payload
			const updatePayload = {
				title: courseData.title.trim(),
				short_description: courseData.short_description.trim(),
				description: courseData.description.trim(),
				level: courseData.level,
				language: courseData.language,
				duration_hours: parseInt(courseData.duration_hours),
				status: courseData.status,
				is_featured: courseData.is_featured
			};

			// Add optional fields
			if (courseData.slug?.trim()) {
				updatePayload.slug = courseData.slug.trim();
			}
			if (courseData.category) {
				updatePayload.category = courseData.category;
			}
			if (courseData.enrollment_limit && parseInt(courseData.enrollment_limit) > 0) {
				updatePayload.enrollment_limit = parseInt(courseData.enrollment_limit);
			}
			if (courseData.prerequisites?.trim()) {
				updatePayload.prerequisites = courseData.prerequisites.trim();
			}
			if (courseData.learning_outcomes?.trim()) {
				updatePayload.learning_outcomes = courseData.learning_outcomes.trim();
			}

			// Update course
			const response = await coursesApi.updateCourse(courseId, updatePayload);
			course = response;

			// Upload thumbnail if provided
			if (thumbnailFile) {
				await uploadThumbnail();
			}

			uiStore.showNotification({
				type: 'success',
				title: 'Course Updated',
				message: 'Your course has been updated successfully'
			});

		} catch (err) {
			console.error('Failed to save course:', err);
			
			uiStore.showNotification({
				type: 'error',
				title: 'Save Failed',
				message: err.message || 'Failed to save course changes'
			});
		} finally {
			saving = false;
		}
	}

	async function uploadThumbnail() {
		if (!thumbnailFile) return;

		uploading = true;
		try {
			await coursesApi.uploadCourseImage(courseId, thumbnailFile);
			thumbnailFile = null;
			
			// Reload course to get updated thumbnail URL
			await loadCourse();
			
		} catch (err) {
			console.error('Failed to upload thumbnail:', err);
			throw err;
		} finally {
			uploading = false;
		}
	}

	function handleThumbnailChange(event) {
		const file = event.target.files[0];
		if (!file) return;

		// Validate file type
		const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
		if (!allowedTypes.includes(file.type)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.invalidFileType'),
				message: $t('errors.uploadImageOnly')
			});
			return;
		}

		// Validate file size (5MB limit)
		if (file.size > 5 * 1024 * 1024) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.fileTooLarge'),
				message: $t('errors.maxFileSize5MB')
			});
			return;
		}

		thumbnailFile = file;

		// Create preview
		const reader = new FileReader();
		reader.onload = (e) => {
			thumbnailPreview = e.target.result;
		};
		reader.readAsDataURL(file);
	}

	async function publishCourse() {
		if (!canPublish) {
			uiStore.showNotification({
				type: 'error',
				title: 'Cannot Publish',
				message: 'Course must have title, description, and at least one module to publish'
			});
			return;
		}

		try {
			await coursesApi.publishCourse(courseId);
			await loadCourse();
			
			showPublishModal = false;
			
			uiStore.showNotification({
				type: 'success',
				title: 'Course Published',
				message: 'Your course is now published and available to students'
			});
		} catch (err) {
			console.error('Failed to publish course:', err);
			uiStore.showNotification({
				type: 'error',
				title: 'Publish Failed',
				message: err.message || 'Failed to publish course'
			});
		}
	}

	async function unpublishCourse() {
		try {
			courseData.status = 'draft';
			await saveCourse();
			
			uiStore.showNotification({
				type: 'success',
				title: 'Course Unpublished',
				message: 'Your course is now in draft mode'
			});
		} catch (err) {
			console.error('Failed to unpublish course:', err);
		}
	}

	async function deleteCourse() {
		try {
			await coursesApi.deleteCourse(courseId);
			
			showDeleteModal = false;
			
			uiStore.showNotification({
				type: 'success',
				title: 'Course Deleted',
				message: 'Course has been permanently deleted'
			});
			
			goto('/my-courses');
		} catch (err) {
			console.error('Failed to delete course:', err);
			uiStore.showNotification({
				type: 'error',
				title: 'Delete Failed',
				message: err.message || 'Failed to delete course'
			});
		}
	}

	const debouncedSave = debounce(saveCourse, 2000);

	function handleInputChange() {
		// Auto-save after user stops typing
		debouncedSave();
	}
</script>

<svelte:head>
	<title>{course?.title ? `Manage ${course.title}` : 'Manage Course'} | E-Learning Platform</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="container mx-auto max-w-6xl px-4 py-8">
		<!-- Header -->
		{#if loading}
			<div class="mb-8" in:fade={{ duration: 300 }}>
				<div class="animate-pulse">
					<div class="h-8 bg-gray-200 rounded-lg w-1/3 mb-4 dark:bg-gray-700"></div>
					<div class="h-4 bg-gray-200 rounded w-1/2 dark:bg-gray-700"></div>
				</div>
			</div>
		{:else if course}
			<div class="mb-8" in:fade={{ duration: 600 }}>
				<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
					<div>
						<div class="flex items-center gap-4 mb-2">
							<Button
								href="/my-courses"
								variant="ghost"
								size="medium"
								class="text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
							>
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
								</svg>
								Back to My Courses
							</Button>
						</div>
						<h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
							Manage Course
						</h1>
						<div class="flex items-center gap-3">
							<p class="text-gray-600 dark:text-gray-400">
								{course.title}
							</p>
							<Badge
								variant={course.status === 'published' ? 'success' : course.status === 'draft' ? 'warning' : 'secondary'}
								size="small"
							>
								{course.status}
							</Badge>
						</div>
					</div>

					<div class="flex flex-col sm:flex-row gap-3">
						<Button
							href="/teacher/courses/{courseId}/analytics"
							variant="outline"
							size="medium"
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
							</svg>
							Analytics
						</Button>

						{#if canPublish}
							<Button
								onclick={() => showPublishModal = true}
								variant="success"
								size="medium"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-8 0h8m-8 0v2m8-2v2M9 20v-6m6 6v-6" />
								</svg>
								Publish
							</Button>
						{:else if canUnpublish}
							<Button
								onclick={unpublishCourse}
								variant="warning"
								size="medium"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636" />
								</svg>
								Unpublish
							</Button>
						{/if}

						<Button
							onclick={saveCourse}
							variant="primary"
							size="medium"
							disabled={saving}
							loading={saving}
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
							</svg>
							Save Changes
						</Button>
					</div>
				</div>

				<!-- Tab Navigation -->
				<Tabs {tabs} bind:selectedTab />
			</div>
		{/if}

		<!-- Error State -->
		{#if error}
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Course Error</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={loadCourse} variant="primary" size="medium">
					Try Again
				</Button>
			</div>
		{:else if loading}
			<div class="space-y-6">
				{#each Array(3) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="h-4 bg-gray-200 rounded w-1/4 mb-4 dark:bg-gray-700"></div>
							<div class="space-y-3">
								<div class="h-3 bg-gray-200 rounded w-full dark:bg-gray-700"></div>
								<div class="h-3 bg-gray-200 rounded w-3/4 dark:bg-gray-700"></div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{:else if course}
			<!-- Tab Content -->
			<div in:fly={{ y: 20, delay: 100, duration: 600 }}>
				{#if selectedTab === 'general'}
					<!-- General Settings -->
					<div class="space-y-6">
						<!-- Basic Information -->
						<Card class="p-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
								Basic Information
							</h3>
							
							<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
								<div class="lg:col-span-2">
									<Input
										label="Course Title *"
										bind:value={courseData.title}
										error={validationErrors.title}
										placeholder="Enter course title"
										onchange={handleInputChange}
									/>
								</div>

								<Input
									label="URL Slug"
									bind:value={courseData.slug}
									placeholder="course-url-slug"
									helperText="Leave empty to auto-generate"
									onchange={handleInputChange}
								/>

								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Category
									</label>
									<select
										bind:value={courseData.category}
										onchange={handleInputChange}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										<option value="">Select a category</option>
										{#each categories as category}
											<option value={category.uuid}>{category.name}</option>
										{/each}
									</select>
								</div>

								<div class="lg:col-span-2">
									<Input
										label="Short Description *"
										bind:value={courseData.short_description}
										error={validationErrors.short_description}
										placeholder="Brief description (max 255 characters)"
										maxlength="255"
										onchange={handleInputChange}
									/>
								</div>

								<div class="lg:col-span-2">
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Full Description *
									</label>
									<textarea
										bind:value={courseData.description}
										onchange={handleInputChange}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="6"
										placeholder="Detailed course description"
										class:border-red-300={validationErrors.description}
									></textarea>
									{#if validationErrors.description}
										<p class="mt-1 text-sm text-red-600">{validationErrors.description}</p>
									{/if}
								</div>
							</div>
						</Card>

						<!-- Course Settings -->
						<Card class="p-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
								Course Settings
							</h3>
							
							<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Level
									</label>
									<select
										bind:value={courseData.level}
										onchange={handleInputChange}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										<option value="beginner">Beginner</option>
										<option value="intermediate">Intermediate</option>
										<option value="advanced">Advanced</option>
									</select>
								</div>

								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Language
									</label>
									<select
										bind:value={courseData.language}
										onchange={handleInputChange}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										<option value="en">English</option>
										<option value="ar">Arabic</option>
									</select>
								</div>

								<Input
									label="Duration (hours)"
									type="number"
									bind:value={courseData.duration_hours}
									error={validationErrors.duration_hours}
									min="1"
									placeholder="1"
									onchange={handleInputChange}
								/>

								<Input
									label="Enrollment Limit"
									type="number"
									bind:value={courseData.enrollment_limit}
									placeholder="Leave empty for unlimited"
									onchange={handleInputChange}
								/>

								<div class="md:col-span-2">
									<label class="flex items-center">
										<input
											type="checkbox"
											bind:checked={courseData.is_featured}
											onchange={handleInputChange}
											class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
										/>
										<span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
											Feature this course
										</span>
									</label>
								</div>
							</div>
						</Card>

						<!-- Course Thumbnail -->
						<Card class="p-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
								Course Thumbnail
							</h3>
							
							<div class="flex flex-col lg:flex-row gap-6">
								{#if thumbnailPreview}
									<div class="lg:w-64">
										<img 
											src={thumbnailPreview} 
											alt="Course thumbnail"
											class="w-full h-36 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
										/>
									</div>
								{/if}

								<div class="flex-1">
									<div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
										<input
											type="file"
											accept="image/*"
											onchange={handleThumbnailChange}
											class="hidden"
											id="thumbnail-upload"
										/>
										<label
											for="thumbnail-upload"
											class="cursor-pointer inline-flex flex-col items-center"
										>
											<svg class="h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
											</svg>
											<span class="text-lg font-medium text-gray-900 dark:text-white">
												Click to upload
											</span>
											<span class="text-sm text-gray-500 dark:text-gray-400">
												or drag and drop
											</span>
											<span class="text-xs text-gray-400 mt-2">
												PNG, JPG, JPEG or WebP (MAX. 5MB)
											</span>
										</label>
									</div>
								</div>
							</div>
						</Card>
					</div>

				{:else if selectedTab === 'content'}
					<!-- Content Management -->
					<Card class="p-6">
						<div class="flex justify-between items-center mb-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
								Course Content
							</h3>
							<Button
								href="/teacher/courses/{courseId}/content/create"
								variant="primary"
								size="medium"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
								</svg>
								Add Module
							</Button>
						</div>

						{#if modules && modules.length > 0}
							<div class="space-y-4">
								{#each modules as module, index}
									<div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
										<div class="flex items-center justify-between">
											<div>
												<h4 class="font-medium text-gray-900 dark:text-white">
													{index + 1}. {module.title}
												</h4>
												<p class="text-sm text-gray-500 dark:text-gray-400">
													{module.lessons?.length || 0} lessons • {module.duration || 0} min
												</p>
											</div>
											<div class="flex items-center gap-2">
												<Button
													href="/teacher/courses/{courseId}/modules/{module.uuid}/edit"
													variant="outline"
													size="small"
												>
													Edit
												</Button>
												<Badge
													variant={module.status === 'published' ? 'success' : 'warning'}
													size="small"
												>
													{module.status}
												</Badge>
											</div>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="text-center py-8 text-gray-500 dark:text-gray-400">
								<svg class="mx-auto h-16 w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
								<p class="text-lg font-medium mb-2">No content yet</p>
								<p class="mb-4">Start building your course by adding modules and lessons</p>
								<Button
									href="/teacher/courses/{courseId}/content/create"
									variant="primary"
									size="medium"
								>
									Create First Module
								</Button>
							</div>
						{/if}
					</Card>

				{:else if selectedTab === 'students'}
					<!-- Student Management -->
					<Card class="p-6">
						<div class="flex justify-between items-center mb-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
								Enrolled Students
							</h3>
							<p class="text-sm text-gray-500 dark:text-gray-400">
								{enrollmentCount} students enrolled
							</p>
						</div>

						{#if students && students.length > 0}
							<div class="overflow-x-auto">
								<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
									<thead class="bg-gray-50 dark:bg-gray-800">
										<tr>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
												Student
											</th>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
												Progress
											</th>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
												Enrolled
											</th>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
												Last Active
											</th>
										</tr>
									</thead>
									<tbody class="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
										{#each students as student}
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
												<td class="px-6 py-4 whitespace-nowrap">
													<div class="flex items-center">
														<div class="w-16 bg-gray-200 rounded-full h-2 mr-3 dark:bg-gray-700">
															<div
																class="bg-blue-600 h-2 rounded-full"
																style="width: {student.progress || 0}%"
															></div>
														</div>
														<span class="text-sm text-gray-900 dark:text-white">
															{student.progress || 0}%
														</span>
													</div>
												</td>
												<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
													{formatters.date(student.enrolled_at)}
												</td>
												<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
													{formatters.relativeTime(student.last_active)}
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						{:else}
							<div class="text-center py-8 text-gray-500 dark:text-gray-400">
								<svg class="mx-auto h-16 w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
								<p class="text-lg font-medium mb-2">No students yet</p>
								<p>Students will appear here when they enroll in your course</p>
							</div>
						{/if}
					</Card>

				{:else if selectedTab === 'settings'}
					<!-- Advanced Settings -->
					<div class="space-y-6">
						<Card class="p-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
								Advanced Settings
							</h3>
							
							<div class="space-y-6">
								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Prerequisites
									</label>
									<textarea
										bind:value={courseData.prerequisites}
										onchange={handleInputChange}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="3"
										placeholder="What students should know before taking this course"
									></textarea>
								</div>

								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Learning Outcomes
									</label>
									<textarea
										bind:value={courseData.learning_outcomes}
										onchange={handleInputChange}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="4"
										placeholder="What students will learn and achieve"
									></textarea>
								</div>
							</div>
						</Card>

						<!-- Danger Zone -->
						<Card class="p-6 border-red-200 dark:border-red-800">
							<h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-6">
								Danger Zone
							</h3>
							
							<div class="space-y-4">
								<div class="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
									<div>
										<h4 class="font-medium text-red-900 dark:text-red-100">Delete Course</h4>
										<p class="text-sm text-red-600 dark:text-red-300">
											Permanently delete this course and all its content. This action cannot be undone.
										</p>
									</div>
									<Button
										onclick={() => showDeleteModal = true}
										variant="danger"
										size="medium"
									>
										Delete Course
									</Button>
								</div>
							</div>
						</Card>
					</div>

				{:else if selectedTab === 'analytics'}
					<!-- Analytics Preview -->
					<Card class="p-8 text-center">
						<div class="mb-4">
							<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
							</svg>
						</div>
						<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
							Detailed Analytics
						</h3>
						<p class="text-gray-600 dark:text-gray-400 mb-6">
							View comprehensive analytics for this course including student progress, engagement metrics, and performance data.
						</p>
						<Button
							href="/teacher/courses/{courseId}/analytics"
							variant="primary"
							size="medium"
						>
							View Full Analytics
						</Button>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</div>

<!-- Publish Confirmation Modal -->
<Modal
	bind:show={showPublishModal}
	title="Publish Course"
	size="medium"
>
	<div class="mb-6">
		<p class="text-gray-600 dark:text-gray-400 mb-4">
			Are you sure you want to publish this course? Once published, students will be able to find and enroll in your course.
		</p>
		<div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
			<h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Before publishing, make sure:</h4>
			<ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
				<li>✓ Course has a clear title and description</li>
				<li>✓ At least one module with lessons is added</li>
				<li>✓ Course thumbnail is uploaded</li>
				<li>✓ Learning outcomes are defined</li>
			</ul>
		</div>
	</div>
	
	<div class="flex justify-end gap-3">
		<Button
			onclick={() => showPublishModal = false}
			variant="outline"
			size="medium"
		>
			Cancel
		</Button>
		<Button
			onclick={publishCourse}
			variant="success"
			size="medium"
		>
			Publish Course
		</Button>
	</div>
</Modal>

<!-- Delete Confirmation Modal -->
<Modal
	bind:show={showDeleteModal}
	title="Delete Course"
	size="medium"
>
	<div class="mb-6">
		<div class="flex items-center mb-4">
			<svg class="h-12 w-12 text-red-400 mr-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<div>
				<h4 class="font-medium text-gray-900 dark:text-white">Permanently delete this course?</h4>
				<p class="text-sm text-gray-600 dark:text-gray-400">This action cannot be undone.</p>
			</div>
		</div>
		
		<div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
			<p class="text-red-800 dark:text-red-200 text-sm">
				All course content, student enrollments, and analytics data will be permanently deleted.
				{#if enrollmentCount > 0}
					<strong>{enrollmentCount} students</strong> are currently enrolled in this course.
				{/if}
			</p>
		</div>
	</div>
	
	<div class="flex justify-end gap-3">
		<Button
			onclick={() => showDeleteModal = false}
			variant="outline"
			size="medium"
		>
			Cancel
		</Button>
		<Button
			onclick={deleteCourse}
			variant="danger"
			size="medium"
		>
			Delete Forever
		</Button>
	</div>
</Modal>
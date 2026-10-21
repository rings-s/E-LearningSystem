<script>
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '#lib/apis/courses.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t, locale } from '#lib/i18n/index.js';
	import { formatters } from '#lib/utils/formatters.js';
	import { debounce } from '#lib/utils/helpers.js';

	// Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import Input from '#lib/components/common/Input.svelte';
	import Modal from '#lib/components/common/Modal.svelte';
	import Tabs from '#lib/components/common/Tabs.svelte';

	// Route params
	let courseId = page.params.uuid;

	// State variables
	let course = $state(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let activeTabIndex = $state(0);
	let showDeleteModal = $state(false);
	let showModuleModal = $state(false);
	let creatingModule = $state(false);
	let newModule = $state({ title: '', description: '' });
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
	const tabs = $derived([
		{ id: 'general', label: $t('courseForm.general'), icon: '⚙️' },
		{ id: 'content', label: $t('courseForm.content'), icon: '📚' },
		{ id: 'students', label: $t('courseForm.students'), icon: '👥' },
		{ id: 'settings', label: $t('courseForm.settings'), icon: '🔧' },
		{ id: 'analytics', label: $t('courseForm.analytics'), icon: '📊' }
	]);
	let selectedTab = $derived(tabs[activeTabIndex].id);

	// Derived states
	let canPublish = $derived.by(() => {
		return (
			course?.status === 'draft' &&
			course?.title?.trim() &&
			course?.description?.trim() &&
			modules.length > 0
		);
	});

	let canUnpublish = $derived.by(() => {
		return course?.status === 'published';
	});

	let enrollmentCount = $derived.by(() => students.length);

	onMount(async () => {
		// Check authorization
		if (!$currentUser || ($currentUser.role !== 'teacher' && !$currentUser.is_staff)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: $t('courseForm.teacherToManage')
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
			if (course.instructor?.id !== $currentUser.id && !$currentUser.is_staff) {
				throw new Error('You are not authorized to manage this course');
			}

			// Populate form data
			courseData = {
				title: course.title || '',
				slug: course.slug || '',
				short_description: course.short_description || '',
				description: course.description || '',
				category: course.category?.id ?? course.category ?? '',
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
			error = err.message || $t('courseForm.loadCourseFailedShort');

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

	async function createModule() {
		if (!newModule.title.trim()) return;
		creatingModule = true;
		try {
			await coursesApi.createModule({
				course: course.id,
				title: newModule.title.trim(),
				description: newModule.description.trim(),
				order: Math.max(0, ...modules.map((m) => m.order || 0)) + 1
			});
			uiStore.showNotification({ type: 'success', title: $t('courseForm.moduleCreated') });
			showModuleModal = false;
			newModule = { title: '', description: '' };
			await loadModules();
		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: $t('courseForm.moduleCreateFailed'),
				message: err.message
			});
		} finally {
			creatingModule = false;
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
		// Mirror the API rules so the teacher sees why a save would fail
		else if (courseData.title.trim().length < 3) {
			errors.title = $t('courseForm.titleMin');
		}
		if (!courseData.short_description?.trim()) {
			errors.short_description = $t('course.shortDescriptionRequired');
		}
		if (!courseData.description?.trim()) {
			errors.description = $t('course.fullDescriptionRequired');
		} else if (courseData.description.trim().length < 50) {
			errors.description = $t('courseForm.descMin', {
				count: courseData.description.trim().length
			});
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
				title: $t('courseForm.courseUpdated'),
				message: $t('courseForm.courseUpdatedMsg')
			});
		} catch (err) {
			console.error('Failed to save course:', err);

			uiStore.showNotification({
				type: 'error',
				title: $t('courseForm.saveFailed'),
				message: err.message || $t('courseForm.saveFailedMsg')
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
				title: $t('courseForm.cannotPublish'),
				message: $t('courseForm.publishRequirements')
			});
			return;
		}

		try {
			await coursesApi.publishCourse(courseId);
			await loadCourse();

			showPublishModal = false;

			uiStore.showNotification({
				type: 'success',
				title: $t('courseForm.coursePublished'),
				message: $t('courseForm.nowPublished')
			});
		} catch (err) {
			console.error('Failed to publish course:', err);
			uiStore.showNotification({
				type: 'error',
				title: $t('courseForm.publishFailed'),
				message: err.message || $t('courseForm.publishFailedMsg')
			});
		}
	}

	async function unpublishCourse() {
		try {
			courseData.status = 'draft';
			await saveCourse();

			uiStore.showNotification({
				type: 'success',
				title: $t('courseForm.courseUnpublished'),
				message: $t('courseForm.nowDraft')
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
				title: $t('courseForm.courseDeleted'),
				message: $t('courseForm.courseDeletedMsg')
			});

			goto('/my-courses');
		} catch (err) {
			console.error('Failed to delete course:', err);
			uiStore.showNotification({
				type: 'error',
				title: $t('courseForm.deleteFailed'),
				message: err.message || $t('courseForm.deleteFailedMsg')
			});
		}
	}

	const debouncedSave = debounce(saveCourse, 2000);

	function handleInputChange() {
		// Auto-save after user stops typing
		debouncedSave();
	}
</script>

<!-- front/src/routes/(app)/teacher/courses/[uuid]/manage/+page.svelte -->
<svelte:head
	><title
		>{course?.title
			? $t('courseForm.managePageTitle', { title: course.title })
			: $t('courseForm.manageCourse')}</title
	></svelte:head
>

<div>
	<div class="mx-auto max-w-6xl">
		<!-- Header -->
		{#if loading}
			<div class="mb-8" in:fade={{ duration: 300 }}>
				<div class="animate-pulse">
					<div class="mb-4 h-8 w-1/3 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-1/2 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>
		{:else if course}
			<div class="mb-8" in:fade={{ duration: 600 }}>
				<div class="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
					<div>
						<div class="mb-2 flex items-center gap-4">
							<Button
								href="/my-courses"
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
									></path>
								</svg>
								{$t('courseForm.backToMyCourses')}
							</Button>
						</div>
						<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
							{$t('courseForm.manageCourse')}
						</h1>
						<div class="flex items-center gap-3">
							<p class="text-gray-600 dark:text-gray-400">
								{course.title}
							</p>
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

					<div class="flex flex-col gap-3 sm:flex-row">
						<Button href="/teacher/courses/{courseId}/analytics" variant="outline" size="medium">
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
								></path>
							</svg>
							{$t('courseForm.analytics')}
						</Button>

						{#if canPublish}
							<Button onclick={() => (showPublishModal = true)} variant="success" size="medium">
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-8 0h8m-8 0v2m8-2v2M9 20v-6m6 6v-6"
									></path>
								</svg>
								{$t('courseForm.publish')}
							</Button>
						{:else if canUnpublish}
							<Button onclick={unpublishCourse} variant="warning" size="medium">
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636"
									></path>
								</svg>
								{$t('courseForm.unpublish')}
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
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
								></path>
							</svg>
							{$t('courseForm.saveChanges')}
						</Button>
					</div>
				</div>

				<!-- Tab Navigation -->
				<Tabs {tabs} bind:activeTab={activeTabIndex} />
			</div>
		{/if}

		<!-- Error State -->
		{#if error}
			<div class="py-12 text-center" in:fade={{ duration: 300 }}>
				<div class="mb-4">
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
						></path>
					</svg>
				</div>
				<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
					{$t('courseForm.courseError')}
				</h3>
				<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
				<Button onclick={loadCourse} variant="primary" size="medium"
					>{$t('courseForm.tryAgain')}</Button
				>
			</div>
		{:else if loading}
			<div class="space-y-6">
				{#each Array(3) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="mb-4 h-4 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="space-y-3">
								<div class="h-3 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-3 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
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
							<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
								{$t('courseForm.basicInformation')}
							</h3>

							<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
								<div class="lg:col-span-2">
									<Input
										label={$t('courseForm.courseTitleReq')}
										bind:value={courseData.title}
										error={validationErrors.title}
										placeholder={$t('courseForm.titlePlaceholder')}
										onchange={handleInputChange}
									/>
								</div>

								<Input
									label={$t('courseForm.urlSlug')}
									bind:value={courseData.slug}
									placeholder="course-url-slug"
									helperText={$t('courseForm.slugHelperShort')}
									onchange={handleInputChange}
								/>

								<div>
									<label
										for="course-category"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('courseForm.category')}
									</label>
									<select
										id="course-category"
										bind:value={courseData.category}
										onchange={handleInputChange}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										<option value="">{$t('courseForm.selectCategory')}</option>
										{#each categories as category}
											<option value={category.id}>{category.name}</option>
										{/each}
									</select>
								</div>

								<div class="lg:col-span-2">
									<Input
										label={$t('courseForm.shortDescReq')}
										bind:value={courseData.short_description}
										error={validationErrors.short_description}
										placeholder={$t('courseForm.shortDescPlaceholder')}
										maxlength="255"
										onchange={handleInputChange}
									/>
								</div>

								<div class="lg:col-span-2">
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.fullDescReq')}
									</label>
									<textarea
										bind:value={courseData.description}
										onchange={handleInputChange}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="6"
										placeholder={$t('courseForm.fullDescPlaceholder')}
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
							<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
								{$t('courseForm.courseSettings')}
							</h3>

							<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
								<div>
									<label
										for="course-level"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('courseForm.level')}
									</label>
									<select
										id="course-level"
										bind:value={courseData.level}
										onchange={handleInputChange}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										<option value="beginner">{$t('courseForm.beginner')}</option>
										<option value="intermediate">{$t('courseForm.intermediate')}</option>
										<option value="advanced">{$t('courseForm.advanced')}</option>
									</select>
								</div>

								<div>
									<label
										for="course-language"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('courseForm.language')}
									</label>
									<select
										id="course-language"
										bind:value={courseData.language}
										onchange={handleInputChange}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										<option value="en">{$t('courseForm.english')}</option>
										<option value="ar">{$t('courseForm.arabic')}</option>
									</select>
								</div>

								<Input
									label={$t('courseForm.durationHours')}
									type="number"
									bind:value={courseData.duration_hours}
									error={validationErrors.duration_hours}
									min="1"
									placeholder="1"
									onchange={handleInputChange}
								/>

								<Input
									label={$t('courseForm.enrollmentLimit')}
									type="number"
									bind:value={courseData.enrollment_limit}
									placeholder={$t('courseForm.unlimitedPlaceholder')}
									onchange={handleInputChange}
								/>

								<div class="md:col-span-2">
									<label class="flex items-center">
										<input
											type="checkbox"
											bind:checked={courseData.is_featured}
											onchange={handleInputChange}
											class="text-primary-600 focus:ring-primary-500 rounded border-gray-300"
										/>
										<span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
											{$t('courseForm.featureThisShort')}
										</span>
									</label>
								</div>
							</div>
						</Card>

						<!-- Course Thumbnail -->
						<Card class="p-6">
							<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
								{$t('courseForm.courseThumbnail')}
							</h3>

							<div class="flex flex-col gap-6 lg:flex-row">
								{#if thumbnailPreview}
									<div class="lg:w-64">
										<img
											src={thumbnailPreview}
											alt={$t('courseForm.thumbnailAlt')}
											class="h-36 w-full rounded-lg border border-gray-200 object-cover dark:border-gray-700"
										/>
									</div>
								{/if}

								<div class="flex-1">
									<div
										class="rounded-lg border-2 border-dashed border-gray-300 p-6 text-center dark:border-gray-600"
									>
										<input
											type="file"
											accept="image/*"
											onchange={handleThumbnailChange}
											class="hidden"
											id="thumbnail-upload"
										/>
										<label
											for="thumbnail-upload"
											class="inline-flex cursor-pointer flex-col items-center"
										>
											<svg
												class="mb-4 h-12 w-12 text-gray-400"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
												></path>
											</svg>
											<span class="text-lg font-medium text-gray-900 dark:text-white">
												{$t('courseForm.clickToUpload')}
											</span>
											<span class="text-sm text-gray-500 dark:text-gray-400">
												{$t('courseForm.dragDrop')}
											</span>
											<span class="mt-2 text-xs text-gray-400">
												{$t('courseForm.imageTypes')}
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
						<div class="mb-6 flex items-center justify-between">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
								{$t('courseForm.courseContent')}
							</h3>
							<Button onclick={() => (showModuleModal = true)} variant="primary" size="medium">
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 4v16m8-8H4"
									></path>
								</svg>
								{$t('courseForm.addModule')}
							</Button>
						</div>

						{#if modules && modules.length > 0}
							<div class="space-y-4">
								{#each modules as module, index}
									<div class="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
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
													href="/teacher/courses/{courseId}/lessons/create?module={module.id}"
													variant="outline"
													size="small"
												>
													{$t('courseForm.addLesson')}
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
							<div class="py-8 text-center text-gray-500 dark:text-gray-400">
								<svg
									class="mx-auto mb-4 h-16 w-16"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
									></path>
								</svg>
								<p class="mb-2 text-lg font-medium">{$t('courseForm.noContent')}</p>
								<p class="mb-4">{$t('courseForm.startBuilding')}</p>
								<Button onclick={() => (showModuleModal = true)} variant="primary" size="medium">
									{$t('courseForm.createFirstModule')}
								</Button>
							</div>
						{/if}
					</Card>
				{:else if selectedTab === 'students'}
					<!-- Student Management -->
					<Card class="p-6">
						<div class="mb-6 flex items-center justify-between">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
								{$t('courseForm.enrolledStudents')}
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
											<th
												class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>
												{$t('courseForm.student')}
											</th>
											<th
												class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>
												{$t('courseForm.progress')}
											</th>
											<th
												class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>
												{$t('courseForm.enrolled')}
											</th>
											<th
												class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>
												{$t('courseForm.lastActive')}
											</th>
										</tr>
									</thead>
									<tbody
										class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-900"
									>
										{#each students as student}
											<tr class="hover:bg-gray-50 dark:hover:bg-gray-800">
												<td class="px-6 py-4 whitespace-nowrap">
													<div class="flex items-center">
														<div
															class="bg-primary-100 dark:bg-primary-900 flex h-10 w-10 items-center justify-center rounded-full"
														>
															<span class="text-primary-600 dark:text-primary-400 font-medium">
																{student.name?.charAt(0)?.toUpperCase() || '?'}
															</span>
														</div>
														<div class="ml-4">
															<div class="text-sm font-medium text-gray-900 dark:text-white">
																{student.name || $t('courseForm.anonymousStudent')}
															</div>
															<div class="text-sm text-gray-500 dark:text-gray-400">
																{student.email || $t('courseForm.noEmail')}
															</div>
														</div>
													</div>
												</td>
												<td class="px-6 py-4 whitespace-nowrap">
													<div class="flex items-center">
														<div class="mr-3 h-2 w-16 rounded-full bg-gray-200 dark:bg-gray-700">
															<div
																class="bg-primary-600 h-2 rounded-full"
																style="width: {student.progress || 0}%"
															></div>
														</div>
														<span class="text-sm text-gray-900 dark:text-white">
															{student.progress || 0}%
														</span>
													</div>
												</td>
												<td
													class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400"
												>
													{formatters.date(student.enrolled_at, $locale)}
												</td>
												<td
													class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400"
												>
													{formatters.relativeTime(student.last_active, $locale)}
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						{:else}
							<div class="py-8 text-center text-gray-500 dark:text-gray-400">
								<svg
									class="mx-auto mb-4 h-16 w-16"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
									></path>
								</svg>
								<p class="mb-2 text-lg font-medium">{$t('courseForm.noStudents')}</p>
								<p>{$t('courseForm.studentsAppear')}</p>
							</div>
						{/if}
					</Card>
				{:else if selectedTab === 'settings'}
					<!-- Advanced Settings -->
					<div class="space-y-6">
						<Card class="p-6">
							<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
								{$t('courseForm.advancedSettings')}
							</h3>

							<div class="space-y-6">
								<div>
									<label
										for="course-prerequisites"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('courseForm.prerequisites')}
									</label>
									<textarea
										id="course-prerequisites"
										bind:value={courseData.prerequisites}
										onchange={handleInputChange}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="3"
										placeholder={$t('courseForm.prereqPlaceholder')}
									></textarea>
								</div>

								<div>
									<label
										for="course-learning-outcomes"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('courseForm.learningOutcomes')}
									</label>
									<textarea
										id="course-learning-outcomes"
										bind:value={courseData.learning_outcomes}
										onchange={handleInputChange}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="4"
										placeholder={$t('courseForm.outcomesPlaceholder2')}
									></textarea>
								</div>
							</div>
						</Card>

						<!-- Danger Zone -->
						<Card class="border-red-200 p-6 dark:border-red-800">
							<h3 class="mb-6 text-lg font-semibold text-red-900 dark:text-red-100">
								{$t('courseForm.dangerZone')}
							</h3>

							<div class="space-y-4">
								<div
									class="flex items-center justify-between rounded-lg bg-red-50 p-4 dark:bg-red-900/20"
								>
									<div>
										<h4 class="font-medium text-red-900 dark:text-red-100">
											{$t('courseForm.deleteCourse')}
										</h4>
										<p class="text-sm text-red-600 dark:text-red-300">
											{$t('courseForm.deleteWarning')}
										</p>
									</div>
									<Button onclick={() => (showDeleteModal = true)} variant="danger" size="medium">
										{$t('courseForm.deleteCourse')}
									</Button>
								</div>
							</div>
						</Card>
					</div>
				{:else if selectedTab === 'analytics'}
					<!-- Analytics Preview -->
					<Card class="p-8 text-center">
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
									d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
								></path>
							</svg>
						</div>
						<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
							{$t('courseForm.detailedAnalytics')}
						</h3>
						<p class="mb-6 text-gray-600 dark:text-gray-400">
							{$t('courseForm.analyticsDesc')}
						</p>
						<Button href="/teacher/courses/{courseId}/analytics" variant="primary" size="medium">
							{$t('courseForm.viewFullAnalytics')}
						</Button>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</div>

<!-- Publish Confirmation Modal -->
<Modal
	open={showPublishModal}
	onClose={() => (showPublishModal = false)}
	title={$t('courseForm.publishCourse')}
	size="medium"
>
	<div class="mb-6">
		<p class="mb-4 text-gray-600 dark:text-gray-400">
			{$t('courseForm.publishConfirm')}
		</p>
		<div class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
			<h4 class="text-primary-900 dark:text-primary-100 mb-2 font-medium">
				{$t('courseForm.beforePublishing')}
			</h4>
			<ul class="text-primary-800 dark:text-primary-200 space-y-1 text-sm">
				<li>{$t('courseForm.checkTitle')}</li>
				<li>{$t('courseForm.checkModules')}</li>
				<li>{$t('courseForm.checkThumbnail')}</li>
				<li>{$t('courseForm.checkOutcomes')}</li>
			</ul>
		</div>
	</div>

	<div class="flex justify-end gap-3">
		<Button onclick={() => (showPublishModal = false)} variant="outline" size="medium">
			{$t('courseForm.cancel')}
		</Button>
		<Button onclick={publishCourse} variant="success" size="medium"
			>{$t('courseForm.publishCourse')}</Button
		>
	</div>
</Modal>

<!-- Delete Confirmation Modal -->
<Modal
	open={showDeleteModal}
	onClose={() => (showDeleteModal = false)}
	title={$t('courseForm.deleteCourse')}
	size="medium"
>
	<div class="mb-6">
		<div class="mb-4 flex items-center">
			<svg
				class="mr-4 h-12 w-12 text-red-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				></path>
			</svg>
			<div>
				<h4 class="font-medium text-gray-900 dark:text-white">{$t('courseForm.deleteQuestion')}</h4>
				<p class="text-sm text-gray-600 dark:text-gray-400">{$t('courseForm.cannotUndo')}</p>
			</div>
		</div>

		<div class="rounded-lg bg-red-50 p-4 dark:bg-red-900/20">
			<p class="text-sm text-red-800 dark:text-red-200">
				All course content, student enrollments, and analytics data will be permanently deleted.
				{#if enrollmentCount > 0}
					<strong>{enrollmentCount} students</strong> are currently enrolled in this course.
				{/if}
			</p>
		</div>
	</div>

	<div class="flex justify-end gap-3">
		<Button onclick={() => (showDeleteModal = false)} variant="outline" size="medium">
			{$t('courseForm.cancel')}
		</Button>
		<Button onclick={deleteCourse} variant="danger" size="medium"
			>{$t('courseForm.deleteForever')}</Button
		>
	</div>
</Modal>

<!-- Add Module Modal -->
<Modal
	open={showModuleModal}
	onClose={() => (showModuleModal = false)}
	title={$t('courseForm.newModule')}
	size="medium"
>
	<form
		class="space-y-4"
		onsubmit={(e) => {
			e.preventDefault();
			createModule();
		}}
	>
		<Input
			label={$t('courseForm.moduleTitle')}
			placeholder={$t('courseForm.moduleTitlePlaceholder')}
			bind:value={newModule.title}
			required
		/>
		<div class="space-y-1.5">
			<label
				for="module-description"
				class="block text-sm font-medium text-gray-800 dark:text-gray-200"
			>
				{$t('courseForm.moduleDescription')}
			</label>
			<textarea
				id="module-description"
				rows="3"
				bind:value={newModule.description}
				class="focus:ring-primary-500 block w-full rounded-xl border-0 bg-white px-3.5 py-2.5 text-sm text-gray-900 shadow-xs ring-1 ring-gray-200 ring-inset focus:ring-2 focus:outline-none dark:bg-white/5 dark:text-white dark:ring-white/10"
			></textarea>
		</div>
		<div class="flex justify-end gap-2 pt-2">
			<Button variant="outline" onclick={() => (showModuleModal = false)}>
				{$t('courseForm.cancel')}
			</Button>
			<Button type="submit" loading={creatingModule} disabled={!newModule.title.trim()}>
				{creatingModule ? $t('courseForm.adding') : $t('courseForm.addModule')}
			</Button>
		</div>
	</form>
</Modal>

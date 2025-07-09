<script>
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t } from '$lib/i18n/index.js';
import { isTeacher } from '$lib/utils/helpers.js';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Steps from '$lib/components/common/Steps.svelte';

	// State variables
	let categories = $state([]);
	let loading = $state(true);
	let creating = $state(false);
	let uploading = $state(false);
	let error = $state('');
	let currentStep = $state(1);

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
		is_featured: false,
		enrollment_limit: null
	});

	let thumbnailFile = $state(null);
	let thumbnailPreview = $state(null);
	let validationErrors = $state({});

	// Step configuration
	const steps = [
		{ id: 1, title: 'Basic Info', completed: false },
		{ id: 2, title: 'Details', completed: false },
		{ id: 3, title: 'Content', completed: false },
		{ id: 4, title: 'Review', completed: false }
	];

	// Form options
	const levelOptions = [
		{ value: 'beginner', label: 'Beginner' },
		{ value: 'intermediate', label: 'Intermediate' },
		{ value: 'advanced', label: 'Advanced' }
	];

	const languageOptions = [
		{ value: 'en', label: 'English' },
		{ value: 'ar', label: 'Arabic' }
	];

	onMount(async () => {
		// Check authorization
		if (!isTeacher($currentUser)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: 'You need to be a teacher to create courses'
			});
			goto('/dashboard');
			return;
		}

		await loadCategories();
		loading = false;
	});

	async function loadCategories() {
		try {
			const response = await coursesApi.getCategories();
			categories = response.results || response || [];
		} catch (err) {
			console.error('Failed to load categories:', err);
			categories = [];
		}
	}

	function validateStep(step) {
		const errors = {};

		if (step === 1) {
			if (!courseData.title?.trim()) {
				errors.title = 'Course title is required';
			}
			if (!courseData.short_description?.trim()) {
				errors.short_description = 'Short description is required';
			}
			if (courseData.short_description?.length > 255) {
				errors.short_description = 'Short description must be less than 255 characters';
			}
			if (!courseData.category) {
				errors.category = 'Please select a category';
			}
		}

		if (step === 2) {
			if (!courseData.description?.trim()) {
				errors.description = 'Full description is required';
			}
			if (courseData.duration_hours < 1) {
				errors.duration_hours = 'Duration must be at least 1 hour';
			}
		}

		if (step === 3) {
			if (!courseData.learning_outcomes?.trim()) {
				errors.learning_outcomes = 'Learning outcomes are required';
			}
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	}

	function nextStep() {
		if (validateStep(currentStep)) {
			steps[currentStep - 1].completed = true;
			if (currentStep < 4) {
				currentStep++;
			}
		} else {
			uiStore.showNotification({
				type: 'error',
				title: 'Validation Error',
				message: 'Please fix the errors before continuing'
			});
		}
	}

	function prevStep() {
		if (currentStep > 1) {
			currentStep--;
		}
	}

	function goToStep(step) {
		if (step <= currentStep || steps[step - 1].completed) {
			currentStep = step;
		}
	}

	async function createCourse() {
		// Validate all steps
		for (let i = 1; i <= 3; i++) {
			if (!validateStep(i)) {
				uiStore.showNotification({
					type: 'error',
					title: 'Validation Error',
					message: `Please fix errors in step ${i}`
				});
				currentStep = i;
				return;
			}
		}

		creating = true;
		try {
			// Prepare course payload
			const coursePayload = {
				title: courseData.title.trim(),
				short_description: courseData.short_description.trim(),
				description: courseData.description.trim(),
				category: courseData.category,
				level: courseData.level,
				language: courseData.language,
				duration_hours: parseInt(courseData.duration_hours),
				is_featured: courseData.is_featured,
				status: 'draft' // Always start as draft
			};

			// Add optional fields
			if (courseData.slug?.trim()) {
				coursePayload.slug = courseData.slug.trim();
			}
			if (courseData.enrollment_limit && parseInt(courseData.enrollment_limit) > 0) {
				coursePayload.enrollment_limit = parseInt(courseData.enrollment_limit);
			}
			if (courseData.prerequisites?.trim()) {
				coursePayload.prerequisites = courseData.prerequisites.trim();
			}
			if (courseData.learning_outcomes?.trim()) {
				coursePayload.learning_outcomes = courseData.learning_outcomes.trim();
			}

			// Create the course
			const response = await coursesApi.createCourse(coursePayload);
			const newCourse = response;

			// Upload thumbnail if provided
			if (thumbnailFile) {
				await uploadThumbnail(newCourse.uuid);
			}

			uiStore.showNotification({
				type: 'success',
				title: 'Course Created',
				message: 'Your course has been created successfully'
			});

			// Redirect to course management
			goto(`/teacher/courses/${newCourse.uuid}/manage`);

		} catch (err) {
			console.error('Failed to create course:', err);
			
			uiStore.showNotification({
				type: 'error',
				title: 'Creation Failed',
				message: err.message || 'Failed to create course'
			});
		} finally {
			creating = false;
		}
	}

	async function uploadThumbnail(courseId) {
		if (!thumbnailFile) return;

		uploading = true;
		try {
			await coursesApi.uploadCourseImage(courseId, thumbnailFile);
		} catch (err) {
			console.warn('Failed to upload thumbnail:', err);
			// Don't throw error - course was created successfully
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
				title: 'Invalid File Type',
				message: 'Please upload a JPEG, PNG, or WebP image'
			});
			return;
		}

		// Validate file size (5MB limit)
		if (file.size > 5 * 1024 * 1024) {
			uiStore.showNotification({
				type: 'error',
				title: 'File Too Large',
				message: 'Please upload an image smaller than 5MB'
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

	function generateSlug() {
		if (courseData.title) {
			courseData.slug = courseData.title
				.toLowerCase()
				.replace(/[^a-z0-9]+/g, '-')
				.replace(/^-+|-+$/g, '');
		}
	}

	function formatFileSize(bytes) {
		if (bytes === 0) return '0 Bytes';
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
	}
</script>

<svelte:head>
	<title>Create Course | E-Learning Platform</title>
	<meta name="description" content="Create a new course and start teaching" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="container mx-auto max-w-4xl px-4 py-8">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="flex items-center gap-4 mb-4">
				<Button
					href="/teacher/courses"
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
				Create New Course
			</h1>
			<p class="text-gray-600 dark:text-gray-400">
				Share your knowledge and create an engaging learning experience
			</p>
		</div>

		<!-- Error State -->
		{#if error}
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Error Loading Form</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={() => window.location.reload()} variant="primary" size="medium">
					Try Again
				</Button>
			</div>
		{:else if loading}
			<!-- Loading State -->
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
		{:else}
			<!-- Steps Indicator -->
			<div class="mb-8" in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<Steps {steps} {currentStep} onStepClick={goToStep} />
			</div>

			<!-- Form Content -->
			<div in:fly={{ y: 20, delay: 200, duration: 600 }}>
				{#if currentStep === 1}
					<!-- Step 1: Basic Information -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
							Basic Information
						</h3>
						
						<div class="space-y-6">
							<Input
								label="Course Title *"
								bind:value={courseData.title}
								error={validationErrors.title}
								placeholder="Enter course title"
								onchange={generateSlug}
							/>

							<Input
								label="URL Slug"
								bind:value={courseData.slug}
								placeholder="course-url-slug"
								helperText="Leave empty to auto-generate from title"
							/>

							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Category *
								</label>
								<select
									bind:value={courseData.category}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									class:border-red-300={validationErrors.category}
								>
									<option value="">Select a category</option>
									{#each categories as category}
										<option value={category.uuid}>{category.name}</option>
									{/each}
								</select>
								{#if validationErrors.category}
									<p class="mt-1 text-sm text-red-600">{validationErrors.category}</p>
								{/if}
							</div>

							<Input
								label="Short Description *"
								bind:value={courseData.short_description}
								error={validationErrors.short_description}
								placeholder="Brief description (max 255 characters)"
								maxlength="255"
							/>

							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Level
									</label>
									<select
										bind:value={courseData.level}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										{#each levelOptions as level}
											<option value={level.value}>{level.label}</option>
										{/each}
									</select>
								</div>

								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Language
									</label>
									<select
										bind:value={courseData.language}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										{#each languageOptions as language}
											<option value={language.value}>{language.label}</option>
										{/each}
									</select>
								</div>
							</div>
						</div>

						<div class="flex justify-end mt-6">
							<Button onclick={nextStep} variant="primary" size="medium">
								Next Step
							</Button>
						</div>
					</Card>

				{:else if currentStep === 2}
					<!-- Step 2: Details -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
							Course Details
						</h3>
						
						<div class="space-y-6">
							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Full Description *
								</label>
								<textarea
									bind:value={courseData.description}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="6"
									placeholder="Detailed course description"
									class:border-red-300={validationErrors.description}
								></textarea>
								{#if validationErrors.description}
									<p class="mt-1 text-sm text-red-600">{validationErrors.description}</p>
								{/if}
							</div>

							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<Input
									label="Duration (hours) *"
									type="number"
									bind:value={courseData.duration_hours}
									error={validationErrors.duration_hours}
									min="1"
									placeholder="1"
								/>

								<Input
									label="Enrollment Limit"
									type="number"
									bind:value={courseData.enrollment_limit}
									placeholder="Leave empty for unlimited"
								/>
							</div>

							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Prerequisites
								</label>
								<textarea
									bind:value={courseData.prerequisites}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="3"
									placeholder="What students should know before taking this course"
								></textarea>
							</div>

							<div>
								<label class="flex items-center">
									<input
										type="checkbox"
										bind:checked={courseData.is_featured}
										class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
									/>
									<span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
										Feature this course (promote visibility)
									</span>
								</label>
							</div>
						</div>

						<div class="flex justify-between mt-6">
							<Button onclick={prevStep} variant="outline" size="medium">
								Previous
							</Button>
							<Button onclick={nextStep} variant="primary" size="medium">
								Next Step
							</Button>
						</div>
					</Card>

				{:else if currentStep === 3}
					<!-- Step 3: Content -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
							Course Content
						</h3>
						
						<div class="space-y-6">
							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Learning Outcomes *
								</label>
								<textarea
									bind:value={courseData.learning_outcomes}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="4"
									placeholder="What will students learn and achieve?"
									class:border-red-300={validationErrors.learning_outcomes}
								></textarea>
								{#if validationErrors.learning_outcomes}
									<p class="mt-1 text-sm text-red-600">{validationErrors.learning_outcomes}</p>
								{/if}
							</div>

							<!-- Course Thumbnail -->
							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Course Thumbnail
								</label>
								
								<div class="flex flex-col lg:flex-row gap-6">
									{#if thumbnailPreview}
										<div class="lg:w-64">
											<img 
												src={thumbnailPreview} 
												alt="Course thumbnail"
												class="w-full h-36 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
											/>
											<div class="mt-2 text-sm text-gray-500 dark:text-gray-400">
												{thumbnailFile ? formatFileSize(thumbnailFile.size) : ''}
											</div>
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
							</div>
						</div>

						<div class="flex justify-between mt-6">
							<Button onclick={prevStep} variant="outline" size="medium">
								Previous
							</Button>
							<Button onclick={nextStep} variant="primary" size="medium">
								Review & Create
							</Button>
						</div>
					</Card>

				{:else if currentStep === 4}
					<!-- Step 4: Review -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
							Review & Create Course
						</h3>
						
						<div class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div>
									<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Basic Information</h4>
									<div class="space-y-2 text-sm">
										<p><span class="font-medium">Title:</span> {courseData.title}</p>
										<p><span class="font-medium">Category:</span> {categories.find(c => c.uuid === courseData.category)?.name || 'None'}</p>
										<p><span class="font-medium">Level:</span> {courseData.level}</p>
										<p><span class="font-medium">Language:</span> {courseData.language === 'en' ? 'English' : 'Arabic'}</p>
										<p><span class="font-medium">Duration:</span> {courseData.duration_hours} hours</p>
									</div>
								</div>

								<div>
									<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Settings</h4>
									<div class="space-y-2 text-sm">
										<p><span class="font-medium">Enrollment Limit:</span> {courseData.enrollment_limit || 'Unlimited'}</p>
										<p><span class="font-medium">Featured:</span> {courseData.is_featured ? 'Yes' : 'No'}</p>
										<p><span class="font-medium">Status:</span> Draft</p>
										<p><span class="font-medium">Thumbnail:</span> {thumbnailFile ? 'Uploaded' : 'None'}</p>
									</div>
								</div>
							</div>

							<div>
								<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Short Description</h4>
								<p class="text-sm text-gray-600 dark:text-gray-400">{courseData.short_description}</p>
							</div>

							<div>
								<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Learning Outcomes</h4>
								<p class="text-sm text-gray-600 dark:text-gray-400">{courseData.learning_outcomes}</p>
							</div>

							{#if courseData.prerequisites}
								<div>
									<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Prerequisites</h4>
									<p class="text-sm text-gray-600 dark:text-gray-400">{courseData.prerequisites}</p>
								</div>
							{/if}

							<div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
								<h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Next Steps</h4>
								<ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
									<li>• Your course will be created in draft mode</li>
									<li>• You can add modules and lessons after creation</li>
									<li>• Publish your course when ready for students</li>
								</ul>
							</div>
						</div>

						<div class="flex justify-between mt-6">
							<Button onclick={prevStep} variant="outline" size="medium">
								Previous
							</Button>
							<Button
								onclick={createCourse}
								variant="success"
								size="medium"
								disabled={creating}
								loading={creating}
							>
								{creating ? 'Creating...' : 'Create Course'}
							</Button>
						</div>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</div>
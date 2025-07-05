<!-- front/src/routes/(app)/courses/create/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { classNames } from '$lib/utils/helpers.js';
	
	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Badge from '$lib/components/common/Badge.svelte';

	// Check if user can create courses
	let canCreateCourse = $derived($currentUser?.role === 'teacher' || $currentUser?.is_staff);

	let currentStep = $state(1);
	let saving = $state(false);
	let validationErrors = $state({});

	let courseData = $state({
		// Basic Info
		title: '',
		slug: '',
		short_description: '',
		description: '',

		// Category & Tags
		category: '',
		tags: [],

		// Settings
		level: 'beginner',
		language: 'en',
		duration_hours: 1,

		// Requirements
		prerequisites: '',
		learning_outcomes: '',

		// Pricing & Access
		price: 0,
		enrollment_limit: null,

		// Status
		status: 'draft',
		is_featured: false
	});

	let categories = $state([]);
	let tagInput = $state('');

	onMount(async () => {
		// Redirect if user can't create courses
		if (!canCreateCourse) {
			uiStore.showNotification({
				type: 'error',
				title: 'Access Denied',
				message: 'You need to be a teacher to create courses.'
			});
			goto('/courses');
			return;
		}

		await fetchCategories();
	});

	// Auto-generate slug from title
	$effect(() => {
		if (courseData.title && !courseData.slug) {
			courseData.slug = courseData.title
				.toLowerCase()
				.replace(/[^a-z0-9]+/g, '-')
				.replace(/(^-|-$)/g, '');
		}
	});

	async function fetchCategories() {
		try {
			const response = await coursesApi.getCategories();
			categories = Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : [];
		} catch (error) {
			console.error('Failed to fetch categories:', error);
			categories = [];
		}
	}

	function addTag() {
		const tag = tagInput.trim();
		if (tag && !courseData.tags.includes(tag)) {
			courseData.tags = [...courseData.tags, tag];
			tagInput = '';
		}
	}

	function removeTag(tag) {
		courseData.tags = courseData.tags.filter((t) => t !== tag);
	}

	function validateStep(step) {
		const errors = {};

		switch (step) {
			case 1:
				if (!courseData.title?.trim()) {
					errors.title = 'Course title is required';
				}
				if (!courseData.short_description?.trim()) {
					errors.short_description = 'Short description is required';
				}
				if (!courseData.description?.trim()) {
					errors.description = 'Full description is required';
				}
				if (courseData.short_description?.length > 255) {
					errors.short_description = 'Short description must be less than 255 characters';
				}
				break;
			case 2:
				if (!courseData.category) {
					errors.category = 'Please select a category';
				}
				if (courseData.duration_hours < 1) {
					errors.duration_hours = 'Duration must be at least 1 hour';
				}
				if (courseData.enrollment_limit && courseData.enrollment_limit < 1) {
					errors.enrollment_limit = 'Enrollment limit must be at least 1';
				}
				break;
			case 3:
				if (!courseData.learning_outcomes?.trim()) {
					errors.learning_outcomes = 'Learning outcomes are required';
				}
				break;
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	}

	function nextStep() {
		if (validateStep(currentStep)) {
			currentStep = Math.min(currentStep + 1, 4);
		} else {
			uiStore.showNotification({
				type: 'error',
				title: 'Validation Error',
				message: 'Please fix the errors before continuing'
			});
		}
	}

	function previousStep() {
		currentStep = Math.max(currentStep - 1, 1);
		validationErrors = {}; // Clear errors when going back
	}

	async function saveCourse() {
		// Validate all steps
		for (let step = 1; step <= 3; step++) {
			if (!validateStep(step)) {
				currentStep = step;
				uiStore.showNotification({
					type: 'error',
					title: 'Validation Error',
					message: 'Please fix all errors before creating the course'
				});
				return;
			}
		}

		saving = true;
		try {
			// Prepare data for API
			const coursePayload = {
				...courseData,
				// Convert tags to proper format
				tags: courseData.tags.map((tag) => ({ name: tag, slug: tag.toLowerCase().replace(/\s+/g, '-') })),
				// Ensure instructor is set
				instructor: $currentUser.uuid,
				// Convert price to number
				price: parseFloat(courseData.price) || 0,
				// Convert duration to number
				duration_hours: parseInt(courseData.duration_hours) || 1,
				// Convert enrollment limit
				enrollment_limit: courseData.enrollment_limit ? parseInt(courseData.enrollment_limit) : null
			};

			const response = await coursesApi.createCourse(coursePayload);

			uiStore.showNotification({
				type: 'success',
				title: 'Course Created Successfully!',
				message: 'Your course has been created. You can now add modules and lessons.'
			});

			// Redirect to course management page
			goto(`/teacher/courses/${response.uuid}/manage`);
		} catch (error) {
			console.error('Failed to create course:', error);
			
			let errorMessage = 'Failed to create course. Please try again.';
			
			// Handle specific API errors
			if (error.response?.data) {
				if (typeof error.response.data === 'string') {
					errorMessage = error.response.data;
				} else if (error.response.data.detail) {
					errorMessage = error.response.data.detail;
				} else if (error.response.data.non_field_errors) {
					errorMessage = error.response.data.non_field_errors[0];
				} else {
					// Handle field-specific errors
					const fieldErrors = Object.values(error.response.data).flat();
					if (fieldErrors.length > 0) {
						errorMessage = fieldErrors[0];
					}
				}
			} else if (error.message) {
				errorMessage = error.message;
			}

			uiStore.showNotification({
				type: 'error',
				title: 'Creation Failed',
				message: errorMessage
			});
		} finally {
			saving = false;
		}
	}

	const steps = [
		{ number: 1, title: 'Basic Information', icon: '📝', description: 'Course title and description' },
		{ number: 2, title: 'Category & Settings', icon: '⚙️', description: 'Category, level, and settings' },
		{ number: 3, title: 'Learning Outcomes', icon: '🎯', description: 'What students will learn' },
		{ number: 4, title: 'Review & Create', icon: '✅', description: 'Review and create course' }
	];

	const levelOptions = [
		{ value: 'beginner', label: 'Beginner', description: 'No prior experience required' },
		{ value: 'intermediate', label: 'Intermediate', description: 'Some experience helpful' },
		{ value: 'advanced', label: 'Advanced', description: 'Significant experience required' }
	];
</script>

<svelte:head>
	<title>Create New Course - 244SCHOOL</title>
	<meta name="description" content="Create and share your knowledge with students around the world" />
</svelte:head>

{#if !canCreateCourse}
	<!-- Access Denied -->
	<div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
		<Card variant="bordered" class="max-w-md text-center p-8">
			<div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/20">
				<svg class="h-8 w-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
				</svg>
			</div>
			<h3 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">Access Denied</h3>
			<p class="mb-6 text-gray-600 dark:text-gray-400">You need to be a teacher to create courses.</p>
			<Button href="/courses" variant="primary">Browse Courses</Button>
		</Card>
	</div>
{:else}
	<div class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
		<div class="container mx-auto max-w-4xl px-4 py-8">
			<!-- Header -->
			<div class="mb-8" in:fade={{ duration: 600 }}>
				<div class="mb-4 flex items-center gap-4">
					<Button
						href="/my-courses"
						variant="ghost"
						size="medium"
						class="text-gray-600 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400"
					>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
						</svg>
						Back to My Courses
					</Button>
				</div>

				<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">Create New Course</h1>
				<p class="text-gray-600 dark:text-gray-400">
					Share your knowledge and create an engaging learning experience for students worldwide
				</p>
			</div>

			<!-- Progress Steps -->
			<div class="mb-8" in:fly={{ y: 20, delay: 200, duration: 600 }}>
				<div class="flex items-center justify-between">
					{#each steps as step, index}
						<div class="relative flex-1">
							<div class="flex items-center">
								<div
									class="relative z-10 flex h-12 w-12 items-center justify-center rounded-full {currentStep >= step.number
										? 'bg-primary-600 text-white shadow-lg'
										: 'bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400'} transition-all duration-300"
								>
									{#if currentStep > step.number}
										<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
										</svg>
									{:else}
										<span class="text-lg">{step.icon}</span>
									{/if}
								</div>
								{#if index < steps.length - 1}
									<div
										class="mx-2 h-1 flex-1 {currentStep > step.number
											? 'bg-primary-600'
											: 'bg-gray-200 dark:bg-gray-700'} transition-all duration-300"
									></div>
								{/if}
							</div>
							<div class="mt-3 text-center">
								<p
									class="text-sm font-medium {currentStep >= step.number
										? 'text-gray-900 dark:text-white'
										: 'text-gray-500 dark:text-gray-400'}"
								>
									{step.title}
								</p>
								<p class="text-xs text-gray-500 dark:text-gray-400">{step.description}</p>
							</div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Form Content -->
			<div in:fly={{ y: 30, delay: 400, duration: 600 }}>
				<Card variant="bordered" class="mb-8 shadow-xl">
					{#if currentStep === 1}
						<!-- Step 1: Basic Information -->
						<div class="space-y-6">
							<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">Basic Information</h2>

							<Input
								label="Course Title *"
								bind:value={courseData.title}
								error={validationErrors.title}
								placeholder="e.g., Complete Web Development Bootcamp"
								helperText="Choose a clear, descriptive title that tells students what they'll learn"
							/>

							<Input
								label="URL Slug *"
								bind:value={courseData.slug}
								error={validationErrors.slug}
								placeholder="complete-web-development-bootcamp"
								helperText="This will be used in the course URL. It's automatically generated from your title."
							/>

							<div>
								<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
									Short Description *
								</label>
								<textarea
									bind:value={courseData.short_description}
									rows="3"
									maxlength="255"
									class={classNames(
										"w-full rounded-lg border bg-white px-3 py-2 text-sm focus:ring-2 dark:bg-gray-800",
										validationErrors.short_description
											? "border-red-300 focus:border-red-500 focus:ring-red-500"
											: "border-gray-300 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600"
									)}
									placeholder="A brief, compelling description that appears in course listings"
								></textarea>
								<div class="mt-1 flex justify-between text-xs">
									<span class={validationErrors.short_description ? "text-red-600" : "text-gray-500"}>
										{validationErrors.short_description || 'This appears in search results and course listings'}
									</span>
									<span class="text-gray-500 dark:text-gray-400">
										{courseData.short_description.length}/255
									</span>
								</div>
							</div>

							<div>
								<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
									Full Description *
								</label>
								<textarea
									bind:value={courseData.description}
									rows="8"
									class={classNames(
										"w-full rounded-lg border bg-white px-3 py-2 text-sm focus:ring-2 dark:bg-gray-800",
										validationErrors.description
											? "border-red-300 focus:border-red-500 focus:ring-red-500"
											: "border-gray-300 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600"
									)}
									placeholder="Provide a detailed description of what students will learn, including key topics, projects, and outcomes"
								></textarea>
								{#if validationErrors.description}
									<p class="mt-1 text-xs text-red-600">{validationErrors.description}</p>
								{/if}
							</div>
						</div>
					{:else if currentStep === 2}
						<!-- Step 2: Category & Settings -->
						<div class="space-y-6">
							<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">Category & Settings</h2>

							<div>
								<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
									Category *
								</label>
								<select
									bind:value={courseData.category}
									class={classNames(
										"w-full rounded-lg border bg-white px-3 py-2 text-sm focus:ring-2 dark:bg-gray-800",
										validationErrors.category
											? "border-red-300 focus:border-red-500 focus:ring-red-500"
											: "border-gray-300 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600"
									)}
								>
									<option value="">Select a category</option>
									{#each categories as category}
										<option value={category.uuid}>{category.name}</option>
									{/each}
								</select>
								{#if validationErrors.category}
									<p class="mt-1 text-xs text-red-600">{validationErrors.category}</p>
								{/if}
							</div>

							<div>
								<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
									Tags
								</label>
								<div class="mb-2 flex gap-2">
									<input
										bind:value={tagInput}
										onkeydown={(e) => {
											if (e.key === 'Enter') {
												e.preventDefault();
												addTag();
											}
										}}
										placeholder="Add tags to help students find your course"
										class="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-800"
									/>
									<Button type="button" onclick={addTag} variant="outline" size="small">
										Add
									</Button>
								</div>
								<div class="flex flex-wrap gap-2">
									{#each courseData.tags as tag}
										<Badge variant="info" class="flex items-center gap-1">
											{tag}
											<button
												type="button"
												onclick={() => removeTag(tag)}
												class="ml-1 text-current hover:text-red-500"
											>
												×
											</button>
										</Badge>
									{/each}
								</div>
							</div>

							<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
								<div>
									<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
										Level *
									</label>
									<select
										bind:value={courseData.level}
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-800"
									>
										{#each levelOptions as option}
											<option value={option.value}>{option.label} - {option.description}</option>
										{/each}
									</select>
								</div>

								<div>
									<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
										Language *
									</label>
									<select
										bind:value={courseData.language}
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-800"
									>
										<option value="en">English</option>
										<option value="ar">Arabic</option>
									</select>
								</div>
							</div>

							<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
								<Input
									type="number"
									label="Duration (hours) *"
									bind:value={courseData.duration_hours}
									error={validationErrors.duration_hours}
									min="1"
									step="0.5"
									helperText="Estimated time to complete the course"
								/>

								<Input
									type="number"
									label="Enrollment Limit"
									bind:value={courseData.enrollment_limit}
									error={validationErrors.enrollment_limit}
									min="1"
									placeholder="Leave empty for unlimited"
									helperText="Maximum number of students (optional)"
								/>
							</div>

							<Input
								type="number"
								label="Price ($)"
								bind:value={courseData.price}
								min="0"
								step="0.01"
								placeholder="0"
								helperText="Set to 0 for free courses"
							/>
						</div>
					{:else if currentStep === 3}
						<!-- Step 3: Learning Outcomes -->
						<div class="space-y-6">
							<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">Learning Outcomes</h2>

							<div>
								<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
									Prerequisites
								</label>
								<textarea
									bind:value={courseData.prerequisites}
									rows="4"
									class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-800"
									placeholder="What should students know before taking this course? (optional)&#10;&#10;Example:&#10;• Basic computer skills&#10;• No programming experience required&#10;• Access to a computer with internet"
								></textarea>
							</div>

							<div>
								<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
									Learning Outcomes *
								</label>
								<textarea
									bind:value={courseData.learning_outcomes}
									rows="8"
									class={classNames(
										"w-full rounded-lg border bg-white px-3 py-2 text-sm focus:ring-2 dark:bg-gray-800",
										validationErrors.learning_outcomes
											? "border-red-300 focus:border-red-500 focus:ring-red-500"
											: "border-gray-300 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600"
									)}
									placeholder="What will students be able to do after completing this course?&#10;&#10;Example:&#10;• Build responsive websites using HTML, CSS, and JavaScript&#10;• Create dynamic web applications with React&#10;• Deploy applications to the cloud&#10;• Understand modern web development best practices"
								></textarea>
								{#if validationErrors.learning_outcomes}
									<p class="mt-1 text-xs text-red-600">{validationErrors.learning_outcomes}</p>
								{:else}
									<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										List specific, measurable skills and knowledge students will gain
									</p>
								{/if}
							</div>
						</div>
					{:else if currentStep === 4}
						<!-- Step 4: Review & Create -->
						<div class="space-y-6">
							<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">Review & Create</h2>

							<div class="space-y-6 rounded-lg bg-gray-50 p-6 dark:bg-gray-800/50">
								<h3 class="mb-4 font-semibold text-gray-900 dark:text-white">Course Summary</h3>

								<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
									<div class="space-y-4">
										<div>
											<span class="text-sm text-gray-500 dark:text-gray-400">Title:</span>
											<p class="font-medium text-gray-900 dark:text-white">{courseData.title}</p>
										</div>

										<div>
											<span class="text-sm text-gray-500 dark:text-gray-400">Level:</span>
											<p class="font-medium text-gray-900 capitalize dark:text-white">{courseData.level}</p>
										</div>

										<div>
											<span class="text-sm text-gray-500 dark:text-gray-400">Duration:</span>
											<p class="font-medium text-gray-900 dark:text-white">
												{courseData.duration_hours} hours
											</p>
										</div>

										<div>
											<span class="text-sm text-gray-500 dark:text-gray-400">Language:</span>
											<p class="font-medium text-gray-900 dark:text-white">
												{courseData.language === 'en' ? 'English' : 'Arabic'}
											</p>
										</div>
									</div>

									<div class="space-y-4">
										<div>
											<span class="text-sm text-gray-500 dark:text-gray-400">Price:</span>
											<p class="font-medium text-gray-900 dark:text-white">
												{courseData.price > 0 ? `$${courseData.price}` : 'Free'}
											</p>
										</div>

										{#if courseData.enrollment_limit}
											<div>
												<span class="text-sm text-gray-500 dark:text-gray-400">Enrollment Limit:</span>
												<p class="font-medium text-gray-900 dark:text-white">
													{courseData.enrollment_limit} students
												</p>
											</div>
										{/if}

										{#if courseData.tags.length > 0}
											<div>
												<span class="text-sm text-gray-500 dark:text-gray-400">Tags:</span>
												<div class="mt-1 flex flex-wrap gap-1">
													{#each courseData.tags as tag}
														<Badge variant="outline" size="small">{tag}</Badge>
													{/each}
												</div>
											</div>
										{/if}
									</div>
								</div>

								<div class="border-t border-gray-200 pt-4 dark:border-gray-700">
									<span class="text-sm text-gray-500 dark:text-gray-400">Description:</span>
									<p class="mt-1 text-gray-900 dark:text-white">{courseData.short_description}</p>
								</div>
							</div>

							<div class="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
								<div class="flex items-start gap-3">
									<svg class="mt-0.5 h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									<div>
										<p class="text-sm font-medium text-blue-800 dark:text-blue-200">
											Ready to create your course?
										</p>
										<p class="text-sm text-blue-700 dark:text-blue-300">
											Your course will be created as a draft. You can add modules, lessons, and content after creation, then publish when ready.
										</p>
									</div>
								</div>
							</div>
						</div>
					{/if}
				</Card>
			</div>

			<!-- Navigation Buttons -->
			<div class="flex justify-between" in:fly={{ y: 20, delay: 600, duration: 600 }}>
				<Button 
					variant="outline" 
					onclick={previousStep} 
					disabled={currentStep === 1}
					class="transition-all"
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
					Previous
				</Button>

				{#if currentStep < 4}
					<Button variant="primary" onclick={nextStep} class="transition-all">
						Next
						<svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
						</svg>
					</Button>
				{:else}
					<Button 
						variant="primary" 
						onclick={saveCourse} 
						loading={saving}
						disabled={saving}
						class="transition-all hover:scale-105"
						size="large"
					>
						{#if saving}
							<svg class="mr-2 h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
							Creating Course...
						{:else}
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Create Course
						{/if}
					</Button>
				{/if}
			</div>
		</div>
	</div>
{/if}
<!-- front/src/routes/(app)/courses/create/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { browser } from '$app/environment';
	import { coursesApi } from '$lib/apis/courses.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { classNames, debounce } from '$lib/utils/helpers.js';
	import { APP_NAME } from '$lib/utils/constants.js';
	
	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Select from '$lib/components/common/Select.svelte';
	import Badge from '$lib/components/common/Badge.svelte';

	// State management with Svelte 5 runes
	let saving = $state(false);
	let loading = $state(false);
	let validationErrors = $state({});
	let autoSaveTimer;

	let courseData = $state({
		title: '',
		slug: '',
		short_description: '',
		description: '',
		category: null, // Changed to null instead of empty string
		tags: [],
		level: 'beginner',
		language: 'en',
		duration_hours: 1,
		prerequisites: '',
		learning_outcomes: '',
		enrollment_limit: null,
		status: 'draft',
		is_featured: false
	});

	let categories = $state([]);
	let tagInput = $state('');
	let thumbnailFile = $state(null);
	let thumbnailPreview = $state(null);

	// Derived states
	let isFormValid = $derived.by(() => {
		return courseData.title?.trim() && 
			   courseData.short_description?.trim() && 
			   courseData.description?.trim() && 
			   courseData.learning_outcomes?.trim();
	});

	let canCreateCourse = $derived(() => {
		const user = $currentUser;
		return user && (user.role === 'teacher' || user.is_staff);
	});

	// Auto-generate slug from title
	const generateSlug = debounce((title) => {
		if (title && (!courseData.slug || courseData.slug === '')) {
			courseData.slug = title
				.toLowerCase()
				.trim()
				.replace(/[^a-z0-9\s-]/g, '') // Remove special characters
				.replace(/\s+/g, '-') // Replace spaces with hyphens
				.replace(/-+/g, '-') // Replace multiple hyphens with single
				.replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
		}
	}, 300);

	// Auto-save draft functionality
	const autoSaveDraft = debounce(() => {
		if (browser && courseData.title?.trim()) {
			try {
				localStorage.setItem('course_draft', JSON.stringify(courseData));
			} catch (err) {
				console.warn('Failed to save draft:', err);
			}
		}
	}, 2000);

	$effect(() => {
		if (courseData.title) {
			generateSlug(courseData.title);
			autoSaveDraft();
		}
	});

	onMount(async () => {
		// Check authentication first
		if (!$currentUser) {
			uiStore.showNotification({
				type: 'error',
				title: 'Authentication Required',
				message: 'Please log in to create courses.'
			});
			goto('/auth/login');
			return;
		}

		// Check permissions
		if (!canCreateCourse) {
			uiStore.showNotification({
				type: 'error',
				title: 'Access Denied',
				message: 'You need to be a teacher to create courses.'
			});
			goto('/courses');
			return;
		}

		loading = true;
		try {
			await fetchCategories();
			loadDraft();
		} catch (err) {
			console.error('Initialization error:', err);
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: 'Failed to load course creation form'
			});
		} finally {
			loading = false;
		}
	});

	onDestroy(() => {
		if (autoSaveTimer) clearTimeout(autoSaveTimer);
	});

	function loadDraft() {
		if (browser) {
			try {
				const saved = localStorage.getItem('course_draft');
				if (saved) {
					const draft = JSON.parse(saved);
					if (draft.title?.trim()) {
						courseData = { ...courseData, ...draft };
					}
				}
			} catch (err) {
				console.warn('Failed to load draft:', err);
			}
		}
	}

	function clearDraft() {
		if (browser) {
			try {
				localStorage.removeItem('course_draft');
			} catch (err) {
				console.warn('Failed to clear draft:', err);
			}
		}
	}

	async function fetchCategories() {
		try {
			const response = await coursesApi.getCategories();
			console.log('Categories API response:', response);
			categories = Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : [];
			console.log('Processed categories:', categories);
			console.log('Categories count:', categories.length);
			
			if (categories.length === 0) {
				console.log('⚠️ No categories available in database');
			}
		} catch (error) {
			console.error('Failed to fetch categories:', error);
			categories = [];
			console.log('⚠️ Failed to load categories, proceeding without category options');
		}
	}

	function addTag() {
		const tag = tagInput.trim();
		if (tag && !courseData.tags.includes(tag) && tag.length <= 50) {
			courseData.tags = [...courseData.tags, tag];
			tagInput = '';
		}
	}

	function removeTag(tag) {
		courseData.tags = courseData.tags.filter((t) => t !== tag);
	}

	function handleThumbnailChange(event) {
		const file = event.target.files[0];
		if (!file) return;

		const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
		if (!allowedTypes.includes(file.type)) {
			uiStore.showNotification({
				type: 'error',
				title: 'Invalid File Type',
				message: 'Please upload a valid image file (JPG, PNG, WebP)'
			});
			return;
		}

		const maxSize = 5 * 1024 * 1024; // 5MB
		if (file.size > maxSize) {
			uiStore.showNotification({
				type: 'error',
				title: 'File Too Large',
				message: 'Image must be smaller than 5MB'
			});
			return;
		}

		thumbnailFile = file;
		
		const reader = new FileReader();
		reader.onload = (e) => {
			thumbnailPreview = e.target.result;
		};
		reader.readAsDataURL(file);
	}

	function removeThumbnail() {
		thumbnailFile = null;
		thumbnailPreview = null;
	}

	function validateForm() {
		const errors = {};

		// Required fields validation
		if (!courseData.title?.trim()) {
			errors.title = 'Course title is required';
		} else if (courseData.title.length > 200) {
			errors.title = 'Title must be under 200 characters';
		}

		if (!courseData.short_description?.trim()) {
			errors.short_description = 'Short description is required';
		} else if (courseData.short_description.length > 255) {
			errors.short_description = 'Short description must be under 255 characters';
		}

		if (!courseData.description?.trim()) {
			errors.description = 'Full description is required';
		}

		if (!courseData.learning_outcomes?.trim()) {
			errors.learning_outcomes = 'Learning outcomes are required';
		}

		// Numeric field validation
		const duration = parseInt(courseData.duration_hours);
		if (isNaN(duration) || duration < 1) {
			errors.duration_hours = 'Duration must be at least 1 hour';
		}

		if (courseData.enrollment_limit) {
			const limit = parseInt(courseData.enrollment_limit);
			if (isNaN(limit) || limit < 1) {
				errors.enrollment_limit = 'Enrollment limit must be a positive number';
			}
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	}

	async function saveCourse(event) {
		event.preventDefault(); // Handle the form submission event
		
		console.log('=== STARTING COURSE CREATION ===');
		
		// Check authentication again
		if (!$currentUser) {
			uiStore.showNotification({
				type: 'error',
				title: 'Authentication Required',
				message: 'Please log in to create courses.'
			});
			goto('/auth/login');
			return;
		}

		if (!validateForm()) {
			uiStore.showNotification({
				type: 'error',
				title: 'Validation Error',
				message: 'Please fix the errors before creating the course'
			});
			return;
		}

		saving = true;
		try {
			// Create clean payload that matches backend expectations exactly
			const coursePayload = {
				// Required fields - ensure they're strings and trimmed
				title: String(courseData.title || '').trim(),
				description: String(courseData.description || '').trim(),
				short_description: String(courseData.short_description || '').trim(),
				learning_outcomes: String(courseData.learning_outcomes || '').trim(),
				
				// Fields with defaults
				level: courseData.level || 'beginner',
				language: courseData.language || 'en',
				duration_hours: Math.max(1, parseInt(courseData.duration_hours) || 1),
				status: 'draft',
				is_featured: false
			};

			// Add optional fields only if they have valid values
			if (courseData.slug && courseData.slug.trim()) {
				coursePayload.slug = String(courseData.slug).trim();
			}

			// Handle category - only include if we have a valid UUID
			console.log('=== CATEGORY PROCESSING ===');
			console.log('Raw category value:', courseData.category);
			console.log('Category type:', typeof courseData.category);
			console.log('Available categories:', categories.length);
			
			if (courseData.category && 
				courseData.category !== '' && 
				courseData.category !== 'null' && 
				courseData.category !== null &&
				categories.length > 0) {
				// Verify this category exists in our loaded categories
				const categoryExists = categories.some(cat => cat.uuid === courseData.category);
				if (categoryExists) {
					coursePayload.category = String(courseData.category).trim();
					console.log('✅ Setting valid category:', coursePayload.category);
				} else {
					console.log('❌ Category not found in available categories, omitting field');
				}
			} else {
				console.log('✅ No category selected, omitting category field entirely');
			}

			// Handle enrollment limit
			if (courseData.enrollment_limit) {
				const limit = parseInt(courseData.enrollment_limit);
				if (!isNaN(limit) && limit > 0) {
					coursePayload.enrollment_limit = limit;
				}
			}

			// Handle prerequisites
			if (courseData.prerequisites && courseData.prerequisites.trim()) {
				coursePayload.prerequisites = String(courseData.prerequisites).trim();
			}

			// Handle tags - ensure it's an array of non-empty strings
			if (Array.isArray(courseData.tags) && courseData.tags.length > 0) {
				coursePayload.tags = courseData.tags
					.map(tag => String(tag || '').trim())
					.filter(tag => tag.length > 0 && tag.length <= 50);
			}

			// Debug logging
			console.log('=== CATEGORY DEBUG ===');
			console.log('Raw category value:', courseData.category);
			console.log('Category type:', typeof courseData.category);
			console.log('Category === null:', courseData.category === null);
			console.log('Category === "":', courseData.category === '');
			console.log('Available categories:', categories);
			console.log('Course payload being sent:', JSON.stringify(coursePayload, null, 2));
			console.log('Current user:', $currentUser);

			// Validate required fields one more time
			if (!coursePayload.title) {
				throw new Error('Title is required but missing');
			}
			if (!coursePayload.description) {
				throw new Error('Description is required but missing');
			}
			if (!coursePayload.short_description) {
				throw new Error('Short description is required but missing');
			}
			if (!coursePayload.learning_outcomes) {
				throw new Error('Learning outcomes are required but missing');
			}

			// Create course
			console.log('Sending request to create course...');
			const response = await coursesApi.createCourse(coursePayload);
			console.log('Course created successfully:', response);

			// Upload thumbnail if provided
			if (thumbnailFile && response.uuid) {
				try {
					console.log('Uploading thumbnail...');
					await coursesApi.uploadCourseImage(response.uuid, thumbnailFile);
					console.log('Thumbnail uploaded successfully');
				} catch (uploadError) {
					console.warn('Failed to upload thumbnail:', uploadError);
					// Don't fail the entire creation for image upload failure
				}
			}

			// Clear draft on successful creation
			clearDraft();

			uiStore.showNotification({
				type: 'success',
				title: 'Course Created!',
				message: 'Your course has been created successfully'
			});

			// Navigate to the course page
			goto(`/courses/${response.uuid}`);
		} catch (error) {
			console.error('=== COURSE CREATION ERROR ===');
			console.error('Error object:', error);
			console.error('Error message:', error.message);
			console.error('Error response:', error.response);
			
			let errorMessage = 'Failed to create course';
			
			// Handle different error types
			if (error.message === 'Authentication credentials were not provided.') {
				errorMessage = 'Please log in to create courses';
				goto('/auth/login');
				return;
			} else if (error.response?.data) {
				if (typeof error.response.data === 'string') {
					errorMessage = error.response.data;
				} else if (error.response.data.detail) {
					errorMessage = error.response.data.detail;
				} else if (error.response.data.non_field_errors) {
					const errors = Array.isArray(error.response.data.non_field_errors) 
						? error.response.data.non_field_errors 
						: [error.response.data.non_field_errors];
					errorMessage = errors.join(', ');
				} else {
					// Handle field-specific errors
					const fieldErrors = [];
					Object.entries(error.response.data).forEach(([field, errors]) => {
						if (Array.isArray(errors)) {
							fieldErrors.push(`${field}: ${errors.join(', ')}`);
						} else {
							fieldErrors.push(`${field}: ${errors}`);
						}
					});
					if (fieldErrors.length > 0) {
						errorMessage = fieldErrors.join('; ');
					}
				}
			} else if (error.message) {
				errorMessage = error.message;
			}

			console.error('Final error message:', errorMessage);

			uiStore.showNotification({
				type: 'error',
				title: 'Creation Failed',
				message: errorMessage
			});
		} finally {
			saving = false;
		}
	}

	const levelOptions = [
		{ value: 'beginner', label: 'Beginner - No prior experience needed' },
		{ value: 'intermediate', label: 'Intermediate - Some experience required' },
		{ value: 'advanced', label: 'Advanced - Extensive experience needed' }
	];
</script>

<svelte:head>
	<title>Create New Course - {APP_NAME}</title>
	<meta name="description" content="Create and share your knowledge with students worldwide" />
</svelte:head>

{#if !$currentUser}
	<!-- Not authenticated -->
	<div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
		<Card variant="bordered" class="max-w-md text-center p-8">
			<div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/20">
				<svg class="h-8 w-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
				</svg>
			</div>
			<h3 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">Authentication Required</h3>
			<p class="mb-6 text-gray-600 dark:text-gray-400">Please log in to create courses.</p>
			<Button href="/auth/login" variant="primary">Log In</Button>
		</Card>
	</div>
{:else if !canCreateCourse}
	<!-- Access denied -->
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
	<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
		<div class="container mx-auto max-w-4xl px-4 py-8">
			<!-- Header -->
			<div class="mb-8" in:fade={{ duration: 600 }}>
				<div class="mb-4 flex items-center justify-between">
					<Button
						href="/courses"
						variant="ghost"
						size="medium"
						class="text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
					>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
						</svg>
						Back to Courses
					</Button>

					{#if browser && localStorage.getItem('course_draft')}
						<Button
							variant="outline"
							size="small"
							onclick={clearDraft}
							class="text-orange-600 border-orange-300 hover:bg-orange-50"
						>
							Clear Draft
						</Button>
					{/if}
				</div>

				<div class="text-center">
					<div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
						<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
						</svg>
					</div>
					<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">Create New Course</h1>
					<p class="text-gray-600 dark:text-gray-400">
						Share your knowledge and create an engaging learning experience
					</p>
				</div>
			</div>

			{#if loading}
				<div class="flex justify-center py-12">
					<div class="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
				</div>
			{:else}
				<!-- Main Form -->
				<div in:fly={{ y: 30, delay: 200, duration: 600 }}>
					<Card variant="bordered" class="shadow-xl">
						<form onsubmit={saveCourse} class="space-y-8">
							<!-- Basic Information -->
							<div class="space-y-6">
								<div class="border-b border-gray-200 pb-4 dark:border-gray-700">
									<h2 class="text-xl font-semibold text-gray-900 dark:text-white">Course Information</h2>
									<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Basic details about your course</p>
								</div>

								<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
									<div class="lg:col-span-2">
										<Input
											label="Course Title"
											bind:value={courseData.title}
											error={validationErrors.title}
											placeholder="e.g., Complete Web Development Bootcamp"
											required
											maxlength="200"
											class="text-lg font-medium"
										/>
									</div>

									<Input
										label="URL Slug"
										bind:value={courseData.slug}
										error={validationErrors.slug}
										placeholder="Auto-generated from title"
										helperText="This will be used in the course URL"
										maxlength="200"
									/>

									<Select
										label="Category"
										bind:value={courseData.category}
										error={validationErrors.category}
										allowNull={true}
										placeholder={categories.length === 0 ? 'No categories available' : 'Select a category (optional)'}
										options={categories.map(cat => ({ value: cat.uuid, label: cat.name }))}
									/>

									<div class="lg:col-span-2">
										<Input
											label="Short Description"
											bind:value={courseData.short_description}
											error={validationErrors.short_description}
											placeholder="A compelling one-line description"
											maxlength="255"
											required
											helperText={`${courseData.short_description.length}/255 characters`}
										/>
									</div>

									<div class="lg:col-span-2">
										<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
											Full Description *
										</label>
										<textarea
											bind:value={courseData.description}
											rows="6"
											placeholder="Describe what students will learn, key topics, and outcomes..."
											class={classNames(
												"w-full rounded-lg border bg-white px-3 py-2 text-sm focus:ring-2 dark:bg-gray-800",
												validationErrors.description
													? "border-red-300 focus:border-red-500 focus:ring-red-500"
													: "border-gray-300 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600"
											)}
											required
										></textarea>
										{#if validationErrors.description}
											<p class="mt-1 text-xs text-red-600">{validationErrors.description}</p>
										{/if}
									</div>
								</div>
							</div>

							<!-- Course Settings -->
							<div class="space-y-6">
								<div class="border-b border-gray-200 pb-4 dark:border-gray-700">
									<h2 class="text-xl font-semibold text-gray-900 dark:text-white">Course Settings</h2>
									<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Configure your course details</p>
								</div>

								<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
									<Select
										label="Level"
										bind:value={courseData.level}
										options={levelOptions}
									/>

									<Select
										label="Language"
										bind:value={courseData.language}
										options={[
											{ value: 'en', label: 'English' },
											{ value: 'ar', label: 'Arabic' }
										]}
									/>

									<Input
										type="number"
										label="Duration (hours)"
										bind:value={courseData.duration_hours}
										error={validationErrors.duration_hours}
										min="1"
										step="0.5"
										required
									/>

									<Input
										type="number"
										label="Enrollment Limit"
										bind:value={courseData.enrollment_limit}
										error={validationErrors.enrollment_limit}
										placeholder="Unlimited"
										min="1"
									/>
								</div>

								<!-- Tags -->
								<div>
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
										Tags
									</label>
									<div class="mb-2 flex gap-2">
										<input
											bind:value={tagInput}
											onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
											placeholder="Add tags to help students find your course"
											maxlength="50"
											class="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800"
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
													aria-label="Remove tag"
												>
													×
												</button>
											</Badge>
										{/each}
									</div>
								</div>
							</div>

							<!-- Learning Outcomes -->
							<div class="space-y-6">
								<div class="border-b border-gray-200 pb-4 dark:border-gray-700">
									<h2 class="text-xl font-semibold text-gray-900 dark:text-white">Learning Outcomes</h2>
									<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">What will students achieve?</p>
								</div>

								<div class="grid grid-cols-1 gap-6">
									<div>
										<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
											Prerequisites
										</label>
										<textarea
											bind:value={courseData.prerequisites}
											rows="3"
											placeholder="What should students know before taking this course? (optional)"
											class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800"
										></textarea>
									</div>

									<div>
										<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
											Learning Outcomes *
										</label>
										<textarea
											bind:value={courseData.learning_outcomes}
											rows="6"
											placeholder="List specific skills and knowledge students will gain..."
											class={classNames(
												"w-full rounded-lg border bg-white px-3 py-2 text-sm focus:ring-2 dark:bg-gray-800",
												validationErrors.learning_outcomes
													? "border-red-300 focus:border-red-500 focus:ring-red-500"
													: "border-gray-300 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600"
											)}
											required
										></textarea>
										{#if validationErrors.learning_outcomes}
											<p class="mt-1 text-xs text-red-600">{validationErrors.learning_outcomes}</p>
										{/if}
									</div>
								</div>
							</div>

							<!-- Course Thumbnail -->
							<div class="space-y-6">
								<div class="border-b border-gray-200 pb-4 dark:border-gray-700">
									<h2 class="text-xl font-semibold text-gray-900 dark:text-white">Course Thumbnail</h2>
									<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Add an eye-catching image (optional)</p>
								</div>

								{#if thumbnailPreview}
									<div class="mb-4" transition:slide>
										<div class="relative inline-block">
											<img 
												src={thumbnailPreview} 
												alt="Course thumbnail preview" 
												class="h-40 w-64 rounded-lg object-cover shadow-md"
											/>
											<button
												type="button"
												onclick={removeThumbnail}
												class="absolute -top-2 -right-2 flex h-8 w-8 items-center justify-center rounded-full bg-red-600 text-white hover:bg-red-700 transition-colors"
												aria-label="Remove thumbnail"
											>
												×
											</button>
										</div>
									</div>
								{/if}

								<div class="flex items-center justify-center w-full">
									<label class="flex flex-col items-center justify-center w-full h-40 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:hover:bg-gray-600 transition-colors">
										<div class="flex flex-col items-center justify-center pt-5 pb-6">
											<svg class="w-8 h-8 mb-3 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
											</svg>
											<p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
												<span class="font-semibold">Click to upload</span> or drag and drop
											</p>
											<p class="text-xs text-gray-500 dark:text-gray-400">PNG, JPG, WebP up to 5MB</p>
										</div>
										<input 
											type="file" 
											class="hidden" 
											accept="image/*"
											onchange={handleThumbnailChange}
										/>
									</label>
								</div>
							</div>

							<!-- Form Actions -->
							<div class="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
								<div class="flex items-center gap-2 text-sm text-gray-500">
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
									</svg>
									Auto-saved as draft
								</div>

								<div class="flex gap-3">
									<Button
										type="button"
										variant="outline"
										onclick={() => goto('/courses')}
									>
										Cancel
									</Button>
									
									<Button
										type="submit"
										variant="primary"
										loading={saving}
										disabled={saving || !isFormValid}
										size="large"
									>
										{saving ? 'Creating Course...' : 'Create Course'}
									</Button>
								</div>
							</div>
						</form>
					</Card>
				</div>
			{/if}
		</div>
	</div>
{/if}
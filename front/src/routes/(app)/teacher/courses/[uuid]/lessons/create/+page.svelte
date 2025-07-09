<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { fade, fly } from 'svelte/transition';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t } from '$lib/i18n/index.js';
import { isTeacher } from '$lib/utils/helpers.js';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Select from '$lib/components/common/Select.svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Steps from '$lib/components/common/Steps.svelte';

	// Route params
	let courseId = $page.params.uuid;

	// State variables
	let course = $state(null);
	let modules = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	let uploading = $state(false);
	let error = $state('');
	let currentStep = $state(1);

	// Form data
	let lessonData = $state({
		title: '',
		description: '',
		content: '',
		module: '',
		duration_minutes: 15,
		order: 1,
		is_preview: false,
		video_url: '',
		content_type: 'text'
	});

	let validationErrors = $state({});
	let resourceFiles = $state([]);
	let showResourceModal = $state(false);

	// Content type options
	const contentTypes = [
		{ value: 'text', label: 'Text Content' },
		{ value: 'video', label: 'Video Lesson' },
		{ value: 'pdf', label: 'PDF Document' },
		{ value: 'quiz', label: 'Quiz/Assessment' }
	];

	// Steps configuration
	const steps = [
		{ id: 1, title: 'Basic Info', completed: false },
		{ id: 2, title: 'Content', completed: false },
		{ id: 3, title: 'Resources', completed: false },
		{ id: 4, title: 'Review', completed: false }
	];

	onMount(async () => {
		// Check authorization
		if (!isTeacher($currentUser)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: 'You need to be a teacher to create lessons'
			});
			goto('/my-courses');
			return;
		}

		await loadCourseData();
	});

	async function loadCourseData() {
		loading = true;
		error = '';

		try {
			// Load course details
			const courseResponse = await coursesApi.getCourse(courseId);
			course = courseResponse;

			// Verify user is the instructor
			if (course.instructor?.uuid !== $currentUser.uuid && !$currentUser.is_staff) {
				throw new Error('You are not authorized to create lessons for this course');
			}

			// Load course modules
			const modulesResponse = await coursesApi.getModules(courseId);
			modules = modulesResponse.results || modulesResponse || [];

			// Set default module if only one exists
			if (modules.length === 1) {
				lessonData.module = modules[0].uuid;
			}

			// Calculate next lesson order
			if (modules.length > 0 && lessonData.module) {
				const moduleData = modules.find(m => m.uuid === lessonData.module);
				lessonData.order = (moduleData?.lessons?.length || 0) + 1;
			}

		} catch (err) {
			console.error('Failed to load course data:', err);
			error = err.message || 'Failed to load course data';
			
			if (err.message.includes('not authorized')) {
				goto('/teacher/courses');
			}
		} finally {
			loading = false;
		}
	}

	function validateStep(step) {
		const errors = {};

		if (step === 1) {
			if (!lessonData.title?.trim()) {
				errors.title = 'Lesson title is required';
			}
			if (!lessonData.module) {
				errors.module = 'Please select a module';
			}
			if (!lessonData.duration_minutes || lessonData.duration_minutes < 1) {
				errors.duration_minutes = 'Duration must be at least 1 minute';
			}
		}

		if (step === 2) {
			if (lessonData.content_type === 'video' && !lessonData.video_url?.trim()) {
				errors.video_url = 'Video URL is required for video lessons';
			}
			if (lessonData.content_type === 'text' && !lessonData.content?.trim()) {
				errors.content = 'Content is required for text lessons';
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

	async function createLesson() {
		if (!validateStep(1) || !validateStep(2)) {
			uiStore.showNotification({
				type: 'error',
				title: 'Validation Error',
				message: 'Please fix all errors before creating the lesson'
			});
			return;
		}

		saving = true;
		try {
			// Prepare lesson payload
			const lessonPayload = {
				title: lessonData.title.trim(),
				description: lessonData.description?.trim() || '',
				content: lessonData.content?.trim() || '',
				module: lessonData.module,
				duration_minutes: parseInt(lessonData.duration_minutes),
				order: parseInt(lessonData.order),
				is_preview: lessonData.is_preview,
				content_type: lessonData.content_type
			};

			// Add video URL if it's a video lesson
			if (lessonData.content_type === 'video' && lessonData.video_url?.trim()) {
				lessonPayload.video_url = lessonData.video_url.trim();
			}

			// Create the lesson
			const response = await coursesApi.createLesson(courseId, lessonPayload);
			const newLesson = response;

			// Upload resources if any
			if (resourceFiles.length > 0) {
				await uploadResources(newLesson.uuid);
			}

			uiStore.showNotification({
				type: 'success',
				title: 'Lesson Created',
				message: 'Your lesson has been created successfully'
			});

			// Redirect to course management
			goto(`/teacher/courses/${courseId}/manage`);

		} catch (err) {
			console.error('Failed to create lesson:', err);
			
			uiStore.showNotification({
				type: 'error',
				title: 'Creation Failed',
				message: err.message || 'Failed to create lesson'
			});
		} finally {
			saving = false;
		}
	}

	async function uploadResources(lessonId) {
		for (const file of resourceFiles) {
			try {
				await coursesApi.uploadLessonResource(courseId, lessonId, file);
			} catch (err) {
				console.warn(`Failed to upload resource ${file.name}:`, err);
			}
		}
	}

	function handleResourceUpload(event) {
		const files = Array.from(event.target.files);
		if (files.length > 0) {
			resourceFiles = [...resourceFiles, ...files];
		}
	}

	function removeResource(index) {
		resourceFiles = resourceFiles.filter((_, i) => i !== index);
	}

	function handleModuleChange() {
		// Update lesson order when module changes
		if (lessonData.module && modules.length > 0) {
			const moduleData = modules.find(m => m.uuid === lessonData.module);
			lessonData.order = (moduleData?.lessons?.length || 0) + 1;
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
	<title>Create Lesson - {course?.title || 'Course'} | E-Learning Platform</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="container mx-auto max-w-4xl px-4 py-8">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="flex items-center gap-4 mb-4">
				<Button
					href="/teacher/courses/{courseId}/manage"
					variant="ghost"
					size="medium"
					class="text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
					Back to Course Management
				</Button>
			</div>
			<h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
				Create New Lesson
			</h1>
			<p class="text-gray-600 dark:text-gray-400">
				Add a new lesson to {course?.title || 'your course'}
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
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Error Loading Course</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={loadCourseData} variant="primary" size="medium">
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
		{:else if modules.length === 0}
			<!-- No Modules State -->
			<Card class="p-8 text-center">
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
					No Modules Found
				</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">
					You need to create at least one module before adding lessons.
				</p>
				<Button
					href="/teacher/courses/{courseId}/manage"
					variant="primary"
					size="medium"
				>
					Create Module First
				</Button>
			</Card>
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
								label="Lesson Title *"
								bind:value={lessonData.title}
								error={validationErrors.title}
								placeholder="Enter lesson title"
							/>

							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Module *
								</label>
								<select
									bind:value={lessonData.module}
									onchange={handleModuleChange}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									class:border-red-300={validationErrors.module}
								>
									<option value="">Select a module</option>
									{#each modules as module}
										<option value={module.uuid}>{module.title}</option>
									{/each}
								</select>
								{#if validationErrors.module}
									<p class="mt-1 text-sm text-red-600">{validationErrors.module}</p>
								{/if}
							</div>

							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<Input
									label="Duration (minutes) *"
									type="number"
									bind:value={lessonData.duration_minutes}
									error={validationErrors.duration_minutes}
									min="1"
									placeholder="15"
								/>

								<Input
									label="Lesson Order"
									type="number"
									bind:value={lessonData.order}
									min="1"
									placeholder="1"
								/>
							</div>

							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Description
								</label>
								<textarea
									bind:value={lessonData.description}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="3"
									placeholder="Brief description of the lesson"
								></textarea>
							</div>

							<div>
								<label class="flex items-center">
									<input
										type="checkbox"
										bind:checked={lessonData.is_preview}
										class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
									/>
									<span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
										Make this lesson available as a preview
									</span>
								</label>
							</div>
						</div>

						<div class="flex justify-end mt-6">
							<Button onclick={nextStep} variant="primary" size="medium">
								Next Step
							</Button>
						</div>
					</Card>

				{:else if currentStep === 2}
					<!-- Step 2: Content -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
							Lesson Content
						</h3>
						
						<div class="space-y-6">
							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Content Type *
								</label>
								<select
									bind:value={lessonData.content_type}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
								>
									{#each contentTypes as type}
										<option value={type.value}>{type.label}</option>
									{/each}
								</select>
							</div>

							{#if lessonData.content_type === 'video'}
								<Input
									label="Video URL *"
									bind:value={lessonData.video_url}
									error={validationErrors.video_url}
									placeholder="https://youtube.com/watch?v=... or upload video file"
								/>
							{/if}

							{#if lessonData.content_type === 'text' || lessonData.content_type === 'quiz'}
								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										Content *
									</label>
									<textarea
										bind:value={lessonData.content}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="12"
										placeholder={lessonData.content_type === 'quiz' ? 'Enter quiz questions and answers...' : 'Enter lesson content...'}
										class:border-red-300={validationErrors.content}
									></textarea>
									{#if validationErrors.content}
										<p class="mt-1 text-sm text-red-600">{validationErrors.content}</p>
									{/if}
								</div>
							{/if}
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
					<!-- Step 3: Resources -->
					<Card class="p-6">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
							Lesson Resources (Optional)
						</h3>
						
						<div class="space-y-6">
							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Upload Files
								</label>
								<div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
									<input
										type="file"
										multiple
										onchange={handleResourceUpload}
										class="hidden"
										id="resource-upload"
										accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.zip"
									/>
									<label
										for="resource-upload"
										class="cursor-pointer inline-flex flex-col items-center"
									>
										<svg class="h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
										</svg>
										<span class="text-lg font-medium text-gray-900 dark:text-white">
											Click to upload resources
										</span>
										<span class="text-sm text-gray-500 dark:text-gray-400">
											or drag and drop
										</span>
										<span class="text-xs text-gray-400 mt-2">
											PDF, DOC, PPT, TXT, ZIP files
										</span>
									</label>
								</div>
							</div>

							{#if resourceFiles.length > 0}
								<div>
									<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
										Uploaded Files ({resourceFiles.length})
									</h4>
									<div class="space-y-2">
										{#each resourceFiles as file, index}
											<div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
												<div class="flex items-center space-x-3">
													<svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
													</svg>
													<div>
														<p class="text-sm font-medium text-gray-900 dark:text-white">
															{file.name}
														</p>
														<p class="text-xs text-gray-500 dark:text-gray-400">
															{formatFileSize(file.size)}
														</p>
													</div>
												</div>
												<Button
													onclick={() => removeResource(index)}
													variant="ghost"
													size="small"
													class="text-red-600 hover:text-red-700"
												>
													<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
													</svg>
												</Button>
											</div>
										{/each}
									</div>
								</div>
							{/if}
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
							Review & Create Lesson
						</h3>
						
						<div class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div>
									<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Basic Information</h4>
									<div class="space-y-2 text-sm">
										<p><span class="font-medium">Title:</span> {lessonData.title}</p>
										<p><span class="font-medium">Module:</span> {modules.find(m => m.uuid === lessonData.module)?.title}</p>
										<p><span class="font-medium">Duration:</span> {lessonData.duration_minutes} minutes</p>
										<p><span class="font-medium">Order:</span> {lessonData.order}</p>
										<p><span class="font-medium">Preview:</span> {lessonData.is_preview ? 'Yes' : 'No'}</p>
									</div>
								</div>

								<div>
									<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Content</h4>
									<div class="space-y-2 text-sm">
										<p><span class="font-medium">Type:</span> {contentTypes.find(t => t.value === lessonData.content_type)?.label}</p>
										{#if lessonData.video_url}
											<p><span class="font-medium">Video URL:</span> {lessonData.video_url}</p>
										{/if}
										<p><span class="font-medium">Resources:</span> {resourceFiles.length} files</p>
									</div>
								</div>
							</div>

							{#if lessonData.description}
								<div>
									<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</h4>
									<p class="text-sm text-gray-600 dark:text-gray-400">{lessonData.description}</p>
								</div>
							{/if}
						</div>

						<div class="flex justify-between mt-6">
							<Button onclick={prevStep} variant="outline" size="medium">
								Previous
							</Button>
							<Button
								onclick={createLesson}
								variant="success"
								size="medium"
								disabled={saving}
								loading={saving}
							>
								Create Lesson
							</Button>
						</div>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</div>
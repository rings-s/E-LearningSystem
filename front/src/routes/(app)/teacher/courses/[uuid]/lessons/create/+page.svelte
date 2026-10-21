<script>
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { fade, fly } from 'svelte/transition';
	import { coursesApi } from '#lib/apis/courses.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t } from '#lib/i18n/index.js';
	import { isTeacher, slugify } from '#lib/utils/helpers.js';

	// Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Input from '#lib/components/common/Input.svelte';
	import Select from '#lib/components/common/Select.svelte';
	import Modal from '#lib/components/common/Modal.svelte';
	import Steps from '#lib/components/common/Steps.svelte';

	// Route params
	let courseId = page.params.uuid;

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
	const contentTypes = $derived([
		{ value: 'text', label: $t('courseForm.textContent') },
		{ value: 'video', label: $t('courseForm.videoLesson') },
		{ value: 'pdf', label: $t('courseForm.pdfDocument') },
		{ value: 'quiz', label: $t('courseForm.quiz') }
	]);

	// Steps configuration
	// Step titles are i18n keys, translated where they are rendered
	const steps = $state([
		{ id: 1, title: 'courseForm.basicInfo', completed: false },
		{ id: 2, title: 'courseForm.content', completed: false },
		{ id: 3, title: 'courseForm.resources', completed: false },
		{ id: 4, title: 'courseForm.review', completed: false }
	]);

	onMount(async () => {
		// Check authorization
		if (!isTeacher($currentUser)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: $t('courseForm.teacherToCreateLessons')
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
			if (course.instructor?.id !== $currentUser.id && !$currentUser.is_staff) {
				throw new Error('You are not authorized to create lessons for this course');
			}

			// Load course modules
			const modulesResponse = await coursesApi.getModules(courseId);
			modules = modulesResponse.results || modulesResponse || [];

			// Set default module if only one exists
			if (modules.length === 1) {
				// Preselect the module passed from the manage page, if any
				const requested = Number(page.url.searchParams.get('module'));
				lessonData.module = modules.some((m) => m.id === requested) ? requested : modules[0].id;
			}

			// Calculate next lesson order
			if (modules.length > 0 && lessonData.module) {
				const moduleData = modules.find((m) => m.id === lessonData.module);
				lessonData.order = (moduleData?.lessons?.length || 0) + 1;
			}
		} catch (err) {
			console.error('Failed to load course data:', err);
			error = err.message || $t('courseForm.loadCourseFailed');

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
				errors.title = $t('courseForm.lessonTitleRequired');
			}
			if (!lessonData.module) {
				errors.module = $t('courseForm.moduleRequired');
			}
			if (!lessonData.duration_minutes || lessonData.duration_minutes < 1) {
				errors.duration_minutes = $t('courseForm.durationMinMinute');
			}
		}

		if (step === 2) {
			if (lessonData.content_type === 'video' && !lessonData.video_url?.trim()) {
				errors.video_url = $t('courseForm.videoUrlRequired');
			}
			if (lessonData.content_type === 'text' && !lessonData.content?.trim()) {
				errors.content = $t('courseForm.contentRequired');
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
				title: $t('courseForm.validationError'),
				message: $t('courseForm.fixBeforeContinue')
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
				title: $t('courseForm.validationError'),
				message: $t('courseForm.fixAllBeforeLesson')
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
				slug: slugify(lessonData.title, 'lesson'),
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
				title: $t('courseForm.lessonCreated'),
				message: $t('courseForm.lessonCreatedMsg')
			});

			// Redirect to course management
			goto(`/teacher/courses/${courseId}/manage`);
		} catch (err) {
			console.error('Failed to create lesson:', err);

			uiStore.showNotification({
				type: 'error',
				title: $t('courseForm.creationFailed'),
				message: err.message || $t('courseForm.createLessonFailed')
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
			const moduleData = modules.find((m) => m.id === lessonData.module);
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
	<title>Create Lesson - {course?.title || $t('courseForm.course')} | E-Learning Platform</title>
</svelte:head>

<div>
	<div class="mx-auto max-w-4xl">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="mb-4 flex items-center gap-4">
				<Button
					href="/teacher/courses/{courseId}/manage"
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
					{$t('courseForm.backToManagement')}
				</Button>
			</div>
			<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
				{$t('courseForm.createNewLesson')}
			</h1>
			<p class="text-gray-600 dark:text-gray-400">
				Add a new lesson to {course?.title || 'your course'}
			</p>
		</div>

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
					{$t('courseForm.errorLoadingCourse')}
				</h3>
				<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
				<Button onclick={loadCourseData} variant="primary" size="medium"
					>{$t('courseForm.tryAgain')}</Button
				>
			</div>
		{:else if loading}
			<!-- Loading State -->
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
		{:else if modules.length === 0}
			<!-- No Modules State -->
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
							d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						></path>
					</svg>
				</div>
				<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
					{$t('courseForm.noModules')}
				</h3>
				<p class="mb-6 text-gray-600 dark:text-gray-400">
					{$t('courseForm.needModule')}
				</p>
				<Button href="/teacher/courses/{courseId}/manage" variant="primary" size="medium">
					{$t('courseForm.createModuleFirst')}
				</Button>
			</Card>
		{:else}
			<!-- Steps Indicator -->

			<div class="mb-8" in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<Steps
					steps={steps.map((step) => ({ ...step, title: $t(step.title) }))}
					{currentStep}
					onStepClick={goToStep}
				/>
			</div>

			<!-- Form Content -->
			<div in:fly={{ y: 20, delay: 200, duration: 600 }}>
				{#if currentStep === 1}
					<!-- Step 1: Basic Information -->
					<Card class="p-6">
						<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
							{$t('courseForm.basicInformation')}
						</h3>

						<div class="space-y-6">
							<Input
								label={$t('courseForm.lessonTitleReq')}
								bind:value={lessonData.title}
								error={validationErrors.title}
								placeholder={$t('courseForm.lessonTitlePlaceholder')}
							/>

							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.moduleReq')}
								</label>
								<select
									bind:value={lessonData.module}
									onchange={handleModuleChange}
									class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									class:border-red-300={validationErrors.module}
								>
									<option value="">{$t('courseForm.selectModule')}</option>
									{#each modules as module}
										<option value={module.id}>{module.title}</option>
									{/each}
								</select>
								{#if validationErrors.module}
									<p class="mt-1 text-sm text-red-600">{validationErrors.module}</p>
								{/if}
							</div>

							<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
								<Input
									label={$t('courseForm.durationMinutesReq')}
									type="number"
									bind:value={lessonData.duration_minutes}
									error={validationErrors.duration_minutes}
									min="1"
									placeholder="15"
								/>

								<Input
									label={$t('courseForm.lessonOrder')}
									type="number"
									bind:value={lessonData.order}
									min="1"
									placeholder="1"
								/>
							</div>

							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.description')}
								</label>
								<textarea
									bind:value={lessonData.description}
									class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="3"
									placeholder={$t('courseForm.lessonDescPlaceholder')}
								></textarea>
							</div>

							<div>
								<label class="flex items-center">
									<input
										type="checkbox"
										bind:checked={lessonData.is_preview}
										class="text-primary-600 focus:ring-primary-500 rounded border-gray-300"
									/>
									<span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
										{$t('courseForm.previewToggle')}
									</span>
								</label>
							</div>
						</div>

						<div class="mt-6 flex justify-end">
							<Button onclick={nextStep} variant="primary" size="medium"
								>{$t('courseForm.nextStep')}</Button
							>
						</div>
					</Card>
				{:else if currentStep === 2}
					<!-- Step 2: Content -->
					<Card class="p-6">
						<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
							{$t('courseForm.lessonContent')}
						</h3>

						<div class="space-y-6">
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.contentTypeReq')}
								</label>
								<select
									bind:value={lessonData.content_type}
									class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
								>
									{#each contentTypes as type}
										<option value={type.value}>{type.label}</option>
									{/each}
								</select>
							</div>

							{#if lessonData.content_type === 'video'}
								<Input
									label={$t('courseForm.videoUrlReq')}
									bind:value={lessonData.video_url}
									error={validationErrors.video_url}
									placeholder={$t('courseForm.videoUrlPlaceholder')}
								/>
							{/if}

							{#if lessonData.content_type === 'text' || lessonData.content_type === 'quiz'}
								<div>
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.contentReq')}
									</label>
									<textarea
										bind:value={lessonData.content}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
										rows="12"
										placeholder={lessonData.content_type === 'quiz'
											? $t('courseForm.quizPlaceholder')
											: $t('courseForm.contentPlaceholder')}
										class:border-red-300={validationErrors.content}
									></textarea>
									{#if validationErrors.content}
										<p class="mt-1 text-sm text-red-600">{validationErrors.content}</p>
									{/if}
								</div>
							{/if}
						</div>

						<div class="mt-6 flex justify-between">
							<Button onclick={prevStep} variant="outline" size="medium"
								>{$t('courseForm.previous')}</Button
							>
							<Button onclick={nextStep} variant="primary" size="medium"
								>{$t('courseForm.nextStep')}</Button
							>
						</div>
					</Card>
				{:else if currentStep === 3}
					<!-- Step 3: Resources -->
					<Card class="p-6">
						<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
							{$t('courseForm.lessonResources')}
						</h3>

						<div class="space-y-6">
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.uploadFiles')}
								</label>
								<div
									class="rounded-lg border-2 border-dashed border-gray-300 p-6 text-center dark:border-gray-600"
								>
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
											{$t('courseForm.clickUploadResources')}
										</span>
										<span class="text-sm text-gray-500 dark:text-gray-400">
											{$t('courseForm.dragDrop')}
										</span>
										<span class="mt-2 text-xs text-gray-400"> {$t('courseForm.fileTypes')} </span>
									</label>
								</div>
							</div>

							{#if resourceFiles.length > 0}
								<div>
									<h4 class="mb-3 text-sm font-medium text-gray-700 dark:text-gray-300">
										Uploaded Files ({resourceFiles.length})
									</h4>
									<div class="space-y-2">
										{#each resourceFiles as file, index}
											<div
												class="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800"
											>
												<div class="flex items-center space-x-3">
													<svg
														class="h-8 w-8 text-gray-400"
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
													<svg
														class="h-4 w-4"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
														></path>
													</svg>
												</Button>
											</div>
										{/each}
									</div>
								</div>
							{/if}
						</div>

						<div class="mt-6 flex justify-between">
							<Button onclick={prevStep} variant="outline" size="medium"
								>{$t('courseForm.previous')}</Button
							>
							<Button onclick={nextStep} variant="primary" size="medium"
								>{$t('courseForm.reviewCreate')}</Button
							>
						</div>
					</Card>
				{:else if currentStep === 4}
					<!-- Step 4: Review -->
					<Card class="p-6">
						<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
							{$t('courseForm.reviewCreateLesson')}
						</h3>

						<div class="space-y-6">
							<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
								<div>
									<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.basicInformation')}
									</h4>
									<div class="space-y-2 text-sm">
										<p>
											<span class="font-medium">{$t('courseForm.titleColon')}</span>
											{lessonData.title}
										</p>

										<p>
											<span class="font-medium">{$t('courseForm.moduleColon')}</span>
											{modules.find((m) => m.id === lessonData.module)?.title}
										</p>

										<p>
											<span class="font-medium">{$t('courseForm.durationColon')}</span>
											{lessonData.duration_minutes} minutes
										</p>

										<p>
											<span class="font-medium">{$t('courseForm.orderColon')}</span>
											{lessonData.order}
										</p>

										<p>
											<span class="font-medium">{$t('courseForm.previewColon')}</span>
											{lessonData.is_preview ? $t('courseForm.yes') : $t('courseForm.no')}
										</p>
									</div>
								</div>

								<div>
									<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.content')}
									</h4>
									<div class="space-y-2 text-sm">
										<p>
											<span class="font-medium">{$t('courseForm.typeColon')}</span>
											{contentTypes.find((t) => t.value === lessonData.content_type)?.label}
										</p>

										{#if lessonData.video_url}
											<p>
												<span class="font-medium">{$t('courseForm.videoUrlColon')}</span>
												{lessonData.video_url}
											</p>
										{/if}
										<p>
											<span class="font-medium">{$t('courseForm.resourcesColon')}</span>
											{resourceFiles.length} files
										</p>
									</div>
								</div>
							</div>

							{#if lessonData.description}
								<div>
									<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.description')}
									</h4>
									<p class="text-sm text-gray-600 dark:text-gray-400">{lessonData.description}</p>
								</div>
							{/if}
						</div>

						<div class="mt-6 flex justify-between">
							<Button onclick={prevStep} variant="outline" size="medium"
								>{$t('courseForm.previous')}</Button
							>
							<Button
								onclick={createLesson}
								variant="success"
								size="medium"
								disabled={saving}
								loading={saving}
							>
								{$t('courseForm.createLesson')}
							</Button>
						</div>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</div>

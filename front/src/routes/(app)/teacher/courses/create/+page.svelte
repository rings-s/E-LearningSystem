<script>
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '#lib/apis/courses.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t } from '#lib/i18n/index.js';
	import { isTeacher, slugify } from '#lib/utils/helpers.js';

	// Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Input from '#lib/components/common/Input.svelte';
	import Steps from '#lib/components/common/Steps.svelte';

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
	// Step titles are i18n keys, translated where they are rendered
	const steps = $state([
		{ id: 1, title: 'courseForm.basicInfo', completed: false },
		{ id: 2, title: 'courseForm.details', completed: false },
		{ id: 3, title: 'courseForm.content', completed: false },
		{ id: 4, title: 'courseForm.review', completed: false }
	]);

	// Form options
	const levelOptions = $derived([
		{ value: 'beginner', label: $t('courseForm.beginner') },
		{ value: 'intermediate', label: $t('courseForm.intermediate') },
		{ value: 'advanced', label: $t('courseForm.advanced') }
	]);

	const languageOptions = $derived([
		{ value: 'en', label: $t('courseForm.english') },
		{ value: 'ar', label: $t('courseForm.arabic') }
	]);

	onMount(async () => {
		// Check authorization
		if (!isTeacher($currentUser)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: $t('courseForm.teacherToCreate')
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
				errors.title = $t('courseForm.titleRequired');
			}
			// Mirror the API rules so the teacher sees why a save would fail
			else if (courseData.title.trim().length < 3) {
				errors.title = $t('courseForm.titleMin');
			}
			if (!courseData.short_description?.trim()) {
				errors.short_description = $t('courseForm.shortDescRequired');
			}
			if (courseData.short_description?.length > 255) {
				errors.short_description = $t('courseForm.shortDescTooLong');
			}
			if (!courseData.category) {
				errors.category = $t('courseForm.categoryRequired');
			}
		}

		if (step === 2) {
			if (!courseData.description?.trim()) {
				errors.description = $t('courseForm.descRequired');
			} else if (courseData.description.trim().length < 50) {
				errors.description = $t('courseForm.descMin', {
					count: courseData.description.trim().length
				});
			}
			if (courseData.duration_hours < 1) {
				errors.duration_hours = $t('courseForm.durationMin');
			}
		}

		if (step === 3) {
			if (!courseData.learning_outcomes?.trim()) {
				errors.learning_outcomes = $t('courseForm.outcomesRequired');
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

	async function createCourse() {
		// Validate all steps
		for (let i = 1; i <= 3; i++) {
			if (!validateStep(i)) {
				uiStore.showNotification({
					type: 'error',
					title: $t('courseForm.validationError'),
					message: $t('courseForm.fixInStep', { step: i })
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
			coursePayload.slug = courseData.slug?.trim() || slugify(courseData.title, 'course');
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
				title: $t('courseForm.courseCreated'),
				message: $t('courseForm.courseCreatedMsg')
			});

			// Redirect to course management
			goto(`/teacher/courses/${newCourse.uuid}/manage`);
		} catch (err) {
			console.error('Failed to create course:', err);

			uiStore.showNotification({
				type: 'error',
				title: $t('courseForm.creationFailed'),
				message: err.message || $t('courseForm.createCourseFailed')
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
				title: $t('courseForm.invalidFileType'),
				message: $t('courseForm.uploadImageType')
			});
			return;
		}

		// Validate file size (5MB limit)
		if (file.size > 5 * 1024 * 1024) {
			uiStore.showNotification({
				type: 'error',
				title: $t('courseForm.fileTooLarge'),
				message: $t('courseForm.uploadImageSize')
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
		if (courseData.title && !courseData.slug) {
			courseData.slug = slugify(courseData.title, 'course');
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
	<title>{$t('courseForm.createPageTitle')}</title>
	<meta name="description" content={$t('courseForm.metaCreate')} />
</svelte:head>

<div>
	<div class="mx-auto max-w-4xl">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="mb-4 flex items-center gap-4">
				<Button
					href="/teacher/courses"
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
					{$t('courseForm.backToMyCourses')}
				</Button>
			</div>
			<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
				{$t('courseForm.createNewCourse')}
			</h1>
			<p class="text-gray-600 dark:text-gray-400">
				{$t('courseForm.createSubtitle')}
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
						/>
					</svg>
				</div>
				<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
					{$t('courseForm.errorLoadingForm')}
				</h3>
				<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
				<Button onclick={() => window.location.reload()} variant="primary" size="medium">
					{$t('courseForm.tryAgain')}
				</Button>
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
								label={$t('courseForm.courseTitleReq')}
								bind:value={courseData.title}
								error={validationErrors.title}
								placeholder={$t('courseForm.titlePlaceholder')}
								onchange={generateSlug}
							/>

							<Input
								label={$t('courseForm.urlSlug')}
								bind:value={courseData.slug}
								placeholder="course-url-slug"
								helperText={$t('courseForm.slugHelper')}
							/>

							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.categoryReq')}
								</label>
								<select
									bind:value={courseData.category}
									class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									class:border-red-300={validationErrors.category}
								>
									<option value="">{$t('courseForm.selectCategory')}</option>
									{#each categories as category}
										<option value={category.id}>{category.name}</option>
									{/each}
								</select>
								{#if validationErrors.category}
									<p class="mt-1 text-sm text-red-600">{validationErrors.category}</p>
								{/if}
							</div>

							<Input
								label={$t('courseForm.shortDescReq')}
								bind:value={courseData.short_description}
								error={validationErrors.short_description}
								placeholder={$t('courseForm.shortDescPlaceholder')}
								maxlength="255"
							/>

							<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
								<div>
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.level')}
									</label>
									<select
										bind:value={courseData.level}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										{#each levelOptions as level}
											<option value={level.value}>{level.label}</option>
										{/each}
									</select>
								</div>

								<div>
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.language')}
									</label>
									<select
										bind:value={courseData.language}
										class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									>
										{#each languageOptions as language}
											<option value={language.value}>{language.label}</option>
										{/each}
									</select>
								</div>
							</div>
						</div>

						<div class="mt-6 flex justify-end">
							<Button onclick={nextStep} variant="primary" size="medium"
								>{$t('courseForm.nextStep')}</Button
							>
						</div>
					</Card>
				{:else if currentStep === 2}
					<!-- Step 2: Details -->
					<Card class="p-6">
						<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
							{$t('courseForm.courseDetails')}
						</h3>

						<div class="space-y-6">
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.fullDescReq')}
								</label>
								<textarea
									bind:value={courseData.description}
									class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="6"
									placeholder={$t('courseForm.fullDescPlaceholder')}
									class:border-red-300={validationErrors.description}
								></textarea>
								{#if validationErrors.description}
									<p class="mt-1 text-sm text-red-600">{validationErrors.description}</p>
								{/if}
							</div>

							<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
								<Input
									label={$t('courseForm.durationHoursReq')}
									type="number"
									bind:value={courseData.duration_hours}
									error={validationErrors.duration_hours}
									min="1"
									placeholder="1"
								/>

								<Input
									label={$t('courseForm.enrollmentLimit')}
									type="number"
									bind:value={courseData.enrollment_limit}
									placeholder={$t('courseForm.unlimitedPlaceholder')}
								/>
							</div>

							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.prerequisites')}
								</label>
								<textarea
									bind:value={courseData.prerequisites}
									class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="3"
									placeholder={$t('courseForm.prereqPlaceholder')}
								></textarea>
							</div>

							<div>
								<label class="flex items-center">
									<input
										type="checkbox"
										bind:checked={courseData.is_featured}
										class="text-primary-600 focus:ring-primary-500 rounded border-gray-300"
									/>
									<span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
										{$t('courseForm.featureThis')}
									</span>
								</label>
							</div>
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
					<!-- Step 3: Content -->
					<Card class="p-6">
						<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
							{$t('courseForm.courseContent')}
						</h3>

						<div class="space-y-6">
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.learningOutcomesReq')}
								</label>
								<textarea
									bind:value={courseData.learning_outcomes}
									class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									rows="4"
									placeholder={$t('courseForm.outcomesPlaceholder')}
									class:border-red-300={validationErrors.learning_outcomes}
								></textarea>
								{#if validationErrors.learning_outcomes}
									<p class="mt-1 text-sm text-red-600">{validationErrors.learning_outcomes}</p>
								{/if}
							</div>

							<!-- Course Thumbnail -->
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.courseThumbnail')}
								</label>

								<div class="flex flex-col gap-6 lg:flex-row">
									{#if thumbnailPreview}
										<div class="lg:w-64">
											<img
												src={thumbnailPreview}
												alt={$t('courseForm.thumbnailAlt')}
												class="h-36 w-full rounded-lg border border-gray-200 object-cover dark:border-gray-700"
											/>
											<div class="mt-2 text-sm text-gray-500 dark:text-gray-400">
												{thumbnailFile ? formatFileSize(thumbnailFile.size) : ''}
											</div>
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
													/>
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
							</div>
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
							{$t('courseForm.reviewCreateCourse')}
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
											{courseData.title}
										</p>
										<p>
											<span class="font-medium">{$t('courseForm.categoryColon')}</span>
											{categories.find((c) => c.id === courseData.category)?.name ||
												$t('courseForm.none')}
										</p>
										<p>
											<span class="font-medium">{$t('courseForm.levelColon')}</span>
											{courseData.level}
										</p>
										<p>
											<span class="font-medium">{$t('courseForm.languageColon')}</span>
											{courseData.language === 'en'
												? $t('courseForm.english')
												: $t('courseForm.arabic')}
										</p>
										<p>
											<span class="font-medium">{$t('courseForm.durationColon')}</span>
											{courseData.duration_hours} hours
										</p>
									</div>
								</div>

								<div>
									<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.settings')}
									</h4>
									<div class="space-y-2 text-sm">
										<p>
											<span class="font-medium">{$t('courseForm.enrollmentLimitColon')}</span>
											{courseData.enrollment_limit || $t('courseForm.unlimited')}
										</p>
										<p>
											<span class="font-medium">{$t('courseForm.featuredColon')}</span>
											{courseData.is_featured ? $t('courseForm.yes') : $t('courseForm.no')}
										</p>
										<p>
											<span class="font-medium">{$t('courseForm.statusColon')}</span>
											{$t('courseForm.draft')}
										</p>
										<p>
											<span class="font-medium">{$t('courseForm.thumbnailColon')}</span>
											{thumbnailFile ? $t('courseForm.uploaded') : $t('courseForm.none')}
										</p>
									</div>
								</div>
							</div>

							<div>
								<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.shortDescription')}
								</h4>
								<p class="text-sm text-gray-600 dark:text-gray-400">
									{courseData.short_description}
								</p>
							</div>

							<div>
								<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('courseForm.learningOutcomes')}
								</h4>
								<p class="text-sm text-gray-600 dark:text-gray-400">
									{courseData.learning_outcomes}
								</p>
							</div>

							{#if courseData.prerequisites}
								<div>
									<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
										{$t('courseForm.prerequisites')}
									</h4>
									<p class="text-sm text-gray-600 dark:text-gray-400">{courseData.prerequisites}</p>
								</div>
							{/if}

							<div class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
								<h4 class="text-primary-900 dark:text-primary-100 mb-2 font-medium">
									{$t('courseForm.nextSteps')}
								</h4>
								<ul class="text-primary-800 dark:text-primary-200 space-y-1 text-sm">
									<li>{$t('courseForm.createdAsDraft')}</li>
									<li>{$t('courseForm.addModulesAfter')}</li>
									<li>{$t('courseForm.publishWhenReady')}</li>
								</ul>
							</div>
						</div>

						<div class="mt-6 flex justify-between">
							<Button onclick={prevStep} variant="outline" size="medium"
								>{$t('courseForm.previous')}</Button
							>
							<Button
								onclick={createCourse}
								variant="success"
								size="medium"
								disabled={creating}
								loading={creating}
							>
								{creating ? $t('courseForm.creating') : $t('courseForm.createCourse')}
							</Button>
						</div>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</div>

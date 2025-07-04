<!-- front/src/routes/courses/create/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t } from '$lib/i18n/index.js';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Badge from '$lib/components/common/Badge.svelte';

	let currentStep = $state(1);
	let saving = $state(false);

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
		enrollment_limit: null,

		// Status
		status: 'draft',
		is_featured: false
	});

	let categories = $state([]);
	let tagInput = $state('');

	$effect(() => {
		fetchCategories();
	});

	async function fetchCategories() {
		try {
			const response = await coursesApi.getCategories();
			categories = response.results || response;
		} catch (error) {
			console.error('Failed to fetch categories:', error);
		}
	}

	$effect(() => {
		if (courseData.title) {
			courseData.slug = courseData.title
				.toLowerCase()
				.replace(/[^a-z0-9]+/g, '-')
				.replace(/(^-|-$)/g, '');
		}
	});

	function addTag() {
		if (tagInput && !courseData.tags.includes(tagInput)) {
			courseData.tags = [...courseData.tags, tagInput];
			tagInput = '';
		}
	}

	function removeTag(tag) {
		courseData.tags = courseData.tags.filter((t) => t !== tag);
	}

	async function saveCourse() {
		if (!validateStep(currentStep)) return;

		saving = true;
		try {
			const response = await coursesApi.createCourse({
				...courseData,
				tags: courseData.tags.map((tag) => ({ name: tag, slug: tag.toLowerCase() }))
			});

			uiStore.showNotification({
				type: 'success',
				title: 'Course Created',
				message: 'Your course has been created successfully!'
			});

			goto(`/courses/${response.uuid}/manage`);
		} catch (error) {
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: error.message || 'Failed to create course'
			});
		} finally {
			saving = false;
		}
	}

	function validateStep(step) {
		switch (step) {
			case 1:
				if (!courseData.title || !courseData.short_description || !courseData.description) {
					uiStore.showNotification({
						type: 'error',
						title: 'Validation Error',
						message: 'Please fill in all required fields'
					});
					return false;
				}
				break;
			case 2:
				if (!courseData.category) {
					uiStore.showNotification({
						type: 'error',
						title: 'Validation Error',
						message: 'Please select a category'
					});
					return false;
				}
				break;
			case 3:
				if (!courseData.learning_outcomes) {
					uiStore.showNotification({
						type: 'error',
						title: 'Validation Error',
						message: 'Please add learning outcomes'
					});
					return false;
				}
				break;
		}
		return true;
	}

	function nextStep() {
		if (validateStep(currentStep)) {
			currentStep = Math.min(currentStep + 1, 4);
		}
	}

	function previousStep() {
		currentStep = Math.max(currentStep - 1, 1);
	}

	const steps = [
		{ number: 1, title: 'Basic Information', icon: '📝' },
		{ number: 2, title: 'Category & Settings', icon: '⚙️' },
		{ number: 3, title: 'Learning Outcomes', icon: '🎯' },
		{ number: 4, title: 'Review & Publish', icon: '✅' }
	];
</script>

<div class="container mx-auto max-w-4xl px-4 py-8">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">Create New Course</h1>
		<p class="text-gray-600 dark:text-gray-400">
			Share your knowledge and create an engaging learning experience
		</p>
	</div>

	<!-- Progress Steps -->
	<div class="mb-8">
		<div class="flex items-center justify-between">
			{#each steps as step, index}
				<div class="relative flex-1">
					<div class="flex items-center">
						<div
							class="relative z-10 flex h-12 w-12 items-center justify-center rounded-full {currentStep >=
							step.number
								? 'bg-primary-600 text-white'
								: 'bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400'}"
						>
							<span class="text-lg">{step.icon}</span>
						</div>
						{#if index < steps.length - 1}
							<div
								class="mx-2 h-1 flex-1 {currentStep > step.number
									? 'bg-primary-600'
									: 'bg-gray-200 dark:bg-gray-700'}"
							></div>
						{/if}
					</div>
					<p
						class="mt-2 text-center text-xs {currentStep >= step.number
							? 'font-medium text-gray-900 dark:text-white'
							: 'text-gray-500 dark:text-gray-400'}"
					>
						{step.title}
					</p>
				</div>
			{/each}
		</div>
	</div>

	<!-- Form Content -->
	<Card variant="bordered" class="mb-8">
		{#if currentStep === 1}
			<!-- Step 1: Basic Information -->
			<div class="space-y-6">
				<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">Basic Information</h2>

				<Input
					label="Course Title"
					bind:value={courseData.title}
					required
					placeholder="e.g., Complete Web Development Bootcamp"
					helperText="Choose a clear, descriptive title for your course"
				/>

				<Input
					label="URL Slug"
					bind:value={courseData.slug}
					required
					placeholder="complete-web-development-bootcamp"
					helperText="This will be used in the course URL"
				/>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
						Short Description
					</label>
					<textarea
						bind:value={courseData.short_description}
						required
						rows="2"
						maxlength="255"
						class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
						placeholder="A brief description that appears in course listings"
					></textarea>
					<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
						{courseData.short_description.length}/255 characters
					</p>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
						Full Description
					</label>
					<textarea
						bind:value={courseData.description}
						required
						rows="8"
						class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
						placeholder="Provide a detailed description of what students will learn"
					></textarea>
				</div>
			</div>
		{:else if currentStep === 2}
			<!-- Step 2: Category & Settings -->
			<div class="space-y-6">
				<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">
					Category & Settings
				</h2>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
						Category
					</label>
					<select
						bind:value={courseData.category}
						required
						class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
					>
						<option value="">Select a category</option>
						{#each categories as category}
							<option value={category.uuid}>{category.name}</option>
						{/each}
					</select>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
						Tags
					</label>
					<div class="mb-2 flex gap-2">
						<input
							bind:value={tagInput}
							onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
							placeholder="Add tags (press Enter)"
							class="focus:ring-primary-500 focus:border-primary-500 flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
						/>
						<Button type="button" onclick={addTag} variant="outline" size="small">Add</Button>
					</div>
					<div class="flex flex-wrap gap-2">
						{#each courseData.tags as tag}
							<Badge variant="info">
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

				<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
							Level
						</label>
						<select
							bind:value={courseData.level}
							class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
						>
							<option value="beginner">Beginner</option>
							<option value="intermediate">Intermediate</option>
							<option value="advanced">Advanced</option>
						</select>
					</div>

					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
							Language
						</label>
						<select
							bind:value={courseData.language}
							class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
						>
							<option value="en">English</option>
							<option value="ar">Arabic</option>
						</select>
					</div>

					<Input
						type="number"
						label="Duration (hours)"
						bind:value={courseData.duration_hours}
						min="1"
						required
					/>
				</div>

				<Input
					type="number"
					label="Enrollment Limit (optional)"
					bind:value={courseData.enrollment_limit}
					placeholder="Leave empty for unlimited"
					helperText="Maximum number of students who can enroll"
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
						class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
						placeholder="What should students know before taking this course? (optional)"
					></textarea>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
						Learning Outcomes
					</label>
					<textarea
						bind:value={courseData.learning_outcomes}
						required
						rows="6"
						class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
						placeholder="What will students be able to do after completing this course? (one per line)"
					></textarea>
					<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
						List specific skills and knowledge students will gain
					</p>
				</div>
			</div>
		{:else if currentStep === 4}
			<!-- Step 4: Review & Publish -->
			<div class="space-y-6">
				<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">Review & Publish</h2>

				<div class="space-y-4 rounded-lg bg-gray-50 p-6 dark:bg-gray-800/50">
					<h3 class="mb-4 font-semibold text-gray-900 dark:text-white">Course Summary</h3>

					<div class="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
						<div>
							<span class="text-gray-500 dark:text-gray-400">Title:</span>
							<p class="font-medium text-gray-900 dark:text-white">{courseData.title}</p>
						</div>

						<div>
							<span class="text-gray-500 dark:text-gray-400">Level:</span>
							<p class="font-medium text-gray-900 capitalize dark:text-white">{courseData.level}</p>
						</div>

						<div>
							<span class="text-gray-500 dark:text-gray-400">Duration:</span>
							<p class="font-medium text-gray-900 dark:text-white">
								{courseData.duration_hours} hours
							</p>
						</div>

						<div>
							<span class="text-gray-500 dark:text-gray-400">Language:</span>
							<p class="font-medium text-gray-900 dark:text-white">
								{courseData.language === 'en' ? 'English' : 'Arabic'}
							</p>
						</div>
					</div>

					<div class="border-t border-gray-200 pt-4 dark:border-gray-700">
						<span class="text-sm text-gray-500 dark:text-gray-400">Description:</span>
						<p class="mt-1 text-gray-900 dark:text-white">{courseData.short_description}</p>
					</div>
				</div>

				<div class="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
					<p class="text-sm text-blue-800 dark:text-blue-200">
						<strong>Note:</strong> Your course will be created as a draft. You can add modules and lessons
						after creation, then publish when ready.
					</p>
				</div>
			</div>
		{/if}
	</Card>

	<!-- Navigation Buttons -->
	<div class="flex justify-between">
		<Button variant="outline" onclick={previousStep} disabled={currentStep === 1}>Previous</Button>

		{#if currentStep < 4}
			<Button variant="primary" onclick={nextStep}>Next</Button>
		{:else}
			<Button variant="primary" onclick={saveCourse} loading={saving}>Create Course</Button>
		{/if}
	</div>
</div>

<!-- front/src/lib/components/course/LessonContent.svelte -->
<script>
	import { onMount } from 'svelte';
	import { courseStore } from '$lib/stores/course.store.js';
	import { classNames } from '$lib/utils/helpers.js';
	import VideoPlayer from './VideoPlayer.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import { formatters } from '$lib/utils/formatters.js';

	let {
		lesson = null,
		enrollment = null,
		onComplete = () => {},
		onNext = () => {},
		onPrevious = () => {},
		hasNext = false,
		hasPrevious = false
	} = $props();

	let isCompleted = $state(false);
	let notes = $state('');
	let showNotes = $state(false);

	onMount(() => {
		// Start learning session
		courseStore.startLearningSession(lesson.module.course.uuid, lesson.uuid);

		// Check if already completed
		isCompleted = lesson.is_completed || false;
	});

	async function handleComplete() {
		const result = await courseStore.completeLesson(lesson.uuid);
		if (result.success) {
			isCompleted = true;
			if (hasNext) {
				setTimeout(() => onNext(), 1000);
			}
		}
	}

	function handleVideoProgress(data) {
		courseStore.updateLessonProgress(lesson.uuid, {
			lastPosition: data.currentTime,
			percentComplete: data.progress
		});
	}

	function saveNotes() {
		courseStore.addNote({
			lessonId: lesson.uuid,
			content: notes,
			timestamp: videoElement?.currentTime || 0
		});
		notes = '';
	}
</script>

<div class="lesson-content space-y-6">
	<!-- Lesson Header -->
	<div class="flex items-center justify-between">
		<div>
			<div class="mb-2 flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
				<span>{lesson.module.title}</span>
				<span>/</span>
				<span>Lesson {lesson.order}</span>
			</div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{lesson.title}
			</h1>
		</div>

		<div class="flex items-center space-x-4">
			{#if isCompleted}
				<Badge variant="success">
					<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					Completed
				</Badge>
			{/if}

			<Badge variant="info">
				{formatters.duration(lesson.estimated_time_minutes * 60)}
			</Badge>
		</div>
	</div>

	<!-- Content Area -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
		<!-- Main Content -->
		<div class="space-y-6 lg:col-span-2">
			{#if lesson.content_type === 'video' && lesson.video_url}
				<Card padding="none" variant="bordered">
					<VideoPlayer
						url={lesson.video_url}
						duration={lesson.video_duration}
						onComplete={handleComplete}
						onProgress={handleVideoProgress}
					/>
				</Card>
			{:else if lesson.content_type === 'text'}
				<Card>
					<div class="prose prose-lg dark:prose-invert max-w-none">
						{@html lesson.text_content}
					</div>
				</Card>
			{:else if lesson.content_type === 'pdf' && lesson.file_attachment}
				<Card padding="none" variant="bordered">
					<iframe
						src={lesson.file_attachment}
						title={lesson.title}
						class="h-[600px] w-full"
						frameborder="0"
					/>
				</Card>
			{:else if lesson.content_type === 'slides'}
				<Card>
					<p class="text-gray-500 dark:text-gray-400">Slides viewer not implemented yet</p>
				</Card>
			{/if}

			<!-- Description -->
			{#if lesson.description}
				<Card>
					<h3 class="mb-3 text-lg font-semibold">About this lesson</h3>
					<p class="text-gray-600 dark:text-gray-400">
						{lesson.description}
					</p>
				</Card>
			{/if}

			<!-- Resources -->
			{#if lesson.resources?.length > 0}
				<Card>
					<h3 class="mb-4 text-lg font-semibold">Resources</h3>
					<div class="space-y-3">
						{#each lesson.resources as resource}
							<a
								href={resource.file || resource.url}
								target="_blank"
								rel="noopener noreferrer"
								class="flex items-center justify-between rounded-lg bg-gray-50 p-3 transition-colors hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600"
							>
								<div class="flex items-center space-x-3">
									<div class="bg-primary-100 dark:bg-primary-900/30 rounded p-2">
										<svg
											class="text-primary-600 dark:text-primary-400 h-5 w-5"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
											/>
										</svg>
									</div>
									<div>
										<p class="font-medium text-gray-900 dark:text-white">
											{resource.title}
										</p>
										{#if resource.description}
											<p class="text-sm text-gray-500 dark:text-gray-400">
												{resource.description}
											</p>
										{/if}
									</div>
								</div>
								<svg
									class="h-5 w-5 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
									/>
								</svg>
							</a>
						{/each}
					</div>
				</Card>
			{/if}
		</div>

		<!-- Sidebar -->
		<div class="space-y-6">
			<!-- Progress Card -->
			<Card>
				<h3 class="mb-4 text-lg font-semibold">Your Progress</h3>
				<div class="space-y-4">
					<div>
						<div class="mb-2 flex justify-between text-sm">
							<span class="text-gray-600 dark:text-gray-400">Course Progress</span>
							<span class="font-medium">{enrollment?.progress_percentage || 0}%</span>
						</div>
						<div class="h-2 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
							<div
								class="bg-primary-500 h-full rounded-full transition-all duration-300"
								style="width: {enrollment?.progress_percentage || 0}%"
							/>
						</div>
					</div>

					{#if !isCompleted}
						<Button onclick={handleComplete} variant="primary" fullWidth>Mark as Complete</Button>
					{/if}
				</div>
			</Card>

			<!-- Notes -->
			<Card>
				<div class="mb-4 flex items-center justify-between">
					<h3 class="text-lg font-semibold">Notes</h3>
					<button
						onclick={() => (showNotes = !showNotes)}
						class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm"
					>
						{showNotes ? 'Hide' : 'Show'}
					</button>
				</div>

				{#if showNotes}
					<div class="space-y-3">
						<textarea
							bind:value={notes}
							placeholder="Take notes here..."
							class="focus:ring-primary-500 focus:border-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
							rows="4"
						/>
						<Button
							onclick={saveNotes}
							variant="outline"
							size="small"
							fullWidth
							disabled={!notes.trim()}
						>
							Save Note
						</Button>
					</div>
				{/if}
			</Card>

			<!-- Navigation -->
			<Card>
				<h3 class="mb-4 text-lg font-semibold">Navigation</h3>
				<div class="space-y-2">
					<Button onclick={onPrevious} variant="outline" fullWidth disabled={!hasPrevious}>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 19l-7-7 7-7"
							/>
						</svg>
						Previous Lesson
					</Button>

					<Button onclick={onNext} variant="primary" fullWidth disabled={!hasNext}>
						Next Lesson
						<svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 5l7 7-7 7"
							/>
						</svg>
					</Button>
				</div>
			</Card>
		</div>
	</div>
</div>

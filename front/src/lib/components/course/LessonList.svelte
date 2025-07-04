<!-- front/src/lib/components/course/LessonList.svelte -->
<script>
	import { fade } from 'svelte/transition';
	import { t } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { classNames } from '$lib/utils/helpers.js';

	let {
		modules = [],
		currentLessonId = null,
		onLessonClick = () => {},
		isEnrolled = false
	} = $props();

	let expandedModules = $state(new Set([0])); // First module expanded by default

	const toggleModule = (index) => {
		if (expandedModules.has(index)) {
			expandedModules.delete(index);
		} else {
			expandedModules.add(index);
		}
		expandedModules = new Set(expandedModules);
	};

	const isLessonAccessible = (lesson, moduleIndex, lessonIndex) => {
		if (!isEnrolled) return lesson.is_preview;
		// Add your logic for lesson accessibility
		return true;
	};
</script>

<div class="lesson-list">
	{#each modules as module, moduleIndex}
		<div class="mb-4 overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
			<!-- Module Header -->
			<button
				onclick={() => toggleModule(moduleIndex)}
				class="flex w-full items-center justify-between bg-gray-50 px-4 py-3 transition-colors hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700"
			>
				<div class="flex items-center gap-3">
					<span
						class="bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium"
					>
						{moduleIndex + 1}
					</span>
					<div class="text-left">
						<h4 class="font-medium text-gray-900 dark:text-white">
							{module.title}
						</h4>
						{#if module.description}
							<p class="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
								{module.description}
							</p>
						{/if}
					</div>
				</div>

				<div class="flex items-center gap-2">
					<span class="text-sm text-gray-500 dark:text-gray-400">
						{module.lessons?.length || 0}
						{$t('course.lessons')}
					</span>
					<svg
						class={classNames(
							'h-5 w-5 text-gray-400 transition-transform duration-200',
							expandedModules.has(moduleIndex) && 'rotate-180'
						)}
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</div>
			</button>

			<!-- Module Lessons -->
			{#if expandedModules.has(moduleIndex)}
				<div transition:fade={{ duration: 200 }}>
					{#each module.lessons as lesson, lessonIndex}
						{@const isAccessible = isLessonAccessible(lesson, moduleIndex, lessonIndex)}
						{@const isCurrent = lesson.uuid === currentLessonId}

						<button
							onclick={() => isAccessible && onLessonClick(lesson)}
							disabled={!isAccessible}
							class={classNames(
								'flex w-full items-center gap-3 border-t border-gray-200 px-4 py-3 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800/50',
								isCurrent && 'bg-primary-50 dark:bg-primary-900/20 border-l-primary-500 border-l-4',
								!isAccessible && 'cursor-not-allowed opacity-50'
							)}
						>
							<!-- Lesson Icon -->
							<div
								class={classNames(
									'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg',
									lesson.is_completed
										? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
										: isCurrent
											? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
											: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
								)}
							>
								{#if lesson.is_completed}
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5 13l4 4L19 7"
										/>
									</svg>
								{:else if lesson.content_type === 'video'}
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
								{:else if lesson.content_type === 'quiz'}
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
										/>
									</svg>
								{:else}
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
										/>
									</svg>
								{/if}
							</div>

							<!-- Lesson Content -->
							<div class="flex-1 text-left">
								<h5
									class={classNames(
										'font-medium',
										isCurrent
											? 'text-primary-700 dark:text-primary-400'
											: 'text-gray-900 dark:text-white'
									)}
								>
									{lesson.title}
								</h5>
								<div class="mt-1 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
									<span>{formatters.duration((lesson.estimated_time_minutes || 0) * 60)}</span>
									{#if lesson.is_preview}
										<span class="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-700">
											{$t('course.preview')}
										</span>
									{/if}
								</div>
							</div>

							<!-- Lock Icon -->
							{#if !isAccessible}
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
										d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
									/>
								</svg>
							{/if}
						</button>
					{/each}
				</div>
			{/if}
		</div>
	{/each}
</div>

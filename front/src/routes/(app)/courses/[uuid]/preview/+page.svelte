<script>
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '#lib/apis/courses.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t } from '#lib/i18n/index.js';
	import { formatters } from '#lib/utils/formatters.js';

	// Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import YouTubePlayer from '#lib/components/course/YouTubePlayer.svelte';
	import PDFViewer from '#lib/components/course/PDFViewer.svelte';
	import CourseProgress from '#lib/components/course/CourseProgress.svelte';

	let courseId = page.params.uuid;

	// State variables
	let course = $state(null);
	let enrollment = $state(null);
	let previewLesson = $state(null);
	let loading = $state(true);
	let enrolling = $state(false);
	let error = $state('');

	// Derived states
	let isEnrolled = $derived.by(() => !!enrollment);
	let canEnroll = $derived.by(() => course && !isEnrolled && course.status === 'published');
	let previewLessons = $derived.by(() => {
		if (!course?.modules) return [];

		return course.modules.flatMap((module) =>
			(module.lessons || []).filter((lesson) => lesson.is_preview === true)
		);
	});

	let courseStats = $derived.by(() => {
		if (!course?.modules) return { totalLessons: 0, totalDuration: 0, totalModules: 0 };

		const totalModules = course.modules.length;
		const totalLessons = course.modules.reduce(
			(sum, module) => sum + (module.lessons?.length || 0),
			0
		);
		const totalDuration = course.modules.reduce(
			(sum, module) =>
				sum +
				(module.lessons?.reduce(
					(lessonSum, lesson) => lessonSum + (lesson.duration_minutes || 0),
					0
				) || 0),
			0
		);

		return { totalLessons, totalDuration, totalModules };
	});

	onMount(async () => {
		await loadCourse();
		if ($currentUser) {
			await checkEnrollment();
		}
	});

	async function loadCourse() {
		loading = true;
		error = '';

		try {
			course = await coursesApi.getCourse(courseId);

			// Load modules if not included
			if (!course.modules || !Array.isArray(course.modules)) {
				try {
					const modulesResponse = await coursesApi.getModules(courseId);
					course.modules = Array.isArray(modulesResponse)
						? modulesResponse
						: modulesResponse.results || [];
				} catch (modulesErr) {
					console.warn('Could not load modules:', modulesErr);
					course.modules = [];
				}
			}

			// Find first preview lesson to display
			const firstPreviewLesson = previewLessons[0];
			if (firstPreviewLesson) {
				try {
					previewLesson = await coursesApi.getCourseLesson(courseId, firstPreviewLesson.uuid);
				} catch (err) {
					console.warn('Could not load preview lesson:', err);
				}
			}
		} catch (err) {
			console.error('Failed to load course:', err);
			error = err.message || $t('preview.loadFailed');
		} finally {
			loading = false;
		}
	}

	async function checkEnrollment() {
		try {
			const response = await coursesApi.getMyEnrollments();

			const enrollmentsList = Array.isArray(response)
				? response
				: response.results || response.enrollments || [];

			if (Array.isArray(enrollmentsList)) {
				enrollment = enrollmentsList.find((e) => e.course?.uuid === courseId) || null;
			}
		} catch (err) {
			console.warn('Could not check enrollment:', err);
			enrollment = null;
		}
	}

	async function enrollInCourse() {
		if (!$currentUser) {
			uiStore.showNotification({
				type: 'info',
				title: $t('preview.loginRequired'),
				message: $t('preview.loginToEnrollMsg')
			});
			goto('/login');
			return;
		}

		if (!canEnroll) {
			uiStore.showNotification({
				type: 'warning',
				title: $t('preview.cannotEnroll'),
				message: $t('preview.unavailableMsg')
			});
			return;
		}

		enrolling = true;
		try {
			await coursesApi.enrollInCourse(courseId);
			enrollment = {
				course,
				enrolled_at: new Date().toISOString(),
				progress_percentage: 0
			};

			uiStore.showNotification({
				type: 'success',
				title: $t('preview.enrollSuccess'),
				message: `You are now enrolled in "${course.title}"`
			});

			// Redirect to learning interface
			setTimeout(() => {
				goto(`/my-courses/${courseId}/learn`);
			}, 1500);
		} catch (err) {
			console.error('Failed to enroll:', err);
			uiStore.showNotification({
				type: 'error',
				title: $t('preview.enrollFailed'),
				message: err.message || $t('preview.enrollFailedMsg')
			});
		} finally {
			enrolling = false;
		}
	}

	function startLearning() {
		if (isEnrolled) {
			goto(`/my-courses/${courseId}/learn`);
		} else {
			enrollInCourse();
		}
	}
</script>

<svelte:head>
	<title>{$t('preview.pageTitle', { title: course?.title || $t('preview.course') })}</title>
	<meta
		name="description"
		content={$t('preview.metaDescription', { title: course?.title || $t('preview.thisCourse') })}
	/>
</svelte:head>

<div>
	<div class="mx-auto max-w-6xl">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="mb-4 flex items-center gap-4">
				<Button
					href="/courses"
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
					{$t('preview.backToCourses')}
				</Button>
			</div>
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
					{$t('preview.courseError')}
				</h3>
				<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
				<Button onclick={loadCourse} variant="primary" size="medium"
					>{$t('preview.tryAgain')}</Button
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
		{:else if course}
			<!-- Course Header -->
			<div
				class="mb-8 grid grid-cols-1 gap-8 lg:grid-cols-3"
				in:fly={{ y: 20, delay: 100, duration: 600 }}
			>
				<!-- Course Info -->
				<div class="lg:col-span-2">
					<Card class="p-6">
						<div class="flex flex-col items-start gap-4 sm:flex-row">
							{#if course.thumbnail}
								<img
									src={course.thumbnail}
									alt={course.title}
									class="h-24 w-24 shrink-0 rounded-lg object-cover"
								/>
							{:else}
								<div
									class="bg-primary-100 dark:bg-primary-900 flex h-24 w-24 shrink-0 items-center justify-center rounded-lg"
								>
									<svg
										class="text-primary-600 dark:text-primary-400 h-12 w-12"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
										></path>
									</svg>
								</div>
							{/if}

							<div class="min-w-0 flex-1">
								<div class="mb-2 flex flex-wrap items-center gap-2">
									<h1 dir="auto" class="text-2xl font-bold text-gray-900 dark:text-white">
										{course.title}
									</h1>
									<Badge variant="info" size="small">{$t('preview.preview')}</Badge>
									{#if isEnrolled}
										<Badge variant="success" size="small">{$t('preview.enrolled')}</Badge>
									{/if}
								</div>

								<p class="mb-4 text-gray-600 dark:text-gray-400">
									{course.short_description || course.description}
								</p>

								<div
									class="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400"
								>
									{#if course.instructor}
										<div class="flex items-center">
											<svg
												class="mr-1 h-4 w-4"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
												></path>
											</svg>
											{course.instructor.name || course.instructor.email}
										</div>
									{/if}

									<div class="flex items-center">
										<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
											></path>
										</svg>
										{formatters.duration(courseStats.totalDuration * 60)}
									</div>

									<div class="flex items-center">
										<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
											></path>
										</svg>
										{courseStats.totalLessons} lessons
									</div>

									{#if course.level}
										<Badge variant="secondary" size="small">
											{course.level}
										</Badge>
									{/if}
								</div>
							</div>
						</div>
					</Card>
				</div>

				<!-- Enrollment Action -->
				<div>
					<Card class="sticky top-8 p-6">
						<div class="space-y-4 text-center">
							{#if isEnrolled}
								<div class="mb-4 text-green-600 dark:text-green-400">
									<svg
										class="mx-auto mb-2 h-12 w-12"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
										></path>
									</svg>
									<p class="font-medium">{$t('preview.youreEnrolled')}</p>
								</div>

								{#if enrollment?.progress_percentage}
									<div class="mb-4">
										<CourseProgress progress={enrollment.progress_percentage} showLabel={true} />
									</div>
								{/if}

								<Button onclick={startLearning} variant="primary" size="large" fullWidth>
									{$t('preview.continueLearning')}
								</Button>
							{:else if canEnroll}
								<div class="mb-4">
									<h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
										{$t('preview.readyLower')}
									</h3>
									<p class="text-sm text-gray-600 dark:text-gray-400">
										{$t('preview.joinThousands')}
									</p>
								</div>

								<Button
									onclick={enrollInCourse}
									variant="primary"
									size="large"
									fullWidth
									loading={enrolling}
									disabled={enrolling}
								>
									{enrolling ? $t('preview.enrolling') : $t('preview.enrollNow')}
								</Button>
							{:else if course.status !== 'published'}
								<div class="text-center text-gray-500 dark:text-gray-400">
									<svg
										class="mx-auto mb-2 h-12 w-12"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
										></path>
									</svg>
									<p class="font-medium">{$t('preview.notAvailable')}</p>
									<p class="text-sm">{$t('preview.notPublished')}</p>
								</div>
							{:else}
								<div class="text-center text-gray-500 dark:text-gray-400">
									<p class="font-medium">{$t('preview.loginRequired')}</p>
									<p class="mb-4 text-sm">{$t('preview.loginToEnroll')}</p>
									<Button href="/login" variant="primary" size="large" fullWidth
										>{$t('preview.logIn')}</Button
									>
								</div>
							{/if}

							<!-- Course Stats -->
							<div class="border-t border-gray-200 pt-4 dark:border-gray-700">
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div class="text-center">
										<div class="font-semibold text-gray-900 dark:text-white">
											{courseStats.totalModules}
										</div>
										<div class="text-gray-500 dark:text-gray-400">{$t('preview.modules')}</div>
									</div>
									<div class="text-center">
										<div class="font-semibold text-gray-900 dark:text-white">
											{courseStats.totalLessons}
										</div>
										<div class="text-gray-500 dark:text-gray-400">{$t('preview.lessons')}</div>
									</div>
								</div>
							</div>
						</div>
					</Card>
				</div>
			</div>

			<!-- Preview Content -->
			{#if previewLesson}
				<div class="mb-8" in:fly={{ y: 20, delay: 200, duration: 600 }}>
					<Card class="p-6">
						<div class="mb-6 flex items-center gap-3">
							<div class="bg-primary-100 dark:bg-primary-900/30 rounded-lg p-3">
								<svg
									class="text-primary-600 dark:text-primary-400 h-6 w-6"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"
									></path>
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900 dark:text-white">
									Preview Lesson: {previewLesson.title}
								</h2>
								<p class="text-gray-600 dark:text-gray-400">
									{$t('preview.tasteText')}
								</p>
							</div>
						</div>

						<!-- Preview Content Player -->
						<div class="mb-6">
							{#if previewLesson.content_type === 'video' && previewLesson.video_url}
								<div
									class="relative w-full overflow-hidden rounded-lg bg-black"
									style="max-height: 600px; min-height: 400px;"
								>
									<div
										class="flex aspect-video h-full max-h-full w-full items-center justify-center"
									>
										<YouTubePlayer
											videoId={previewLesson.video_url}
											class="h-full w-full [&_iframe]:h-full [&_iframe]:w-full [&_iframe]:object-contain"
										/>
									</div>
								</div>
							{:else if previewLesson.content_type === 'pdf' && previewLesson.file_attachment}
								<div class="w-full overflow-hidden rounded-lg" style="height: 500px;">
									<PDFViewer
										src={previewLesson.file_attachment}
										title={previewLesson.title}
										height="100%"
									/>
								</div>
							{:else if previewLesson.content_type === 'text' && previewLesson.text_content}
								<div
									class="prose prose-lg dark:prose-invert max-w-none rounded-lg bg-gray-50 p-6 dark:bg-gray-800"
								>
									{@html previewLesson.text_content}
								</div>
							{:else}
								<div
									class="flex h-64 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-800"
								>
									<div class="text-center text-gray-500 dark:text-gray-400">
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
										<p>{$t('preview.previewUnavailable')}</p>
									</div>
								</div>
							{/if}
						</div>

						{#if previewLesson.description}
							<div class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
								<h4 class="text-primary-900 dark:text-primary-100 mb-2 font-medium">
									{$t('preview.aboutLesson')}
								</h4>
								<p class="text-primary-800 dark:text-primary-200 text-sm">
									{previewLesson.description}
								</p>
							</div>
						{/if}
					</Card>
				</div>
			{/if}

			<!-- Course Content Overview -->
			<div
				class="grid grid-cols-1 gap-8 lg:grid-cols-2"
				in:fly={{ y: 20, delay: 300, duration: 600 }}
			>
				<!-- What You'll Learn -->
				<Card class="p-6">
					<div class="mb-6 flex items-center gap-3">
						<div class="rounded-lg bg-green-100 p-3 dark:bg-green-900/30">
							<svg
								class="h-6 w-6 text-green-600 dark:text-green-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
								></path>
							</svg>
						</div>
						<h3 class="text-xl font-bold text-gray-900 dark:text-white">
							{$t('preview.whatYoullLearn')}
						</h3>
					</div>

					{#if course.learning_outcomes}
						<div class="prose prose-gray dark:prose-invert max-w-none">
							{course.learning_outcomes}
						</div>
					{:else}
						<div class="space-y-3">
							{#if course.modules && course.modules.length > 0}
								{#each course.modules.slice(0, 5) as module}
									<div class="flex items-start gap-3">
										<div class="mt-1 rounded-full bg-green-100 p-1 dark:bg-green-900/30">
											<svg
												class="h-3 w-3 text-green-600 dark:text-green-400"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M5 13l4 4L19 7"
												></path>
											</svg>
										</div>
										<div>
											<h4 class="font-medium text-gray-900 dark:text-white">{module.title}</h4>
											{#if module.description}
												<p class="text-sm text-gray-600 dark:text-gray-400">{module.description}</p>
											{/if}
										</div>
									</div>
								{/each}
								{#if course.modules.length > 5}
									<p class="pt-2 text-center text-sm text-gray-500 dark:text-gray-400">
										...and {course.modules.length - 5} more modules
									</p>
								{/if}
							{:else}
								<p class="text-gray-600 dark:text-gray-400">
									{$t('preview.defaultContent')}
								</p>
							{/if}
						</div>
					{/if}
				</Card>

				<!-- Course Requirements -->
				<Card class="p-6">
					<div class="mb-6 flex items-center gap-3">
						<div class="bg-secondary-100 dark:bg-secondary-900/30 rounded-lg p-3">
							<svg
								class="text-secondary-600 dark:text-secondary-400 h-6 w-6"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
								></path>
							</svg>
						</div>
						<h3 class="text-xl font-bold text-gray-900 dark:text-white">
							{$t('preview.prerequisites')}
						</h3>
					</div>

					{#if course.prerequisites}
						<div class="prose prose-gray dark:prose-invert max-w-none">
							{course.prerequisites}
						</div>
					{:else}
						<p class="text-gray-600 dark:text-gray-400">
							{$t('preview.noPrereq')}
						</p>
					{/if}

					<!-- Additional Course Info -->
					<div class="mt-6 border-t border-gray-200 pt-6 dark:border-gray-700">
						<div class="space-y-3 text-sm">
							{#if course.language}
								<div class="flex items-center justify-between">
									<span class="text-gray-600 dark:text-gray-400">{$t('preview.language')}</span>
									<span class="font-medium"
										>{course.language === 'en' ? $t('preview.english') : course.language}</span
									>
								</div>
							{/if}

							<div class="flex items-center justify-between">
								<span class="text-gray-600 dark:text-gray-400">{$t('preview.duration')}</span>
								<span class="font-medium"
									>{formatters.duration(courseStats.totalDuration * 60)}</span
								>
							</div>

							<div class="flex items-center justify-between">
								<span class="text-gray-600 dark:text-gray-400">{$t('preview.level')}</span>
								<Badge variant="secondary" size="small">
									{course.level ? $t(`catalog.${course.level}`) : $t('preview.allLevels')}
								</Badge>
							</div>

							{#if course.enrollment_count}
								<div class="flex items-center justify-between">
									<span class="text-gray-600 dark:text-gray-400"
										>{$t('preview.studentsEnrolled')}</span
									>
									<span class="font-medium">{course.enrollment_count}</span>
								</div>
							{/if}
						</div>
					</div>
				</Card>
			</div>

			<!-- Full Description -->
			{#if course.description && course.description !== course.short_description}
				<div class="mt-8" in:fly={{ y: 20, delay: 400, duration: 600 }}>
					<Card class="p-6">
						<h3 class="mb-6 text-xl font-bold text-gray-900 dark:text-white">
							{$t('preview.courseDescription')}
						</h3>
						<div class="prose prose-lg dark:prose-invert max-w-none">
							{course.description}
						</div>
					</Card>
				</div>
			{/if}

			<!-- Action Footer -->
			{#if !isEnrolled && canEnroll}
				<div class="mt-8 text-center" in:fly={{ y: 20, delay: 500, duration: 600 }}>
					<Card class="p-8">
						<h3 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
							{$t('preview.readyTitle')}
						</h3>
						<p class="mb-6 text-gray-600 dark:text-gray-400">
							{$t('preview.joinToday')}
						</p>
						<Button
							onclick={enrollInCourse}
							variant="primary"
							size="large"
							loading={enrolling}
							disabled={enrolling}
						>
							{enrolling ? $t('preview.enrolling') : $t('preview.enrollFree')}
						</Button>
					</Card>
				</div>
			{/if}
		{/if}
	</div>
</div>

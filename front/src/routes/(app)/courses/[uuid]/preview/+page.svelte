<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import YouTubePlayer from '$lib/components/course/YouTubePlayer.svelte';
	import PDFViewer from '$lib/components/course/PDFViewer.svelte';
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';

	let courseId = $page.params.uuid;

	// State variables
	let course = $state(null);
	let enrollment = $state(null);
	let previewLesson = $state(null);
	let loading = $state(true);
	let enrolling = $state(false);
	let error = $state('');

	// Derived states
	let isEnrolled = $derived(() => !!enrollment);
	let canEnroll = $derived(() => course && !isEnrolled && course.status === 'published');
	let previewLessons = $derived(() => {
		if (!course?.modules) return [];
		
		return course.modules.flatMap(module => 
			(module.lessons || []).filter(lesson => lesson.is_preview === true)
		);
	});

	let courseStats = $derived(() => {
		if (!course?.modules) return { totalLessons: 0, totalDuration: 0, totalModules: 0 };
		
		const totalModules = course.modules.length;
		const totalLessons = course.modules.reduce((sum, module) => sum + (module.lessons?.length || 0), 0);
		const totalDuration = course.modules.reduce((sum, module) => 
			sum + (module.lessons?.reduce((lessonSum, lesson) => 
				lessonSum + (lesson.duration_minutes || 0), 0) || 0), 0);
		
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
					course.modules = Array.isArray(modulesResponse) ? modulesResponse : (modulesResponse.results || []);
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
			error = err.message || 'Failed to load course';
		} finally {
			loading = false;
		}
	}

	async function checkEnrollment() {
		try {
			const response = await coursesApi.getMyEnrollments();
			const enrollmentsList = Array.isArray(response) ? response : (response.results || response.enrollments || []);
			
			if (Array.isArray(enrollmentsList)) {
				enrollment = enrollmentsList.find(e => e.course?.uuid === courseId) || null;
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
				title: 'Login Required',
				message: 'Please log in to enroll in this course'
			});
			goto('/auth/login');
			return;
		}

		if (!canEnroll) {
			uiStore.showNotification({
				type: 'warning',
				title: 'Cannot Enroll',
				message: 'You are already enrolled or the course is not available'
			});
			return;
		}

		enrolling = true;
		try {
			await coursesApi.enrollInCourse(courseId);
			enrollment = {
				course: course,
				enrolled_at: new Date().toISOString(),
				progress_percentage: 0
			};

			uiStore.showNotification({
				type: 'success',
				title: 'Enrollment Successful',
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
				title: 'Enrollment Failed',
				message: err.message || 'Failed to enroll in course'
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
	<title>Preview: {course?.title || 'Course'} | E-Learning Platform</title>
	<meta name="description" content="Preview {course?.title || 'this course'} and see what you'll learn" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="container mx-auto max-w-6xl px-4 py-8">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="flex items-center gap-4 mb-4">
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
			</div>
		</div>

		<!-- Error State -->
		{#if error}
			<div class="text-center py-12" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg class="mx-auto h-16 w-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Course Error</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
				<Button onclick={loadCourse} variant="primary" size="medium">
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
		{:else if course}
			<!-- Course Header -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8" in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<!-- Course Info -->
				<div class="lg:col-span-2">
					<Card class="p-6">
						<div class="flex items-start gap-4">
							{#if course.thumbnail}
								<img 
									src={course.thumbnail} 
									alt={course.title}
									class="w-24 h-24 object-cover rounded-lg flex-shrink-0"
								/>
							{:else}
								<div class="w-24 h-24 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center flex-shrink-0">
									<svg class="h-12 w-12 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
									</svg>
								</div>
							{/if}

							<div class="flex-1">
								<div class="flex items-center gap-3 mb-2">
									<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
										{course.title}
									</h1>
									<Badge variant="info" size="small">Preview</Badge>
									{#if isEnrolled}
										<Badge variant="success" size="small">Enrolled</Badge>
									{/if}
								</div>

								<p class="text-gray-600 dark:text-gray-400 mb-4">
									{course.short_description || course.description}
								</p>

								<div class="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
									{#if course.instructor}
										<div class="flex items-center">
											<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
											</svg>
											{course.instructor.name || course.instructor.email}
										</div>
									{/if}

									<div class="flex items-center">
										<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
										</svg>
										{formatters.duration(courseStats.totalDuration * 60)}
									</div>

									<div class="flex items-center">
										<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
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
					<Card class="p-6 sticky top-8">
						<div class="text-center space-y-4">
							{#if isEnrolled}
								<div class="text-green-600 dark:text-green-400 mb-4">
									<svg class="h-12 w-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									<p class="font-medium">You're enrolled!</p>
								</div>

								{#if enrollment?.progress_percentage}
									<div class="mb-4">
										<CourseProgress progress={enrollment.progress_percentage} showLabel={true} />
									</div>
								{/if}

								<Button
									onclick={startLearning}
									variant="primary"
									size="large"
									fullWidth
								>
									Continue Learning
								</Button>
							{:else if canEnroll}
								<div class="mb-4">
									<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
										Ready to start learning?
									</h3>
									<p class="text-sm text-gray-600 dark:text-gray-400">
										Join thousands of students already enrolled
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
									{enrolling ? 'Enrolling...' : 'Enroll Now'}
								</Button>
							{:else if course.status !== 'published'}
								<div class="text-center text-gray-500 dark:text-gray-400">
									<svg class="h-12 w-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
									</svg>
									<p class="font-medium">Course Not Available</p>
									<p class="text-sm">This course is not published yet</p>
								</div>
							{:else}
								<div class="text-center text-gray-500 dark:text-gray-400">
									<p class="font-medium">Login Required</p>
									<p class="text-sm mb-4">Please log in to enroll</p>
									<Button
										href="/auth/login"
										variant="primary"
										size="large"
										fullWidth
									>
										Log In
									</Button>
								</div>
							{/if}

							<!-- Course Stats -->
							<div class="pt-4 border-t border-gray-200 dark:border-gray-700">
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div class="text-center">
										<div class="font-semibold text-gray-900 dark:text-white">{courseStats.totalModules}</div>
										<div class="text-gray-500 dark:text-gray-400">Modules</div>
									</div>
									<div class="text-center">
										<div class="font-semibold text-gray-900 dark:text-white">{courseStats.totalLessons}</div>
										<div class="text-gray-500 dark:text-gray-400">Lessons</div>
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
						<div class="flex items-center gap-3 mb-6">
							<div class="rounded-lg bg-blue-100 p-3 dark:bg-blue-900/30">
								<svg class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900 dark:text-white">
									Preview Lesson: {previewLesson.title}
								</h2>
								<p class="text-gray-600 dark:text-gray-400">
									Get a taste of what you'll learn in this course
								</p>
							</div>
						</div>

						<!-- Preview Content Player -->
						<div class="mb-6">
							{#if previewLesson.content_type === 'video' && previewLesson.video_url}
								<div class="relative w-full bg-black rounded-lg overflow-hidden" style="max-height: 600px; min-height: 400px;">
									<div class="aspect-video w-full h-full max-h-full flex items-center justify-center">
										<YouTubePlayer
											videoId={previewLesson.video_url}
											class="h-full w-full [&_iframe]:object-contain [&_iframe]:w-full [&_iframe]:h-full"
										/>
									</div>
								</div>
							{:else if previewLesson.content_type === 'pdf' && previewLesson.file_attachment}
								<div class="w-full rounded-lg overflow-hidden" style="height: 500px;">
									<PDFViewer
										src={previewLesson.file_attachment}
										title={previewLesson.title}
										height="100%"
									/>
								</div>
							{:else if previewLesson.content_type === 'text' && previewLesson.text_content}
								<div class="prose prose-lg dark:prose-invert max-w-none p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
									{@html previewLesson.text_content}
								</div>
							{:else}
								<div class="flex h-64 items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-lg">
									<div class="text-center text-gray-500 dark:text-gray-400">
										<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
										</svg>
										<p>Preview content not available</p>
									</div>
								</div>
							{/if}
						</div>

						{#if previewLesson.description}
							<div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
								<h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">About This Lesson</h4>
								<p class="text-blue-800 dark:text-blue-200 text-sm">
									{previewLesson.description}
								</p>
							</div>
						{/if}
					</Card>
				</div>
			{/if}

			<!-- Course Content Overview -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8" in:fly={{ y: 20, delay: 300, duration: 600 }}>
				<!-- What You'll Learn -->
				<Card class="p-6">
					<div class="flex items-center gap-3 mb-6">
						<div class="rounded-lg bg-green-100 p-3 dark:bg-green-900/30">
							<svg class="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
						<h3 class="text-xl font-bold text-gray-900 dark:text-white">
							What You'll Learn
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
										<div class="rounded-full bg-green-100 p-1 mt-1 dark:bg-green-900/30">
											<svg class="h-3 w-3 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
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
									<p class="text-sm text-gray-500 dark:text-gray-400 text-center pt-2">
										...and {course.modules.length - 5} more modules
									</p>
								{/if}
							{:else}
								<p class="text-gray-600 dark:text-gray-400">
									Comprehensive course content covering all essential topics.
								</p>
							{/if}
						</div>
					{/if}
				</Card>

				<!-- Course Requirements -->
				<Card class="p-6">
					<div class="flex items-center gap-3 mb-6">
						<div class="rounded-lg bg-purple-100 p-3 dark:bg-purple-900/30">
							<svg class="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
							</svg>
						</div>
						<h3 class="text-xl font-bold text-gray-900 dark:text-white">
							Prerequisites
						</h3>
					</div>

					{#if course.prerequisites}
						<div class="prose prose-gray dark:prose-invert max-w-none">
							{course.prerequisites}
						</div>
					{:else}
						<p class="text-gray-600 dark:text-gray-400">
							No specific prerequisites required. This course is designed to be accessible to learners at all levels.
						</p>
					{/if}

					<!-- Additional Course Info -->
					<div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
						<div class="space-y-3 text-sm">
							{#if course.language}
								<div class="flex items-center justify-between">
									<span class="text-gray-600 dark:text-gray-400">Language</span>
									<span class="font-medium">{course.language === 'en' ? 'English' : course.language}</span>
								</div>
							{/if}
							
							<div class="flex items-center justify-between">
								<span class="text-gray-600 dark:text-gray-400">Duration</span>
								<span class="font-medium">{formatters.duration(courseStats.totalDuration * 60)}</span>
							</div>
							
							<div class="flex items-center justify-between">
								<span class="text-gray-600 dark:text-gray-400">Level</span>
								<Badge variant="secondary" size="small">
									{course.level || 'All Levels'}
								</Badge>
							</div>
							
							{#if course.enrollment_count}
								<div class="flex items-center justify-between">
									<span class="text-gray-600 dark:text-gray-400">Students Enrolled</span>
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
						<h3 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
							Course Description
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
						<h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
							Ready to Start Learning?
						</h3>
						<p class="text-gray-600 dark:text-gray-400 mb-6">
							Join thousands of students and start your learning journey today.
						</p>
						<Button
							onclick={enrollInCourse}
							variant="primary"
							size="large"
							loading={enrolling}
							disabled={enrolling}
						>
							{enrolling ? 'Enrolling...' : 'Enroll Now - It\'s Free!'}
						</Button>
					</Card>
				</div>
			{/if}
		{/if}
	</div>
</div>
<!-- front/src/routes/(app)/courses/[uuid]/learn/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { debounce } from '$lib/utils/helpers.js';
	import { formatters } from '$lib/utils/formatters.js';

	// Components
	import YouTubePlayer from '$lib/components/course/YouTubePlayer.svelte';
	import PDFViewer from '$lib/components/course/PDFViewer.svelte';
	import LessonList from '$lib/components/course/LessonList.svelte';
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';

	const courseId = $page.params.uuid;

	// State management
	let course = $state(null);
	let enrollment = $state(null);
	let currentLesson = $state(null);
	let loading = $state(true);
	let completingLesson = $state(false);
	let videoProgress = $state({ currentTime: 0, duration: 0, progress: 0 });
	let errorMessage = $state('');

	// Computed values
	const lessons = $derived(() => {
		if (!course?.modules) return [];
		return course.modules.flatMap(module => 
			(module.lessons || []).map(lesson => ({
				...lesson,
				moduleTitle: module.title
			}))
		);
	});

	const currentLessonIndex = $derived(() => {
		if (!currentLesson || !lessons.length) return -1;
		return lessons.findIndex(lesson => lesson.uuid === currentLesson.uuid);
	});

	const previousLesson = $derived(() => 
		currentLessonIndex > 0 ? lessons[currentLessonIndex - 1] : null
	);

	const nextLesson = $derived(() => 
		currentLessonIndex < lessons.length - 1 ? lessons[currentLessonIndex + 1] : null
	);

	const totalLessonsCount = $derived(() => lessons.length);
	const completedLessonsCount = $derived(() => 
		lessons.filter(l => l.is_completed).length
	);
	const remainingLessonsCount = $derived(() => 
		totalLessonsCount - completedLessonsCount
	);
	const calculatedProgress = $derived(() => {
		if (totalLessonsCount === 0) return 0;
		return Math.round((completedLessonsCount / totalLessonsCount) * 100);
	});

	const isInstructor = $derived(() => {
		if (!course || !$currentUser) return false;
		return course.instructor.uuid === $currentUser.uuid || 
			   course.co_instructors?.some(inst => inst.uuid === $currentUser.uuid);
	});

	const hasAccess = $derived(() => 
		isInstructor || (enrollment && enrollment.is_active)
	);

	const pageState = $derived(() => {
		if (loading) return 'loading';
		if (errorMessage) return 'error';
		if (!course) return 'no-course';
		if (!hasAccess) return 'no-access';
		if (!currentLesson) return 'no-lesson';
		return 'learning';
	});

	onMount(async () => {
		await initializePage();
	});

	async function initializePage() {
		try {
			await Promise.all([loadCourse(), loadEnrollment()]);
		} catch (error) {
			handleError(error);
		} finally {
			loading = false;
		}
	}

	async function loadCourse() {
		course = await coursesApi.getCourse(courseId);
		
		if (!course.modules?.length) {
			throw new Error('This course has no lessons yet');
		}

		// Find first incomplete lesson or first lesson
		const firstIncompleteLesson = lessons.find(lesson => !lesson.is_completed);
		const lessonToLoad = firstIncompleteLesson || lessons[0];
		
		if (lessonToLoad) {
			await loadLesson(lessonToLoad);
		}
	}

	async function loadEnrollment() {
		const enrollments = await coursesApi.getMyEnrollments();
		enrollment = enrollments.find(e => e.course.uuid === courseId);
	}

	async function loadLesson(lesson) {
		currentLesson = await coursesApi.getLesson(lesson.uuid);
		videoProgress = { currentTime: 0, duration: 0, progress: 0 };
	}

	async function completeLesson() {
		if (!currentLesson || currentLesson.is_completed) return;

		completingLesson = true;
		try {
			await coursesApi.completeLesson(currentLesson.uuid);
			currentLesson.is_completed = true;

			// Update lesson in array
			const lessonIndex = lessons.findIndex(l => l.uuid === currentLesson.uuid);
			if (lessonIndex !== -1) {
				lessons[lessonIndex].is_completed = true;
			}

			// Update enrollment progress
			if (enrollment) {
				enrollment.progress_percentage = calculatedProgress;
			}

			showSuccessNotification();
			
			if (nextLesson) {
				setTimeout(() => loadLesson(nextLesson), 2000);
			}
		} catch (error) {
			showErrorNotification('Failed to complete lesson');
		} finally {
			completingLesson = false;
		}
	}

	function handleVideoProgress(data) {
		videoProgress = data;
		if (data.progress >= 90 && !currentLesson.is_completed) {
			completeLesson();
		}
	}

	function handleError(error) {
		const message = error.message || 'An unexpected error occurred';
		errorMessage = message;
	}

	function showSuccessNotification() {
		uiStore.showNotification({
			type: 'success',
			title: 'Lesson Completed! 🎉',
			message: 'Great job! Keep up the excellent work.'
		});
	}

	function showErrorNotification(message) {
		uiStore.showNotification({
			type: 'error',
			title: 'Error',
			message
		});
	}
</script>

<svelte:head>
	<title>{currentLesson?.title || 'Learning'} - {course?.title || 'Course'} - 244SCHOOL</title>
	<meta name="description" content="Continue your learning journey with {course?.title || 'this course'} on 244SCHOOL" />
</svelte:head>

<!-- Main Content Wrapper -->
<div class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
	
	<!-- Loading State -->
	{#if pageState === 'loading'}
		<div class="flex h-screen items-center justify-center" in:fade={{ duration: 300 }}>
			<div class="text-center" in:fly={{ y: 20, duration: 600, delay: 200 }}>
				<div class="mx-auto mb-6 h-20 w-20 animate-spin rounded-full border-4 border-primary-500 border-t-transparent shadow-lg"></div>
				<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">Loading your course...</h3>
				<p class="text-gray-600 dark:text-gray-400">Please wait while we prepare your learning experience</p>
			</div>
		</div>
	{/if}

	<!-- Error State -->
	{#if pageState === 'error'}
		<div in:fade={{ duration: 600 }}>
			{@render ErrorSection(errorMessage, courseId)}
		</div>
	{/if}

	<!-- No Access State -->
	{#if pageState === 'no-access'}
		<div in:fade={{ duration: 600 }}>
			{@render NoAccessSection(courseId)}
		</div>
	{/if}

	<!-- Learning Interface -->
	{#if pageState === 'learning'}
		<div in:fade={{ duration: 600 }}>
			<!-- Hero Section -->
			{@render HeroSection(
				course, 
				currentLesson, 
				courseId, 
				currentLessonIndex, 
				lessons, 
				calculatedProgress, 
				completedLessonsCount, 
				totalLessonsCount, 
				remainingLessonsCount
			)}

			<!-- Main Content -->
			<div class="container mx-auto px-4 py-12">
				<div class="grid grid-cols-1 gap-8 lg:grid-cols-4">
					
					<!-- Content Area -->
					<div class="lg:col-span-3 space-y-8">
						{@render LessonContent(
							currentLesson, 
							videoProgress, 
							handleVideoProgress, 
							completingLesson, 
							completeLesson, 
							previousLesson, 
							nextLesson, 
							loadLesson
						)}
					</div>

					<!-- Sidebar -->
					<div class="space-y-6">
						{@render ProgressOverview(
							calculatedProgress, 
							videoProgress, 
							completedLessonsCount, 
							remainingLessonsCount
						)}
						
						{@render CourseNavigation(
							course, 
							currentLesson, 
							loadLesson, 
							hasAccess
						)}
						
						{@render QuickActions(courseId)}
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Component Snippets -->
{#snippet ErrorSection(errorMessage, courseId)}
	<div class="relative overflow-hidden bg-gradient-to-br from-red-600 via-red-700 to-red-800 text-white">
		<div class="container relative mx-auto px-4 py-16">
			<div class="mx-auto max-w-2xl text-center">
				<div class="mx-auto mb-6 rounded-full bg-white/20 p-6">
					<svg class="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h1 class="mb-4 text-3xl font-bold lg:text-5xl">Something went wrong</h1>
				<p class="mb-8 text-xl text-white/90">{errorMessage}</p>
			</div>
		</div>
	</div>
	
	<div class="container mx-auto px-4 py-12">
		<div class="mx-auto max-w-md">
			<Card variant="bordered" class="p-8 shadow-2xl text-center">
				<div class="flex flex-col gap-4">
					<Button onclick={() => window.location.reload()} variant="primary">Try Again</Button>
					<Button href="/courses" variant="outline">Browse Courses</Button>
				</div>
			</Card>
		</div>
	</div>
{/snippet}

{#snippet NoAccessSection(courseId)}
	<div class="relative overflow-hidden bg-gradient-to-br from-orange-600 via-orange-700 to-red-600 text-white">
		<div class="container relative mx-auto px-4 py-16">
			<div class="mx-auto max-w-2xl text-center">
				<div class="mx-auto mb-6 rounded-full bg-white/20 p-6">
					<svg class="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
					</svg>
				</div>
				<h1 class="mb-4 text-3xl font-bold lg:text-5xl">Access Denied</h1>
				<p class="mb-8 text-xl text-white/90">You need to be enrolled in this course to access the learning materials.</p>
			</div>
		</div>
	</div>
	
	<div class="container mx-auto px-4 py-12">
		<div class="mx-auto max-w-md">
			<Card variant="bordered" class="p-8 shadow-2xl text-center">
				<div class="flex flex-col gap-4">
					<Button href={`/courses/${courseId}`} variant="primary">View Course Details</Button>
					<Button href="/courses" variant="outline">Browse Courses</Button>
				</div>
			</Card>
		</div>
	</div>
{/snippet}

{#snippet HeroSection(course, currentLesson, courseId, currentLessonIndex, lessons, calculatedProgress, completedLessonsCount, totalLessonsCount, remainingLessonsCount)}
	<div class="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600 text-white">
		<div class="absolute inset-0 opacity-10">
			<div class="h-full w-full bg-white bg-opacity-5" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0); background-size: 40px 40px;"></div>
		</div>
		
		<div class="container relative mx-auto px-4 py-12">
			<div class="mx-auto max-w-6xl">
				<div in:fly={{ y: 30, delay: 200, duration: 800 }} class="mb-6">
					<!-- Navigation breadcrumb -->
					<div class="mb-4 flex items-center gap-2 text-white/70">
						<Button href="/courses" variant="ghost" size="small" class="text-white/70 hover:text-white transition-colors">
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
							</svg>
							All Courses
						</Button>
						<span>/</span>
						<Button href={`/courses/${courseId}`} variant="ghost" size="small" class="text-white/70 hover:text-white transition-colors">
							Course Details
						</Button>
						<span>/</span>
						<span class="text-white">Learning</span>
					</div>

					<h1 class="mb-4 text-3xl font-bold leading-tight lg:text-5xl">
						{currentLesson.title}
					</h1>
					
					<div class="flex flex-wrap items-center gap-6 text-white/90">
						<div class="flex items-center gap-2">
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
							</svg>
							<span>{course.title}</span>
						</div>
						
						<div class="flex items-center gap-2">
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
							<span>{currentLesson.moduleTitle}</span>
						</div>
						
						<div class="flex items-center gap-2">
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<span>Lesson {currentLessonIndex + 1} of {lessons.length}</span>
						</div>
					</div>
				</div>

				<!-- Progress Bar -->
				<div in:fly={{ y: 30, delay: 400, duration: 800 }} class="rounded-2xl bg-white/10 p-6 backdrop-blur-sm">
					<div class="mb-3 flex items-center justify-between">
						<span class="font-medium text-white/90">Course Progress</span>
						<span class="font-bold text-yellow-400">{calculatedProgress}%</span>
					</div>
					<CourseProgress progress={calculatedProgress} showLabel={false} size="large" class="mb-2" />
					<div class="flex items-center justify-between text-sm text-white/70">
						<span>{completedLessonsCount} of {totalLessonsCount} completed</span>
						<span>{remainingLessonsCount} remaining</span>
					</div>
				</div>
			</div>
		</div>
	</div>
{/snippet}

{#snippet LessonContent(currentLesson, videoProgress, handleVideoProgress, completingLesson, completeLesson, previousLesson, nextLesson, loadLesson)}
	<!-- Video/PDF Content -->
	<div in:fly={{ y: 20, duration: 600, delay: 200 }}>
		<Card variant="bordered" class="overflow-hidden shadow-2xl">
			<div class="-m-6">
				{#if currentLesson.content_type === 'video' && currentLesson.video_url}
					<YouTubePlayer
						videoId={currentLesson.video_url}
						onProgress={handleVideoProgress}
						class="w-full aspect-video"
					/>
				{:else if currentLesson.content_type === 'pdf' && currentLesson.file_attachment}
					<PDFViewer
						src={currentLesson.file_attachment}
						title={currentLesson.title}
						class="h-[600px] w-full"
					/>
				{:else if currentLesson.content_type === 'text' && currentLesson.text_content}
					<div class="p-6 prose prose-gray dark:prose-invert max-w-none">
						{@html currentLesson.text_content}
					</div>
				{/if}
			</div>
		</Card>
	</div>

	<!-- Lesson Controls -->
	<div in:fly={{ y: 20, delay: 300, duration: 600 }}>
		<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-lg dark:bg-gray-800/95">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-4">
					{#if currentLesson.is_completed}
						<Badge variant="success" size="large" class="shadow-lg">
							<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
							Completed
						</Badge>
					{:else}
						<Button
							onclick={completeLesson}
							variant="primary"
							loading={completingLesson}
							size="medium"
							class="shadow-lg transition-all hover:scale-105"
						>
							{completingLesson ? 'Completing...' : 'Mark Complete'}
						</Button>
					{/if}

					{#if videoProgress.duration > 0}
						<div class="text-sm text-gray-600 dark:text-gray-400">
							Video: {Math.round(videoProgress.progress)}% complete
						</div>
					{/if}
				</div>

				<!-- Navigation Buttons -->
				<div class="flex items-center gap-2">
					<Button
						onclick={() => previousLesson && loadLesson(previousLesson)}
						variant="outline"
						disabled={!previousLesson}
						size="medium"
					>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
						</svg>
						Previous
					</Button>

					<Button
						onclick={() => nextLesson && loadLesson(nextLesson)}
						variant="primary"
						disabled={!nextLesson}
						size="medium"
					>
						Next
						<svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
						</svg>
					</Button>
				</div>
			</div>
		</Card>
	</div>

	<!-- Lesson Description -->
	{#if currentLesson.description}
		<div in:fly={{ y: 20, delay: 400, duration: 600 }}>
			<Card variant="bordered" class="shadow-lg">
				<div class="flex items-center gap-3 mb-4">
					<div class="rounded-lg bg-primary-100 p-3 dark:bg-primary-900/30">
						<svg class="h-6 w-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 dark:text-white">About This Lesson</h3>
				</div>
				<div class="prose prose-gray dark:prose-invert max-w-none">
					{currentLesson.description}
				</div>
			</Card>
		</div>
	{/if}

	<!-- Resources -->
	{#if currentLesson.resources?.length > 0}
		<div in:fly={{ y: 20, delay: 500, duration: 600 }}>
			<Card variant="bordered" class="shadow-lg">
				<div class="flex items-center gap-3 mb-6">
					<div class="rounded-lg bg-purple-100 p-3 dark:bg-purple-900/30">
						<svg class="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 dark:text-white">Additional Resources</h3>
				</div>
				<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
					{#each currentLesson.resources as resource}
						<a
							href={resource.file || resource.url}
							target="_blank"
							rel="noopener noreferrer"
							class="group flex items-center gap-4 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 p-4 transition-all hover:from-primary-50 hover:to-primary-100 hover:shadow-md hover:scale-[1.02] dark:from-gray-800/50 dark:to-gray-700/50"
						>
							<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-100 transition-all group-hover:scale-110 dark:bg-primary-900/30">
								<svg class="h-6 w-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
							</div>
							<div class="flex-1">
								<h4 class="font-medium text-gray-900 group-hover:text-primary-600 dark:text-white">
									{resource.title}
								</h4>
								{#if resource.description}
									<p class="text-sm text-gray-600 dark:text-gray-400">
										{resource.description}
									</p>
								{/if}
							</div>
						</a>
					{/each}
				</div>
			</Card>
		</div>
	{/if}
{/snippet}

{#snippet ProgressOverview(calculatedProgress, videoProgress, completedLessonsCount, remainingLessonsCount)}
	<div in:fly={{ y: 20, delay: 300, duration: 600 }}>
		<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-lg dark:bg-gray-800/95">
			<div class="flex items-center gap-3 mb-4">
				<div class="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
					<svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
					</svg>
				</div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Progress Overview</h3>
			</div>
			
			<div class="space-y-4">
				<div>
					<div class="mb-2 flex justify-between text-sm">
						<span class="font-medium text-gray-700 dark:text-gray-300">Course Progress</span>
						<span class="font-semibold text-primary-600 dark:text-primary-400">{calculatedProgress}%</span>
					</div>
					<CourseProgress progress={calculatedProgress} size="medium" />
				</div>

				{#if videoProgress.duration > 0}
					<div>
						<div class="mb-2 flex justify-between text-sm">
							<span class="font-medium text-gray-700 dark:text-gray-300">Video Progress</span>
							<span class="font-semibold text-blue-600 dark:text-blue-400">{Math.round(videoProgress.progress)}%</span>
						</div>
						<CourseProgress progress={videoProgress.progress} variant="info" size="medium" />
					</div>
				{/if}

				<div class="grid grid-cols-2 gap-4 pt-2 border-t border-gray-200 dark:border-gray-700">
					<div class="text-center">
						<div class="text-2xl font-bold text-green-600 dark:text-green-400">{completedLessonsCount}</div>
						<div class="text-xs text-gray-600 dark:text-gray-400">Completed</div>
					</div>
					<div class="text-center">
						<div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{remainingLessonsCount}</div>
						<div class="text-xs text-gray-600 dark:text-gray-400">Remaining</div>
					</div>
				</div>
			</div>
		</Card>
	</div>
{/snippet}

{#snippet CourseNavigation(course, currentLesson, loadLesson, hasAccess)}
	<div in:fly={{ y: 20, delay: 400, duration: 600 }}>
		<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-lg dark:bg-gray-800/95">
			<div class="flex items-center gap-3 mb-4">
				<div class="rounded-lg bg-indigo-100 p-2 dark:bg-indigo-900/30">
					<svg class="h-5 w-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
					</svg>
				</div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Course Content</h3>
			</div>
			
			<div class="max-h-96 overflow-y-auto">
				<LessonList
					modules={course.modules}
					currentLessonId={currentLesson.uuid}
					onLessonClick={loadLesson}
					isEnrolled={hasAccess}
					compact={true}
				/>
			</div>
		</Card>
	</div>
 {/snippet}
 
 {#snippet QuickActions(courseId)}
	<div in:fly={{ y: 20, delay: 500, duration: 600 }}>
		<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-lg dark:bg-gray-800/95">
			<div class="flex items-center gap-3 mb-4">
				<div class="rounded-lg bg-purple-100 p-2 dark:bg-purple-900/30">
					<svg class="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
					</svg>
				</div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h3>
			</div>
			
			<div class="space-y-2">
				<Button
					href="/forum"
					variant="outline"
					size="small"
					fullWidth
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
					</svg>
					Discussion Forum
				</Button>
 
				<Button 
					href={`/courses/${courseId}`} 
					variant="outline" 
					size="small" 
					fullWidth 
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Course Overview
				</Button>
 
				<Button 
					href="/my-courses" 
					variant="outline" 
					size="small" 
					fullWidth 
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
					</svg>
					My Courses
				</Button>
 
				<Button 
					href="/certificates" 
					variant="outline" 
					size="small" 
					fullWidth 
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
					</svg>
					My Certificates
				</Button>
			</div>
		</Card>
	</div>
 {/snippet}
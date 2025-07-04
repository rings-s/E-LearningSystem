<!-- front/src/routes/(app)/courses/[uuid]/learn/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { classNames, debounce } from '$lib/utils/helpers.js';
	import { formatters } from '$lib/utils/formatters.js';

	// Components
	import YouTubePlayer from '$lib/components/course/YouTubePlayer.svelte';
	import LessonList from '$lib/components/course/LessonList.svelte';
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';

	const courseId = $page.params.uuid;

	let course = $state(null);
	let enrollment = $state(null);
	let currentLesson = $state(null);
	let loading = $state(true);
	let completingLesson = $state(false);
	let sidebarOpen = $state(true);
	let notes = $state('');
	let videoProgress = $state({ currentTime: 0, duration: 0, progress: 0 });
	let notesSaving = $state(false);
	let notesLastSaved = $state(null);

	// Error tracking
	let errorState = $state({
		type: null, // 'not_found', 'no_access', 'no_lessons', 'network_error', 'auth_error'
		message: '',
		details: ''
	});

	// Navigation state
	let lessons = $derived(() => {
		if (!course?.modules) return [];
		return course.modules.flatMap((module) =>
			module.lessons.map((lesson) => ({ ...lesson, moduleTitle: module.title }))
		);
	});

	let currentLessonIndex = $derived(() => {
		if (!currentLesson || !lessons.length) return -1;
		return lessons.findIndex((lesson) => lesson.uuid === currentLesson.uuid);
	});

	let previousLesson = $derived(() => {
		return currentLessonIndex > 0 ? lessons[currentLessonIndex - 1] : null;
	});

	let nextLesson = $derived(() => {
		return currentLessonIndex < lessons.length - 1 ? lessons[currentLessonIndex + 1] : null;
	});

	onMount(async () => {
		await Promise.all([fetchCourse(), fetchEnrollment()]);
	});

	const fetchCourse = async () => {
		try {
			course = await coursesApi.getCourse(courseId);

			// Check if course has any content
			if (!course.modules || course.modules.length === 0) {
				errorState = {
					type: 'no_lessons',
					message: 'This course has no lessons yet',
					details:
						"The course instructor hasn't added any lessons to this course yet. Please check back later or contact the instructor."
				};
				return;
			}

			// Find first incomplete lesson or first lesson
			let foundLesson = null;

			for (const module of course.modules) {
				if (!module.lessons || module.lessons.length === 0) continue;

				for (const lesson of module.lessons) {
					if (!lesson.is_completed && !foundLesson) {
						foundLesson = lesson;
						break;
					}
				}
				if (foundLesson) break;
			}

			// If all completed, load first lesson
			if (!foundLesson) {
				// Find the first lesson in any module
				for (const module of course.modules) {
					if (module.lessons && module.lessons.length > 0) {
						foundLesson = module.lessons[0];
						break;
					}
				}
			}

			if (foundLesson) {
				await loadLesson(foundLesson);
			} else {
				errorState = {
					type: 'no_lessons',
					message: 'No lessons available',
					details:
						"This course doesn't have any lessons available yet. Please contact the instructor or check back later."
				};
			}
		} catch (error) {
			// Determine error type based on error message or status
			if (error.message.includes('Unauthorized') || error.message.includes('401')) {
				errorState = {
					type: 'auth_error',
					message: 'Authentication required',
					details: 'Please log in to access this course. You may need to refresh your session.'
				};
			} else if (error.message.includes('404') || error.message.includes('Not found')) {
				errorState = {
					type: 'not_found',
					message: 'Course not found',
					details:
						"The course you're looking for doesn't exist or may have been removed. Please check the URL and try again."
				};
			} else if (error.message.includes('403') || error.message.includes('Forbidden')) {
				errorState = {
					type: 'no_access',
					message: 'Access denied',
					details: "You don't have permission to access this course. You may need to enroll first."
				};
			} else {
				errorState = {
					type: 'network_error',
					message: 'Unable to load course',
					details:
						'There was a problem connecting to the server. Please check your internet connection and try again.'
				};
			}
		} finally {
			loading = false;
		}
	};

	const fetchEnrollment = async () => {
		try {
			const enrollments = await coursesApi.getMyEnrollments();
			enrollment = enrollments.find((e) => e.course.uuid === courseId);
		} catch (error) {
			// Enrollment fetch failed - user may not be enrolled
		}
	};

	// Check if current user is instructor or co-instructor
	const isInstructor = $derived(() => {
		if (!course || !$currentUser) return false;
		return (
			course.instructor.uuid === $currentUser.uuid ||
			course.co_instructors?.some((inst) => inst.uuid === $currentUser.uuid)
		);
	});

	// Check if user has access to course content
	const hasAccess = $derived(() => {
		return isInstructor || (enrollment && enrollment.is_active);
	});

	const loadLesson = async (lesson) => {
		try {
			currentLesson = await coursesApi.getLesson(lesson.uuid);
			videoProgress = { currentTime: 0, duration: 0, progress: 0 };
			// Notes will be loaded by the $effect below
		} catch (error) {
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: 'Failed to load lesson'
			});
		}
	};

	const completeLesson = async () => {
		if (!currentLesson || currentLesson.is_completed) return;

		completingLesson = true;
		try {
			await coursesApi.completeLesson(currentLesson.uuid);
			currentLesson.is_completed = true;

			// Update enrollment progress
			if (enrollment) {
				const totalLessons = lessons.length;
				const completedLessons = lessons.filter(
					(l) => l.is_completed || l.uuid === currentLesson.uuid
				).length;
				enrollment.progress_percentage = Math.round((completedLessons / totalLessons) * 100);
			}

			uiStore.showNotification({
				type: 'success',
				title: 'Lesson Completed! 🎉',
				message: 'Great job! Keep up the excellent work.'
			});

			// Auto-advance to next lesson after 2 seconds
			if (nextLesson) {
				setTimeout(() => {
					loadLesson(nextLesson);
				}, 2000);
			} else {
				// Course completed
				uiStore.showNotification({
					type: 'success',
					title: 'Course Completed! 🏆',
					message: 'Congratulations! You have completed all lessons in this course.'
				});
			}
		} catch (error) {
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: 'Failed to complete lesson'
			});
		} finally {
			completingLesson = false;
		}
	};

	const handleVideoProgress = (data) => {
		videoProgress = data;

		// Auto-complete lesson when video reaches 90%
		if (data.progress >= 90 && !currentLesson.is_completed) {
			completeLesson();
		}
	};

	const saveNotes = async (showNotification = true) => {
		if (!notes.trim() || !currentLesson) return;

		notesSaving = true;
		try {
			await coursesApi.saveLessonNotes(currentLesson.uuid, notes);
			
			// Also save to localStorage as backup
			localStorage.setItem(`notes_${currentLesson.uuid}`, notes);
			notesLastSaved = new Date();

			if (showNotification) {
				uiStore.showNotification({
					type: 'success',
					title: 'Notes Saved',
					message: 'Your notes have been saved'
				});
			}
		} catch (error) {
			if (showNotification) {
				uiStore.showNotification({
					type: 'error',
					title: 'Error',
					message: 'Failed to save notes'
				});
			}
		} finally {
			notesSaving = false;
		}
	};

	// Debounced auto-save function
	const debouncedAutoSave = debounce(() => {
		saveNotes(false); // Auto-save without notification
	}, 2000);

	const loadNotes = async (lessonId) => {
		try {
			// Try to load from API first
			const response = await coursesApi.getLessonNotes(lessonId);
			notes = response.notes || '';
		} catch (error) {
			// Fallback to localStorage
			const savedNotes = localStorage.getItem(`notes_${lessonId}`);
			notes = savedNotes || '';
		}
	};

	// Load notes when lesson changes
	$effect(() => {
		if (currentLesson) {
			loadNotes(currentLesson.uuid);
		}
	});

	// Auto-save when notes change
	$effect(() => {
		if (notes && currentLesson) {
			debouncedAutoSave();
		}
	});
</script>

<svelte:head>
	<title>{currentLesson?.title || 'Learning'} - {course?.title || 'Course'} - 244SCHOOL</title>
</svelte:head>

{#if loading}
	<div class="flex h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800" in:fade={{ duration: 300 }}>
		<div class="text-center" in:fly={{ y: 20, duration: 600, delay: 200 }}>
			<div class="border-primary-500 mx-auto mb-6 h-20 w-20 animate-spin rounded-full border-4 border-t-transparent shadow-lg"></div>
			<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">Loading your course...</h3>
			<p class="text-gray-600 dark:text-gray-400">Please wait while we prepare your learning experience</p>
		</div>
	</div>
{:else if course && currentLesson && hasAccess}
	<div class="flex h-screen overflow-hidden bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800" in:fade={{ duration: 600 }}>
		<!-- Modern Sidebar -->
		<aside
			class={classNames(
				'flex-shrink-0 overflow-hidden transition-all duration-300 ease-out border-r border-gray-200/50 backdrop-blur-sm dark:border-gray-700/50',
				sidebarOpen ? 'w-96' : 'w-0'
			)}
		>
			<div class="flex h-full flex-col bg-white/95 dark:bg-gray-800/95">
				<!-- Enhanced Sidebar Header -->
				<div class="border-b border-gray-200/50 bg-gradient-to-r from-primary-50 to-secondary-50 p-6 dark:border-gray-700/50 dark:from-primary-900/20 dark:to-secondary-900/20">
					<div class="mb-4 flex items-center justify-between">
						<Button
							href={`/courses/${courseId}`}
							variant="ghost"
							size="small"
							class="group hover:text-primary-600 dark:hover:text-primary-400 text-gray-600 dark:text-gray-400 transition-all hover:scale-105"
						>
							<svg class="mr-2 h-4 w-4 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
							</svg>
							Back to Course
						</Button>

						<button
							onclick={() => (sidebarOpen = false)}
							class="rounded-lg p-2 text-gray-400 transition-all hover:bg-white/50 hover:text-gray-600 lg:hidden dark:hover:bg-gray-700/50 dark:hover:text-gray-300"
							aria-label="Close sidebar"
						>
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</div>

					<div class="space-y-4">
						<h2 class="line-clamp-2 text-lg font-bold text-gray-900 dark:text-white">
							{course.title}
						</h2>

						<!-- Enhanced Progress Display -->
						<div class="rounded-xl bg-white/80 p-4 backdrop-blur-sm dark:bg-gray-800/80">
							<div class="mb-3 flex items-center justify-between">
								<span class="text-sm font-medium text-gray-700 dark:text-gray-300">Course Progress</span>
								<span class="text-sm font-bold text-primary-600 dark:text-primary-400">
									{enrollment?.progress_percentage || 0}%
								</span>
							</div>
							<CourseProgress
								progress={enrollment?.progress_percentage || 0}
								showLabel={false}
								size="large"
								class="mb-2"
							/>
							<div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
								<span>{lessons.filter(l => l.is_completed).length} of {lessons.length} completed</span>
								<span>{lessons.length - lessons.filter(l => l.is_completed).length} remaining</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Lesson List with Enhanced Styling -->
				<div class="flex-1 overflow-y-auto">
					<LessonList
						modules={course.modules}
						currentLessonId={currentLesson.uuid}
						onLessonClick={loadLesson}
						isEnrolled={hasAccess}
						class="p-2"
					/>
				</div>
			</div>
		</aside>

		<!-- Main Content Area -->
		<main class="flex min-w-0 flex-1 flex-col">
			<!-- Modern Header -->
			<header class="flex-shrink-0 border-b border-gray-200/50 bg-white/95 px-6 py-4 backdrop-blur-sm dark:border-gray-700/50 dark:bg-gray-800/95">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-4">
						{#if !sidebarOpen}
							<button
								onclick={() => (sidebarOpen = true)}
								class="rounded-lg p-2 text-gray-500 transition-all hover:bg-gray-100 hover:text-gray-700 hover:scale-105 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200"
								aria-label="Open sidebar"
							>
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
								</svg>
							</button>
						{/if}

						<div class="space-y-1">
							<h1 class="text-xl font-bold text-gray-900 dark:text-white">
								{currentLesson.title}
							</h1>
							<p class="text-sm text-gray-600 dark:text-gray-400">
								{#if currentLesson?.moduleTitle && lessons.length > 0 && currentLessonIndex >= 0}
									{currentLesson.moduleTitle} • Lesson {currentLessonIndex + 1} of {lessons.length}
								{:else if currentLesson?.moduleTitle}
									{currentLesson.moduleTitle}
								{/if}
							</p>
						</div>
					</div>

					<div class="flex items-center gap-3">
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
					</div>
				</div>
			</header>

			<!-- Content Area with Enhanced Layout -->
			<div class="flex-1 overflow-y-auto">
				<div class="mx-auto max-w-7xl p-6">
					<!-- Video Player Section -->
					{#if currentLesson.video_url}
						<div class="mb-8" in:fly={{ y: 20, duration: 600, delay: 200 }}>
							<Card variant="bordered" class="overflow-hidden shadow-2xl">
								<div class="-m-6">
									<YouTubePlayer
										videoId={currentLesson.video_url}
										onProgress={handleVideoProgress}
										onReady={() => {}}
										class="w-full"
									/>
								</div>
							</Card>
						</div>
					{/if}

					<!-- Content Grid -->
					<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
						<!-- Main Content -->
						<div class="space-y-6 lg:col-span-2">
							<!-- Lesson Description -->
							{#if currentLesson.description}
								<div in:fly={{ y: 20, delay: 300, duration: 600 }}>
									<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
										<div class="flex items-center gap-3 mb-4">
											<div class="rounded-lg bg-primary-100 p-2 dark:bg-primary-900/30">
												<svg class="h-5 w-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											</div>
											<h3 class="text-lg font-semibold text-gray-900 dark:text-white">About This Lesson</h3>
										</div>
										<div class="prose prose-gray dark:prose-invert max-w-none">
											{currentLesson.description}
										</div>
									</Card>
								</div>
							{/if}

							<!-- Text Content -->
							{#if currentLesson.text_content}
								<div in:fly={{ y: 20, delay: 400, duration: 600 }}>
									<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
									<div class="flex items-center gap-3 mb-4">
										<div class="rounded-lg bg-green-100 p-2 dark:bg-green-900/30">
											<svg class="h-5 w-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
											</svg>
										</div>
										<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Lesson Materials</h3>
									</div>
										<div class="prose prose-gray dark:prose-invert max-w-none">
											{@html currentLesson.text_content}
										</div>
									</Card>
								</div>
							{/if}

							<!-- Resources -->
							{#if currentLesson.resources?.length > 0}
								<div in:fly={{ y: 20, delay: 500, duration: 600 }}>
									<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
									<div class="flex items-center gap-3 mb-4">
										<div class="rounded-lg bg-purple-100 p-2 dark:bg-purple-900/30">
											<svg class="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
											</svg>
										</div>
										<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Additional Resources</h3>
									</div>
									<div class="space-y-3">
										{#each currentLesson.resources as resource}
											<a
												href={resource.file || resource.url}
												target="_blank"
												rel="noopener noreferrer"
												class="group flex items-center justify-between rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 p-4 transition-all hover:from-primary-50 hover:to-primary-100 hover:shadow-md dark:from-gray-800/50 dark:to-gray-700/50 dark:hover:from-primary-900/20 dark:hover:to-primary-800/20"
											>
												<div class="flex items-center gap-4">
													<div class="bg-primary-100 dark:bg-primary-900/30 flex h-12 w-12 items-center justify-center rounded-xl transition-all group-hover:scale-110">
														<svg class="text-primary-600 dark:text-primary-400 h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
															<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
														</svg>
													</div>
													<div>
														<h4 class="group-hover:text-primary-600 dark:group-hover:text-primary-400 font-medium text-gray-900 transition-colors dark:text-white">
															{resource.title}
														</h4>
														{#if resource.description}
															<p class="text-sm text-gray-600 dark:text-gray-400">
																{resource.description}
															</p>
														{/if}
													</div>
												</div>

												<svg class="group-hover:text-primary-600 dark:group-hover:text-primary-400 h-5 w-5 text-gray-400 transition-all group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
												</svg>
											</a>
											{/each}
										</div>
									</Card>
								</div>
							{/if}

							<!-- Navigation -->
							<div in:fly={{ y: 20, delay: 600, duration: 600 }}>
								<Card variant="bordered" class="shadow-lg">
								<div class="flex items-center justify-between">
									<Button
										onclick={() => previousLesson && loadLesson(previousLesson)}
										variant="outline"
										disabled={!previousLesson}
										size="medium"
										class="transition-all hover:scale-105"
									>
										<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
										</svg>
										Previous Lesson
									</Button>

									<span class="text-sm text-gray-500 dark:text-gray-400">
										{#if lessons.length > 0 && currentLessonIndex >= 0}
											{currentLessonIndex + 1} of {lessons.length}
										{:else}
											-
										{/if}
									</span>

									<Button
										onclick={() => nextLesson && loadLesson(nextLesson)}
										variant="primary"
										disabled={!nextLesson}
										size="medium"
										class="transition-all hover:scale-105"
									>
										Next Lesson
										<svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
										</svg>
									</Button>
								</div>
							</Card>
						</div>
						</div>

						<!-- Enhanced Sidebar -->
						<div class="space-y-6">
							<!-- Progress Card -->
							<div in:fly={{ y: 20, delay: 300, duration: 600 }}>
								<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
								<div class="flex items-center gap-3 mb-4">
									<div class="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
										<svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
										</svg>
									</div>
									<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Your Progress</h3>
								</div>
								<div class="space-y-4">
									<div>
										<div class="mb-2 flex justify-between text-sm">
											<span class="font-medium text-gray-700 dark:text-gray-300">Course Progress</span>
											<span class="font-semibold text-primary-600 dark:text-primary-400">{enrollment?.progress_percentage || 0}%</span>
										</div>
										<CourseProgress progress={enrollment?.progress_percentage || 0} size="medium" />
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
								</div>
							</Card>
						</div>

							<!-- Enhanced Notes -->
							<div in:fly={{ y: 20, delay: 400, duration: 600 }}>
								<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
								<div class="mb-4 flex items-center justify-between">
									<div class="flex items-center gap-3">
										<div class="rounded-lg bg-yellow-100 p-2 dark:bg-yellow-900/30">
											<svg class="h-5 w-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
											</svg>
										</div>
										<h3 class="text-lg font-semibold text-gray-900 dark:text-white">My Notes</h3>
									</div>
									<div class="text-xs text-gray-500 dark:text-gray-400">
										{#if notesSaving}
											<span class="flex items-center gap-1">
												<div class="h-3 w-3 animate-spin rounded-full border border-primary-500 border-t-transparent"></div>
												Saving...
											</span>
										{:else if notesLastSaved}
											<span>Saved {formatters.relativeTime(notesLastSaved)}</span>
										{:else}
											<span>Auto-saves as you type</span>
										{/if}
									</div>
								</div>
								<div class="space-y-3">
									<textarea
										bind:value={notes}
										placeholder="Take notes about this lesson... Notes are automatically saved to your account."
										class="focus:ring-primary-500 focus:border-primary-500 h-32 w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 transition-all focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
									></textarea>

									<div class="flex items-center justify-between">
										<div class="text-xs text-gray-500 dark:text-gray-400">
											Notes are stored in your account and synced across devices
										</div>
										<Button
											onclick={() => saveNotes(true)}
											variant="outline"
											size="small"
											disabled={!notes.trim() || notesSaving}
											loading={notesSaving}
											class="transition-all hover:scale-105"
										>
											{notesSaving ? 'Saving...' : 'Save Now'}
										</Button>
									</div>
								</div>
							</Card>
						</div>

							<!-- Quick Actions -->
							<div in:fly={{ y: 20, delay: 500, duration: 600 }}>
								<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
								<div class="flex items-center gap-3 mb-4">
									<div class="rounded-lg bg-indigo-100 p-2 dark:bg-indigo-900/30">
										<svg class="h-5 w-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
										class="transition-all hover:scale-[1.02]"
									>
										<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
										</svg>
										Discussion Forum
									</Button>

									<Button href={`/courses/${courseId}`} variant="outline" size="small" fullWidth class="transition-all hover:scale-[1.02]">
										<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
										</svg>
										Course Info
									</Button>

									<Button href={`/my-courses/${courseId}/notes`} variant="outline" size="small" fullWidth class="transition-all hover:scale-[1.02]">
										<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
										</svg>
										View All Notes
									</Button>
								</div>
							</Card>
						</div>
						</div>
					</div>
				</div>
			</div>
		</main>
	</div>
{:else}
	<!-- Enhanced Error States -->
	<div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-white p-6 dark:from-gray-900 dark:to-gray-800" in:fade={{ duration: 600 }}>
		<div class="w-full max-w-md text-center">
			<Card variant="bordered" class="p-8 shadow-2xl">
				<div in:scale={{ duration: 600, start: 0.8 }}>
					<!-- Error Icons -->
					{#if errorState.type === 'not_found'}
						<div class="mx-auto mb-6 rounded-full bg-red-100 p-4 dark:bg-red-900/20">
							<svg class="h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
						</div>
					{:else if errorState.type === 'no_access'}
						<div class="mx-auto mb-6 rounded-full bg-orange-100 p-4 dark:bg-orange-900/20">
							<svg class="h-12 w-12 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
							</svg>
						</div>
					{:else if errorState.type === 'no_lessons'}
						<div class="mx-auto mb-6 rounded-full bg-blue-100 p-4 dark:bg-blue-900/20">
							<svg class="h-12 w-12 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
							</svg>
						</div>
					{:else if errorState.type === 'auth_error'}
						<div class="mx-auto mb-6 rounded-full bg-yellow-100 p-4 dark:bg-yellow-900/20">
							<svg class="h-12 w-12 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
						</div>
					{:else}
						<div class="mx-auto mb-6 rounded-full bg-gray-100 p-4 dark:bg-gray-800">
							<svg class="h-12 w-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
					{/if}

					<!-- Error Title -->
					<h2 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
						{#if errorState.type}
							{errorState.message}
						{:else if course && !hasAccess}
							Access Denied
						{:else}
							Something went wrong
						{/if}
					</h2>

					<!-- Error Details -->
					<p class="mb-8 leading-relaxed text-gray-600 dark:text-gray-400">
						{#if errorState.type}
							{errorState.details}
						{:else if course && !hasAccess}
							You need to be enrolled in this course to access the learning materials.
						{:else}
							We encountered an unexpected issue. Please try again later.
						{/if}
					</p>

					<!-- Action Buttons -->
					<div class="flex flex-col justify-center gap-4 sm:flex-row">
						{#if errorState.type === 'not_found'}
							<Button href="/courses" variant="primary" class="transition-all hover:scale-105">Browse Courses</Button>
							<Button href="/my-courses" variant="outline" class="transition-all hover:scale-105">My Courses</Button>
						{:else if errorState.type === 'no_access'}
							<Button href={`/courses/${courseId}`} variant="primary" class="transition-all hover:scale-105">View Course Details</Button>
							<Button href={`/courses/${courseId}#enroll`} variant="outline" class="transition-all hover:scale-105">Enroll Now</Button>
						{:else if errorState.type === 'no_lessons'}
							<Button href={`/courses/${courseId}`} variant="primary" class="transition-all hover:scale-105">Course Information</Button>
							{#if isInstructor}
								<Button href={`/courses/${courseId}/manage`} variant="outline" class="transition-all hover:scale-105">Add Lessons</Button>
							{:else}
								<Button href="/courses" variant="outline" class="transition-all hover:scale-105">Browse Other Courses</Button>
							{/if}
						{:else if errorState.type === 'auth_error'}
							<Button href="/login" variant="primary" class="transition-all hover:scale-105">Sign In</Button>
							<Button onclick={() => window.location.reload()} variant="outline" class="transition-all hover:scale-105">Refresh Page</Button>
						{:else}
							<Button onclick={() => window.location.reload()} variant="primary" class="transition-all hover:scale-105">Try Again</Button>
							<Button href="/courses" variant="outline" class="transition-all hover:scale-105">Browse Courses</Button>
						{/if}
					</div>
				</div>
			</Card>
		</div>
	</div>
{/if}
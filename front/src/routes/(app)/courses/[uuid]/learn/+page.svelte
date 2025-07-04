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
		type: null,
		message: '',
		details: ''
	});

	// Navigation state
	let lessons = $derived(() => {
		const modules = course?.modules;
		if (!Array.isArray(modules)) {
			console.log('No modules found or not an array:', modules);
			return [];
		}
		try {
			const allLessons = modules.flatMap((module) => {
				if (!module || !Array.isArray(module.lessons)) return [];
				return module.lessons.map((lesson) => ({ 
					...lesson, 
					moduleTitle: module.title || '',
					module_title: module.title || ''
				}));
			});
			console.log('Processed lessons:', allLessons);
			return allLessons;
		} catch (error) {
			console.error('Error processing lessons:', error);
			return [];
		}
	});

	let currentLessonIndex = $derived(() => {
		if (!currentLesson || !lessons.length) return -1;
		const index = lessons.findIndex((lesson) => lesson.uuid === currentLesson.uuid);
		console.log('Current lesson index:', index);
		return index;
	});

	let previousLesson = $derived(() => {
		return currentLessonIndex > 0 ? lessons[currentLessonIndex - 1] : null;
	});

	let nextLesson = $derived(() => {
		return currentLessonIndex < lessons.length - 1 ? lessons[currentLessonIndex + 1] : null;
	});

	let totalLessonsCount = $derived(() => lessons.length);
	let completedLessonsCount = $derived(() => lessons.filter(l => l.is_completed).length);
	let remainingLessonsCount = $derived(() => totalLessonsCount - completedLessonsCount);

	onMount(async () => {
		console.log('Learn page mounted for course:', courseId);
		await Promise.all([fetchCourse(), fetchEnrollment()]);
	});

	const fetchCourse = async () => {
		try {
			console.log('Fetching course data...');
			course = await coursesApi.getCourse(courseId);
			console.log('Course data loaded:', course);

			if (!course.modules || course.modules.length === 0) {
				console.warn('Course has no modules');
				errorState = {
					type: 'no_lessons',
					message: 'This course has no lessons yet',
					details: "The course instructor hasn't added any lessons to this course yet. Please check back later or contact the instructor."
				};
				return;
			}

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

			if (!foundLesson) {
				for (const module of course.modules) {
					if (module.lessons && module.lessons.length > 0) {
						foundLesson = module.lessons[0];
						break;
					}
				}
			}

			if (foundLesson) {
				console.log('Loading lesson:', foundLesson);
				await loadLesson(foundLesson);
			} else {
				console.warn('No lessons found in course');
				errorState = {
					type: 'no_lessons',
					message: 'No lessons available',
					details: "This course doesn't have any lessons available yet. Please contact the instructor or check back later."
				};
			}
		} catch (error) {
			console.error('Error fetching course:', error);
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
					details: "The course you're looking for doesn't exist or may have been removed. Please check the URL and try again."
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
					details: 'There was a problem connecting to the server. Please check your internet connection and try again.'
				};
			}
		} finally {
			loading = false;
		}
	};

	const fetchEnrollment = async () => {
		try {
			console.log('Fetching enrollment data...');
			const enrollments = await coursesApi.getMyEnrollments();
			enrollment = enrollments.find((e) => e.course.uuid === courseId);
			console.log('Enrollment found:', enrollment);
		} catch (error) {
			console.error('Error fetching enrollment:', error);
		}
	};

	const isInstructor = $derived(() => {
		if (!course || !$currentUser) return false;
		return (
			course.instructor.uuid === $currentUser.uuid ||
			course.co_instructors?.some((inst) => inst.uuid === $currentUser.uuid)
		);
	});

	const hasAccess = $derived(() => {
		return isInstructor || (enrollment && enrollment.is_active);
	});

	const loadLesson = async (lesson) => {
		try {
			console.log('Loading lesson:', lesson.uuid);
			currentLesson = await coursesApi.getLesson(lesson.uuid);
			console.log('Lesson loaded:', currentLesson);
			videoProgress = { currentTime: 0, duration: 0, progress: 0 };
		} catch (error) {
			console.error('Error loading lesson:', error);
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: 'Failed to load lesson'
			});
		}
	};

	const completeLesson = async () => {
		if (!currentLesson || currentLesson.is_completed) return;

		console.log('Completing lesson:', currentLesson.uuid);
		completingLesson = true;
		try {
			await coursesApi.completeLesson(currentLesson.uuid);
			currentLesson.is_completed = true;

			if (enrollment) {
				const totalLessons = lessons.length;
				const completedLessons = lessons.filter(
					(l) => l.is_completed || l.uuid === currentLesson.uuid
				).length;
				enrollment.progress_percentage = Math.round((completedLessons / totalLessons) * 100);
				console.log('Updated progress:', enrollment.progress_percentage);
			}

			uiStore.showNotification({
				type: 'success',
				title: 'Lesson Completed! 🎉',
				message: 'Great job! Keep up the excellent work.'
			});

			if (nextLesson) {
				setTimeout(() => {
					console.log('Auto-advancing to next lesson');
					loadLesson(nextLesson);
				}, 2000);
			} else {
				console.log('Course completed!');
				uiStore.showNotification({
					type: 'success',
					title: 'Course Completed! 🏆',
					message: 'Congratulations! You have completed all lessons in this course.'
				});
			}
		} catch (error) {
			console.error('Error completing lesson:', error);
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
		console.log('Video progress:', data);

		if (data.progress >= 90 && !currentLesson.is_completed) {
			console.log('Auto-completing lesson at 90% video progress');
			completeLesson();
		}
	};

	const saveNotes = async (showNotification = true) => {
		if (!notes.trim() || !currentLesson) return;

		console.log('Saving notes for lesson:', currentLesson.uuid);
		notesSaving = true;
		try {
			await coursesApi.saveLessonNotes(currentLesson.uuid, notes);
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
			console.error('Error saving notes:', error);
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

	const debouncedAutoSave = debounce(() => {
		console.log('Auto-saving notes...');
		saveNotes(false);
	}, 2000);

	const loadNotes = async (lessonId) => {
		try {
			console.log('Loading notes for lesson:', lessonId);
			const response = await coursesApi.getLessonNotes(lessonId);
			notes = response.notes || '';
		} catch (error) {
			console.log('API notes failed, trying localStorage:', error);
			const savedNotes = localStorage.getItem(`notes_${lessonId}`);
			notes = savedNotes || '';
		}
	};

	$effect(() => {
		if (currentLesson) {
			loadNotes(currentLesson.uuid);
		}
	});

	$effect(() => {
		if (notes && currentLesson) {
			debouncedAutoSave();
		}
	});
</script>

<svelte:head>
	<title>{currentLesson?.title || 'Learning'} - {course?.title || 'Course'} - 244SCHOOL</title>
	<meta
		name="description"
		content="Continue your learning journey with {course?.title || 'this course'} on 244SCHOOL"
	/>
</svelte:head>

<!-- Loading State -->
{#if loading}
	<div class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800" in:fade={{ duration: 300 }}>
		<div class="flex h-screen items-center justify-center">
			<div class="text-center" in:fly={{ y: 20, duration: 600, delay: 200 }}>
				<div class="mx-auto mb-6 h-20 w-20 animate-spin rounded-full border-4 border-primary-500 border-t-transparent shadow-lg"></div>
				<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">Loading your course...</h3>
				<p class="text-gray-600 dark:text-gray-400">Please wait while we prepare your learning experience</p>
			</div>
		</div>
	</div>

<!-- Main Learning Interface -->
{:else if course && currentLesson && hasAccess}
	<div class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800" in:fade={{ duration: 600 }}>
		<!-- Hero Section - Similar to courses page -->
		<div class="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600 text-white">
			<!-- Background Pattern -->
			<div class="absolute inset-0 opacity-10">
				<div class="h-full w-full bg-white bg-opacity-5" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0); background-size: 40px 40px;"></div>
			</div>
			
			<div class="container relative mx-auto px-4 py-12">
				<div class="mx-auto max-w-6xl">
					<div in:fly={{ y: 30, delay: 200, duration: 800 }} class="mb-6">
						<!-- Navigation breadcrumb -->
						<div class="mb-4 flex items-center gap-2 text-white/70">
							<Button
								href="/courses"
								variant="ghost"
								size="small"
								class="text-white/70 hover:text-white transition-colors"
							>
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
								</svg>
								All Courses
							</Button>
							<span>/</span>
							<Button
								href={`/courses/${courseId}`}
								variant="ghost"
								size="small"
								class="text-white/70 hover:text-white transition-colors"
							>
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
							
							{#if currentLesson?.moduleTitle && lessons.length > 0 && currentLessonIndex >= 0}
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
							{/if}
						</div>
					</div>

					<!-- Progress Bar -->
					<div in:fly={{ y: 30, delay: 400, duration: 800 }} class="rounded-2xl bg-white/10 p-6 backdrop-blur-sm">
						<div class="mb-3 flex items-center justify-between">
							<span class="font-medium text-white/90">Course Progress</span>
							<span class="font-bold text-yellow-400">
								{enrollment?.progress_percentage || 0}%
							</span>
						</div>
						<CourseProgress
							progress={enrollment?.progress_percentage || 0}
							showLabel={false}
							size="large"
							class="mb-2"
						/>
						<div class="flex items-center justify-between text-sm text-white/70">
							<span>{completedLessonsCount} of {totalLessonsCount} completed</span>
							<span>{remainingLessonsCount} remaining</span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="container mx-auto px-4 py-12">
			<!-- Main Content Layout -->
			<div class="grid grid-cols-1 gap-8 lg:grid-cols-4">
				
				<!-- Main Content Area -->
				<div class="lg:col-span-3 space-y-8">
					
					<!-- Video Player -->
					{#if currentLesson.video_url}
						<div in:fly={{ y: 20, duration: 600, delay: 200 }}>
							<Card variant="bordered" class="overflow-hidden shadow-2xl">
								<div class="-m-6">
									<YouTubePlayer
										videoId={currentLesson.video_url}
										onProgress={handleVideoProgress}
										onReady={() => {}}
										class="w-full aspect-video"
									/>
								</div>
							</Card>
						</div>
					{/if}

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
										class="transition-all hover:scale-105"
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
										class="transition-all hover:scale-105"
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

					<!-- Lesson Content -->
					{#if currentLesson.description}
						<div in:fly={{ y: 20, delay: 400, duration: 600 }}>
							<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
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

					{#if currentLesson.text_content}
						<div in:fly={{ y: 20, delay: 500, duration: 600 }}>
							<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
								<div class="flex items-center gap-3 mb-4">
									<div class="rounded-lg bg-green-100 p-3 dark:bg-green-900/30">
										<svg class="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
										</svg>
									</div>
									<h3 class="text-xl font-semibold text-gray-900 dark:text-white">Lesson Materials</h3>
								</div>
								<div class="prose prose-gray dark:prose-invert max-w-none">
									{@html currentLesson.text_content}
								</div>
							</Card>
						</div>
					{/if}

					<!-- Resources -->
					{#if currentLesson.resources?.length > 0}
						<div in:fly={{ y: 20, delay: 600, duration: 600 }}>
							<Card variant="bordered" class="shadow-lg transition-all hover:shadow-xl">
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
											class="group flex items-center gap-4 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 p-4 transition-all hover:from-primary-50 hover:to-primary-100 hover:shadow-md hover:scale-[1.02] dark:from-gray-800/50 dark:to-gray-700/50 dark:hover:from-primary-900/20 dark:hover:to-primary-800/20"
										>
											<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-100 transition-all group-hover:scale-110 dark:bg-primary-900/30">
												<svg class="h-6 w-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
												</svg>
											</div>
											<div class="flex-1">
												<h4 class="font-medium text-gray-900 transition-colors group-hover:text-primary-600 dark:text-white dark:group-hover:text-primary-400">
													{resource.title}
												</h4>
												{#if resource.description}
													<p class="text-sm text-gray-600 dark:text-gray-400">
														{resource.description}
													</p>
												{/if}
											</div>
											<svg class="h-5 w-5 text-gray-400 transition-all group-hover:text-primary-600 group-hover:translate-x-1 dark:group-hover:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
											</svg>
										</a>
									{/each}
								</div>
							</Card>
						</div>
					{/if}
				</div>

				<!-- Enhanced Sidebar -->
				<div class="space-y-6">
					
					<!-- Course Overview -->
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

   				<!-- Lesson Navigation -->
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

   				<!-- Notes Section -->
   				<div in:fly={{ y: 20, delay: 500, duration: 600 }}>
   					<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-lg dark:bg-gray-800/95">
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
   									<span>Auto-saves</span>
   								{/if}
   							</div>
   						</div>
   						
   						<div class="space-y-3">
   							<textarea
   								bind:value={notes}
   								placeholder="Take notes about this lesson... Notes are automatically saved to your account."
   								class="h-32 w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 transition-all focus:border-primary-500 focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
   							></textarea>

   							<div class="flex items-center justify-between">
   								<div class="text-xs text-gray-500 dark:text-gray-400">
   									Notes are synced across devices
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
   				<div in:fly={{ y: 20, delay: 600, duration: 600 }}>
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
   								class="transition-all hover:scale-[1.02]"
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
   								class="transition-all hover:scale-[1.02]"
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
   								class="transition-all hover:scale-[1.02]"
   							>
   								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
   									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
   								</svg>
   								My Courses
   							</Button>
   						</div>
   					</Card>
   				</div>
   			</div>
   		</div>
   	</div>
   </div>

<!-- Error States -->
{:else}
   <div class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800" in:fade={{ duration: 600 }}>
   	<!-- Hero Section for Error State -->
   	<div class="relative overflow-hidden bg-gradient-to-br from-red-600 via-red-700 to-red-800 text-white">
   		<div class="absolute inset-0 opacity-10">
   			<div class="h-full w-full bg-white bg-opacity-5" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0); background-size: 40px 40px;"></div>
   		</div>
   		
   		<div class="container relative mx-auto px-4 py-16">
   			<div class="mx-auto max-w-2xl text-center">
   				<div in:scale={{ duration: 600, start: 0.8 }}>
   					<!-- Error Icons -->
   					{#if errorState.type === 'not_found'}
   						<div class="mx-auto mb-6 rounded-full bg-white/20 p-6">
   							<svg class="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
   								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
   							</svg>
   						</div>
   					{:else if errorState.type === 'no_access'}
   						<div class="mx-auto mb-6 rounded-full bg-white/20 p-6">
   							<svg class="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
   								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
   							</svg>
   						</div>
   					{:else if errorState.type === 'no_lessons'}
   						<div class="mx-auto mb-6 rounded-full bg-white/20 p-6">
   							<svg class="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
   								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
   							</svg>
   						</div>
   					{:else if errorState.type === 'auth_error'}
   						<div class="mx-auto mb-6 rounded-full bg-white/20 p-6">
   							<svg class="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
   								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
   							</svg>
   						</div>
   					{:else}
   						<div class="mx-auto mb-6 rounded-full bg-white/20 p-6">
   							<svg class="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
   								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
   							</svg>
   						</div>
   					{/if}

   					<h1 class="mb-4 text-3xl font-bold leading-tight lg:text-5xl">
   						{#if errorState.type}
   							{errorState.message}
   						{:else if course && !hasAccess}
   							Access Denied
   						{:else}
   							Something went wrong
   						{/if}
   					</h1>

   					<p class="mb-8 text-xl leading-relaxed text-white/90">
   						{#if errorState.type}
   							{errorState.details}
   						{:else if course && !hasAccess}
   							You need to be enrolled in this course to access the learning materials.
   						{:else}
   							We encountered an unexpected issue. Please try again later.
   						{/if}
   					</p>
   				</div>
   			</div>
   		</div>
   	</div>

   	<div class="container mx-auto px-4 py-12">
   		<div class="mx-auto max-w-md">
   			<Card variant="bordered" class="p-8 shadow-2xl text-center">
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
   			</Card>
   		</div>
   	</div>
   </div>
{/if}
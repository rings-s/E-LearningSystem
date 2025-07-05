<!-- front/src/routes/(app)/courses/[uuid]/learn/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { debounce, classNames } from '$lib/utils/helpers.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { browser } from '$app/environment';

	// Components
	import YouTubePlayer from '$lib/components/course/YouTubePlayer.svelte';
	import PDFViewer from '$lib/components/course/PDFViewer.svelte';
	import LessonList from '$lib/components/course/LessonList.svelte';
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	let courseId = $page.params.uuid;

	// State variables with proper initialization
	let course = $state(null);
	let enrollment = $state(null);
	let currentLesson = $state(null);
	let loading = $state(true);
	let error = $state('');
	let completingLesson = $state(false);

	// Progress tracking
	let videoProgress = $state({ currentTime: 0, duration: 0, progress: 0 });
	let learningSession = $state({
		startTime: null,
		totalTime: 0,
		lastActiveTime: Date.now()
	});

	// Note-taking
	let notes = $state([]);
	let currentNote = $state('');
	let noteSearchQuery = $state('');
	let showNotes = $state(false);

	// Quiz system
	let currentQuiz = $state(null);
	let quizResponses = $state({});
	let showQuiz = $state(false);

	// UI state
	let sidebar = $state({ 
		collapsed: false, 
		activeTab: 'overview',
		mobileMenuOpen: false 
	});
	let showKeyboardShortcuts = $state(false);
	let isMobile = $state(false);

	// Computed values with proper null checks
	let lessons = [];
	let currentLessonIndex = -1;
	let previousLesson = null;
	let nextLesson = null;
	let totalLessonsCount = 0;
	let completedLessonsCount = 0;
	let calculatedProgress = 0;

	// Reactive updates for computed values
	$effect(() => {
		if (course?.modules) {
			lessons = course.modules.flatMap(module => 
				(module.lessons || []).map(lesson => ({
					...lesson,
					moduleTitle: module.title
				}))
			);
		} else {
			lessons = [];
		}
	});

	$effect(() => {
		if (currentLesson && lessons.length > 0) {
			currentLessonIndex = lessons.findIndex(lesson => lesson.uuid === currentLesson.uuid);
		} else {
			currentLessonIndex = -1;
		}
	});

	$effect(() => {
		previousLesson = currentLessonIndex > 0 ? lessons[currentLessonIndex - 1] : null;
		nextLesson = currentLessonIndex < lessons.length - 1 ? lessons[currentLessonIndex + 1] : null;
	});

	$effect(() => {
		totalLessonsCount = lessons.length;
		completedLessonsCount = lessons.filter(l => l.is_completed).length;
		calculatedProgress = totalLessonsCount > 0 ? Math.round((completedLessonsCount / totalLessonsCount) * 100) : 0;
	});

	// Session timers
	let sessionTimer;
	let autosaveTimer;

	onMount(async () => {
		await initializePage();
		setupEventListeners();
		startLearningSession();
	});

	onDestroy(() => {
		cleanup();
	});

	async function initializePage() {
		try {
			await Promise.all([
				loadCourse(),
				loadEnrollment(),
				loadNotes()
			]);
		} catch (err) {
			error = err.message || 'Failed to load course data';
			console.error('Initialization error:', err);
		} finally {
			loading = false;
		}
	}

	async function loadCourse() {
		try {
			course = await coursesApi.getCourse(courseId);
			
			if (!course.modules?.length) {
				throw new Error('This course has no content yet');
			}

			// Find appropriate lesson to start
			const urlParams = new URLSearchParams(window.location.search);
			const lessonId = urlParams.get('lesson');
			
			let lessonToLoad;
			if (lessonId && course.modules) {
				const allLessons = course.modules.flatMap(m => m.lessons || []);
				lessonToLoad = allLessons.find(l => l.uuid === lessonId);
			}
			
			if (!lessonToLoad && course.modules) {
				const allLessons = course.modules.flatMap(m => m.lessons || []);
				lessonToLoad = allLessons.find(lesson => !lesson.is_completed) || allLessons[0];
			}
			
			if (lessonToLoad) {
				await loadLesson(lessonToLoad);
			}
		} catch (err) {
			console.error('Failed to load course:', err);
			throw err;
		}
	}

	async function loadEnrollment() {
		try {
			const enrollments = await coursesApi.getMyEnrollments();
			enrollment = enrollments.find(e => e.course.uuid === courseId) || null;
		} catch (err) {
			console.warn('Could not load enrollment:', err);
		}
	}

	async function loadLesson(lesson) {
		try {
			currentLesson = await coursesApi.getLesson(lesson.uuid);
			videoProgress = { currentTime: 0, duration: 0, progress: 0 };
			
			// Update URL
			if (browser) {
				const url = new URL(window.location);
				url.searchParams.set('lesson', lesson.uuid);
				window.history.replaceState({}, '', url);
			}

			// Load lesson-specific data
			await loadLessonNotes();
			
		} catch (err) {
			console.error('Failed to load lesson:', err);
			uiStore.showNotification({
				type: 'error',
				title: 'Error loading lesson',
				message: err.message
			});
		}
	}

	async function loadLessonNotes() {
		try {
			const response = await coursesApi.getLessonNotes(currentLesson.uuid);
			// Filter and update notes for current lesson
			notes = notes.filter(n => n.lessonId !== currentLesson.uuid);
			if (response.notes) {
				const lessonNotes = response.notes.map(n => ({
					...n,
					lessonId: currentLesson.uuid,
					lessonTitle: currentLesson.title
				}));
				notes = [...notes, ...lessonNotes];
			}
		} catch (err) {
			console.warn('Could not load lesson notes:', err);
		}
	}

	async function loadNotes() {
		try {
			if (browser) {
				const saved = localStorage.getItem(`course_notes_${courseId}`);
				if (saved) {
					notes = JSON.parse(saved);
				}
			}
		} catch (err) {
			console.warn('Could not load notes:', err);
		}
	}

	// Learning session management
	function startLearningSession() {
		learningSession.startTime = Date.now();
		learningSession.lastActiveTime = Date.now();

		// Track session time
		sessionTimer = setInterval(() => {
			learningSession.totalTime += 1;
		}, 1000);

		// Auto-save progress
		autosaveTimer = setInterval(saveProgress, 30000);
	}

	function cleanup() {
		if (sessionTimer) clearInterval(sessionTimer);
		if (autosaveTimer) clearInterval(autosaveTimer);
	}

	// Progress tracking
	const saveProgress = debounce(() => {
		if (currentLesson && browser) {
			const progress = {
				lessonId: currentLesson.uuid,
				videoProgress,
				timeSpent: learningSession.totalTime,
				lastAccessed: Date.now(),
				completed: currentLesson.is_completed
			};
			
			localStorage.setItem(`lesson_progress_${currentLesson.uuid}`, JSON.stringify(progress));

			// Sync with server
			coursesApi.updateLessonProgress(currentLesson.uuid, progress)
				.catch(err => console.warn('Failed to sync progress:', err));
		}
	}, 2000);

	const saveNotes = debounce(() => {
		if (browser) {
			localStorage.setItem(`course_notes_${courseId}`, JSON.stringify(notes));
		}
	}, 1000);

	async function completeLesson() {
		if (!currentLesson || currentLesson.is_completed || completingLesson) return;

		completingLesson = true;
		try {
			await coursesApi.completeLesson(currentLesson.uuid);
			currentLesson.is_completed = true;

			// Update enrollment progress
			if (enrollment) {
				enrollment.progress_percentage = calculatedProgress;
			}

			uiStore.showNotification({
				type: 'success',
				title: '🎉 Lesson Completed!',
				message: `Great job! You've completed "${currentLesson.title}"`
			});
			
			// Auto-advance if next lesson exists
			if (nextLesson) {
				setTimeout(() => loadLesson(nextLesson), 2000);
			}

		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: 'Failed to mark lesson as complete'
			});
		} finally {
			completingLesson = false;
		}
	}

	// Video player handlers
	function handleVideoProgress(data) {
		videoProgress = data;
		learningSession.lastActiveTime = Date.now();

		// Auto-complete at 95%
		if (data.progress >= 95 && !currentLesson.is_completed && !completingLesson) {
			completeLesson();
		}

		saveProgress();
	}

	// Note-taking system
	function addNote() {
		if (!currentNote.trim()) return;

		const note = {
			id: Date.now(),
			content: currentNote,
			timestamp: videoProgress.currentTime,
			lessonId: currentLesson?.uuid,
			lessonTitle: currentLesson?.title,
			createdAt: new Date().toISOString()
		};

		notes = [note, ...notes];
		currentNote = '';
		saveNotes();

		uiStore.showNotification({
			type: 'success',
			title: 'Note saved',
			message: 'Your note has been saved'
		});
	}

	function deleteNote(noteId) {
		notes = notes.filter(n => n.id !== noteId);
		saveNotes();
	}

	// Navigation
	function navigateToLesson(lesson) {
		if (lesson) {
			loadLesson(lesson);
		}
	}

	function navigatePrevious() {
		if (previousLesson) {
			loadLesson(previousLesson);
		}
	}

	function navigateNext() {
		if (nextLesson) {
			loadLesson(nextLesson);
		}
	}

	// Event listeners
	function setupEventListeners() {
		if (!browser) return;

		function handleResize() {
			isMobile = window.innerWidth < 768;
		}

		function handleKeyboard(e) {
			if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

			switch (e.key) {
				case 'ArrowLeft':
					e.preventDefault();
					navigatePrevious();
					break;
				case 'ArrowRight':
					e.preventDefault();
					navigateNext();
					break;
				case '?':
					e.preventDefault();
					showKeyboardShortcuts = true;
					break;
				case 'Escape':
					e.preventDefault();
					showKeyboardShortcuts = false;
					showQuiz = false;
					break;
			}
		}

		window.addEventListener('resize', handleResize);
		window.addEventListener('keydown', handleKeyboard);
		handleResize(); // Initial check

		return () => {
			window.removeEventListener('resize', handleResize);
			window.removeEventListener('keydown', handleKeyboard);
		};
	}

	// Filter notes
	$effect(() => {
		// This effect will run when noteSearchQuery changes
	});

	let filteredNotes = [];
	$effect(() => {
		if (!noteSearchQuery) {
			filteredNotes = notes;
		} else {
			filteredNotes = notes.filter(note => 
				note.content.toLowerCase().includes(noteSearchQuery.toLowerCase()) ||
				note.lessonTitle?.toLowerCase().includes(noteSearchQuery.toLowerCase())
			);
		}
	});
</script>

<svelte:head>
	<title>{currentLesson?.title || 'Learning'} - {course?.title || 'Course'} - 244SCHOOL</title>
	<meta name="description" content="Continue your learning journey with {course?.title || 'this course'}" />
</svelte:head>

<!-- Loading State -->
{#if loading}
	<div class="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900" in:fade>
		<div class="text-center">
			<div class="mx-auto mb-6 h-16 w-16 animate-spin rounded-full border-4 border-primary-600 border-t-transparent"></div>
			<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">Loading your course...</h3>
			<p class="text-gray-600 dark:text-gray-400">Preparing your learning experience</p>
		</div>
	</div>
{/if}

<!-- Error State -->
{#if error && !loading}
	<div class="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900" in:fade>
		<div class="text-center">
			<div class="mx-auto mb-6 rounded-full bg-red-100 p-6 dark:bg-red-900/30">
				<svg class="h-16 w-16 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
				</svg>
			</div>
			<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">Something went wrong</h3>
			<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
			<div class="flex gap-4 justify-center">
				<Button onclick={() => window.location.reload()} variant="primary">Try Again</Button>
				<Button href="/courses" variant="outline">Browse Courses</Button>
			</div>
		</div>
	</div>
{/if}

<!-- Main Learning Interface -->
{#if !loading && !error && currentLesson}
	<div class="flex h-screen bg-gray-50 dark:bg-gray-900" in:fade>
		
		<!-- Sidebar -->
		<div class={classNames(
			'transition-all duration-300 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
			sidebar.collapsed ? 'w-16' : 'w-80',
			isMobile && 'absolute z-50 h-full shadow-xl',
			isMobile && !sidebar.mobileMenuOpen && '-translate-x-full'
		)}>
			
			<!-- Sidebar Header -->
			<div class="flex h-16 items-center justify-between border-b border-gray-200 px-4 dark:border-gray-700">
				{#if !sidebar.collapsed}
					<h2 class="font-semibold text-gray-900 dark:text-white truncate">
						{course?.title || 'Course'}
					</h2>
				{/if}
				
				<button
					onclick={() => sidebar.collapsed = !sidebar.collapsed}
					class="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
					title={sidebar.collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
							d={sidebar.collapsed ? "M13 5l7 7-7 7M5 5l7 7-7 7" : "M11 19l-7-7 7-7m8 14l-7-7 7-7"}></path>
					</svg>
				</button>
			</div>

			{#if !sidebar.collapsed}
				<!-- Sidebar Tabs -->
				<div class="flex border-b border-gray-200 dark:border-gray-700">
					{#each [
						{ id: 'overview', label: 'Overview', icon: '📊' },
						{ id: 'lessons', label: 'Lessons', icon: '📚' },
						{ id: 'notes', label: 'Notes', icon: '📝' }
					] as tab}
						<button
							onclick={() => sidebar.activeTab = tab.id}
							class={classNames(
								'flex-1 px-3 py-2 text-sm font-medium transition-colors',
								sidebar.activeTab === tab.id 
									? 'border-b-2 border-primary-600 text-primary-600 dark:text-primary-400'
									: 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
							)}
						>
							<span class="mr-1">{tab.icon}</span>
							{tab.label}
						</button>
					{/each}
				</div>

				<!-- Sidebar Content -->
				<div class="flex-1 overflow-y-auto p-4">
					
					{#if sidebar.activeTab === 'overview'}
						<!-- Course Overview -->
						<div class="space-y-4">
							<div>
								<h3 class="mb-2 font-medium text-gray-900 dark:text-white">Progress Overview</h3>
								<CourseProgress progress={calculatedProgress} showLabel={true} size="large" />
								<div class="mt-2 grid grid-cols-2 gap-2 text-sm">
									<div class="text-center">
										<div class="font-semibold text-green-600">{completedLessonsCount}</div>
										<div class="text-gray-500">Completed</div>
									</div>
									<div class="text-center">
										<div class="font-semibold text-blue-600">{totalLessonsCount - completedLessonsCount}</div>
										<div class="text-gray-500">Remaining</div>
									</div>
								</div>
							</div>

							<div>
								<h3 class="mb-2 font-medium text-gray-900 dark:text-white">Learning Stats</h3>
								<div class="space-y-2 text-sm">
									<div class="flex justify-between">
										<span class="text-gray-600 dark:text-gray-400">Time Spent</span>
										<span class="font-medium">{formatters.duration(learningSession.totalTime)}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-gray-600 dark:text-gray-400">Current Session</span>
										<span class="font-medium">{formatters.duration(learningSession.totalTime)}</span>
									</div>
								</div>
							</div>
						</div>

					{:else if sidebar.activeTab === 'lessons'}
						<!-- Lesson List -->
						{#if course?.modules}
							<LessonList
								modules={course.modules}
								currentLessonId={currentLesson.uuid}
								onLessonClick={navigateToLesson}
								isEnrolled={!!enrollment}
							/>
						{/if}

					{:else if sidebar.activeTab === 'notes'}
						<!-- Note-taking Interface -->
						<div class="space-y-4">
							<div>
								<div class="mb-2 flex items-center justify-between">
									<h3 class="font-medium text-gray-900 dark:text-white">My Notes</h3>
									<Badge variant="info" size="small">{notes.length}</Badge>
								</div>
								
								<!-- Note Input -->
								<div class="space-y-2">
									<textarea
										bind:value={currentNote}
										placeholder="Add a note..."
										rows="3"
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
									></textarea>
									
									<Button onclick={addNote} disabled={!currentNote.trim()} size="small" variant="primary">
										Add Note
									</Button>
								</div>

								<!-- Note Search -->
								{#if notes.length > 0}
									<Input
										bind:value={noteSearchQuery}
										placeholder="Search notes..."
										size="small"
									/>
								{/if}
							</div>

							<!-- Notes List -->
							<div class="space-y-3">
								{#each filteredNotes as note (note.id)}
									<div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-700/50" transition:slide>
										<div class="mb-1 flex items-start justify-between">
											<div class="flex-1">
												<p class="text-sm text-gray-900 dark:text-white">{note.content}</p>
												<div class="mt-1 flex items-center gap-2 text-xs text-gray-500">
													{#if note.lessonTitle}
														<span>{note.lessonTitle}</span>
														<span>•</span>
													{/if}
													{#if note.timestamp > 0}
														<span>{formatters.duration(note.timestamp)}</span>
														<span>•</span>
													{/if}
													<span>{formatters.relativeTime(note.createdAt)}</span>
												</div>
											</div>
											<button
												onclick={() => deleteNote(note.id)}
												class="ml-2 text-gray-400 hover:text-red-500"
											>
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
												</svg>
											</button>
										</div>
									</div>
								{/each}

								{#if filteredNotes.length === 0}
									<div class="text-center text-gray-500 dark:text-gray-400">
										{noteSearchQuery ? 'No notes found' : 'No notes yet'}
									</div>
								{/if}
							</div>
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Main Content -->
		<div class="flex flex-1 flex-col">
			
			<!-- Top Bar -->
			<div class="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 dark:border-gray-700 dark:bg-gray-800">
				
				<!-- Mobile menu button -->
				{#if isMobile}
					<button
						onclick={() => sidebar.mobileMenuOpen = !sidebar.mobileMenuOpen}
						class="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
					>
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
						</svg>
					</button>
				{/if}

				<!-- Lesson Info -->
				<div class="flex-1">
					<div class="flex items-center gap-3">
						<h1 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
							{currentLesson.title}
						</h1>
						<Badge variant="info" size="small">
							{currentLessonIndex + 1} of {totalLessonsCount}
						</Badge>
						{#if currentLesson.is_completed}
							<Badge variant="success" size="small">
								<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
								</svg>
								Completed
							</Badge>
						{/if}
					</div>
					<div class="mt-1 text-sm text-gray-500 dark:text-gray-400">
						{currentLesson.moduleTitle || 'Module'} • {formatters.duration((currentLesson.estimated_time_minutes || 0) * 60)}
					</div>
				</div>

				<!-- Actions -->
				<div class="flex items-center gap-2">
					<Button
						onclick={() => showKeyboardShortcuts = true}
						variant="ghost"
						size="small"
						title="Keyboard shortcuts (?)"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
						</svg>
					</Button>
				</div>
			</div>

			<!-- Content Area -->
			<div class="flex-1 overflow-hidden">
				<div class="h-full p-6">
					
					<!-- Video/Content Player -->
					<div class="mb-6">
						<Card variant="bordered" class="overflow-hidden shadow-lg">
							<div class="-m-6">
								{#if currentLesson.content_type === 'video' && currentLesson.video_url}
									<YouTubePlayer
										videoId={currentLesson.video_url}
										onProgress={handleVideoProgress}
										class="aspect-video w-full"
									/>
								{:else if currentLesson.content_type === 'pdf' && currentLesson.file_attachment}
									<PDFViewer
										src={currentLesson.file_attachment}
										title={currentLesson.title}
										height="600px"
									/>
								{:else if currentLesson.content_type === 'text' && currentLesson.text_content}
									<div class="prose prose-lg dark:prose-invert max-w-none p-6">
										{@html currentLesson.text_content}
									</div>
								{:else}
									<div class="flex h-96 items-center justify-center bg-gray-100 dark:bg-gray-800">
										<div class="text-center text-gray-500 dark:text-gray-400">
											<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
											</svg>
											<p>Content not available</p>
										</div>
									</div>
								{/if}
							</div>
						</Card>
					</div>

					<!-- Lesson Controls -->
					<div class="mb-6">
						<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-md dark:bg-gray-800/95">
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-4">
									{#if !currentLesson.is_completed}
										<Button
											onclick={completeLesson}
											variant="primary"
											loading={completingLesson}
											disabled={completingLesson}
										>
											{completingLesson ? 'Completing...' : 'Mark Complete'}
										</Button>
									{:else}
										<Badge variant="success" size="large">
											<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
											</svg>
											Completed
										</Badge>
									{/if}

									{#if videoProgress.duration > 0}
										<div class="text-sm text-gray-600 dark:text-gray-400">
											Video Progress: {Math.round(videoProgress.progress)}%
										</div>
									{/if}
								</div>

								<!-- Navigation -->
								<div class="flex items-center gap-2">
									<Button
										onclick={navigatePrevious}
										variant="outline"
										size="small"
										disabled={!previousLesson}
										title="Previous lesson (←)"
									>
										<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
										</svg>
										Previous
									</Button>

									<Button
										onclick={navigateNext}
										variant="primary"
										size="small"
										disabled={!nextLesson}
										title="Next lesson (→)"
									>
										Next
										<svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
										</svg>
									</Button>
								</div>
							</div>
						</Card>
					</div>

					<!-- Lesson Description -->
					{#if currentLesson.description}
						<div class="mb-6">
							<Card variant="bordered" class="shadow-md">
								<div class="flex items-start gap-4">
									<div class="rounded-lg bg-blue-100 p-3 dark:bg-blue-900/30">
										<svg class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
										</svg>
									</div>
									<div class="flex-1">
										<h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
											About This Lesson
										</h3>
										<div class="prose prose-gray dark:prose-invert max-w-none">
											{currentLesson.description}
										</div>
									</div>
								</div>
							</Card>
						</div>
					{/if}

					<!-- Resources -->
					{#if currentLesson.resources?.length > 0}
						<div class="mb-6">
							<Card variant="bordered" class="shadow-md">
								<div class="flex items-start gap-4">
									<div class="rounded-lg bg-purple-100 p-3 dark:bg-purple-900/30">
										<svg class="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
										</svg>
									</div>
									<div class="flex-1">
										<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
											Additional Resources
										</h3>
										<div class="grid grid-cols-1 gap-3 md:grid-cols-2">
											{#each currentLesson.resources as resource}
												<a
													href={resource.file || resource.url}
													target="_blank"
													rel="noopener noreferrer"
													class="group flex items-center gap-3 rounded-lg bg-gray-50 p-3 transition-all hover:bg-gray-100 hover:shadow-md dark:bg-gray-700/50 dark:hover:bg-gray-600/50"
												>
													<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 transition-transform group-hover:scale-110 dark:bg-primary-900/30">
														<svg class="h-5 w-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
															<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
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
													<svg class="h-4 w-4 text-gray-400 group-hover:text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
													</svg>
												</a>
											{/each}
										</div>
									</div>
								</div>
							</Card>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Keyboard Shortcuts Modal -->
{#if showKeyboardShortcuts}
	<Modal isOpen={showKeyboardShortcuts} onClose={() => showKeyboardShortcuts = false}>
		<div class="p-6">
			<h2 class="mb-6 text-xl font-bold text-gray-900 dark:text-white">Keyboard Shortcuts</h2>
			
			<div class="space-y-4">
				{#each [
					{ keys: ['←'], description: 'Previous lesson' },
					{ keys: ['→'], description: 'Next lesson' },
					{ keys: ['?'], description: 'Show shortcuts' },
					{ keys: ['Esc'], description: 'Close modal' }
				] as shortcut}
					<div class="flex items-center justify-between">
						<span class="text-gray-900 dark:text-white">{shortcut.description}</span>
						<div class="flex gap-1">
							{#each shortcut.keys as key}
								<kbd class="rounded bg-gray-100 px-2 py-1 text-xs font-mono text-gray-700 dark:bg-gray-700 dark:text-gray-300">
									{key}
								</kbd>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>
	</Modal>
{/if}

<!-- Mobile Sidebar Overlay -->
{#if isMobile && sidebar.mobileMenuOpen}
	<div 
		class="fixed inset-0 z-40 bg-black/50"
		onclick={() => sidebar.mobileMenuOpen = false}
		transition:fade
	></div>
{/if}
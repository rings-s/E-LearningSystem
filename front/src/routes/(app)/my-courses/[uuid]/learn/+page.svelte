<script>
	import { page } from '$app/stores';
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { debounce, classNames } from '$lib/utils/helpers.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { APP_NAME } from '$lib/utils/constants.js';
	import { browser } from '$app/environment';
	import { locale, t } from '$lib/i18n/index.js';
	import { replaceState } from '$app/navigation';

	// Components
	import YouTubePlayer from '$lib/components/course/YouTubePlayer.svelte';
	import PDFViewer from '$lib/components/course/PDFViewer.svelte';
	import LessonList from '$lib/components/course/LessonList.svelte';
	import CourseProgress from '$lib/components/course/CourseProgress.svelte';
	import NotesSection from '$lib/components/course/NotesSection.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	let courseId = $page.params.uuid;

	// State variables
	let course = $state(null);
	let enrollment = $state(null);
	let currentLesson = $state(null);
	let loading = $state(true);
	let error = $state('');
	let completingLesson = $state(false);

	// Enhanced Analytics Tracking
	let analytics = $state({
		sessionStartTime: null,
		totalTimeSpent: 0,
		lessonTimeSpent: 0,
		interactionCount: 0,
		lastProgressUpdate: null
	});

	// Progress tracking
	let videoProgress = $state({ currentTime: 0, duration: 0, progress: 0 });
	let learningSession = $state(null);

	// Enhanced note-taking
	let notes = $state([]);
	let currentNote = $state('');
	let noteSearchQuery = $state('');
	let showNotes = $state(false);
	let savingNote = $state(false);
	let loadingNotes = $state(false);
	let autoSaveTimer = null;

	// UI state
	let sidebar = $state({ 
		collapsed: false, 
		activeTab: 'overview',
		mobileMenuOpen: false 
	});
	let showKeyboardShortcuts = $state(false);
	let isMobile = $state(false);

	// Derived states
	let lessons = $derived(() => {
		if (!course?.modules || !Array.isArray(course.modules)) return [];
		
		return course.modules.flatMap(module => {
			if (!module || !module.lessons || !Array.isArray(module.lessons)) return [];
			return module.lessons
				.filter(lesson => lesson && typeof lesson === 'object' && lesson.uuid)
				.map(lesson => ({
					...lesson,
					moduleTitle: module.title || 'Unknown Module',
					is_completed: Boolean(lesson.is_completed)
				}));
		});
	});

	let currentLessonIndex = $derived(() => {
		if (!currentLesson?.uuid || !Array.isArray(lessons) || lessons.length === 0) return -1;
		return lessons.findIndex(lesson => lesson?.uuid === currentLesson.uuid);
	});

	let previousLesson = $derived(() => {
		const index = currentLessonIndex;
		if (index <= 0 || !Array.isArray(lessons) || lessons.length === 0) return null;
		const prevLesson = lessons[index - 1];
		return (prevLesson?.uuid) ? prevLesson : null;
	});

	let nextLesson = $derived(() => {
		const index = currentLessonIndex;
		if (index < 0 || !Array.isArray(lessons) || lessons.length === 0 || index >= lessons.length - 1) return null;
		const nextLesson = lessons[index + 1];
		return (nextLesson?.uuid) ? nextLesson : null;
	});

	let totalLessonsCount = $derived(() => {
		return Array.isArray(lessons) ? lessons.length : 0;
	});

	let completedLessonsCount = $derived.by(() => {
		if (!Array.isArray(lessons)) return 0;
		return lessons.filter(lesson => 
			lesson && 
			typeof lesson === 'object' && 
			'is_completed' in lesson && 
			lesson.is_completed === true
		).length;
	});

	let progressValue = $derived.by(() => {
		const total = totalLessonsCount;
		const completed = completedLessonsCount;
		
		if (!total || total === 0) return 0;
		return Math.round((completed / total) * 100);
	});

	onMount(async () => {
		// Check if user is logged in and enrolled
		if (!$currentUser) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: 'Please log in to access course content'
			});
			goto('/auth/login');
			return;
		}

		await initializePage();
		setupEventListeners();
		startLearningSession();
		startAnalyticsTracking();
	});

	onDestroy(() => {
		cleanup();
	});

	async function initializePage() {
		try {
			await Promise.all([
				loadCourse(),
				loadEnrollment()
			]);
			
			// Check if user is enrolled
			if (!enrollment) {
				uiStore.showNotification({
					type: 'error',
					title: 'Not Enrolled',
					message: 'You need to enroll in this course to access the content'
				});
				goto(`/courses/${courseId}`);
				return;
			}
			
			await loadNotes();
		} catch (err) {
			error = err.message || $t('course.somethingWentWrong');
			console.error('Initialization error:', err);
		} finally {
			loading = false;
		}
	}

	async function loadCourse() {
		try {
			course = await coursesApi.getCourse(courseId);
			
			if (!course.modules || !Array.isArray(course.modules)) {
				try {
					const modulesResponse = await coursesApi.getModules(courseId);
					course.modules = Array.isArray(modulesResponse) ? modulesResponse : (modulesResponse.results || []);
				} catch (modulesErr) {
					console.warn('Could not load modules:', modulesErr);
					course.modules = [];
				}
			}
			
			const allLessons = course.modules?.flatMap(m => m.lessons || []) || [];
			if (allLessons.length === 0) {
				console.warn('Course has no lessons yet');
				return;
			}

			// Find appropriate lesson to start
			const urlParams = new URLSearchParams(window.location.search);
			const lessonId = urlParams.get('lesson');
			
			let lessonToLoad;
			if (lessonId && course.modules) {
				lessonToLoad = allLessons.find(l => l.uuid === lessonId);
			}
			
			if (!lessonToLoad && course.modules) {
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
			const response = await coursesApi.getMyEnrollments();
			const enrollmentsList = Array.isArray(response) ? response : (response.results || response.enrollments || []);
			
			if (Array.isArray(enrollmentsList)) {
				enrollment = enrollmentsList.find(e => e.course?.uuid === courseId) || null;
			} else {
				console.warn('Enrollment response is not an array:', response);
				enrollment = null;
			}
		} catch (err) {
			console.warn('Could not load enrollment:', err);
			enrollment = null;
		}
	}

	async function loadLesson(lesson) {
		try {
			if (!lesson || !lesson.uuid) {
				throw new Error('Invalid lesson: lesson object is missing UUID property');
			}

			if (currentLesson) {
				await endLessonTracking();
			}

			currentLesson = await coursesApi.getCourseLesson(courseId, lesson.uuid);
			videoProgress = { currentTime: 0, duration: 0, progress: 0 };
			
			if (browser) {
				const url = new URL(window.location);
				url.searchParams.set('lesson', lesson.uuid);
				replaceState(url.toString(), {});
			}

			await loadLessonNotes();
			await startLessonTracking();
			
		} catch (err) {
			console.error('Failed to load lesson:', err);
			
			let errorMessage = 'Failed to load lesson';
			if (err.message) {
				if (err.message.includes('404') || err.message.includes('Not Found')) {
					errorMessage = 'Lesson not found or you may not have access to it.';
				} else if (err.message.includes('403') || err.message.includes('Forbidden')) {
					errorMessage = 'You do not have permission to access this lesson.';
				} else {
					errorMessage = err.message;
				}
			}
			
			uiStore.showNotification({
				type: 'error',
				title: $t('common.error'),
				message: errorMessage
			});
		}
	}

	function startAnalyticsTracking() {
		analytics.sessionStartTime = Date.now();
		analytics.interactionCount = 0;

		if (browser) {
			['click', 'keydown', 'scroll'].forEach(event => {
				document.addEventListener(event, trackInteraction);
			});
		}
	}

	function trackInteraction() {
		analytics.interactionCount++;
		analytics.lastProgressUpdate = Date.now();
	}

	async function startLessonTracking() {
		if (!currentLesson) return;
		analytics.lessonTimeSpent = 0;
		console.log('Started lesson tracking for:', currentLesson.title);
	}

	async function endLessonTracking() {
		if (!currentLesson || !analytics.sessionStartTime) return;
		const timeSpent = Date.now() - analytics.sessionStartTime;
		console.log('Ended lesson tracking. Time spent:', Math.floor(timeSpent / 1000), 'seconds');
	}

	async function loadLessonNotes() {
		if (!currentLesson) return;
		
		loadingNotes = true;
		try {
			const response = await coursesApi.getLessonNotes(courseId, currentLesson.uuid);
			
			const existingNotes = notes.filter(n => n.lessonId !== currentLesson.uuid);
			
			if (response && response.notes) {
				let lessonNotes = [];
				try {
					const parsedNotes = JSON.parse(response.notes);
					if (Array.isArray(parsedNotes)) {
						lessonNotes = parsedNotes
							.filter(n => n && n.content)
							.map(n => ({
								...n,
								lessonId: currentLesson.uuid,
								lessonTitle: currentLesson.title
							}));
					} else if (typeof parsedNotes === 'string' && parsedNotes.trim()) {
						lessonNotes = [{
							id: Date.now(),
							content: parsedNotes,
							lessonId: currentLesson.uuid,
							lessonTitle: currentLesson.title,
							timestamp: 0,
							createdAt: new Date().toISOString()
						}];
					}
				} catch (parseError) {
					if (response.notes.trim()) {
						lessonNotes = [{
							id: Date.now(),
							content: response.notes,
							lessonId: currentLesson.uuid,
							lessonTitle: currentLesson.title,
							timestamp: 0,
							createdAt: new Date().toISOString()
						}];
					}
				}
				
				if (lessonNotes.length > 0) {
					notes = [...existingNotes, ...lessonNotes];
				} else {
					notes = existingNotes;
				}
			} else {
				notes = existingNotes;
			}
		} catch (err) {
			console.warn('Could not load lesson notes:', err);
		} finally {
			loadingNotes = false;
		}
	}

	async function loadNotes() {
		try {
			if (browser) {
				const saved = localStorage.getItem(`course_notes_${courseId}`);
				if (saved) {
					const parsedNotes = JSON.parse(saved);
					if (Array.isArray(parsedNotes)) {
						notes = parsedNotes;
					}
				}
			}
		} catch (err) {
			console.warn('Could not load notes from localStorage:', err);
		}
	}

	function startLearningSession() {
		learningSession = {
			startTime: Date.now(),
			courseId,
			lessonId: currentLesson?.uuid
		};
		
		setInterval(() => {
			if (learningSession) {
				console.log('Session update:', {
					timeSpent: Date.now() - learningSession.startTime,
					videoProgress,
					lessonProgress: progressValue
				});
			}
		}, 30000);
	}

	function cleanup() {
		if (learningSession) {
			console.log('Learning session ended');
		}
		
		if (autoSaveTimer) {
			clearTimeout(autoSaveTimer);
		}

		if (browser) {
			['click', 'keydown', 'scroll'].forEach(event => {
				document.removeEventListener(event, trackInteraction);
			});
		}

		endLessonTracking();
	}

	const saveProgress = debounce(async () => {
		if (currentLesson && browser) {
			const progressData = {
				lessonId: currentLesson.uuid,
				videoProgress,
				timeSpent: Date.now() - (analytics.sessionStartTime || Date.now()),
				lastAccessed: Date.now(),
				completed: currentLesson.is_completed,
				interactionCount: analytics.interactionCount
			};
			
			localStorage.setItem(`lesson_progress_${currentLesson.uuid}`, JSON.stringify(progressData));
		}
	}, 2000);

	const saveNotes = debounce(async () => {
		if (browser) {
			try {
				localStorage.setItem(`course_notes_${courseId}`, JSON.stringify(notes));
			} catch (err) {
				console.warn('Could not save notes to localStorage:', err);
			}
		}
		
		if (currentLesson) {
			const lessonNotes = notes.filter(n => n.lessonId === currentLesson.uuid);
			try {
				await coursesApi.saveLessonNotes(courseId, currentLesson.uuid, JSON.stringify(lessonNotes));
			} catch (err) {
				console.warn('Failed to save notes to backend:', err);
			}
		}
	}, 1000);

	async function completeLesson() {
		if (!currentLesson || currentLesson.is_completed || completingLesson) return;

		completingLesson = true;
		try {
			await coursesApi.completeLesson(courseId, currentLesson.uuid);
			currentLesson.is_completed = true;

			if (enrollment) {
				enrollment.progress_percentage = progressValue;
			}

			uiStore.showNotification({
				type: 'success',
				title: $t('course.lessonCompleted'),
				message: `${$t('course.greatJob')} "${currentLesson.title}"`
			});
			
			setTimeout(() => {
				try {
					const lesson = nextLesson;
					if (lesson && typeof lesson === 'object' && lesson.uuid) {
						loadLesson(lesson);
					}
				} catch (error) {
					console.error('Error in auto-advance:', error);
				}
			}, 2000);

		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: $t('common.error'),
				message: 'Failed to mark lesson as complete'
			});
		} finally {
			completingLesson = false;
		}
	}

	function handleVideoProgress(data) {
		videoProgress = data;
		analytics.lastProgressUpdate = Date.now();

		if (data.progress >= 95 && !currentLesson.is_completed && !completingLesson) {
			completeLesson();
		}

		saveProgress();
	}

	async function addNote() {
		if (!currentNote.trim()) return;

		savingNote = true;
		try {
			const note = {
				id: Date.now(),
				content: currentNote.trim(),
				timestamp: videoProgress.currentTime,
				lessonId: currentLesson?.uuid,
				lessonTitle: currentLesson?.title,
				createdAt: new Date().toISOString()
			};

			notes = [note, ...notes];
			currentNote = '';
			
			setupAutoSave();

			uiStore.showNotification({
				type: 'success',
				title: $t('course.noteAdded'),
				message: $t('course.notesSaved')
			});
		} catch (err) {
			console.error('Failed to add note:', err);
			uiStore.showNotification({
				type: 'error',
				title: $t('common.error'),
				message: 'Failed to save note'
			});
		} finally {
			savingNote = false;
		}
	}

	function setupAutoSave() {
		if (autoSaveTimer) {
			clearTimeout(autoSaveTimer);
		}
		
		autoSaveTimer = setTimeout(() => {
			saveNotes();
		}, 2000);
	}

	function deleteNote(noteId) {
		notes = notes.filter(n => n.id !== noteId);
		setupAutoSave();
	}

	async function navigateToLesson(lesson) {
		if (!lesson || !lesson.uuid) {
			console.warn('navigateToLesson: Invalid lesson provided');
			return;
		}

		try {
			await loadLesson(lesson);
		} catch (err) {
			console.error('Navigation error:', err);
			uiStore.showNotification({
				type: 'error',
				title: $t('common.error'),
				message: err.message || 'Failed to load lesson'
			});
		}
	}

	function navigatePrevious() {
		try {
			const lesson = previousLesson;
			if (lesson && typeof lesson === 'object' && lesson.uuid) {
				navigateToLesson(lesson);
			} else {
				uiStore.showNotification({
					type: 'info',
					title: $t('course.navigation'),
					message: 'This is the first lesson'
				});
			}
		} catch (error) {
			console.error('Error in navigatePrevious:', error);
		}
	}

	function navigateNext() {
		try {
			const lesson = nextLesson;
			if (lesson && typeof lesson === 'object' && lesson.uuid) {
				navigateToLesson(lesson);
			} else {
				uiStore.showNotification({
					type: 'info',
					title: $t('course.navigation'),
					message: 'This is the last lesson'
				});
			}
		} catch (error) {
			console.error('Error in navigateNext:', error);
		}
	}

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
					break;
			}
		}

		window.addEventListener('resize', handleResize);
		window.addEventListener('keydown', handleKeyboard);
		handleResize();

		return () => {
			window.removeEventListener('resize', handleResize);
			window.removeEventListener('keydown', handleKeyboard);
		};
	}

	let filteredNotes = $derived.by(() => {
		if (!Array.isArray(notes)) return [];
		
		if (!noteSearchQuery || !noteSearchQuery.trim()) {
			return notes;
		}
		
		const query = noteSearchQuery.toLowerCase();
		return notes.filter(note => {
			if (!note) return false;
			
			const contentMatch = note.content && note.content.toLowerCase().includes(query);
			const titleMatch = note.lessonTitle && note.lessonTitle.toLowerCase().includes(query);
			
			return contentMatch || titleMatch;
		});
	});
</script>

<svelte:head>
	<title>{currentLesson?.title || $t('course.loading')} - {course?.title || 'Course'} - {APP_NAME}</title>
	<meta name="description" content="Continue your learning journey with {course?.title || 'this course'} on {APP_NAME}" />
</svelte:head>

<!-- Loading State -->
{#if loading}
	<div class="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900" in:fade>
		<div class="text-center">
			<div class="mx-auto mb-6 h-16 w-16 animate-spin rounded-full border-4 border-primary-600 border-t-transparent"></div>
			<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">{$t('course.loading')}</h3>
			<p class="text-gray-600 dark:text-gray-400">{$t('course.preparingExperience')}</p>
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
			<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">{$t('course.somethingWentWrong')}</h3>
			<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
			<div class="flex gap-4 justify-center">
				<Button onclick={() => window.location.reload()} variant="primary">{$t('course.tryAgain')}</Button>
				<Button href="/my-courses" variant="outline">My Courses</Button>
			</div>
		</div>
	</div>
{/if}

<!-- No Content State -->
{#if !loading && !error && course && (!course.modules || course.modules.length === 0 || lessons.length === 0)}
	<div class="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900" in:fade>
		<div class="text-center max-w-md">
			<div class="mx-auto mb-6 rounded-full bg-blue-100 p-6 dark:bg-blue-900/30">
				<svg class="h-16 w-16 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
				</svg>
			</div>
			<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">Course Content Coming Soon</h3>
			<p class="mb-6 text-gray-600 dark:text-gray-400">
				The instructor is still preparing the lessons for "{course.title}". 
				Please check back later or contact support if you think this is an error.
			</p>
			<div class="flex gap-4 justify-center">
				<Button href="/courses" variant="primary">Browse Other Courses</Button>
				<Button href={`/courses/${courseId}`} variant="outline">Course Details</Button>
			</div>
		</div>
	</div>
{/if}

<!-- Main Learning Interface -->
{#if !loading && !error && currentLesson}
	<div class="flex h-screen bg-gray-50 dark:bg-gray-900" in:fade>
		
		<!-- Enhanced Sidebar -->
		<div class={classNames(
			'transition-all duration-300 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
			sidebar.collapsed ? 'w-16' : 'w-80',
			isMobile && 'absolute z-50 h-full shadow-xl',
			isMobile && !sidebar.mobileMenuOpen && '-translate-x-full'
		)}>
			
			<!-- Sidebar Header -->
			<div class="flex h-16 items-center justify-between border-b border-gray-200 px-4 dark:border-gray-700">
				{#if !sidebar.collapsed}
					<div>
						<h2 class="font-semibold text-gray-900 dark:text-white truncate">
							{course?.title || 'Course'}
						</h2>
						<div class="text-xs text-gray-500 dark:text-gray-400">
							Student Learning Mode
						</div>
					</div>
				{/if}
				
				<button
					onclick={() => sidebar.collapsed = !sidebar.collapsed}
					class="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
					aria-label={sidebar.collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
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
						{ id: 'overview', label: $t('course.overview'), icon: '📊' },
						{ id: 'lessons', label: $t('course.lessons'), icon: '📚' },
						{ id: 'notes', label: $t('course.notes'), icon: '📝' },
						{ id: 'progress', label: 'Progress', icon: '📈' }
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
								<h3 class="mb-2 font-medium text-gray-900 dark:text-white">{$t('course.progress')} Overview</h3>
								<CourseProgress progress={progressValue} showLabel={true} size="large" />
								<div class="mt-2 grid grid-cols-2 gap-2 text-sm">
									<div class="text-center">
										<div class="font-semibold text-green-600">{completedLessonsCount}</div>
										<div class="text-gray-500">{$t('course.completed')}</div>
									</div>
									<div class="text-center">
										<div class="font-semibold text-blue-600">{Math.max(0, totalLessonsCount - completedLessonsCount)}</div>
										<div class="text-gray-500">{$t('course.remaining')}</div>
									</div>
								</div>
							</div>

							<!-- Back to Course -->
							<div class="pt-4 border-t border-gray-200 dark:border-gray-700">
								<Button
									href={`/courses/${courseId}`}
									variant="outline"
									size="medium"
									fullWidth
									class="justify-start"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
									</svg>
									<span class="ml-2">Back to Course Details</span>
								</Button>
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
						<NotesSection
							bind:notes
							bind:currentNote
							bind:noteSearchQuery
							{savingNote}
							{loadingNotes}
							{currentLesson}
							{videoProgress}
							onAddNote={addNote}
							onDeleteNote={deleteNote}
						/>

					{:else if sidebar.activeTab === 'progress'}
						<!-- Learning Progress -->
						<div class="space-y-4">
							<h3 class="font-medium text-gray-900 dark:text-white">Your Learning Progress</h3>
							
							<div class="rounded-lg bg-blue-50 p-3 dark:bg-blue-900/20">
								<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
									{progressValue || 0}%
								</div>
								<div class="text-sm text-blue-800 dark:text-blue-200">Course Completion</div>
							</div>

							<div class="grid grid-cols-2 gap-2">
								<div class="rounded-lg bg-green-50 p-3 dark:bg-green-900/20">
									<div class="text-lg font-bold text-green-600 dark:text-green-400">
										{formatters.duration(analytics.sessionStartTime ? (Date.now() - analytics.sessionStartTime) / 1000 : 0)}
									</div>
									<div class="text-xs text-green-800 dark:text-green-200">Session Time</div>
								</div>
								<div class="rounded-lg bg-purple-50 p-3 dark:bg-purple-900/20">
									<div class="text-lg font-bold text-purple-600 dark:text-purple-400">
										{analytics.interactionCount}
									</div>
									<div class="text-xs text-purple-800 dark:text-purple-200">Interactions</div>
								</div>
							</div>

							<div class="space-y-2">
								<div class="text-sm font-medium">Lesson Progress</div>
								<div class="text-xs text-gray-600 dark:text-gray-400">
									Lesson {Math.max(1, currentLessonIndex + 1)} of {totalLessonsCount}
								</div>
								<div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
									<div 
										class="bg-gradient-to-r from-primary-500 to-secondary-500 h-2 rounded-full transition-all duration-300" 
										style="width: {totalLessonsCount > 0 ? ((currentLessonIndex + 1) / totalLessonsCount) * 100 : 0}%"
									></div>
								</div>
							</div>

							<!-- Certificate Progress -->
							{#if progressValue >= 100}
								<div class="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
									<div class="flex items-center">
										<svg class="h-8 w-8 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
										</svg>
										<div class="ml-3">
											<h4 class="font-semibold text-yellow-800 dark:text-yellow-200">Course Completed!</h4>
											<p class="text-sm text-yellow-600 dark:text-yellow-300">Your certificate is ready</p>
										</div>
									</div>
									<Button
										href="/certificates"
										variant="primary"
										size="small"
										class="mt-3 w-full"
									>
										View Certificate
									</Button>
								</div>
							{/if}
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Main Content -->
		<div class="flex flex-1 flex-col">
			<!-- Top Bar -->
			<div class="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 dark:border-gray-700 dark:bg-gray-800">
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

				<div class="flex-1">
					<div class="flex items-center gap-3">
						<h1 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
							{currentLesson.title}
						</h1>
						<Badge variant="info" size="small">
							{Math.max(1, currentLessonIndex + 1)} of {totalLessonsCount}
						</Badge>
						{#if currentLesson.is_completed}
							<Badge variant="success" size="small">
								<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
								</svg>
								{$t('course.completed')}
							</Badge>
						{/if}
					</div>
					<div class="mt-1 text-sm text-gray-500 dark:text-gray-400">
						{currentLesson.moduleTitle || 'Module'} • {formatters.duration((currentLesson.estimated_time_minutes || 0) * 60)}
					</div>
				</div>

				<div class="flex items-center gap-2">
					<Button
						onclick={() => showKeyboardShortcuts = true}
						variant="ghost"
						size="small"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
						</svg>
					</Button>
					
					<div class="text-sm text-gray-500 dark:text-gray-400">
						{progressValue}% Complete
					</div>
				</div>
			</div>

			<!-- Content Area -->
			<div class="flex-1 overflow-hidden">
				<div class="h-full p-4 md:p-6">
					<!-- Video/Content Player -->
					<div class="mb-6">
						<Card variant="bordered" class="overflow-hidden shadow-lg">
							<div class="-m-6">
								{#if currentLesson.content_type === 'video' && currentLesson.video_url}
									<div class="relative w-full bg-black" style="max-height: calc(100vh - 300px); min-height: 400px;">
										<div class="aspect-video w-full h-full max-h-full flex items-center justify-center">
											<YouTubePlayer
												videoId={currentLesson.video_url}
												onProgress={handleVideoProgress}
												class="h-full w-full [&_iframe]:object-contain [&_iframe]:w-full [&_iframe]:h-full"
											/>
										</div>
									</div>
								{:else if currentLesson.content_type === 'pdf' && currentLesson.file_attachment}
									<div class="w-full" style="height: calc(100vh - 300px); max-height: 600px;">
										<PDFViewer
											src={currentLesson.file_attachment}
											title={currentLesson.title}
											height="100%"
										/>
									</div>
								{:else if currentLesson.content_type === 'text' && currentLesson.text_content}
									<div class="prose prose-lg dark:prose-invert max-w-none p-6 max-h-96 overflow-y-auto">
										{@html currentLesson.text_content}
									</div>
								{:else}
									<div class="flex h-96 items-center justify-center bg-gray-100 dark:bg-gray-800">
										<div class="text-center text-gray-500 dark:text-gray-400">
											<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
											</svg>
											<p>{$t('course.contentNotAvailable')}</p>
										</div>
									</div>
								{/if}
							</div>
						</Card>
					</div>

					<!-- Lesson Controls -->
					<div class="mb-6 lg:fixed lg:bottom-6 lg:left-1/2 lg:transform lg:-translate-x-1/2 lg:z-40" style="lg:max-width: calc(100vw - 400px);">
						<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-md dark:bg-gray-800/95 lg:shadow-2xl mx-auto max-w-4xl">
							<div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
								<div class="flex flex-wrap items-center gap-4">
									{#if !currentLesson.is_completed}
										<Button
											onclick={completeLesson}
											variant="primary"
											loading={completingLesson}
											disabled={completingLesson}
											size="large"
										>
											{completingLesson ? $t('course.completing') : $t('course.markComplete')}
										</Button>
									{:else}
										<Badge variant="success" size="large">
											<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
											</svg>
											{$t('course.completed')}
										</Badge>
									{/if}

									{#if videoProgress.duration > 0}
										<div class="text-sm text-gray-600 dark:text-gray-400">
											Video: {Math.round(videoProgress.progress)}% • 
											{formatters.duration(videoProgress.currentTime)} / {formatters.duration(videoProgress.duration)}
										</div>
									{/if}
								</div>

								<div class="flex items-center gap-2">
									<Button
										onclick={navigatePrevious}
										variant="outline"
										size="large"
										disabled={!previousLesson}
									>
										<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
										</svg>
										{$t('course.previous')}
									</Button>

									<Button
										onclick={navigateNext}
										variant="primary"
										size="large"
										disabled={!nextLesson}
									>
										{$t('course.next')}
										<svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
										</svg>
									</Button>
								</div>
							</div>
						</Card>
					</div>

					<!-- Bottom Spacer -->
					<div class="hidden lg:block lg:h-24"></div>

					<!-- Lesson Description -->
					{#if currentLesson.description}
						<div class="mb-6 lg:mb-32">
							<Card variant="bordered" class="shadow-md">
								<div class="flex items-start gap-4">
									<div class="rounded-lg bg-blue-100 p-3 dark:bg-blue-900/30">
										<svg class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
										</svg>
									</div>
									<div class="flex-1">
										<h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
											{$t('course.aboutThisLesson')}
										</h3>
										<div class="prose prose-gray dark:prose-invert max-w-none">
											{currentLesson.description}
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
			<h2 class="mb-6 text-xl font-bold text-gray-900 dark:text-white">{$t('course.showShortcuts')}</h2>
			
			<div class="space-y-4">
				{#each [
					{ keys: ['←'], description: $t('shortcuts.previousLesson') },
					{ keys: ['→'], description: $t('shortcuts.nextLesson') },
					{ keys: ['?'], description: $t('shortcuts.showShortcuts') },
					{ keys: ['Esc'], description: $t('shortcuts.closeModal') }
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
	<button 
		class="fixed inset-0 z-40 bg-black/50"
		onclick={() => sidebar.mobileMenuOpen = false}
		onkeydown={(e) => e.key === 'Enter' && (sidebar.mobileMenuOpen = false)}
		transition:fade
		aria-label="Close mobile menu"
	></button>
{/if}
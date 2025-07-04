// front/src/lib/stores/course.store.js
import { writable, derived } from 'svelte/store';
import { courseService } from '../services/course.service.js';

function createCourseStore() {
	const { subscribe, set, update } = writable({
		// Lists
		courses: [],
		enrollments: [],
		categories: [],

		// Current selections
		currentCourse: null,
		currentLesson: null,
		currentQuiz: null,

		// Filters and search
		filters: {
			search: '',
			category: '',
			level: '',
			language: '',
			status: '',
			sortBy: 'relevance'
		},

		// Pagination
		pagination: {
			page: 1,
			pageSize: 20,
			total: 0,
			totalPages: 0
		},

		// Learning state
		learningSession: {
			startTime: null,
			lessonProgress: {},
			quizAnswers: {},
			notes: []
		},

		// UI state
		loading: false,
		error: null
	});

	return {
		subscribe,

		// Course browsing
		async searchCourses(filters = {}) {
			update((state) => ({
				...state,
				loading: true,
				error: null,
				filters: { ...state.filters, ...filters }
			}));

			try {
				const result = await courseService.searchCourses(filters);
				update((state) => ({
					...state,
					courses: result,
					loading: false
				}));
				return result;
			} catch (error) {
				update((state) => ({
					...state,
					loading: false,
					error: error.message
				}));
				throw error;
			}
		},

		async loadCourseDetails(courseId) {
			update((state) => ({ ...state, loading: true }));

			try {
				const course = await courseService.getCourseDetails(courseId);
				update((state) => ({
					...state,
					currentCourse: course,
					loading: false
				}));
				return course;
			} catch (error) {
				update((state) => ({
					...state,
					loading: false,
					error: error.message
				}));
				throw error;
			}
		},

		// Enrollment management
		async loadMyEnrollments() {
			update((state) => ({ ...state, loading: true }));

			try {
				const result = await courseService.getMyEnrollments();
				update((state) => ({
					...state,
					enrollments: result.enrollments,
					loading: false
				}));
				return result;
			} catch (error) {
				update((state) => ({
					...state,
					loading: false,
					error: error.message
				}));
				throw error;
			}
		},

		async enrollInCourse(courseId) {
			const result = await courseService.enrollInCourse(courseId);

			if (result.success) {
				update((state) => ({
					...state,
					enrollments: [...state.enrollments, result.enrollment]
				}));

				// Update current course enrollment status
				if (state.currentCourse?.uuid === courseId) {
					update((state) => ({
						...state,
						currentCourse: {
							...state.currentCourse,
							is_enrolled: true
						}
					}));
				}
			}

			return result;
		},

		// Learning session management
		startLearningSession(courseId, lessonId) {
			update((state) => ({
				...state,
				learningSession: {
					...state.learningSession,
					startTime: Date.now(),
					currentCourseId: courseId,
					currentLessonId: lessonId
				}
			}));
		},

		updateLessonProgress(lessonId, progress) {
			update((state) => ({
				...state,
				learningSession: {
					...state.learningSession,
					lessonProgress: {
						...state.learningSession.lessonProgress,
						[lessonId]: progress
					}
				}
			}));

			// Sync with backend
			courseService.updateLessonProgress(lessonId, progress);
		},

		async completeLesson(lessonId) {
			const result = await courseService.completeLesson(lessonId);

			if (result.success) {
				update((state) => {
					const newState = { ...state };

					// Update lesson progress
					newState.learningSession.lessonProgress[lessonId] = {
						completed: true,
						completedAt: Date.now()
					};

					// Update current lesson if applicable
					if (newState.currentLesson?.uuid === lessonId) {
						newState.currentLesson.is_completed = true;
					}

					return newState;
				});
			}

			return result;
		},

		// Quiz management
		setCurrentQuiz(quiz) {
			update((state) => ({
				...state,
				currentQuiz: quiz,
				learningSession: {
					...state.learningSession,
					quizAnswers: {}
				}
			}));
		},

		saveQuizAnswer(questionId, answer) {
			update((state) => ({
				...state,
				learningSession: {
					...state.learningSession,
					quizAnswers: {
						...state.learningSession.quizAnswers,
						[questionId]: answer
					}
				}
			}));
		},

		async submitQuiz(quizId) {
			const state = get(courseStore);
			const responses = Object.entries(state.learningSession.quizAnswers).map(
				([questionId, answer]) => ({
					question_id: questionId,
					...answer
				})
			);

			const result = await courseService.submitQuiz(quizId, responses);

			if (result.success) {
				// Clear quiz answers
				update((state) => ({
					...state,
					learningSession: {
						...state.learningSession,
						quizAnswers: {}
					}
				}));
			}

			return result;
		},

		// Notes management
		addNote(note) {
			update((state) => ({
				...state,
				learningSession: {
					...state.learningSession,
					notes: [
						...state.learningSession.notes,
						{
							id: Date.now(),
							...note,
							createdAt: new Date().toISOString()
						}
					]
				}
			}));
		},

		updateNote(noteId, content) {
			update((state) => ({
				...state,
				learningSession: {
					...state.learningSession,
					notes: state.learningSession.notes.map((note) =>
						note.id === noteId ? { ...note, content, updatedAt: new Date().toISOString() } : note
					)
				}
			}));
		},

		deleteNote(noteId) {
			update((state) => ({
				...state,
				learningSession: {
					...state.learningSession,
					notes: state.learningSession.notes.filter((note) => note.id !== noteId)
				}
			}));
		},

		// Filter management
		updateFilters(filters) {
			update((state) => ({
				...state,
				filters: {
					...state.filters,
					...filters
				},
				pagination: {
					...state.pagination,
					page: 1 // Reset to first page on filter change
				}
			}));

			// Trigger new search
			this.searchCourses();
		},

		clearFilters() {
			update((state) => ({
				...state,
				filters: {
					search: '',
					category: '',
					level: '',
					language: '',
					status: '',
					sortBy: 'relevance'
				}
			}));

			this.searchCourses();
		},

		// Pagination
		setPage(page) {
			update((state) => ({
				...state,
				pagination: {
					...state.pagination,
					page
				}
			}));

			this.searchCourses();
		},

		// Reset store
		reset() {
			set({
				courses: [],
				enrollments: [],
				categories: [],
				currentCourse: null,
				currentLesson: null,
				currentQuiz: null,
				filters: {
					search: '',
					category: '',
					level: '',
					language: '',
					status: '',
					sortBy: 'relevance'
				},
				pagination: {
					page: 1,
					pageSize: 20,
					total: 0,
					totalPages: 0
				},
				learningSession: {
					startTime: null,
					lessonProgress: {},
					quizAnswers: {},
					notes: []
				},
				loading: false,
				error: null
			});
		}
	};
}

export const courseStore = createCourseStore();

// Derived stores
export const courses = derived(courseStore, ($store) => $store.courses);
export const enrollments = derived(courseStore, ($store) => $store.enrollments);
export const currentCourse = derived(courseStore, ($store) => $store.currentCourse);
export const currentLesson = derived(courseStore, ($store) => $store.currentLesson);
export const courseFilters = derived(courseStore, ($store) => $store.filters);
export const isLoading = derived(courseStore, ($store) => $store.loading);

// Computed enrollments
export const activeEnrollments = derived(courseStore, ($store) =>
	$store.enrollments.filter((e) => e.status === 'in_progress')
);

export const completedEnrollments = derived(courseStore, ($store) =>
	$store.enrollments.filter((e) => e.status === 'completed')
);

// Learning progress
export const currentLearningProgress = derived(courseStore, ($store) => {
	if (!$store.currentLesson) return null;
	return $store.learningSession.lessonProgress[$store.currentLesson.uuid] || {};
});

// front/src/lib/apis/courses.js - Add missing methods
import { api } from './index.js';

export const coursesApi = {
	// Courses
	async getCourses(params = {}) {
		const queryString = new URLSearchParams(params).toString();
		return api.get(`/courses/?${queryString}`);
	},

	async getCourse(uuid) {
		try {
			const response = await api.get(`/courses/${uuid}/`);
			return response;
		} catch (error) {
			console.error('Failed to get course:', error);
			throw error;
		}
	},

	async createCourse(data) {
		return api.post('/courses/', data);
	},

	async updateCourse(uuid, data) {
		return api.patch(`/courses/${uuid}/`, data);
	},

	async enrollInCourse(uuid) {
		return api.post(`/courses/${uuid}/enroll/`);
	},

	async publishCourse(uuid) {
		return api.post(`/courses/${uuid}/publish/`);
	},

	async getCourseAnalytics(uuid) {
		return api.get(`/courses/${uuid}/analytics/`);
	},

	// Categories - Add this missing method
	async getCategories() {
		return api.get('/categories/');
	},

	// Enrollments
	async getMyEnrollments() {
		try {
			const response = await api.get('/enrollments/my-courses/');
			return response;
		} catch (error) {
			console.error('Failed to get enrollments:', error);
			throw error;
		}
	},

	async getEnrollment(uuid) {
		return api.get(`/enrollments/${uuid}/`);
	},

	// Modules
	async getModules(courseUuid) {
		return api.get(`/modules/?course=${courseUuid}`);
	},

	async createModule(data) {
		return api.post('/modules/', data);
	},

	async updateModule(uuid, data) {
		return api.patch(`/modules/${uuid}/`, data);
	},

	// Lessons
	async getLessons(moduleUuid) {
		return api.get(`/lessons/?module=${moduleUuid}`);
	},

	async getLesson(uuid) {
		try {
			const response = await api.get(`/lessons/${uuid}/`);
			return response;
		} catch (error) {
			console.error('Failed to get lesson:', error);
			throw error;
		}
	},

	async createLesson(data) {
		return api.post('/lessons/', data);
	},

	async updateLesson(uuid, data) {
		return api.patch(`/lessons/${uuid}/`, data);
	},

	async completeLesson(uuid) {
		return api.post(`/lessons/${uuid}/complete/`);
	},

	async getLessonNotes(uuid) {
		try {
			const response = await api.get(`/lessons/${uuid}/notes/`);
			return response;
		} catch (error) {
			console.error('Failed to get lesson notes:', error);
			return { notes: '' }; // Return empty notes on error
		}
	},

	async saveLessonNotes(uuid, notes) {
		try {
			const response = await api.patch(`/lessons/${uuid}/notes/`, { notes });
			return response;
		} catch (error) {
			console.error('Failed to save lesson notes:', error);
			throw error;
		}
	},

	// Quizzes
	async getQuizzes(courseUuid) {
		return api.get(`/quizzes/?course=${courseUuid}`);
	},

	async getQuiz(uuid) {
		return api.get(`/quizzes/${uuid}/`);
	},

	async startQuizAttempt(uuid) {
		return api.post(`/quizzes/${uuid}/start/`);
	},

	async submitQuiz(uuid, responses) {
		return api.post(`/quizzes/${uuid}/submit/`, { quiz_id: uuid, responses });
	},

	// Reviews
	async getCourseReviews(courseUuid) {
		return api.get(`/reviews/?course=${courseUuid}`);
	},

	async createReview(data) {
		return api.post('/reviews/', data);
	},

	// Certificates
	async getMyCertificates() {
		return api.get('/certificates/');
	},

	async getCertificate(uuid) {
		return api.get(`/certificates/${uuid}/`);
	},

	async verifyCertificate(uuid) {
		return api.get(`/certificates/${uuid}/verify/`);
	},

	// Favorites (placeholder - to be implemented in backend)
	async addToFavorites(courseUuid) {
		// For now, store in localStorage until backend is implemented
		const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
		if (!favorites.includes(courseUuid)) {
			favorites.push(courseUuid);
			localStorage.setItem('favorites', JSON.stringify(favorites));
		}
		return { success: true };
	},

	async removeFromFavorites(courseUuid) {
		// For now, store in localStorage until backend is implemented
		const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
		const updatedFavorites = favorites.filter(uuid => uuid !== courseUuid);
		localStorage.setItem('favorites', JSON.stringify(updatedFavorites));
		return { success: true };
	},

	async getFavorites() {
		// For now, get from localStorage until backend is implemented
		return JSON.parse(localStorage.getItem('favorites') || '[]');
	},

	async isFavorite(courseUuid) {
		// For now, check localStorage until backend is implemented
		const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
		return favorites.includes(courseUuid);
	}
};

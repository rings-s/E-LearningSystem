// front/src/lib/apis/courses.js - Add missing methods
import { api } from './index.js';

export const coursesApi = {
    // Courses
    async getCourses(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return api.get(`/courses/?${queryString}`);
    },

    async getCourse(uuid) {
        return api.get(`/courses/${uuid}/`);
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
        return api.get('/enrollments/my-courses/');
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
        return api.get(`/lessons/${uuid}/`);
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
    }
};
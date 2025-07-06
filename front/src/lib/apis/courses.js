// front/src/lib/apis/courses.js - Complete API following new backend structure
import { api } from './index.js';

export const coursesApi = {
    // Categories
    async getCategories() {
        return api.get('/categories/');
    },

    async getCategory(slug) {
        return api.get(`/categories/${slug}/`);
    },

    // Courses - Main CRUD (following DRF conventions)
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

    async deleteCourse(uuid) {
        return api.delete(`/courses/${uuid}/`);
    },

    // Course Actions
    async enrollInCourse(uuid) {
        return api.post(`/courses/${uuid}/enroll/`);
    },

    async publishCourse(uuid) {
        return api.post(`/courses/${uuid}/publish/`);
    },

    async getCourseAnalytics(uuid) {
        return api.get(`/courses/${uuid}/analytics/`);
    },

    async uploadCourseImage(uuid, file) {
        const formData = new FormData();
        formData.append('thumbnail', file);
        return api.upload(`/courses/${uuid}/upload-image/`, formData);
    },

    // Lessons under Course (nested)
    async getCourseLessons(courseUuid) {
        return api.get(`/courses/${courseUuid}/lessons/`);
    },

    async getCourseLesson(courseUuid, lessonUuid) {
        try {
            const response = await api.get(`/courses/${courseUuid}/lessons/${lessonUuid}/`);
            return response;
        } catch (error) {
            console.error('Failed to get lesson:', error);
            throw error;
        }
    },

    async createCourseLesson(courseUuid, lessonData) {
        return api.post(`/courses/${courseUuid}/lessons/`, lessonData);
    },

    async updateCourseLesson(courseUuid, lessonUuid, data) {
        return api.patch(`/courses/${courseUuid}/lessons/${lessonUuid}/`, data);
    },

    async deleteCourseLesson(courseUuid, lessonUuid) {
        return api.delete(`/courses/${courseUuid}/lessons/${lessonUuid}/`);
    },

    async uploadLessonFile(courseUuid, lessonUuid, file) {
        const formData = new FormData();
        formData.append('file', file);
        return api.upload(`/courses/${courseUuid}/lessons/${lessonUuid}/upload/`, formData);
    },

    async completeLesson(courseUuid, lessonUuid) {
        return api.post(`/courses/${courseUuid}/lessons/${lessonUuid}/complete/`);
    },

    async getLessonNotes(courseUuid, lessonUuid) {
        try {
            const response = await api.get(`/courses/${courseUuid}/lessons/${lessonUuid}/notes/`);
            return response;
        } catch (error) {
            console.error('Failed to get lesson notes:', error);
            return { notes: '' };
        }
    },

    async saveLessonNotes(courseUuid, lessonUuid, notes) {
        try {
            const response = await api.post(`/courses/${courseUuid}/lessons/${lessonUuid}/notes/`, { notes });
            return response;
        } catch (error) {
            console.error('Failed to save lesson notes:', error);
            throw error;
        }
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

    async getEnrollments() {
        return api.get('/enrollments/');
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

    async deleteModule(uuid) {
        return api.delete(`/modules/${uuid}/`);
    },

    // Reviews
    async getCourseReviews(courseUuid) {
        return api.get(`/reviews/?course=${courseUuid}`);
    },

    async createReview(data) {
        return api.post('/reviews/', data);
    },

    async updateReview(uuid, data) {
        return api.patch(`/reviews/${uuid}/`, data);
    },

    async deleteReview(uuid) {
        return api.delete(`/reviews/${uuid}/`);
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

    // Favorites
    async isFavorite(courseUuid) {
        try {
            const response = await api.get(`/courses/${courseUuid}/is-favorite/`);
            return response.is_favorite;
        } catch (error) {
            console.error('Failed to check favorite status:', error);
            return false;
        }
    },

    async addToFavorites(courseUuid) {
        try {
            const response = await api.post(`/courses/${courseUuid}/add-to-favorites/`);
            return response;
        } catch (error) {
            console.error('Failed to add to favorites:', error);
            throw error;
        }
    },

    async removeFromFavorites(courseUuid) {
        try {
            const response = await api.delete(`/courses/${courseUuid}/remove-from-favorites/`);
            return response;
        } catch (error) {
            console.error('Failed to remove from favorites:', error);
            throw error;
        }
    },

    // Convenience method for lesson creation with file
    async createLessonWithFile(courseUuid, lessonData, file = null) {
        try {
            // First create the lesson
            const lesson = await this.createCourseLesson(courseUuid, lessonData);
            
            // Then upload file if provided
            if (file && lesson.uuid) {
                await this.uploadLessonFile(courseUuid, lesson.uuid, file);
            }
            
            return lesson;
        } catch (error) {
            console.error('Failed to create lesson with file:', error);
            throw error;
        }
    },

    // Course Students Management
    async getCourseStudents(courseUuid, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return api.get(`/courses/${courseUuid}/students/?${queryString}`);
    }
};
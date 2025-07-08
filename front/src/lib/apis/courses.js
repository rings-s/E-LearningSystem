// front/src/lib/apis/courses.js
import { api } from './index.js';

export const coursesApi = {
    // Categories
    async getCategories() {
        try {
            return await api.get('/api/categories/');
        } catch (error) {
            console.error('Failed to get categories:', error);
            throw error;
        }
    },

    async getCategory(slug) {
        try {
            return await api.get(`/api/categories/${slug}/`);
        } catch (error) {
            console.error('Failed to get category:', error);
            throw error;
        }
    },

    // Courses - Main CRUD
    async getCourses(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            return await api.get(`/api/courses/${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Failed to get courses:', error);
            throw error;
        }
    },

    async getCourse(uuid) {
        try {
            return await api.get(`/api/courses/${uuid}/`);
        } catch (error) {
            console.error('Failed to get course:', error);
            throw error;
        }
    },

    async createCourse(data) {
        try {
            return await api.post('/api/courses/', data);
        } catch (error) {
            console.error('Failed to create course:', error);
            throw error;
        }
    },

    async updateCourse(uuid, data) {
        try {
            return await api.patch(`/api/courses/${uuid}/`, data);
        } catch (error) {
            console.error('Failed to update course:', error);
            throw error;
        }
    },

    async deleteCourse(uuid) {
        try {
            return await api.delete(`/api/courses/${uuid}/`);
        } catch (error) {
            console.error('Failed to delete course:', error);
            throw error;
        }
    },

    // Course Actions
    async enrollInCourse(uuid) {
        try {
            return await api.post(`/api/courses/${uuid}/enroll/`);
        } catch (error) {
            console.error('Failed to enroll in course:', error);
            throw error;
        }
    },

    async publishCourse(uuid) {
        try {
            return await api.post(`/api/courses/${uuid}/publish/`);
        } catch (error) {
            console.error('Failed to publish course:', error);
            throw error;
        }
    },

    async getCourseAnalytics(uuid) {
        try {
            return await api.get(`/api/courses/${uuid}/analytics/`);
        } catch (error) {
            console.error('Failed to get course analytics:', error);
            throw error;
        }
    },

    async uploadCourseImage(uuid, file) {
        try {
            const formData = new FormData();
            formData.append('thumbnail', file);
            return await api.upload(`/api/courses/${uuid}/upload-image/`, formData);
        } catch (error) {
            console.error('Failed to upload course image:', error);
            throw error;
        }
    },

    // Course Favorites
    async isFavorite(courseUuid) {
        try {
            const response = await api.get(`/api/courses/${courseUuid}/is-favorite/`);
            return response.is_favorite || false;
        } catch (error) {
            console.error('Failed to check favorite status:', error);
            return false;
        }
    },

    async addToFavorites(courseUuid) {
        try {
            return await api.post(`/api/courses/${courseUuid}/add-to-favorites/`);
        } catch (error) {
            console.error('Failed to add to favorites:', error);
            throw error;
        }
    },

    async removeFromFavorites(courseUuid) {
        try {
            return await api.delete(`/api/courses/${courseUuid}/remove-from-favorites/`);
        } catch (error) {
            console.error('Failed to remove from favorites:', error);
            throw error;
        }
    },

    // Lessons under Course
    async getCourseLessons(courseUuid) {
        try {
            return await api.get(`/api/courses/${courseUuid}/lessons/`);
        } catch (error) {
            console.error('Failed to get course lessons:', error);
            throw error;
        }
    },

    async getCourseLesson(courseUuid, lessonUuid) {
        try {
            return await api.get(`/api/courses/${courseUuid}/lessons/${lessonUuid}/`);
        } catch (error) {
            console.error('Failed to get lesson:', error);
            throw error;
        }
    },

    async createCourseLesson(courseUuid, lessonData) {
        try {
            return await api.post(`/api/courses/${courseUuid}/lessons/`, lessonData);
        } catch (error) {
            console.error('Failed to create lesson:', error);
            throw error;
        }
    },

    async updateCourseLesson(courseUuid, lessonUuid, data) {
        try {
            return await api.patch(`/api/courses/${courseUuid}/lessons/${lessonUuid}/`, data);
        } catch (error) {
            console.error('Failed to update lesson:', error);
            throw error;
        }
    },

    async deleteCourseLesson(courseUuid, lessonUuid) {
        try {
            return await api.delete(`/api/courses/${courseUuid}/lessons/${lessonUuid}/`);
        } catch (error) {
            console.error('Failed to delete lesson:', error);
            throw error;
        }
    },

    async uploadLessonFile(courseUuid, lessonUuid, file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            return await api.upload(`/api/courses/${courseUuid}/lessons/${lessonUuid}/upload/`, formData);
        } catch (error) {
            console.error('Failed to upload lesson file:', error);
            throw error;
        }
    },

    async completeLesson(courseUuid, lessonUuid) {
        try {
            return await api.post(`/api/courses/${courseUuid}/lessons/${lessonUuid}/complete/`);
        } catch (error) {
            console.error('Failed to complete lesson:', error);
            throw error;
        }
    },

    async getLessonNotes(courseUuid, lessonUuid) {
        try {
            return await api.get(`/api/courses/${courseUuid}/lessons/${lessonUuid}/notes/`);
        } catch (error) {
            console.error('Failed to get lesson notes:', error);
            return { notes: '' };
        }
    },

    async saveLessonNotes(courseUuid, lessonUuid, notes) {
        try {
            return await api.post(`/api/courses/${courseUuid}/lessons/${lessonUuid}/notes/`, { notes });
        } catch (error) {
            console.error('Failed to save lesson notes:', error);
            throw error;
        }
    },

    // Enrollments
    async getMyEnrollments() {
        try {
            return await api.get('/api/courses/enrollments/my-courses/');
        } catch (error) {
            console.error('Failed to get enrollments:', error);
            throw error;
        }
    },

    async getEnrollments() {
        try {
            return await api.get('/api/courses/enrollments/');
        } catch (error) {
            console.error('Failed to get enrollments:', error);
            throw error;
        }
    },

    // Teacher Courses
    async getMyCourses() {
        try {
            return await api.get('/api/courses/?my_courses=true');
        } catch (error) {
            console.error('Failed to get teacher courses:', error);
            throw error;
        }
    },

    // Modules
    async getModules(courseUuid) {
        try {
            return await api.get(`/api/courses/modules/?course=${courseUuid}`);
        } catch (error) {
            console.error('Failed to get modules:', error);
            throw error;
        }
    },

    async createModule(data) {
        try {
            return await api.post('/api/courses/modules/', data);
        } catch (error) {
            console.error('Failed to create module:', error);
            throw error;
        }
    },

    async getModule(uuid) {
        try {
            return await api.get(`/api/courses/modules/${uuid}/`);
        } catch (error) {
            console.error('Failed to get module:', error);
            throw error;
        }
    },

    async updateModule(uuid, data) {
        try {
            return await api.patch(`/api/courses/modules/${uuid}/`, data);
        } catch (error) {
            console.error('Failed to update module:', error);
            throw error;
        }
    },

    async deleteModule(uuid) {
        try {
            return await api.delete(`/api/courses/modules/${uuid}/`);
        } catch (error) {
            console.error('Failed to delete module:', error);
            throw error;
        }
    },

    // Reviews
    async getCourseReviews(courseUuid) {
        try {
            return await api.get(`/api/courses/reviews/?course=${courseUuid}`);
        } catch (error) {
            console.error('Failed to get course reviews:', error);
            throw error;
        }
    },

    async createReview(data) {
        try {
            return await api.post('/api/courses/reviews/', data);
        } catch (error) {
            console.error('Failed to create review:', error);
            throw error;
        }
    },

    async updateReview(uuid, data) {
        try {
            return await api.patch(`/api/courses/reviews/${uuid}/`, data);
        } catch (error) {
            console.error('Failed to update review:', error);
            throw error;
        }
    },

    async deleteReview(uuid) {
        try {
            return await api.delete(`/api/courses/reviews/${uuid}/`);
        } catch (error) {
            console.error('Failed to delete review:', error);
            throw error;
        }
    },

    // Certificates
    async getMyCertificates() {
        try {
            return await api.get('/api/courses/certificates/');
        } catch (error) {
            console.error('Failed to get certificates:', error);
            throw error;
        }
    },

    async getCertificate(uuid) {
        try {
            return await api.get(`/api/courses/certificates/${uuid}/`);
        } catch (error) {
            console.error('Failed to get certificate:', error);
            throw error;
        }
    },

    async verifyCertificate(uuid) {
        try {
            return await api.get(`/api/courses/certificates/${uuid}/verify/`);
        } catch (error) {
            console.error('Failed to verify certificate:', error);
            throw error;
        }
    },

    // Utility Methods
    async createLessonWithFile(courseUuid, lessonData, file = null) {
        try {
            const lesson = await this.createCourseLesson(courseUuid, lessonData);
            
            if (file && lesson.uuid) {
                await this.uploadLessonFile(courseUuid, lesson.uuid, file);
            }
            
            return lesson;
        } catch (error) {
            console.error('Failed to create lesson with file:', error);
            throw error;
        }
    },

    // Search and Filter Helpers
    async searchCourses(query, filters = {}) {
        try {
            const params = { search: query, ...filters };
            return await this.getCourses(params);
        } catch (error) {
            console.error('Failed to search courses:', error);
            throw error;
        }
    },

    async getCoursesByCategory(categorySlug, additionalParams = {}) {
        try {
            const params = { category: categorySlug, ...additionalParams };
            return await this.getCourses(params);
        } catch (error) {
            console.error('Failed to get courses by category:', error);
            throw error;
        }
    },

    async getFeaturedCourses() {
        try {
            return await this.getCourses({ is_featured: true });
        } catch (error) {
            console.error('Failed to get featured courses:', error);
            throw error;
        }
    }
};
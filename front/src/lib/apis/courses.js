// front/src/lib/apis/courses.js
import { api } from './index.js';
import { validateUUID, isValidUUID } from '../utils/helpers.js';

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
            const validation = validateUUID(uuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/courses/${validation.value}/`);
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
            const validation = validateUUID(uuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.patch(`/api/courses/${validation.value}/`, data);
        } catch (error) {
            console.error('Failed to update course:', error);
            throw error;
        }
    },

    async deleteCourse(uuid) {
        try {
            const validation = validateUUID(uuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.delete(`/api/courses/${validation.value}/`);
        } catch (error) {
            console.error('Failed to delete course:', error);
            throw error;
        }
    },

    // Course Actions
    async enrollInCourse(uuid) {
        try {
            const validation = validateUUID(uuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.post(`/api/courses/${validation.value}/enroll/`);
        } catch (error) {
            console.error('Failed to enroll in course:', error);
            throw error;
        }
    },

    async publishCourse(uuid) {
        try {
            const validation = validateUUID(uuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.post(`/api/courses/${validation.value}/publish/`);
        } catch (error) {
            console.error('Failed to publish course:', error);
            throw error;
        }
    },

    async getCourseAnalytics(uuid) {
        try {
            const validation = validateUUID(uuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/courses/${validation.value}/analytics/`);
        } catch (error) {
            console.error('Failed to get course analytics:', error);
            throw error;
        }
    },

    async uploadCourseImage(uuid, file) {
        try {
            const validation = validateUUID(uuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            const formData = new FormData();
            formData.append('thumbnail', file);
            return await api.upload(`/api/courses/${validation.value}/upload-image/`, formData);
        } catch (error) {
            console.error('Failed to upload course image:', error);
            throw error;
        }
    },

    // Course Favorites
    async isFavorite(courseUuid) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                console.error('Invalid course UUID for favorite check:', validation.error);
                return false;
            }
            const response = await api.get(`/api/courses/${validation.value}/is-favorite/`);
            return response.is_favorite || false;
        } catch (error) {
            console.error('Failed to check favorite status:', error);
            return false;
        }
    },

    async addToFavorites(courseUuid) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.post(`/api/courses/${validation.value}/add-to-favorites/`);
        } catch (error) {
            console.error('Failed to add to favorites:', error);
            throw error;
        }
    },

    async removeFromFavorites(courseUuid) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.delete(`/api/courses/${validation.value}/remove-from-favorites/`);
        } catch (error) {
            console.error('Failed to remove from favorites:', error);
            throw error;
        }
    },

    // Lessons under Course
    async getCourseLessons(courseUuid) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/courses/${validation.value}/lessons/`);
        } catch (error) {
            console.error('Failed to get course lessons:', error);
            throw error;
        }
    },

    async getCourseLesson(courseUuid, lessonUuid) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                throw new Error(courseValidation.error);
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                throw new Error(lessonValidation.error);
            }
            return await api.get(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/`);
        } catch (error) {
            console.error('Failed to get lesson:', error);
            throw error;
        }
    },

    async createCourseLesson(courseUuid, lessonData) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.post(`/api/courses/${validation.value}/lessons/`, lessonData);
        } catch (error) {
            console.error('Failed to create lesson:', error);
            throw error;
        }
    },

    // Alias for createCourseLesson to match new route usage
    async createLesson(courseUuid, lessonData) {
        return this.createCourseLesson(courseUuid, lessonData);
    },

    async uploadLessonResource(courseUuid, lessonUuid, file) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                throw new Error(courseValidation.error);
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                throw new Error(lessonValidation.error);
            }
            const formData = new FormData();
            formData.append('resource', file);
            return await api.upload(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/upload/`, formData);
        } catch (error) {
            console.error('Failed to upload lesson resource:', error);
            throw error;
        }
    },

    async updateCourseLesson(courseUuid, lessonUuid, data) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                throw new Error(courseValidation.error);
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                throw new Error(lessonValidation.error);
            }
            return await api.patch(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/`, data);
        } catch (error) {
            console.error('Failed to update lesson:', error);
            throw error;
        }
    },

    async deleteCourseLesson(courseUuid, lessonUuid) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                throw new Error(courseValidation.error);
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                throw new Error(lessonValidation.error);
            }
            return await api.delete(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/`);
        } catch (error) {
            console.error('Failed to delete lesson:', error);
            throw error;
        }
    },

    async uploadLessonFile(courseUuid, lessonUuid, file) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                throw new Error(courseValidation.error);
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                throw new Error(lessonValidation.error);
            }
            const formData = new FormData();
            formData.append('file', file);
            return await api.upload(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/upload/`, formData);
        } catch (error) {
            console.error('Failed to upload lesson file:', error);
            throw error;
        }
    },

    async completeLesson(courseUuid, lessonUuid) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                throw new Error(courseValidation.error);
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                throw new Error(lessonValidation.error);
            }
            return await api.post(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/complete/`);
        } catch (error) {
            console.error('Failed to complete lesson:', error);
            throw error;
        }
    },

    async getLessonNotes(courseUuid, lessonUuid) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                console.error('Invalid course UUID for notes:', courseValidation.error);
                return { notes: '' };
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                console.error('Invalid lesson UUID for notes:', lessonValidation.error);
                return { notes: '' };
            }
            return await api.get(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/notes/`);
        } catch (error) {
            console.error('Failed to get lesson notes:', error);
            return { notes: '' };
        }
    },

    async saveLessonNotes(courseUuid, lessonUuid, notes) {
        try {
            const courseValidation = validateUUID(courseUuid, 'Course ID');
            if (!courseValidation.isValid) {
                throw new Error(courseValidation.error);
            }
            const lessonValidation = validateUUID(lessonUuid, 'Lesson ID');
            if (!lessonValidation.isValid) {
                throw new Error(lessonValidation.error);
            }
            return await api.post(`/api/courses/${courseValidation.value}/lessons/${lessonValidation.value}/notes/`, { notes });
        } catch (error) {
            console.error('Failed to save lesson notes:', error);
            throw error;
        }
    },

    async getTeacherCourses() {
        try {
            console.log('🔍 [API] Fetching teacher courses...');
            const response = await api.get('/api/courses/teacher/');
            
            console.log('📦 [API] Teacher courses raw response:', response);
            console.log('📦 [API] Response type:', typeof response);
            console.log('📦 [API] Is array:', Array.isArray(response));
            console.log('📦 [API] Response constructor:', response?.constructor?.name);
            
            // Log all response properties if it's an object
            if (response && typeof response === 'object' && !Array.isArray(response)) {
                console.log('📦 [API] Response keys:', Object.keys(response));
                console.log('📦 [API] Response entries:', Object.entries(response));
            }
            
            // Handle direct array response (Django ListView returns array directly)
            if (Array.isArray(response)) {
                console.log('✅ [API] Direct array response with', response.length, 'courses');
                return response;
            }
            
            // Handle paginated response with results
            if (response?.results && Array.isArray(response.results)) {
                console.log('✅ [API] Paginated response with', response.results.length, 'courses');
                return response.results;
            }
            
            // Handle response with data property
            if (response?.data && Array.isArray(response.data)) {
                console.log('✅ [API] Data property response with', response.data.length, 'courses');
                return response.data;
            }
            
            // Handle response with courses property
            if (response?.courses && Array.isArray(response.courses)) {
                console.log('✅ [API] Courses property response with', response.courses.length, 'courses');
                return response.courses;
            }
            
            // Handle single course object - wrap in array
            if (response && typeof response === 'object' && response.uuid) {
                console.log('✅ [API] Single course object, wrapping in array');
                return [response];
            }
            
            // If response is truthy but not in expected format, try to extract what we can
            if (response) {
                console.log('⚠️ [API] Unexpected response format, attempting to handle:', response);
                // If it's an object with properties that look like course data, wrap it
                if (typeof response === 'object') {
                    return [response];
                }
            }
            
            console.log('⚠️ [API] No courses found or unexpected format');
            return [];
        } catch (error) {
            console.error('❌ [API] Failed to get teacher courses:', error);
            throw error;
        }
    },

    async getTeacherStudents() {
        try {
            console.log('🔍 [API] Fetching teacher students...');
            const response = await api.get('/api/courses/teacher/students/');
            
            console.log('📦 [API] Teacher students response:', response);
            console.log('📦 [API] Response type:', typeof response);
            console.log('📦 [API] Has results:', !!response?.results);
            console.log('📦 [API] Results is array:', Array.isArray(response?.results));
            
            // Handle response with results array (expected format)
            if (response?.results && Array.isArray(response.results)) {
                console.log('✅ [API] Results array response with', response.results.length, 'students');
                response.results.forEach((student, index) => {
                    console.log(`👨‍🎓 [API] Student ${index + 1}:`, {
                        name: student.name,
                        email: student.email,
                        course_name: student.course_name,
                        progress: student.progress
                    });
                });
                return response.results;
            }
            
            // Handle direct array response
            if (Array.isArray(response)) {
                console.log('✅ [API] Direct array response with', response.length, 'students');
                return response;
            }
            
            console.log('⚠️ [API] No students found or unexpected format');
            return [];
        } catch (error) {
            console.error('❌ [API] Failed to get teacher students:', error);
            throw error;
        }
    },



    // Enrollments
    async getMyEnrollments() {
        try {
            return await api.get('/api/enrollments/my-courses/');
        } catch (error) {
            console.error('Failed to get enrollments:', error);
            throw error;
        }
    },

    async getEnrollments() {
        try {
            return await api.get('/api/enrollments/');
        } catch (error) {
            console.error('Failed to get enrollments:', error);
            throw error;
        }
    },

    // Teacher Courses
    
    // Fix the existing getMyCourses method
    async getMyCourses() {
        try {
            return await api.get('/api/courses/?my_courses=true');
        } catch (error) {
            console.error('Failed to get my courses:', error);
            throw error;
        }
    },


    async getCourseStudents(courseUuid) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            // Get enrolled students for a specific course
            return await api.get(`/api/enrollments/?course=${validation.value}`);
        } catch (error) {
            console.error('Failed to get course students:', error);
            throw error;
        }
    },

    // Modules
    async getModules(courseUuid) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/modules/?course=${validation.value}`);
        } catch (error) {
            console.error('Failed to get modules:', error);
            throw error;
        }
    },

    async createModule(data) {
        try {
            // Validate course UUID if provided in data
            if (data.course && !isValidUUID(data.course)) {
                throw new Error('Invalid Course ID format in module data');
            }
            return await api.post('/api/modules/', data);
        } catch (error) {
            console.error('Failed to create module:', error);
            throw error;
        }
    },

    async getModule(uuid) {
        try {
            const validation = validateUUID(uuid, 'Module ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/modules/${validation.value}/`);
        } catch (error) {
            console.error('Failed to get module:', error);
            throw error;
        }
    },

    async updateModule(uuid, data) {
        try {
            const validation = validateUUID(uuid, 'Module ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.patch(`/api/modules/${validation.value}/`, data);
        } catch (error) {
            console.error('Failed to update module:', error);
            throw error;
        }
    },

    async deleteModule(uuid) {
        try {
            const validation = validateUUID(uuid, 'Module ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.delete(`/api/modules/${validation.value}/`);
        } catch (error) {
            console.error('Failed to delete module:', error);
            throw error;
        }
    },

    // Reviews
    async getCourseReviews(courseUuid) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/reviews/?course=${validation.value}`);
        } catch (error) {
            console.error('Failed to get course reviews:', error);
            throw error;
        }
    },

    async createReview(data) {
        try {
            // Validate course UUID if provided in data
            if (data.course && !isValidUUID(data.course)) {
                throw new Error('Invalid Course ID format in review data');
            }
            return await api.post('/api/reviews/', data);
        } catch (error) {
            console.error('Failed to create review:', error);
            throw error;
        }
    },

    async updateReview(uuid, data) {
        try {
            const validation = validateUUID(uuid, 'Review ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.patch(`/api/reviews/${validation.value}/`, data);
        } catch (error) {
            console.error('Failed to update review:', error);
            throw error;
        }
    },

    async deleteReview(uuid) {
        try {
            const validation = validateUUID(uuid, 'Review ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.delete(`/api/reviews/${validation.value}/`);
        } catch (error) {
            console.error('Failed to delete review:', error);
            throw error;
        }
    },

    // Certificates
    async getMyCertificates() {
        try {
            return await api.get('/api/certificates/');
        } catch (error) {
            console.error('Failed to get certificates:', error);
            throw error;
        }
    },

    async getCertificate(uuid) {
        try {
            const validation = validateUUID(uuid, 'Certificate ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/certificates/${validation.value}/`);
        } catch (error) {
            console.error('Failed to get certificate:', error);
            throw error;
        }
    },

    async verifyCertificate(uuid) {
        try {
            const validation = validateUUID(uuid, 'Certificate ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            return await api.get(`/api/certificates/${validation.value}/verify/`);
        } catch (error) {
            console.error('Failed to verify certificate:', error);
            throw error;
        }
    },

    // Utility Methods
    async createLessonWithFile(courseUuid, lessonData, file = null) {
        try {
            const validation = validateUUID(courseUuid, 'Course ID');
            if (!validation.isValid) {
                throw new Error(validation.error);
            }
            
            const lesson = await this.createCourseLesson(validation.value, lessonData);
            
            if (file && lesson.uuid) {
                await this.uploadLessonFile(validation.value, lesson.uuid, file);
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
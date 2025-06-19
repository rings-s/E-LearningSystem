// front/src/lib/services/course.service.js
import { coursesApi } from '../apis/courses.js';
import { coreApi } from '../apis/core.js';

class CourseService {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    // Course Management
    async searchCourses(filters = {}) {
        const cacheKey = `courses_${JSON.stringify(filters)}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        try {
            const response = await coursesApi.getCourses(filters);
            const courses = response.results || response;
            
            // Enrich course data
            const enrichedCourses = courses.map(course => ({
                ...course,
                formattedDuration: this.formatDuration(course.duration_hours),
                difficultyLevel: this.getDifficultyLevel(course.level),
                enrollmentStatus: this.getEnrollmentStatus(course)
            }));

            this.setCache(cacheKey, enrichedCourses);
            return enrichedCourses;
        } catch (error) {
            console.error('Failed to search courses:', error);
            throw error;
        }
    }

    async getCourseDetails(courseId) {
        const cacheKey = `course_${courseId}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        try {
            const course = await coursesApi.getCourse(courseId);
            
            // Calculate additional metrics
            const enrichedCourse = {
                ...course,
                totalLessons: this.countTotalLessons(course.modules),
                estimatedWeeks: Math.ceil(course.duration_hours / 5), // 5 hours per week
                completionRate: this.calculateAverageCompletionRate(course),
                difficultyScore: this.calculateDifficultyScore(course)
            };

            this.setCache(cacheKey, enrichedCourse);
            return enrichedCourse;
        } catch (error) {
            console.error('Failed to get course details:', error);
            throw error;
        }
    }

    // Enrollment Management
    async enrollInCourse(courseId) {
        try {
            const enrollment = await coursesApi.enrollInCourse(courseId);
            
            // Clear relevant caches
            this.clearCache('my_enrollments');
            this.clearCache(`course_${courseId}`);
            
            // Track enrollment analytics
            await this.trackEnrollment(courseId);
            
            return { success: true, enrollment };
        } catch (error) {
            return { 
                success: false, 
                error: this.parseEnrollmentError(error) 
            };
        }
    }

    async getMyEnrollments(filters = {}) {
        const cacheKey = `my_enrollments_${JSON.stringify(filters)}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        try {
            const enrollments = await coursesApi.getMyEnrollments();
            
            // Group by status and calculate stats
            const grouped = this.groupEnrollmentsByStatus(enrollments);
            const stats = this.calculateEnrollmentStats(enrollments);

            const result = {
                enrollments,
                grouped,
                stats
            };

            this.setCache(cacheKey, result);
            return result;
        } catch (error) {
            console.error('Failed to get enrollments:', error);
            throw error;
        }
    }

    // Learning Progress
    async updateLessonProgress(lessonId, progress) {
        try {
            const response = await coursesApi.updateLessonProgress(lessonId, progress);
            
            // Update local progress tracking
            this.updateLocalProgress(lessonId, progress);
            
            return response;
        } catch (error) {
            console.error('Failed to update lesson progress:', error);
            throw error;
        }
    }

    async completeLesson(lessonId) {
        try {
            const response = await coursesApi.completeLesson(lessonId);
            
            // Clear caches
            this.clearCache('my_enrollments');
            
            // Calculate achievement
            const achievement = await this.checkForAchievements(lessonId);
            
            return { 
                success: true, 
                response,
                achievement 
            };
        } catch (error) {
            return { 
                success: false, 
                error: error.message 
            };
        }
    }

    // Quiz Management
    async startQuiz(quizId) {
        try {
            const attempt = await coursesApi.startQuizAttempt(quizId);
            
            // Set quiz timer
            this.startQuizTimer(attempt.uuid, attempt.time_limit_minutes);
            
            return { success: true, attempt };
        } catch (error) {
            return { 
                success: false, 
                error: this.parseQuizError(error) 
            };
        }
    }

    async submitQuiz(quizId, responses) {
        try {
            // Validate responses
            const validation = this.validateQuizResponses(responses);
            if (!validation.valid) {
                return { 
                    success: false, 
                    error: validation.error 
                };
            }

            const result = await coursesApi.submitQuiz(quizId, responses);
            
            // Clear quiz timer
            this.clearQuizTimer(quizId);
            
            // Check for achievements
            const achievement = result.passed ? 
                await this.checkQuizAchievement(result) : null;

            return { 
                success: true, 
                result,
                achievement 
            };
        } catch (error) {
            return { 
                success: false, 
                error: error.message 
            };
        }
    }

    // Certificate Management
    async generateCertificate(courseId) {
        try {
            const certificate = await coursesApi.generateCertificate(courseId);
            return { success: true, certificate };
        } catch (error) {
            return { 
                success: false, 
                error: error.message 
            };
        }
    }

    async getMyCertificates() {
        const cacheKey = 'my_certificates';
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        try {
            const certificates = await coursesApi.getMyCertificates();
            this.setCache(cacheKey, certificates);
            return certificates;
        } catch (error) {
            console.error('Failed to get certificates:', error);
            throw error;
        }
    }

    // Helper Methods
    formatDuration(hours) {
        if (hours < 1) {
            return `${Math.round(hours * 60)} minutes`;
        } else if (hours === 1) {
            return '1 hour';
        } else if (hours < 10) {
            return `${hours} hours`;
        } else {
            const weeks = Math.ceil(hours / 40); // 40 hours per week
            return `${weeks} ${weeks === 1 ? 'week' : 'weeks'}`;
        }
    }

    getDifficultyLevel(level) {
        const levels = {
            beginner: { text: 'Beginner', color: 'success', score: 1 },
            intermediate: { text: 'Intermediate', color: 'warning', score: 2 },
            advanced: { text: 'Advanced', color: 'danger', score: 3 }
        };
        return levels[level] || levels.beginner;
    }

    getEnrollmentStatus(course) {
        if (course.is_enrolled) {
            if (course.progress === 100) {
                return { text: 'Completed', color: 'success' };
            } else if (course.progress > 0) {
                return { text: 'In Progress', color: 'warning' };
            } else {
                return { text: 'Enrolled', color: 'info' };
            }
        }
        return { text: 'Not Enrolled', color: 'default' };
    }

    countTotalLessons(modules) {
        if (!modules) return 0;
        return modules.reduce((total, module) => 
            total + (module.lessons?.length || 0), 0
        );
    }

    calculateAverageCompletionRate(course) {
        // This would typically come from backend
        return course.average_completion_rate || 0;
    }

    calculateDifficultyScore(course) {
        const levelScore = { beginner: 1, intermediate: 2, advanced: 3 };
        const baseScore = levelScore[course.level] || 1;
        
        // Adjust based on course metrics
        let score = baseScore;
        if (course.duration_hours > 40) score += 0.5;
        if (course.total_quizzes > 10) score += 0.5;
        
        return Math.min(score, 5);
    }

    groupEnrollmentsByStatus(enrollments) {
        return enrollments.reduce((groups, enrollment) => {
            const status = enrollment.status || 'enrolled';
            if (!groups[status]) {
                groups[status] = [];
            }
            groups[status].push(enrollment);
            return groups;
        }, {});
    }

    calculateEnrollmentStats(enrollments) {
        const stats = {
            total: enrollments.length,
            completed: 0,
            inProgress: 0,
            notStarted: 0,
            totalHours: 0,
            averageProgress: 0
        };

        enrollments.forEach(enrollment => {
            if (enrollment.status === 'completed') {
                stats.completed++;
            } else if (enrollment.progress_percentage > 0) {
                stats.inProgress++;
            } else {
                stats.notStarted++;
            }
            
            stats.totalHours += enrollment.course.duration_hours || 0;
            stats.averageProgress += enrollment.progress_percentage || 0;
        });

        if (enrollments.length > 0) {
            stats.averageProgress /= enrollments.length;
        }

        return stats;
    }

    parseEnrollmentError(error) {
        if (error.message?.includes('already enrolled')) {
            return 'You are already enrolled in this course';
        }
        if (error.message?.includes('limit reached')) {
            return 'This course has reached its enrollment limit';
        }
        return error.message || 'Failed to enroll in course';
    }

    parseQuizError(error) {
        if (error.message?.includes('max attempts')) {
            return 'You have reached the maximum number of attempts for this quiz';
        }
        if (error.message?.includes('not available')) {
            return 'This quiz is not currently available';
        }
        return error.message || 'Failed to process quiz';
    }

    validateQuizResponses(responses) {
        if (!Array.isArray(responses)) {
            return { valid: false, error: 'Invalid response format' };
        }

        for (const response of responses) {
            if (!response.question_id) {
                return { valid: false, error: 'Missing question ID' };
            }
            if (!response.answer_id && !response.text_response) {
                return { valid: false, error: 'Missing answer' };
            }
        }

        return { valid: true };
    }

    // Cache Management
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        this.cache.delete(key);
        return null;
    }

    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    clearCache(pattern = null) {
        if (!pattern) {
            this.cache.clear();
        } else {
            for (const key of this.cache.keys()) {
                if (key.includes(pattern)) {
                    this.cache.delete(key);
                }
            }
        }
    }

    // Analytics and Tracking
    async trackEnrollment(courseId) {
        try {
            await coreApi.trackActivity({
                activity_type: 'course_enrollment',
                course_id: courseId,
                metadata: {
                    timestamp: new Date().toISOString(),
                    source: 'web'
                }
            });
        } catch (error) {
            console.error('Failed to track enrollment:', error);
        }
    }

    async checkForAchievements(lessonId) {
        // Check for various achievements
        const achievements = [];

        // First lesson completed
        const progress = await this.getMyProgress();
        if (progress.totalLessonsCompleted === 1) {
            achievements.push({
                type: 'first_lesson',
                title: 'First Step',
                description: 'Completed your first lesson!'
            });
        }

        // Streak achievement
        if (progress.currentStreak >= 7) {
            achievements.push({
                type: 'week_streak',
                title: 'Week Warrior',
                description: '7-day learning streak!'
            });
        }

        return achievements;
    }

    async checkQuizAchievement(result) {
        if (result.score === 100) {
            return {
                type: 'perfect_score',
                title: 'Perfect Score!',
                description: 'Scored 100% on a quiz'
            };
        }
        return null;
    }

    // Timer Management
    startQuizTimer(quizId, timeLimitMinutes) {
        if (!timeLimitMinutes) return;

        const endTime = Date.now() + (timeLimitMinutes * 60 * 1000);
        if (typeof window !== 'undefined') {
            window.localStorage.setItem(`quiz_timer_${quizId}`, endTime);
        }
    }

    clearQuizTimer(quizId) {
        if (typeof window !== 'undefined') {
            window.localStorage.removeItem(`quiz_timer_${quizId}`);
        }
    }

    getQuizTimeRemaining(quizId) {
        if (typeof window === 'undefined') return null;

        const endTime = window.localStorage.getItem(`quiz_timer_${quizId}`);
        if (!endTime) return null;

        const remaining = parseInt(endTime) - Date.now();
        return Math.max(0, Math.floor(remaining / 1000)); // Return seconds
    }

    // Progress Tracking
    updateLocalProgress(lessonId, progress) {
        if (typeof window === 'undefined') return;

        const key = `lesson_progress_${lessonId}`;
        window.localStorage.setItem(key, JSON.stringify({
            ...progress,
            updatedAt: Date.now()
        }));
    }

    async getMyProgress() {
        // This would typically come from an API endpoint
        const enrollments = await this.getMyEnrollments();
        
        return {
            totalLessonsCompleted: enrollments.stats.completed,
            currentStreak: this.calculateStreak(enrollments.enrollments),
            totalHoursLearned: enrollments.stats.totalHours
        };
    }

    calculateStreak(enrollments) {
        // Simple streak calculation based on last accessed dates
        let streak = 0;
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        enrollments.forEach(enrollment => {
            if (enrollment.last_accessed) {
                const lastAccessed = new Date(enrollment.last_accessed);
                lastAccessed.setHours(0, 0, 0, 0);
                
                const daysDiff = Math.floor((today - lastAccessed) / (1000 * 60 * 60 * 24));
                if (daysDiff === 0 || daysDiff === 1) {
                    streak = Math.max(streak, enrollment.current_streak || 1);
                }
            }
        });

        return streak;
    }
}

export const courseService = new CourseService();
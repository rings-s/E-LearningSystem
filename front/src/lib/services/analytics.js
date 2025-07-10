// front/src/lib/services/analytics.js
import { coreApi } from '$lib/apis/core.js';

export const analyticsService = {
    /**
     * Get teacher analytics data
     * @returns {Promise<Object>} Teacher analytics data
     */
    async getTeacherAnalytics() {
        try {
            return await coreApi.getTeacherAnalytics();
        } catch (error) {
            console.error('Analytics Service - Failed to get teacher analytics:', error);
            throw error;
        }
    },

    /**
     * Get student analytics data
     * @returns {Promise<Object>} Student analytics data
     */
    async getStudentAnalytics() {
        try {
            return await coreApi.getStudentAnalytics();
        } catch (error) {
            console.error('Analytics Service - Failed to get student analytics:', error);
            throw error;
        }
    },

    /**
     * Get platform-wide analytics data
     * @returns {Promise<Object>} Platform analytics data
     */
    async getPlatformAnalytics() {
        try {
            return await coreApi.getPlatformAnalytics();
        } catch (error) {
            console.error('Analytics Service - Failed to get platform analytics:', error);
            throw error;
        }
    }
};
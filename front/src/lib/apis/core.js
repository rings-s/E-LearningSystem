// front/src/lib/apis/core.js
import { api } from './index.js';

export const coreApi = {
	// Dashboard
	async getDashboard() {
        return api.get('/api/core/dashboard/');
    },

    async getDashboardSummary() {
        return api.get('/api/core/dashboard/summary/');
    },

	// Enhanced Analytics Endpoints
	async getStudentAnalytics() {
		return api.get('/api/core/student-analytics/');
	},

	async getTeacherAnalytics() {
		return api.get('/api/core/teacher-analytics/');
	},

	async getPlatformAnalytics() {
		return api.get('/api/core/platform-analytics/');
	},

	// Study Session Tracking
	async trackStudySession(sessionData) {
		return api.post('/api/core/track-study-session/', sessionData);
	},

	// Activity Tracking
	async trackActivity(activityData) {
		return api.post('/api/core/track-activity/', activityData);
	},

	// Forums & Discussions
	async getForums() {
		return api.get('/api/core/forums/');
	},

	async getDiscussions(params = {}) {
		const queryString = new URLSearchParams(params).toString();
		return api.get(`/api/core/discussions/?${queryString}`);
	},

	async createDiscussion(data) {
		return api.post('/api/core/discussions/', data);
	},

	async getDiscussion(uuid) {
		return api.get(`/api/core/discussions/${uuid}/`);
	},

	async createReply(data) {
		return api.post('/api/core/replies/', data);
	},

	// Notifications
	async getNotifications(params = {}) {
		const queryString = new URLSearchParams(params).toString();
		return api.get(`/api/core/notifications/?${queryString}`);
	},

	async markNotificationRead(uuid) {
		return api.patch(`/api/core/notifications/${uuid}/`, { is_read: true });
	},

	async markAllNotificationsRead() {
		return api.post('/api/core/notifications/mark-all-read/');
	},

	async getUnreadCount() {
		return api.get('/api/core/notifications/unread-count/');
	},

	// Announcements
	async getAnnouncements() {
		return api.get('/api/core/announcements/');
	},

	// Support
	async createSupportTicket(data) {
		return api.post('/api/core/support-tickets/', data);
	},

	async getSupportTickets() {
		return api.get('/api/core/support-tickets/');
	},

	// Media
	async uploadMedia(file, data) {
		const formData = new FormData();
		formData.append('file', file);
		Object.keys(data).forEach((key) => {
			formData.append(key, data[key]);
		});
		return api.upload('/api/core/media/', formData);
	},

};
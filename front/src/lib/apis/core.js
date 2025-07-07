// front/src/lib/apis/core.js
import { api } from './index.js';

export const coreApi = {
	// Dashboard
	async getDashboard() {
        try {
            return await api.get('/api/core/dashboard/');
        } catch (error) {
            console.error('Failed to get dashboard:', error);
            throw error;
        }
    },

    async getDashboardSummary() {
        try {
            return await api.get('/api/core/dashboard/summary/');
        } catch (error) {
            console.error('Failed to get dashboard summary:', error);
            throw error;
        }
    },

	// Analytics Endpoints
	async getStudentAnalytics() {
        try {
            return await api.get('/api/core/student-analytics/');
        } catch (error) {
            console.error('Failed to get student analytics:', error);
            throw error;
        }
	},

	async getTeacherAnalytics() {
        try {
            return await api.get('/api/core/teacher-analytics/');
        } catch (error) {
            console.error('Failed to get teacher analytics:', error);
            throw error;
        }
	},

	async getPlatformAnalytics() {
        try {
            return await api.get('/api/core/platform-analytics/');
        } catch (error) {
            console.error('Failed to get platform analytics:', error);
            throw error;
        }
	},

	// Activity Tracking
	async getActivityLogs(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            return await api.get(`/api/core/activities/${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Failed to get activity logs:', error);
            throw error;
        }
    },

	// Forums & Discussions
	async getForums() {
        try {
            return await api.get('/api/core/forums/');
        } catch (error) {
            console.error('Failed to get forums:', error);
            throw error;
        }
	},

    async getForum(uuid) {
        try {
            return await api.get(`/api/core/forums/${uuid}/`);
        } catch (error) {
            console.error('Failed to get forum:', error);
            throw error;
        }
    },

	async getDiscussions(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            return await api.get(`/api/core/discussions/${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Failed to get discussions:', error);
            throw error;
        }
	},

	async createDiscussion(data) {
        try {
            return await api.post('/api/core/discussions/', data);
        } catch (error) {
            console.error('Failed to create discussion:', error);
            throw error;
        }
	},

	async getDiscussion(uuid) {
        try {
            return await api.get(`/api/core/discussions/${uuid}/`);
        } catch (error) {
            console.error('Failed to get discussion:', error);
            throw error;
        }
	},

    // Discussion Actions
    async pinDiscussion(uuid) {
        try {
            return await api.post(`/api/core/discussions/${uuid}/pin/`);
        } catch (error) {
            console.error('Failed to pin discussion:', error);
            throw error;
        }
    },

    async lockDiscussion(uuid) {
        try {
            return await api.post(`/api/core/discussions/${uuid}/lock/`);
        } catch (error) {
            console.error('Failed to lock discussion:', error);
            throw error;
        }
    },

    async resolveDiscussion(uuid) {
        try {
            return await api.post(`/api/core/discussions/${uuid}/resolve/`);
        } catch (error) {
            console.error('Failed to resolve discussion:', error);
            throw error;
        }
    },

    // Replies
    async getReplies(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            return await api.get(`/api/core/replies/${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Failed to get replies:', error);
            throw error;
        }
    },

	async createReply(data) {
        try {
            return await api.post('/api/core/replies/', data);
        } catch (error) {
            console.error('Failed to create reply:', error);
            throw error;
        }
	},

    async upvoteReply(uuid) {
        try {
            return await api.post(`/api/core/replies/${uuid}/upvote/`);
        } catch (error) {
            console.error('Failed to upvote reply:', error);
            throw error;
        }
    },

    async markSolution(uuid) {
        try {
            return await api.post(`/api/core/replies/${uuid}/mark-solution/`);
        } catch (error) {
            console.error('Failed to mark solution:', error);
            throw error;
        }
    },

	// Notifications
	async getNotifications(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            return await api.get(`/api/core/notifications/${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Failed to get notifications:', error);
            throw error;
        }
	},

	async markNotificationRead(uuid) {
        try {
            return await api.patch(`/api/core/notifications/${uuid}/`, { is_read: true });
        } catch (error) {
            console.error('Failed to mark notification read:', error);
            throw error;
        }
	},

	async markAllNotificationsRead() {
        try {
            return await api.post('/api/core/notifications/mark-all-read/');
        } catch (error) {
            console.error('Failed to mark all notifications read:', error);
            throw error;
        }
	},

	async getUnreadCount() {
        try {
            return await api.get('/api/core/notifications/unread-count/');
        } catch (error) {
            console.error('Failed to get unread count:', error);
            return { unread_count: 0 };
        }
	},

	// Announcements
	async getAnnouncements() {
        try {
            return await api.get('/api/core/announcements/');
        } catch (error) {
            console.error('Failed to get announcements:', error);
            throw error;
        }
	},

    async createAnnouncement(data) {
        try {
            return await api.post('/api/core/announcements/', data);
        } catch (error) {
            console.error('Failed to create announcement:', error);
            throw error;
        }
    },

	// Support
	async createSupportTicket(data) {
        try {
            return await api.post('/api/core/support-tickets/', data);
        } catch (error) {
            console.error('Failed to create support ticket:', error);
            throw error;
        }
	},

	async getSupportTickets() {
        try {
            return await api.get('/api/core/support-tickets/');
        } catch (error) {
            console.error('Failed to get support tickets:', error);
            throw error;
        }
	},

    async getSupportTicket(uuid) {
        try {
            return await api.get(`/api/core/support-tickets/${uuid}/`);
        } catch (error) {
            console.error('Failed to get support ticket:', error);
            throw error;
        }
    },

	// Media
	async getMedia() {
        try {
            return await api.get('/api/core/media/');
        } catch (error) {
            console.error('Failed to get media:', error);
            throw error;
        }
    },

	async uploadMedia(file, data = {}) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            Object.keys(data).forEach((key) => {
                formData.append(key, data[key]);
            });
            return await api.upload('/api/core/media/', formData);
        } catch (error) {
            console.error('Failed to upload media:', error);
            throw error;
        }
	}
};
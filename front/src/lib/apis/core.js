// front/src/lib/apis/core.js
import { api } from './index.js';

export const coreApi = {
    // Dashboard
    async getDashboard() {
        return api.get('/core/dashboard/');
    },

    // Forums & Discussions
    async getForums() {
        return api.get('/core/forums/');
    },

    async getDiscussions(forumUuid) {
        return api.get(`/core/discussions/?forum=${forumUuid}`);
    },

    async createDiscussion(data) {
        return api.post('/core/discussions/', data);
    },

    async getDiscussion(uuid) {
        return api.get(`/core/discussions/${uuid}/`);
    },

    async createReply(data) {
        return api.post('/core/replies/', data);
    },

    // Notifications
    async getNotifications(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return api.get(`/core/notifications/?${queryString}`);
    },

    async markNotificationRead(uuid) {
        return api.patch(`/core/notifications/${uuid}/`, { is_read: true });
    },

    async markAllNotificationsRead() {
        return api.post('/core/notifications/mark-all-read/');
    },

    async getUnreadCount() {
        return api.get('/core/notifications/unread-count/');
    },

    // Announcements
    async getAnnouncements() {
        return api.get('/core/announcements/');
    },

    // Support
    async createSupportTicket(data) {
        return api.post('/core/support-tickets/', data);
    },

    async getSupportTickets() {
        return api.get('/core/support-tickets/');
    },

    // Media
    async uploadMedia(file, data) {
        const formData = new FormData();
        formData.append('file', file);
        Object.keys(data).forEach(key => {
            formData.append(key, data[key]);
        });
        return api.upload('/core/media/', formData);
    }
};
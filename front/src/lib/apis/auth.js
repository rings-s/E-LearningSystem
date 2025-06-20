// front/src/lib/apis/auth.js
import { api } from './index.js';

export const authApi = {
    async register(userData) {
        return api.post('/auth/register/', userData, { skipAuth: true });
    },

    async login(credentials) {
        return api.post('/auth/login/', credentials, { skipAuth: true });
    },

    async verifyEmail(data) {
        return api.post('/auth/verify-email/', data, { skipAuth: true });
    },

    async resendVerification(email) {
        return api.post('/auth/resend-verification/', { email }, { skipAuth: true });
    },

    async refreshToken(refreshToken) {
        return api.post('/auth/refresh/', { refresh: refreshToken }, { skipAuth: true });
    },

    async changePassword(data) {
        return api.post('/auth/change-password/', data);
    },

    async requestPasswordReset(email) {
        return api.post('/auth/password-reset/', { email }, { skipAuth: true });
    },

    async confirmPasswordReset(data) {
        return api.post('/auth/password-reset-confirm/', data, { skipAuth: true });
    },

    async getCurrentUser() {
        return api.get('/auth/users/me/');
    },

    async updateProfile(data) {
        return api.patch('/auth/users/me/', data);
    },

    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);
        return api.upload('/auth/users/me/avatar/', formData);
    }
};
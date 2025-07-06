// front/src/lib/apis/auth.js
import { api } from './index.js';

export const authApi = {
	async register(userData) {
		return api.post('/api/auth/register/', userData, { skipAuth: true });
	},

	async login(credentials) {
		return api.post('/api/auth/login/', credentials, { skipAuth: true });
	},

	async verifyEmail(data) {
		return api.post('/api/auth/verify-email/', data, { skipAuth: true });
	},

	async resendVerification(email) {
		return api.post('/api/auth/resend-verification/', { email }, { skipAuth: true });
	},

	async getCurrentUser() {
		return api.get('/api/auth/users/me/');
	},

	async updateProfile(data) {
		return api.patch('/api/auth/users/me/', data);
	},

	async uploadAvatar(file) {
		const formData = new FormData();
		formData.append('avatar', file);
		return api.upload('/api/auth/users/me/avatar/', formData);
	},

	async refreshToken(refreshToken) {
		return api.post('/api/auth/refresh/', { refresh: refreshToken }, { skipAuth: true });
	},

	async requestPasswordReset(email) {
		return api.post('/api/auth/password-reset/', { email }, { skipAuth: true });
	},

	async confirmPasswordReset(data) {
		return api.post('/api/auth/password-reset-confirm/', data, { skipAuth: true });
	}
};

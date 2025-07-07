// front/src/lib/apis/auth.js
import { api } from './index.js';

export const authApi = {
	async register(userData) {
		try {
			return await api.post('/api/accounts/register/', userData, { skipAuth: true });
		} catch (error) {
			console.error('Failed to register:', error);
			throw error;
		}
	},

	async login(credentials) {
		try {
			return await api.post('/api/accounts/login/', credentials, { skipAuth: true });
		} catch (error) {
			console.error('Failed to login:', error);
			throw error;
		}
	},

	async verifyEmail(data) {
		try {
			return await api.post('/api/accounts/verify-email/', data, { skipAuth: true });
		} catch (error) {
			console.error('Failed to verify email:', error);
			throw error;
		}
	},

	async resendVerification(email) {
		try {
			return await api.post('/api/accounts/resend-verification/', { email }, { skipAuth: true });
		} catch (error) {
			console.error('Failed to resend verification:', error);
			throw error;
		}
	},

	async getCurrentUser() {
		try {
			return await api.get('/api/accounts/users/me/');
		} catch (error) {
			console.error('Failed to get current user:', error);
			throw error;
		}
	},

	async updateProfile(data) {
		try {
			return await api.patch('/api/accounts/users/me/', data);
		} catch (error) {
			console.error('Failed to update profile:', error);
			throw error;
		}
	},

	async uploadAvatar(file) {
		try {
			const formData = new FormData();
			formData.append('avatar', file);
			return await api.upload('/api/accounts/users/me/avatar/', formData);
		} catch (error) {
			console.error('Failed to upload avatar:', error);
			throw error;
		}
	},

	async refreshToken(refreshToken) {
		try {
			return await api.post('/api/accounts/refresh/', { refresh: refreshToken }, { skipAuth: true });
		} catch (error) {
			console.error('Failed to refresh token:', error);
			throw error;
		}
	},

	async requestPasswordReset(email) {
		try {
			return await api.post('/api/accounts/password-reset/', { email }, { skipAuth: true });
		} catch (error) {
			console.error('Failed to request password reset:', error);
			throw error;
		}
	},

	async confirmPasswordReset(data) {
		try {
			return await api.post('/api/accounts/password-reset-confirm/', data, { skipAuth: true });
		} catch (error) {
			console.error('Failed to confirm password reset:', error);
			throw error;
		}
	},

	async changePassword(data) {
		try {
			return await api.post('/api/accounts/change-password/', data);
		} catch (error) {
			console.error('Failed to change password:', error);
			throw error;
		}
	},

	// User management (for admin/staff)
	async getUsers(params = {}) {
		try {
			const queryString = new URLSearchParams(params).toString();
			return await api.get(`/api/accounts/users/${queryString ? '?' + queryString : ''}`);
		} catch (error) {
			console.error('Failed to get users:', error);
			throw error;
		}
	},

	async getUser(uuid) {
		try {
			return await api.get(`/api/accounts/users/${uuid}/`);
		} catch (error) {
			console.error('Failed to get user:', error);
			throw error;
		}
	},

	async updateUser(uuid, data) {
		try {
			return await api.patch(`/api/accounts/users/${uuid}/`, data);
		} catch (error) {
			console.error('Failed to update user:', error);
			throw error;
		}
	},

	async deleteUser(uuid) {
		try {
			return await api.delete(`/api/accounts/users/${uuid}/`);
		} catch (error) {
			console.error('Failed to delete user:', error);
			throw error;
		}
	}
};
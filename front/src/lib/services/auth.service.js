// front/src/lib/services/auth.service.js
import { authApi } from '$lib/apis/auth.js';
import { browser } from '$app/environment';
import { writable, derived } from 'svelte/store';

class AuthService {
    constructor() {
        this.tokenKey = 'access_token';
        this.refreshKey = 'refresh_token';
        this.userKey = 'user_data';
    }

    // Token Management
    setTokens(tokens) {
        if (!browser) return;
        
        if (tokens.access) {
            localStorage.setItem(this.tokenKey, tokens.access);
        }
        if (tokens.refresh) {
            localStorage.setItem(this.refreshKey, tokens.refresh);
        }
    }

    getAccessToken() {
        if (!browser) return null;
        return localStorage.getItem(this.tokenKey);
    }

    getRefreshToken() {
        return tokenManager.getRefreshToken();
    }

    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            this.logout();
            throw new Error('No refresh token available');
        }

        try {
            const { access } = await authApi.refreshToken(refreshToken);
            tokenManager.setTokens(access);
            return access;
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.logout();
            throw error;
        }
    }

    async register(userData) {
        try {
            const response = await authApi.register(userData);
            return { 
                success: true, 
                data: response,
                email: userData.email 
            };
        } catch (error) {
            return { 
                success: false, 
                error: this.parseRegistrationError(error) 
            };
        }
    }

    async verifyEmail(email, code) {
        try {
            const response = await authApi.verifyEmail({ 
                email, 
                verification_code: code 
            });
            
            if (response.tokens) {
                tokenManager.setTokens(response.tokens.access, response.tokens.refresh);
                const user = await this.getCurrentUser();
                currentUser.set(user);
            }
            
            return { success: true, user: response.user };
        } catch (error) {
            return { 
                success: false, 
                error: error.message || 'Invalid verification code' 
            };
        }
    }

            return user;
        } catch (error) {
            if (error.message === 'Unauthorized') {
                this.clearTokens();
            }
            throw error;
        }
    }

    async updateProfile(data) {
        try {
            const response = await authApi.updateProfile(data);
            const updatedUser = response.data || response;
            
            // Update stored user data
            const currentUser = this.getUserData();
            if (currentUser) {
                const mergedUser = { ...currentUser, ...updatedUser };
                this.setUserData(mergedUser);
            }
            
            return { success: true, user: updatedUser };
        } catch (error) {
            return { 
                success: false, 
                error: error.message || 'Failed to update profile' 
            };
        }
    }

    async changePassword(currentPassword, newPassword) {
        try {
            await authApi.changePassword({
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: newPassword
            });
            return { success: true };
        } catch (error) {
            return { 
                success: false, 
                error: error.message || 'Failed to change password' 
            };
        }
    }

    logout() {
        this.clearTokens();
        currentUser.set(null);
    }

    // Helper Methods
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    hasRole(role) {
        const user = this.getUserData();
        return user?.role === role || user?.is_superuser;
    }

    parseRegistrationError(error) {
        if (error.response?.data?.error) {
            const errors = error.response.data.error;
            if (errors.email) {
                return 'Email already exists';
            }
            if (errors.password) {
                return errors.password[0];
            }
        }
        return error.message || 'Registration failed';
    }

    // Session Management
    async validateSession() {
        if (!this.isAuthenticated()) {
            return false;
        }

        try {
            await this.getCurrentUser();
            return true;
        } catch (error) {
            return false;
        }
    }

    getSessionInfo() {
        const token = this.getAccessToken();
        if (!token) return null;

        try {
            // Decode JWT without verification (for display purposes only)
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(atob(base64));
            
            return {
                userId: payload.user_id,
                expiresAt: new Date(payload.exp * 1000),
                issuedAt: new Date(payload.iat * 1000)
            };
        } catch (error) {
            return null;
        }
    }
}

export const authService = new AuthService();
export const currentUser = writable(authService.getUserData());
export const userRole = derived(currentUser, $currentUser => $currentUser?.role);
export const isAuthenticated = derived(currentUser, $currentUser => !!$currentUser);
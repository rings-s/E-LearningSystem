// front/src/lib/stores/auth.store.js - Fix updateProfile method
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';

function createAuthStore() {
    const { subscribe, set, update } = writable({
        user: null,
        isLoading: false,
        isInitialized: false
    });

    function getToken() {
        if (!browser) return null;
        return localStorage.getItem('access_token');
    }

    function setTokens(accessToken, refreshToken) {
        if (!browser) return;
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
    }

    function clearTokens() {
        if (!browser) return;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    return {
        subscribe,
        
        async init() {
            if (!browser) return;
            
            update(state => ({ ...state, isLoading: true }));
            
            try {
                const token = getToken();
                if (token) {
                    const userData = await authApi.getCurrentUser();
                    set({
                        user: userData,
                        isLoading: false,
                        isInitialized: true
                    });
                } else {
                    set({
                        user: null,
                        isLoading: false,
                        isInitialized: true
                    });
                }
            } catch (error) {
                console.error('Auth initialization failed:', error);
                clearTokens();
                set({
                    user: null,
                    isLoading: false,
                    isInitialized: true
                });
            }
        },

        async login(credentials) {
            update(state => ({ ...state, isLoading: true }));
            
            try {
                const response = await authApi.login(credentials);
                
                const accessToken = response.tokens?.access || response.access;
                const refreshToken = response.tokens?.refresh || response.refresh;
                const userData = response.user;
                
                if (accessToken && userData) {
                    setTokens(accessToken, refreshToken);
                    update(state => ({
                        ...state,
                        user: userData,
                        isLoading: false
                    }));
                    return { success: true, user: userData };
                } else {
                    update(state => ({ ...state, isLoading: false }));
                    return { success: false, error: 'Invalid response format' };
                }
            } catch (error) {
                update(state => ({ ...state, isLoading: false }));
                return { success: false, error: error.message || 'Login failed' };
            }
        },

        async register(userData) {
            update(state => ({ ...state, isLoading: true }));
            
            try {
                const response = await authApi.register(userData);
                update(state => ({ ...state, isLoading: false }));
                return { success: true, data: response };
            } catch (error) {
                update(state => ({ ...state, isLoading: false }));
                return { success: false, error: error.message || 'Registration failed' };
            }
        },

        async verifyEmail(email, code) {
            update(state => ({ ...state, isLoading: true }));
            
            try {
                const response = await authApi.verifyEmail({ 
                    email, 
                    verification_code: code 
                });
                
                const accessToken = response.tokens?.access || response.access;
                const refreshToken = response.tokens?.refresh || response.refresh;
                const userData = response.user;
                
                if (accessToken && userData) {
                    setTokens(accessToken, refreshToken);
                    update(state => ({
                        ...state,
                        user: userData,
                        isLoading: false
                    }));
                    return { success: true, user: userData };
                } else {
                    update(state => ({ ...state, isLoading: false }));
                    return { success: false, error: 'Invalid response format' };
                }
            } catch (error) {
                update(state => ({ ...state, isLoading: false }));
                return { success: false, error: error.message || 'Verification failed' };
            }
        },

        async resendVerification(email) {
            update(state => ({ ...state, isLoading: true }));
            
            try {
                await authApi.resendVerification(email);
                update(state => ({ ...state, isLoading: false }));
                return { success: true };
            } catch (error) {
                update(state => ({ ...state, isLoading: false }));
                return { success: false, error: error.message || 'Failed to resend verification' };
            }
        },

        // Fix updateProfile method
        async updateProfile(profileData) {
            try {
                const response = await authApi.updateProfile(profileData);
                
                // Update the user in the store with the new data
                update(state => ({
                    ...state,
                    user: {
                        ...state.user,
                        ...response  // Merge the response data
                    }
                }));
                
                return { success: true, data: response };
            } catch (error) {
                console.error('Profile update error:', error);
                return { success: false, error: error.message || 'Failed to update profile' };
            }
        },

        logout() {
            clearTokens();
            set({
                user: null,
                isLoading: false,
                isInitialized: true
            });
        }
    };
}

export const authStore = createAuthStore();

// Derived stores for convenience
export const isAuthenticated = derived(
    authStore, 
    $auth => !!$auth.user && !!getTokenFromStorage()
);

export const currentUser = derived(authStore, $auth => $auth.user);
export const userRole = derived(authStore, $auth => $auth.user?.role || null);
export const isLoading = derived(authStore, $auth => $auth.isLoading);
export const isInitialized = derived(authStore, $auth => $auth.isInitialized);

// Helper function for isAuthenticated
function getTokenFromStorage() {
    if (!browser) return null;
    return localStorage.getItem('access_token');
}
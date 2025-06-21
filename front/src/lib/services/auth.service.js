// front/src/lib/services/auth.service.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';

function createAuthStore() {
    const initialState = {
        user: null,
        token: null,
        refreshToken: null,
        isLoading: true,
        isAuthenticated: false,
        isInitialized: false
    };

    const { subscribe, set, update } = writable(initialState);

    let currentState = initialState;
    
    subscribe(state => {
        currentState = state;
    });

    return {
        subscribe,
        
        async init() {
            if (!browser) return;
            
            const token = localStorage.getItem('access_token');
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (token) {
                try {
                    const userData = await authApi.getCurrentUser();
                    update(state => ({
                        ...state,
                        user: userData.data || userData,
                        token,
                        refreshToken,
                        isAuthenticated: true,
                        isLoading: false,
                        isInitialized: true
                    }));
                } catch (error) {
                    console.warn('Token validation failed:', error);
                    this.clearAuth();
                }
            } else {
                update(state => ({ 
                    ...state, 
                    isLoading: false,
                    isInitialized: true 
                }));
            }
        },

        async login(credentials) {
            try {
                const response = await authApi.login(credentials);
                const { access, refresh, user } = response;
                
                if (browser) {
                    localStorage.setItem('access_token', access);
                    localStorage.setItem('refresh_token', refresh);
                }
                
                update(state => ({
                    ...state,
                    user,
                    token: access,
                    refreshToken: refresh,
                    isAuthenticated: true,
                    isLoading: false,
                    isInitialized: true
                }));
                
                return { success: true, user };
            } catch (error) {
                return { 
                    success: false, 
                    error: error.message || 'Login failed'
                };
            }
        },

        async register(userData) {
            try {
                const response = await authApi.register(userData);
                return { success: true, data: response };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        async verifyEmail(email, code) {
            try {
                const response = await authApi.verifyEmail({ email, code });
                const { access, refresh, user } = response;
                
                if (browser && access) {
                    localStorage.setItem('access_token', access);
                    localStorage.setItem('refresh_token', refresh);
                }
                
                update(state => ({
                    ...state,
                    user,
                    token: access,
                    refreshToken: refresh,
                    isAuthenticated: true,
                    isLoading: false
                }));
                
                return { success: true, user };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        async resendVerification(email) {
            try {
                await authApi.resendVerification(email);
                return { success: true };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        async updateProfile(data) {
            try {
                const response = await authApi.updateProfile(data);
                update(state => ({
                    ...state,
                    user: { ...state.user, ...response.data }
                }));
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        clearAuth() {
            if (browser) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
            set({
                user: null,
                token: null,
                refreshToken: null,
                isAuthenticated: false,
                isLoading: false,
                isInitialized: true
            });
        },

        logout() {
            this.clearAuth();
        }
    };
}

export const authStore = createAuthStore();

// Derived stores
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const currentUser = derived(authStore, $auth => $auth.user);
export const userRole = derived(authStore, $auth => $auth.user?.role || 'guest');
export const isLoading = derived(authStore, $auth => $auth.isLoading);
export const isInitialized = derived(authStore, $auth => $auth.isInitialized);
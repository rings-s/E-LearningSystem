import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';
import { goto } from '$app/navigation';

// Auth store with better state management
function createAuthStore() {
    const initialState = {
        user: null,
        token: null,
        refreshToken: null,
        isLoading: true,
        isAuthenticated: false,
        loginAttempts: 0,
        lastLoginAttempt: null
    };

    const { subscribe, set, update } = writable(initialState);

    let currentState = initialState;
    
    // Subscribe to state changes to keep currentState updated
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
                    this.setAuthData({
                        user: userData.data || userData,
                        token,
                        refreshToken,
                        isAuthenticated: true,
                        isLoading: false
                    });
                } catch (error) {
                    console.warn('Token validation failed:', error);
                    this.logout();
                }
            } else {
                update(state => ({ ...state, isLoading: false }));
            }
        },

        setAuthData(authData) {
            update(state => ({ ...state, ...authData, loginAttempts: 0 }));
        },

        async login(credentials) {
            // Rate limiting check
            const now = Date.now();
            
            if (currentState.loginAttempts >= 5 && now - currentState.lastLoginAttempt < 15 * 60 * 1000) {
                return { 
                    success: false, 
                    error: 'Too many login attempts. Please wait 15 minutes.' 
                };
            }

            try {
                update(state => ({ 
                    ...state, 
                    lastLoginAttempt: now,
                    loginAttempts: state.loginAttempts + 1 
                }));

                const response = await authApi.login(credentials);
                const { access, refresh, user } = response;
                
                if (browser) {
                    localStorage.setItem('access_token', access);
                    localStorage.setItem('refresh_token', refresh);
                }
                
                this.setAuthData({
                    user,
                    token: access,
                    refreshToken: refresh,
                    isAuthenticated: true,
                    isLoading: false
                });
                
                return { success: true, user };
            } catch (error) {
                return { 
                    success: false, 
                    error: this.parseError(error) 
                };
            }
        },

        async register(userData) {
            try {
                const response = await authApi.register(userData);
                return { success: true, data: response };
            } catch (error) {
                return { 
                    success: false, 
                    error: this.parseError(error) 
                };
            }
        },

        async verifyEmail(email, code) {
            try {
                const response = await authApi.verifyEmail({ email, verification_code: code });
                
                if (response.tokens) {
                    if (browser) {
                        localStorage.setItem('access_token', response.tokens.access);
                        localStorage.setItem('refresh_token', response.tokens.refresh);
                    }
                    
                    this.setAuthData({
                        user: response.user,
                        token: response.tokens.access,
                        refreshToken: response.tokens.refresh,
                        isAuthenticated: true,
                        isLoading: false
                    });
                }
                
                return { success: true, user: response.user };
            } catch (error) {
                return { 
                    success: false, 
                    error: this.parseError(error) 
                };
            }
        },

        async resendVerification(email) {
            try {
                const response = await authApi.resendVerification(email);
                return { success: true, data: response };
            } catch (error) {
                return { 
                    success: false, 
                    error: this.parseError(error) 
                };
            }
        },

        async refreshToken() {
            if (!currentState.refreshToken) {
                this.logout();
                return null;
            }

            try {
                const response = await authApi.refreshToken(currentState.refreshToken);
                if (browser) {
                    localStorage.setItem('access_token', response.access);
                }
                
                update(s => ({ ...s, token: response.access }));
                return response.access;
            } catch (error) {
                this.logout();
                throw error;
            }
        },

        logout() {
            if (browser) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
            
            set({ ...initialState, isLoading: false });
            
            if (browser) {
                goto('/login');
            }
        },

        parseError(error) {
            if (error.response?.data?.error) {
                const errors = error.response.data.error;
                if (typeof errors === 'object') {
                    const firstError = Object.values(errors)[0];
                    return Array.isArray(firstError) ? firstError[0] : firstError;
                }
                return errors;
            }
            return error.message || 'An unexpected error occurred';
        },

        getState() {
            return currentState;
        }
    };
}

export const authStore = createAuthStore();

// Derived stores
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const currentUser = derived(authStore, $auth => $auth.user);
export const userRole = derived(authStore, $auth => $auth.user?.role || 'guest');
export const isLoading = derived(authStore, $auth => $auth.isLoading);
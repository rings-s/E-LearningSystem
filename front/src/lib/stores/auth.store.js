// front/src/lib/stores/auth.store.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';

function createAuthStore() {
    const { subscribe, set, update } = writable({
        user: null,
        token: null,
        refreshToken: null,
        isLoading: false,
        isInitialized: false
    });

    return {
        subscribe,
        
        async init() {
            if (!browser) return;
            
            update(state => ({ ...state, isLoading: true }));
            
            try {
                const storedToken = localStorage.getItem('access_token');
                const storedRefreshToken = localStorage.getItem('refresh_token');
                
                if (storedToken && storedRefreshToken) {
                    try {
                        const response = await authApi.getCurrentUser();
                        const userData = response.data || response;
                        
                        set({
                            user: userData,
                            token: storedToken,
                            refreshToken: storedRefreshToken,
                            isLoading: false,
                            isInitialized: true
                        });
                    } catch (error) {
                        console.error('Token validation failed:', error);
                        this.clearAuth();
                    }
                } else {
                    update(state => ({ 
                        ...state, 
                        isLoading: false, 
                        isInitialized: true 
                    }));
                }
            } catch (error) {
                console.error('Auth initialization error:', error);
                this.clearAuth();
            }
        },

        async login(credentials) {
            update(state => ({ ...state, isLoading: true }));
            
            try {
                const response = await authApi.login(credentials);
                
                // Handle different response structures
                let access, refresh, user;
                
                if (response.tokens && response.user) {
                    access = response.tokens.access;
                    refresh = response.tokens.refresh;
                    user = response.user;
                } else if (response.access && response.user) {
                    access = response.access;
                    refresh = response.refresh;
                    user = response.user;
                } else {
                    access = response.access;
                    refresh = response.refresh;
                    user = response.user;
                }
                
                if (access && user) {
                    this.setAuth({ access, refresh }, user);
                    return { success: true, user };
                } else {
                    update(state => ({ ...state, isLoading: false }));
                    return { success: false, error: 'Invalid response format' };
                }
            } catch (error) {
                console.error('Login error:', error);
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
                console.error('Registration error:', error);
                update(state => ({ ...state, isLoading: false }));
                return { success: false, error: error.message || 'Registration failed' };
            }
        },

        async verifyEmail(email, code) {
            update(state => ({ ...state, isLoading: true }));
            
            try {
                const response = await authApi.verifyEmail({ email, verification_code: code });
                
                let access, refresh, user;
                
                if (response.tokens && response.user) {
                    access = response.tokens.access;
                    refresh = response.tokens.refresh;
                    user = response.user;
                } else {
                    access = response.access;
                    refresh = response.refresh;
                    user = response.user;
                }
                
                if (access && user) {
                    this.setAuth({ access, refresh }, user);
                    return { success: true, user };
                } else {
                    update(state => ({ ...state, isLoading: false }));
                    return { success: false, error: 'Invalid response format' };
                }
            } catch (error) {
                console.error('Email verification error:', error);
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
                console.error('Resend verification error:', error);
                update(state => ({ ...state, isLoading: false }));
                return { success: false, error: error.message || 'Failed to resend verification' };
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

        setAuth(tokens, user) {
            set({
                user,
                token: tokens.access,
                refreshToken: tokens.refresh,
                isLoading: false,
                isInitialized: true
            });
            
            if (browser) {
                localStorage.setItem('access_token', tokens.access);
                localStorage.setItem('refresh_token', tokens.refresh);
            }
        },

        clearAuth() {
            set({
                user: null,
                token: null,
                refreshToken: null,
                isLoading: false,
                isInitialized: true
            });
            
            if (browser) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
        },

        logout() {
            this.clearAuth();
        }
    };
}

export const authStore = createAuthStore();

// Export derived stores for reactive values
export const isAuthenticated = derived(authStore, $auth => !!$auth.token && !!$auth.user);
export const currentUser = derived(authStore, $auth => $auth.user);
export const userRole = derived(authStore, $auth => $auth.user?.role || null);
export const isLoading = derived(authStore, $auth => $auth.isLoading);
export const isInitialized = derived(authStore, $auth => $auth.isInitialized);
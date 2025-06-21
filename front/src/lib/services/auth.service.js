// front/src/lib/services/auth.service.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';
import { goto } from '$app/navigation';

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
                        isLoading: false
                    }));
                } catch (error) {
                    console.warn('Token validation failed:', error);
                    this.logout(false); // Don't redirect on init failure
                }
            } else {
                update(state => ({ ...state, isLoading: false }));
            }
        },

        setAuthData(authData) {
            update(state => ({ ...state, ...authData, loginAttempts: 0 }));
        },

        async login(credentials) {
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

        logout(redirect = true) {
            if (browser) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
            
            set({ ...initialState, isLoading: false });
            
            if (browser && redirect) {
                goto('/login');
            }
        },

        // ... rest of the methods remain the same
    };
}

export const authStore = createAuthStore();
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const currentUser = derived(authStore, $auth => $auth.user);
export const userRole = derived(authStore, $auth => $auth.user?.role || 'guest');
export const isLoading = derived(authStore, $auth => $auth.isLoading);
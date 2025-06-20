// front/src/lib/stores/auth.store.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';

function createAuthStore() {
    const { subscribe, set, update } = writable({
        user: null,
        token: null,
        refreshToken: null,
        isLoading: true,
        isAuthenticated: false
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
                    this.logout();
                }
            } else {
                update(state => ({ ...state, isLoading: false }));
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
                
                set({
                    user,
                    token: access,
                    refreshToken: refresh,
                    isAuthenticated: true,
                    isLoading: false
                });
                
                return { success: true, user };
            } catch (error) {
                return { success: false, error: error.message };
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

        logout() {
            if (browser) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
            set({
                user: null,
                token: null,
                refreshToken: null,
                isAuthenticated: false,
                isLoading: false
            });
        }
    };
}

export const authStore = createAuthStore();

// Derived stores
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const currentUser = derived(authStore, $auth => $auth.user);
export const userRole = derived(authStore, $auth => $auth.user?.role || 'guest');
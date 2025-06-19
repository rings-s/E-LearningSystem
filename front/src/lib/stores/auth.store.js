// front/src/lib/stores/user.store.js
import { writable, derived } from 'svelte/store';
import { authApi } from '../apis/auth.js';
import { authService } from '../services/auth.service.js';

function createUserStore() {
    const { subscribe, set, update } = writable({
        profile: null,
        preferences: {
            language: 'en',
            theme: 'light',
            notifications: {
                email: true,
                push: true,
                sms: false
            },
            privacy: {
                showProfile: true,
                showActivity: true,
                showProgress: true
            }
        },
        stats: {
            coursesEnrolled: 0,
            coursesCompleted: 0,
            totalStudyHours: 0,
            certificatesEarned: 0,
            currentStreak: 0,
            longestStreak: 0
        },
        achievements: [],
        loading: false,
        error: null
    });

    return {
        subscribe,
        
        async loadProfile() {
            update(state => ({ ...state, loading: true, error: null }));
            
            try {
                const user = await authService.getCurrentUser();
                update(state => ({
                    ...state,
                    profile: user,
                    loading: false
                }));
                
                // Load preferences from localStorage
                this.loadPreferences();
                
                return user;
            } catch (error) {
                update(state => ({
                    ...state,
                    loading: false,
                    error: error.message
                }));
                throw error;
            }
        },

        async updateProfile(data) {
            update(state => ({ ...state, loading: true, error: null }));
            
            try {
                const result = await authService.updateProfile(data);
                if (result.success) {
                    update(state => ({
                        ...state,
                        profile: { ...state.profile, ...result.user },
                        loading: false
                    }));
                }
                return result;
            } catch (error) {
                update(state => ({
                    ...state,
                    loading: false,
                    error: error.message
                }));
                throw error;
            }
        },

        async uploadAvatar(file) {
            try {
                const response = await authApi.uploadAvatar(file);
                update(state => ({
                    ...state,
                    profile: {
                        ...state.profile,
                        avatar: response.avatar
                    }
                }));
                return { success: true };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        updatePreferences(preferences) {
            update(state => {
                const newState = {
                    ...state,
                    preferences: {
                        ...state.preferences,
                        ...preferences
                    }
                };
                
                // Save to localStorage
                if (typeof window !== 'undefined') {
                    localStorage.setItem('user_preferences', 
                        JSON.stringify(newState.preferences)
                    );
                }
                
                return newState;
            });
        },

        loadPreferences() {
            if (typeof window === 'undefined') return;
            
            const saved = localStorage.getItem('user_preferences');
            if (saved) {
                try {
                    const preferences = JSON.parse(saved);
                    update(state => ({
                        ...state,
                        preferences: {
                            ...state.preferences,
                            ...preferences
                        }
                    }));
                } catch (error) {
                    console.error('Failed to load preferences:', error);
                }
            }
        },

        updateStats(stats) {
            update(state => ({
                ...state,
                stats: {
                    ...state.stats,
                    ...stats
                }
            }));
        },

        addAchievement(achievement) {
            update(state => ({
                ...state,
                achievements: [...state.achievements, achievement]
            }));
        },

        reset() {
            set({
                profile: null,
                preferences: {
                    language: 'en',
                    theme: 'light',
                    notifications: {
                        email: true,
                        push: true,
                        sms: false
                    },
                    privacy: {
                        showProfile: true,
                        showActivity: true,
                        showProgress: true
                    }
                },
                stats: {
                    coursesEnrolled: 0,
                    coursesCompleted: 0,
                    totalStudyHours: 0,
                    certificatesEarned: 0,
                    currentStreak: 0,
                    longestStreak: 0
                },
                achievements: [],
                loading: false,
                error: null
            });
        }
    };
}

export const userStore = createUserStore();

// Derived stores
export const userProfile = derived(userStore, $user => $user.profile);
export const userPreferences = derived(userStore, $user => $user.preferences);
export const userStats = derived(userStore, $user => $user.stats);
export const userAchievements = derived(userStore, $user => $user.achievements);
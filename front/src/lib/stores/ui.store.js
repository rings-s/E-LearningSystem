// front/src/lib/stores/ui.store.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

function createUIStore() {
    const { subscribe, set, update } = writable({
        theme: 'light',
        sidebarOpen: true,
        mobileMenuOpen: false,
        language: 'en',
        loading: false,
        notifications: []
    });

    return {
        subscribe,

        init() {
            if (!browser) return;
            
            const savedTheme = localStorage.getItem('theme') || 'light';
            const savedLanguage = localStorage.getItem('language') || 'en';
            const savedSidebarState = localStorage.getItem('sidebarOpen') !== 'false';
            
            update(state => ({
                ...state,
                theme: savedTheme,
                language: savedLanguage,
                sidebarOpen: window.innerWidth > 768 ? savedSidebarState : false
            }));
            
            // Apply theme to document
            document.documentElement.classList.toggle('dark', savedTheme === 'dark');
            document.documentElement.lang = savedLanguage;
            document.documentElement.dir = savedLanguage === 'ar' ? 'rtl' : 'ltr';
        },

        toggleTheme() {
            update(state => {
                const newTheme = state.theme === 'light' ? 'dark' : 'light';
                if (browser) {
                    localStorage.setItem('theme', newTheme);
                    document.documentElement.classList.toggle('dark', newTheme === 'dark');
                }
                return { ...state, theme: newTheme };
            });
        },

        setLanguage(lang) {
            update(state => {
                if (browser) {
                    localStorage.setItem('language', lang);
                    document.documentElement.lang = lang;
                    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
                }
                return { ...state, language: lang };
            });
        },

        toggleSidebar() {
            update(state => {
                const newState = !state.sidebarOpen;
                if (browser) {
                    localStorage.setItem('sidebarOpen', newState);
                }
                return { ...state, sidebarOpen: newState };
            });
        },

        toggleMobileMenu() {
            update(state => ({ ...state, mobileMenuOpen: !state.mobileMenuOpen }));
        },

        setLoading(loading) {
            update(state => ({ ...state, loading }));
        },

        showNotification(notification) {
            const id = Date.now();
            update(state => ({
                ...state,
                notifications: [...state.notifications, { ...notification, id }]
            }));
            
            // Auto remove after duration
            if (notification.duration !== 0) {
                setTimeout(() => {
                    this.removeNotification(id);
                }, notification.duration || 5000);
            }
        },

        removeNotification(id) {
            update(state => ({
                ...state,
                notifications: state.notifications.filter(n => n.id !== id)
            }));
        }
    };
}

export const uiStore = createUIStore();

// Derived stores
export const theme = derived(uiStore, $ui => $ui.theme);
export const language = derived(uiStore, $ui => $ui.language);
export const isRTL = derived(uiStore, $ui => $ui.language === 'ar');
export const loading = derived(uiStore, $ui => $ui.loading);
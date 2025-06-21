// front/src/lib/i18n/index.js
import { derived, writable } from 'svelte/store';
import { browser } from '$app/environment';
import en from './en.js';
import ar from './ar.js';
import { languages, defaultLanguage } from './config.js';

const translations = { en, ar };

function createI18n() {
    const locale = writable(defaultLanguage);
    
    const t = derived(locale, ($locale) => {
        const translation = translations[$locale] || translations[defaultLanguage];
        
        return (key, params = {}) => {
            let text = key.split('.').reduce((obj, k) => obj?.[k], translation) || key;
            
            // Replace parameters
            Object.keys(params).forEach(param => {
                text = text.replace(new RegExp(`{${param}}`, 'g'), params[param]);
            });
            
            return text;
        };
    });

    // Initialize from localStorage
    if (browser) {
        const savedLocale = localStorage.getItem('language') || defaultLanguage;
        locale.set(savedLocale);
        const lang = languages[savedLocale];
        if (lang) {
            document.documentElement.lang = lang.code;
            document.documentElement.dir = lang.dir;
        }
    }

    return {
        locale,
        t,
        setLocale: (newLocale) => {
            if (translations[newLocale]) {
                locale.set(newLocale);
                const lang = languages[newLocale];
                if (browser && lang) {
                    localStorage.setItem('language', newLocale);
                    document.documentElement.lang = lang.code;
                    document.documentElement.dir = lang.dir;
                }
            }
        },
        languages
    };
}

export const { locale, t, setLocale, languages: availableLanguages } = createI18n();
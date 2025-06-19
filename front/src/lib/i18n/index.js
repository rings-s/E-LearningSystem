// front/src/lib/i18n/index.js
import { derived, writable } from 'svelte/store';
import { browser } from '$app/environment';
import en from './en.js';
import ar from './ar.js';

const translations = {
    en,
    ar
};

function createI18n() {
    const locale = writable('en');
    
    const translate = derived(locale, ($locale) => {
        const translation = translations[$locale] || translations.en;
        
        return (key, params = {}) => {
            let text = key.split('.').reduce((obj, k) => obj?.[k], translation) || key;
            
            // Replace parameters
            Object.keys(params).forEach(param => {
                text = text.replace(`{${param}}`, params[param]);
            });
            
            return text;
        };
    });

    return {
        locale,
        t: translate,
        setLocale: (newLocale) => {
            if (translations[newLocale]) {
                locale.set(newLocale);
                if (browser) {
                    localStorage.setItem('language', newLocale);
                    document.documentElement.lang = newLocale;
                    document.documentElement.dir = newLocale === 'ar' ? 'rtl' : 'ltr';
                }
            }
        }
    };
}

export const { locale, t, setLocale } = createI18n();
// front/src/lib/utils/helpers.js
import { browser } from '$app/environment';

export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

export function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

export function getInitials(name) {
    if (!name) return '';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function generateColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 50%)`;
}

export function classNames(...classes) {
    return classes.filter(Boolean).join(' ');
}

export function focusTrap(node) {
    const focusableElements = node.querySelectorAll(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    );
    const firstFocusableElement = focusableElements[0];
    const lastFocusableElement = focusableElements[focusableElements.length - 1];

    function handleKeydown(e) {
        if (e.key !== 'Tab') return;

        if (e.shiftKey) {
            if (document.activeElement === firstFocusableElement) {
                lastFocusableElement.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastFocusableElement) {
                firstFocusableElement.focus();
                e.preventDefault();
            }
        }
    }

    node.addEventListener('keydown', handleKeydown);
    firstFocusableElement?.focus();

    return {
        destroy() {
            node.removeEventListener('keydown', handleKeydown);
        }
    };
}

export function clickOutside(node, callback) {
    function handleClick(e) {
        if (!node.contains(e.target)) {
            callback();
        }
    }

    document.addEventListener('click', handleClick, true);

    return {
        destroy() {
            document.removeEventListener('click', handleClick, true);
        }
    };
}

export function portal(node, target = 'body') {
    let targetEl;
    
    if (typeof target === 'string') {
        targetEl = document.querySelector(target);
        if (!targetEl) {
            throw new Error(`Target element "${target}" not found`);
        }
    } else {
        targetEl = target;
    }

    targetEl.appendChild(node);

    return {
        destroy() {
            node.parentElement?.removeChild(node);
        }
    };
}

export function scrollLock(shouldLock = true) {
    if (!browser) return;
    
    const body = document.body;
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    
    if (shouldLock) {
        body.style.overflow = 'hidden';
        body.style.paddingRight = `${scrollbarWidth}px`;
    } else {
        body.style.overflow = '';
        body.style.paddingRight = '';
    }
}

export function getErrorMessage(error) {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    if (error?.error?.message) return error.error.message;
    if (error?.error) return error.error;
    return 'An unexpected error occurred';
}

export function downloadFile(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'download';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

export function copyToClipboard(text) {
    if (!browser) return Promise.reject();
    
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text);
    }
    
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return Promise.resolve();
    } catch (err) {
        document.body.removeChild(textarea);
        return Promise.reject(err);
    }
}
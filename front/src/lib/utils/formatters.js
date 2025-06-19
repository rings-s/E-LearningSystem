// front/src/lib/utils/formatters.js
export const formatters = {
    date(date, locale = 'en') {
        if (!date) return '';
        const d = new Date(date);
        return new Intl.DateTimeFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(d);
    },

    dateTime(date, locale = 'en') {
        if (!date) return '';
        const d = new Date(date);
        return new Intl.DateTimeFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(d);
    },

    time(date, locale = 'en') {
        if (!date) return '';
        const d = new Date(date);
        return new Intl.DateTimeFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(d);
    },

    relativeTime(date, locale = 'en') {
        if (!date) return '';
        const d = new Date(date);
        const now = new Date();
        const diff = now - d;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        const rtf = new Intl.RelativeTimeFormat(locale === 'ar' ? 'ar' : 'en', { 
            numeric: 'auto' 
        });
        
        if (days > 0) return rtf.format(-days, 'day');
        if (hours > 0) return rtf.format(-hours, 'hour');
        if (minutes > 0) return rtf.format(-minutes, 'minute');
        return rtf.format(-seconds, 'second');
    },

    number(value, locale = 'en') {
        if (value === null || value === undefined) return '';
        return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US').format(value);
    },

    percent(value, locale = 'en') {
        if (value === null || value === undefined) return '';
        return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
            style: 'percent',
            minimumFractionDigits: 0,
            maximumFractionDigits: 1
        }).format(value / 100);
    },

    duration(seconds) {
        if (!seconds) return '0m';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
    },

    fileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    },

    truncate(text, length = 100) {
        if (!text || text.length <= length) return text;
        return text.substring(0, length) + '...';
    }
};
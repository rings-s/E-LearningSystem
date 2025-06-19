// front/src/lib/services/notification.service.js
import { coreApi } from '../apis/core.js';
import { browser } from '$app/environment';

class NotificationService {
    constructor() {
        this.subscribers = new Set();
        this.unreadCount = 0;
        this.notifications = [];
        this.wsConnection = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    // WebSocket Management
    async connect(userId) {
        if (!browser || this.wsConnection) return;

        const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/notifications/`;
        
        try {
            this.wsConnection = new WebSocket(wsUrl);
            
            this.wsConnection.onopen = () => {
                console.log('Notification WebSocket connected');
                this.reconnectAttempts = 0;
                this.authenticate(userId);
            };

            this.wsConnection.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.wsConnection.onclose = () => {
                this.wsConnection = null;
                this.attemptReconnect(userId);
            };
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
        }
    }

    authenticate(userId) {
        if (this.wsConnection?.readyState === WebSocket.OPEN) {
            this.wsConnection.send(JSON.stringify({
                type: 'authenticate',
                user_id: userId
            }));
        }
    }

    disconnect() {
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
        }
    }

    attemptReconnect(userId) {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        
        setTimeout(() => {
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            this.connect(userId);
        }, delay);
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'notification':
                this.addNotification(data.notification);
                break;
            case 'notification_read':
                this.markAsRead(data.notification_id);
                break;
            case 'bulk_read':
                this.markAllAsRead();
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }

    // Notification Management
    async fetchNotifications(params = {}) {
        try {
            const response = await coreApi.getNotifications(params);
            const notifications = response.results || response;
            
            this.notifications = notifications;
            this.updateUnreadCount();
            this.notifySubscribers();
            
            return notifications;
        } catch (error) {
            console.error('Failed to fetch notifications:', error);
            throw error;
        }
    }

    async fetchUnreadCount() {
        try {
            const response = await coreApi.getUnreadCount();
            this.unreadCount = response.unread_count;
            this.notifySubscribers();
            return this.unreadCount;
        } catch (error) {
            console.error('Failed to fetch unread count:', error);
            return 0;
        }
    }

    addNotification(notification) {
        // Add to beginning of array
        this.notifications.unshift(notification);
        
        // Update unread count
        if (!notification.is_read) {
            this.unreadCount++;
        }
        
        // Show browser notification if permitted
        this.showBrowserNotification(notification);
        
        // Notify subscribers
        this.notifySubscribers();
        
        // Play notification sound
        this.playNotificationSound();
    }

    async markAsRead(notificationId) {
        try {
            await coreApi.markNotificationRead(notificationId);
            
            // Update local state
            const notification = this.notifications.find(n => n.uuid === notificationId);
            if (notification && !notification.is_read) {
                notification.is_read = true;
                notification.read_at = new Date().toISOString();
                this.unreadCount = Math.max(0, this.unreadCount - 1);
                this.notifySubscribers();
            }
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
            throw error;
        }
    }

    async markAllAsRead() {
        try {
            await coreApi.markAllNotificationsRead();
            
            // Update local state
            this.notifications.forEach(notification => {
                if (!notification.is_read) {
                    notification.is_read = true;
                    notification.read_at = new Date().toISOString();
                }
            });
            
            this.unreadCount = 0;
            this.notifySubscribers();
        } catch (error) {
            console.error('Failed to mark all as read:', error);
            throw error;
        }
    }

    // Browser Notifications
    async requestPermission() {
        if (!browser || !('Notification' in window)) {
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }

        return false;
    }

    showBrowserNotification(notification) {
        if (!browser || Notification.permission !== 'granted') {
            return;
        }

        const options = {
            body: notification.message,
            icon: '/icon-192.png',
            badge: '/badge-72.png',
            tag: notification.uuid,
            renotify: true,
            requireInteraction: false,
            data: {
                url: notification.action_url || '/'
            }
        };

        const browserNotification = new Notification(notification.title, options);
        
        browserNotification.onclick = (event) => {
            event.preventDefault();
            window.focus();
            window.location.href = event.target.data.url;
            browserNotification.close();
        };

        // Auto close after 5 seconds
        setTimeout(() => browserNotification.close(), 5000);
    }

    playNotificationSound() {
        if (!browser || !this.shouldPlaySound()) return;

        try {
            const audio = new Audio('/sounds/notification.mp3');
            audio.volume = 0.5;
            audio.play().catch(error => {
                console.log('Failed to play notification sound:', error);
            });
        } catch (error) {
            console.log('Failed to play notification sound:', error);
        }
    }

    shouldPlaySound() {
        // Check user preferences
        const preferences = this.getNotificationPreferences();
        return preferences.soundEnabled !== false;
    }

    // Preferences Management
    getNotificationPreferences() {
        if (!browser) return {};
        
        const stored = localStorage.getItem('notification_preferences');
        return stored ? JSON.parse(stored) : {
            soundEnabled: true,
            desktopEnabled: true,
            emailEnabled: true,
            types: {
                enrollment: true,
                course_update: true,
                lesson_available: true,
                assignment_due: true,
                quiz_result: true,
                certificate_ready: true,
                forum_reply: true,
                announcement: true,
                system: true
            }
        };
    }

    setNotificationPreferences(preferences) {
        if (!browser) return;
        
        localStorage.setItem('notification_preferences', JSON.stringify(preferences));
        this.notifySubscribers();
    }

    shouldShowNotificationType(type) {
        const preferences = this.getNotificationPreferences();
        return preferences.types?.[type] !== false;
    }

    // Filtering and Grouping
    getFilteredNotifications(filter = 'all') {
        let filtered = [...this.notifications];

        switch (filter) {
            case 'unread':
                filtered = filtered.filter(n => !n.is_read);
                break;
            case 'course':
                filtered = filtered.filter(n => n.course);
                break;
            case 'system':
                filtered = filtered.filter(n => n.notification_type === 'system');
                break;
            // Add more filters as needed
        }

        // Filter by enabled types
        filtered = filtered.filter(n => 
            this.shouldShowNotificationType(n.notification_type)
        );

        return filtered;
    }

    groupNotificationsByDate() {
        const groups = {
            today: [],
            yesterday: [],
            thisWeek: [],
            thisMonth: [],
            older: []
        };

        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        const monthAgo = new Date(today);
        monthAgo.setMonth(monthAgo.getMonth() - 1);

        this.notifications.forEach(notification => {
            const date = new Date(notification.created_at);
            
            if (date >= today) {
                groups.today.push(notification);
            } else if (date >= yesterday) {
                groups.yesterday.push(notification);
            } else if (date >= weekAgo) {
                groups.thisWeek.push(notification);
            } else if (date >= monthAgo) {
                groups.thisMonth.push(notification);
            } else {
                groups.older.push(notification);
            }
        });

        return groups;
    }

    // Subscription Management
    subscribe(callback) {
        this.subscribers.add(callback);
        
        // Return unsubscribe function
        return () => {
            this.subscribers.delete(callback);
        };
    }

    notifySubscribers() {
        const state = {
            notifications: this.notifications,
            unreadCount: this.unreadCount,
            preferences: this.getNotificationPreferences()
        };

        this.subscribers.forEach(callback => {
            try {
                callback(state);
            } catch (error) {
                console.error('Notification subscriber error:', error);
            }
        });
    }

    // Utility Methods
    updateUnreadCount() {
        this.unreadCount = this.notifications.filter(n => !n.is_read).length;
    }

    clearAll() {
        this.notifications = [];
        this.unreadCount = 0;
        this.notifySubscribers();
    }

    getNotificationIcon(type) {
        const icons = {
            enrollment: '📚',
            course_update: '🔄',
            lesson_available: '📖',
            assignment_due: '📝',
            quiz_result: '✅',
            certificate_ready: '🎓',
            forum_reply: '💬',
            announcement: '📢',
            system: '⚙️'
        };
        return icons[type] || '🔔';
    }

    getNotificationColor(type) {
        const colors = {
            enrollment: 'primary',
            course_update: 'info',
            lesson_available: 'success',
            assignment_due: 'warning',
            quiz_result: 'primary',
            certificate_ready: 'success',
            forum_reply: 'info',
            announcement: 'primary',
            system: 'default'
        };
        return colors[type] || 'default';
    }

    formatNotificationTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 7) {
            return date.toLocaleDateString();
        } else if (days > 0) {
            return `${days} day${days > 1 ? 's' : ''} ago`;
        } else if (hours > 0) {
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else if (minutes > 0) {
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else {
            return 'Just now';
        }
    }
}

export const notificationService = new NotificationService();
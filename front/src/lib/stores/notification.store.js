// front/src/lib/stores/notification.store.js
import { writable, derived } from 'svelte/store';
import { notificationService } from '../services/notification.service.js';
import { browser } from '$app/environment';

function createNotificationStore() {
	const { subscribe, set, update } = writable({
		notifications: [],
		unreadCount: 0,
		preferences: {
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
		},
		filter: 'all',
		loading: false,
		error: null,
		wsConnected: false
	});

	// Subscribe to notification service updates
	if (browser) {
		notificationService.subscribe((serviceState) => {
			update((state) => ({
				...state,
				notifications: serviceState.notifications,
				unreadCount: serviceState.unreadCount,
				preferences: serviceState.preferences
			}));
		});
	}

	return {
		subscribe,

		async init(userId) {
			if (!browser) return;

			// Connect WebSocket
			await notificationService.connect(userId);

			// Load initial notifications
			await this.loadNotifications();

			// Request browser notification permission
			await notificationService.requestPermission();

			update((state) => ({ ...state, wsConnected: true }));
		},

		async loadNotifications(params = {}) {
			update((state) => ({ ...state, loading: true, error: null }));

			try {
				const notifications = await notificationService.fetchNotifications(params);
				update((state) => ({
					...state,
					loading: false
				}));
				return notifications;
			} catch (error) {
				update((state) => ({
					...state,
					loading: false,
					error: error.message
				}));
				throw error;
			}
		},

		async markAsRead(notificationId) {
			try {
				await notificationService.markAsRead(notificationId);
			} catch (error) {
				console.error('Failed to mark notification as read:', error);
			}
		},

		async markAllAsRead() {
			try {
				await notificationService.markAllAsRead();
			} catch (error) {
				console.error('Failed to mark all as read:', error);
			}
		},

		setFilter(filter) {
			update((state) => ({ ...state, filter }));
		},

		updatePreferences(preferences) {
			notificationService.setNotificationPreferences(preferences);
			update((state) => ({
				...state,
				preferences: {
					...state.preferences,
					...preferences
				}
			}));
		},

		toggleNotificationType(type) {
			update((state) => {
				const newState = {
					...state,
					preferences: {
						...state.preferences,
						types: {
							...state.preferences.types,
							[type]: !state.preferences.types[type]
						}
					}
				};

				notificationService.setNotificationPreferences(newState.preferences);
				return newState;
			});
		},

		disconnect() {
			notificationService.disconnect();
			update((state) => ({ ...state, wsConnected: false }));
		},

		clearAll() {
			notificationService.clearAll();
		},

		reset() {
			this.disconnect();
			set({
				notifications: [],
				unreadCount: 0,
				preferences: {
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
				},
				filter: 'all',
				loading: false,
				error: null,
				wsConnected: false
			});
		}
	};
}

export const notificationStore = createNotificationStore();

// Derived stores
export const notifications = derived(notificationStore, ($store) => {
	const filtered = notificationService.getFilteredNotifications($store.filter);
	return filtered;
});

export const unreadCount = derived(notificationStore, ($store) => $store.unreadCount);

export const groupedNotifications = derived(notifications, ($notifications) =>
	notificationService.groupNotificationsByDate()
);

export const hasUnread = derived(unreadCount, ($count) => $count > 0);

export const notificationPreferences = derived(notificationStore, ($store) => $store.preferences);

export const isConnected = derived(notificationStore, ($store) => $store.wsConnected);

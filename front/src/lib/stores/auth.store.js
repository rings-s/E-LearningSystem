// front/src/lib/stores/auth.store.js - Enhanced with better session persistence
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';

function createAuthStore() {
	const { subscribe, set, update } = writable({
		user: null,
		isLoading: false,
		isInitialized: false
	});

	let refreshTimer = null;

	function getToken() {
		if (!browser) return null;
		return localStorage.getItem('access_token');
	}

	function getRefreshToken() {
		if (!browser) return null;
		return localStorage.getItem('refresh_token');
	}

	function setTokens(accessToken, refreshToken) {
		if (!browser) return;
		
		if (accessToken) {
			localStorage.setItem('access_token', accessToken);
			// Schedule token refresh
			scheduleTokenRefresh(accessToken);
		}
		if (refreshToken) {
			localStorage.setItem('refresh_token', refreshToken);
		}
	}

	function clearTokens() {
		if (!browser) return;
		localStorage.removeItem('access_token');
		localStorage.removeItem('refresh_token');
		clearTokenRefreshTimer();
	}

	function parseJWTPayload(token) {
		try {
			const base64Url = token.split('.')[1];
			const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
			const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
				return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
			}).join(''));
			return JSON.parse(jsonPayload);
		} catch {
			return null;
		}
	}

	function scheduleTokenRefresh(token) {
		clearTokenRefreshTimer();
		
		const payload = parseJWTPayload(token);
		if (!payload || !payload.exp) return;
		
		// Refresh 2 minutes before expiry
		const refreshTime = (payload.exp * 1000) - Date.now() - (2 * 60 * 1000);
		
		if (refreshTime > 0) {
			refreshTimer = setTimeout(() => {
				refreshAccessToken();
			}, refreshTime);
		}
	}

	function clearTokenRefreshTimer() {
		if (refreshTimer) {
			clearTimeout(refreshTimer);
			refreshTimer = null;
		}
	}

	async function refreshAccessToken() {
		const refreshToken = getRefreshToken();
		if (!refreshToken) return false;
		
		try {
			const response = await authApi.refreshToken(refreshToken);
			const newAccessToken = response.access;
			
			if (newAccessToken) {
				setTokens(newAccessToken, response.refresh || refreshToken);
				return true;
			}
			return false;
		} catch (error) {
			console.error('Token refresh failed:', error);
			if (error.status === 401 || error.status === 403) {
				// Refresh token is invalid, need to re-login
				logout();
			}
			return false;
		}
	}

	// Enhanced API call wrapper with automatic retry
	async function makeAuthenticatedRequest(apiCall, retryCount = 0) {
		try {
			return await apiCall();
		} catch (error) {
			if (error.status === 401 && retryCount === 0) {
				const refreshed = await refreshAccessToken();
				if (refreshed) {
					return await makeAuthenticatedRequest(apiCall, 1);
				}
			}
			throw error;
		}
	}

	return {
		subscribe,

		async init() {
			if (!browser) return;

			update((state) => ({ ...state, isLoading: true }));

			try {
				const token = getToken();
				const refreshToken = getRefreshToken();
				
				if (!token || !refreshToken) {
					set({ user: null, isLoading: false, isInitialized: true });
					return;
				}

				// Check if token is expired
				const payload = parseJWTPayload(token);
				const isExpired = payload ? (payload.exp * 1000) < Date.now() : true;
				
				if (isExpired) {
					// Try to refresh token
					const refreshSuccess = await refreshAccessToken();
					if (!refreshSuccess) {
						clearTokens();
						set({ user: null, isLoading: false, isInitialized: true });
						return;
					}
				} else {
					// Schedule refresh for valid token
					scheduleTokenRefresh(token);
				}

				// Get current user data
				const userData = await authApi.getCurrentUser();
				
				if (userData && userData.id) {
					set({ user: userData, isLoading: false, isInitialized: true });
				} else {
					clearTokens();
					set({ user: null, isLoading: false, isInitialized: true });
				}
			} catch (error) {
				console.error('Auth initialization failed:', error);
				
				if (error.status === 401 || error.status === 403) {
					clearTokens();
				}
				
				set({ user: null, isLoading: false, isInitialized: true });
			}
		},

		async login(credentials) {
			update((state) => ({ ...state, isLoading: true }));

			try {
				const response = await authApi.login(credentials);
				
				const accessToken = response.tokens?.access || response.access;
				const refreshToken = response.tokens?.refresh || response.refresh;
				const userData = response.user;

				if (accessToken && userData) {
					setTokens(accessToken, refreshToken);
					update((state) => ({ ...state, user: userData, isLoading: false }));
					return { success: true, user: userData };
				} else {
					update((state) => ({ ...state, isLoading: false }));
					return { success: false, error: 'Invalid response format' };
				}
			} catch (error) {
				update((state) => ({ ...state, isLoading: false }));
				return { success: false, error: error.message || 'Login failed' };
			}
		},

		async register(userData) {
			update((state) => ({ ...state, isLoading: true }));

			try {
				const response = await authApi.register(userData);
				update((state) => ({ ...state, isLoading: false }));
				return { success: true, data: response };
			} catch (error) {
				update((state) => ({ ...state, isLoading: false }));
				return { success: false, error: error.message || 'Registration failed' };
			}
		},

		async verifyEmail(email, code) {
			update((state) => ({ ...state, isLoading: true }));

			try {
				const response = await authApi.verifyEmail({ email, verification_code: code });
				
				const accessToken = response.tokens?.access || response.access;
				const refreshToken = response.tokens?.refresh || response.refresh;
				const userData = response.user;

				if (accessToken && userData) {
					setTokens(accessToken, refreshToken);
					update((state) => ({ ...state, user: userData, isLoading: false }));
					return { success: true, user: userData };
				} else {
					update((state) => ({ ...state, isLoading: false }));
					return { success: false, error: 'Invalid response format' };
				}
			} catch (error) {
				update((state) => ({ ...state, isLoading: false }));
				return { success: false, error: error.message || 'Verification failed' };
			}
		},

		async resendVerification(email) {
			update((state) => ({ ...state, isLoading: true }));

			try {
				await authApi.resendVerification(email);
				update((state) => ({ ...state, isLoading: false }));
				return { success: true };
			} catch (error) {
				update((state) => ({ ...state, isLoading: false }));
				return { success: false, error: error.message || 'Failed to resend verification' };
			}
		},

		async updateProfile(profileData) {
			try {
				const response = await makeAuthenticatedRequest(() => 
					authApi.updateProfile(profileData)
				);

				update((state) => ({
					...state,
					user: { ...state.user, ...response }
				}));

				return { success: true, data: response };
			} catch (error) {
				console.error('Profile update error:', error);
				return { success: false, error: error.message || 'Failed to update profile' };
			}
		},

		async logout() {
			try {
				const refreshToken = getRefreshToken();
				if (refreshToken) {
					await authApi.logout({ refresh_token: refreshToken });
				}
			} catch (error) {
				console.error('Logout API call failed:', error);
			} finally {
				clearTokens();
				clearTokenRefreshTimer();
				set({ user: null, isLoading: false, isInitialized: true });
			}
		},

		// Manual token refresh
		async refreshToken() {
			return await refreshAccessToken();
		},

		// API call wrapper with automatic token refresh
		async makeAuthenticatedRequest(apiCall, retryCount = 0) {
			try {
				return await apiCall();
			} catch (error) {
				if (error.status === 401 && retryCount === 0) {
					const refreshed = await refreshAccessToken();
					if (refreshed) {
						return await this.makeAuthenticatedRequest(apiCall, 1);
					}
				}
				throw error;
			}
		}
	};
}

export const authStore = createAuthStore();

// Derived stores
export const isAuthenticated = derived(
	authStore,
	($auth) => {
		if (!$auth.isInitialized) return false;
		
		// Check if we have valid tokens
		const hasValidToken = !!getTokenFromStorage();
		return hasValidToken && !!$auth.user;
	}
);

export const currentUser = derived(authStore, ($auth) => $auth.user);
export const userRole = derived(authStore, ($auth) => $auth.user?.role || null);
export const isLoading = derived(authStore, ($auth) => $auth.isLoading);
export const isInitialized = derived(authStore, ($auth) => $auth.isInitialized);

// Helper function
function getTokenFromStorage() {
	if (!browser) return null;
	return localStorage.getItem('access_token');
}
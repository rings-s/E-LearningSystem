// front/src/lib/stores/auth.store.js - Fix updateProfile method
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '../apis/auth.js';

function createAuthStore() {
	const { subscribe, set, update } = writable({
		user: null,
		isLoading: false,
		isInitialized: false
	});

	function getToken() {
		if (!browser) return null;
		return localStorage.getItem('access_token');
	}

	function setTokens(accessToken, refreshToken) {
		if (!browser) return;
		localStorage.setItem('access_token', accessToken);
		if (refreshToken) {
			localStorage.setItem('refresh_token', refreshToken);
		}
	}

	function clearTokens() {
		if (!browser) return;
		localStorage.removeItem('access_token');
		localStorage.removeItem('refresh_token');
	}

	return {
		subscribe,

		async refreshToken() {
			if (!browser) return false;
			
			const refreshToken = localStorage.getItem('refresh_token');
			if (!refreshToken) return false;
			
			try {
				const response = await authApi.refreshToken(refreshToken);
				const newAccessToken = response.access;
				
				if (newAccessToken) {
					setTokens(newAccessToken, response.refresh);
					return true;
				}
				return false;
			} catch (error) {
				console.error('Token refresh failed:', error);
				// Only clear tokens if refresh specifically failed, not for network errors
				if (error.status === 401 || error.status === 403) {
					clearTokens();
				}
				return false;
			}
		},

		// Wrapper for API calls that handles token refresh automatically
		async makeAuthenticatedRequest(apiCall) {
			try {
				return await apiCall();
			} catch (error) {
				// If we get a 401, try to refresh token and retry once
				if (error.status === 401) {
					console.log('Got 401, attempting token refresh...');
					const refreshed = await this.refreshToken();
					if (refreshed) {
						console.log('Token refreshed successfully, retrying request...');
						try {
							return await apiCall();
						} catch (retryError) {
							// If retry also fails with 401, user needs to re-login
							if (retryError.status === 401) {
								console.log('Retry also failed with 401, logging out user');
								clearTokens();
								update((state) => ({ ...state, user: null }));
							}
							throw retryError;
						}
					} else {
						// Refresh failed, user needs to re-login
						console.log('Token refresh failed, logging out user');
						clearTokens();
						update((state) => ({ ...state, user: null }));
						throw error;
					}
				}
				throw error;
			}
		},

		async init() {
			if (!browser) return;

			update((state) => ({ ...state, isLoading: true }));

			try {
				const token = getToken();
				if (token) {
					// Validate token and get user data with retry logic
					const userData = await this._getCurrentUserWithRetry();
					
					// Ensure we have valid user data
					if (userData && userData.id) {
						set({
							user: userData,
							isLoading: false,
							isInitialized: true
						});
					} else {
						// Invalid user data, clear tokens
						clearTokens();
						set({
							user: null,
							isLoading: false,
							isInitialized: true
						});
					}
				} else {
					set({
						user: null,
						isLoading: false,
						isInitialized: true
					});
				}
			} catch (error) {
				console.error('Auth initialization failed:', error);
				
				// Only clear tokens for genuine authentication errors
				if (error.status === 401 || error.status === 403) {
					console.log('Authentication failed - clearing tokens');
					clearTokens();
				} else {
					// For network errors or other issues, preserve tokens and user state
					console.log('Network error during auth init - preserving session');
				}
				
				set({
					user: null,
					isLoading: false,
					isInitialized: true
				});
			}
		},

		async _getCurrentUserWithRetry(maxRetries = 2) {
			let lastError;
			
			for (let attempt = 0; attempt <= maxRetries; attempt++) {
				try {
					const userData = await authApi.getCurrentUser();
					return userData;
				} catch (error) {
					lastError = error;
					
					// If it's a 401, try to refresh token once
					if (error.status === 401 && attempt === 0) {
						const refreshSuccess = await this.refreshToken();
						if (refreshSuccess) {
							continue; // Retry with new token
						}
					}
					
					// If it's not an auth error, add a small delay before retry
					if (error.status !== 401 && error.status !== 403 && attempt < maxRetries) {
						await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
						continue;
					}
					
					break; // Don't retry for auth errors or after max retries
				}
			}
			
			throw lastError;
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
					update((state) => ({
						...state,
						user: userData,
						isLoading: false
					}));
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
				const response = await authApi.verifyEmail({
					email,
					verification_code: code
				});

				const accessToken = response.tokens?.access || response.access;
				const refreshToken = response.tokens?.refresh || response.refresh;
				const userData = response.user;

				if (accessToken && userData) {
					setTokens(accessToken, refreshToken);
					update((state) => ({
						...state,
						user: userData,
						isLoading: false
					}));
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

		// Fix updateProfile method
		async updateProfile(profileData) {
			try {
				const response = await this.makeAuthenticatedRequest(() => 
					authApi.updateProfile(profileData)
				);

				// Update the user in the store with the new data
				update((state) => ({
					...state,
					user: {
						...state.user,
						...response // Merge the response data
					}
				}));

				return { success: true, data: response };
			} catch (error) {
				console.error('Profile update error:', error);
				return { success: false, error: error.message || 'Failed to update profile' };
			}
		},

		logout() {
			clearTokens();
			set({
				user: null,
				isLoading: false,
				isInitialized: true
			});
		}
	};
}

export const authStore = createAuthStore();

// Derived stores for convenience
export const isAuthenticated = derived(
	authStore,
	($auth) => {
		// Only consider authentication after initialization
		if (!$auth.isInitialized) return false;
		
		// Check if we have a valid token in storage
		const hasToken = !!getTokenFromStorage();
		
		// If no token, definitely not authenticated
		if (!hasToken) return false;
		
		// If we have a token, we're authenticated regardless of user data
		// (user data might be missing due to network issues, but token is still valid)
		return true;
	}
);

export const currentUser = derived(authStore, ($auth) => $auth.user);
export const userRole = derived(authStore, ($auth) => $auth.user?.role || null);
export const isLoading = derived(authStore, ($auth) => $auth.isLoading);
export const isInitialized = derived(authStore, ($auth) => $auth.isInitialized);

// Helper function for isAuthenticated
function getTokenFromStorage() {
	if (!browser) return null;
	return localStorage.getItem('access_token');
}

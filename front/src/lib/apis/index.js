// front/src/lib/apis/index.js
import { browser } from '$app/environment';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
	constructor() {
		this.baseURL = API_BASE_URL;
		this.refreshPromise = null; // Prevent multiple refresh attempts
	}

	getToken() {
		if (!browser) return null;
		return localStorage.getItem('access_token');
	}

	getRefreshToken() {
		if (!browser) return null;
		return localStorage.getItem('refresh_token');
	}

	setTokens(accessToken, refreshToken) {
		if (!browser) return;
		if (accessToken) localStorage.setItem('access_token', accessToken);
		if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
	}

	clearTokens() {
		if (!browser) return;
		localStorage.removeItem('access_token');
		localStorage.removeItem('refresh_token');
	}

	async refreshAccessToken() {
		if (this.refreshPromise) {
			return this.refreshPromise;
		}

		const refreshToken = this.getRefreshToken();
		if (!refreshToken) {
			throw new Error('No refresh token available');
		}

		this.refreshPromise = (async () => {
			try {
				const response = await fetch(`${this.baseURL}/api/accounts/refresh/`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({ refresh: refreshToken })
				});

				if (!response.ok) {
					throw new Error('Failed to refresh token');
				}

				const data = await response.json();
				
				// Handle standardized response format
				const tokenData = data.data || data;
				const newAccessToken = tokenData.access;
				
				if (newAccessToken) {
					this.setTokens(newAccessToken, refreshToken);
					return newAccessToken;
				}
				
				throw new Error('No access token in refresh response');
			} finally {
				this.refreshPromise = null;
			}
		})();

		return this.refreshPromise;
	}

	async request(endpoint, options = {}) {
		const baseURL = this.baseURL || 'http://localhost:8000';
		const cleanEndpoint = String(endpoint || '').trim();
		
		// Construct URL properly
		const url = `${baseURL}${cleanEndpoint.startsWith('/') ? cleanEndpoint : '/' + cleanEndpoint}`;
		
		const token = this.getToken();

		const config = {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options.headers
			}
		};

		// Add auth token if available
		if (token && !options.skipAuth) {
			config.headers.Authorization = `Bearer ${token}`;
		}

		try {
			const response = await fetch(url, config);
			
			// Handle 401 with token refresh
			if (response.status === 401 && !options.skipAuth && !options._isRetry) {
				try {
					await this.refreshAccessToken();
					// Retry the request with new token
					return this.request(endpoint, { ...options, _isRetry: true });
				} catch (refreshError) {
					console.error('Token refresh failed:', refreshError);
					this.clearTokens();
					// Redirect to login or emit auth event
					if (browser && window.dispatchEvent) {
						window.dispatchEvent(new CustomEvent('auth:logout'));
					}
					throw new Error('Authentication failed');
				}
			}
			
			if (!response.ok) {
				let errorData;
				try {
					errorData = await response.json();
				} catch (jsonError) {
					errorData = { message: `HTTP ${response.status} ${response.statusText}` };
				}
				
				// Handle standardized error response
				const error = new Error(
					errorData.message || 
					errorData.error?.message ||
					errorData.errors?.detail?.[0] || 
					errorData.detail || 
					`HTTP ${response.status}`
				);
				error.status = response.status;
				error.data = errorData;
				error.response = { data: errorData, status: response.status };
				throw error;
			}

			const data = await response.json();
			
			// Handle standardized success response format
			if (data.success !== undefined || data.status === 'success') {
				return data.data || data;
			}
			
			// Fallback for direct data responses
			return data;
		} catch (error) {
			if (error.name === 'TypeError' && error.message.includes('fetch')) {
				const networkError = new Error('Network error - please check your connection');
				networkError.isNetworkError = true;
				throw networkError;
			}
			
			// Don't log 401 errors during token refresh
			if (error.status !== 401 || options._isRetry) {
				console.error('API Error:', {
					url,
					method: options.method || 'GET',
					status: error.status,
					message: error.message
				});
			}
			throw error;
		}
	}

	get(endpoint, options = {}) {
		return this.request(endpoint, { ...options, method: 'GET' });
	}

	post(endpoint, data, options = {}) {
		return this.request(endpoint, {
			...options,
			method: 'POST',
			body: JSON.stringify(data)
		});
	}

	patch(endpoint, data, options = {}) {
		return this.request(endpoint, {
			...options,
			method: 'PATCH',
			body: JSON.stringify(data)
		});
	}

	put(endpoint, data, options = {}) {
		return this.request(endpoint, {
			...options,
			method: 'PUT',
			body: JSON.stringify(data)
		});
	}

	delete(endpoint, options = {}) {
		return this.request(endpoint, { ...options, method: 'DELETE' });
	}

	upload(endpoint, formData, options = {}) {
		const config = {
			...options,
			method: 'POST',
			body: formData,
			headers: {
				...options.headers
			}
		};
		// Remove Content-Type for FormData
		delete config.headers['Content-Type'];
		return this.request(endpoint, config);
	}
}

export const api = new ApiClient();
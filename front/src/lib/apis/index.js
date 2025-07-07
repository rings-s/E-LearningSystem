// front/src/lib/apis/index.js
import { browser } from '$app/environment';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
	constructor() {
		this.baseURL = API_BASE_URL;
		console.log('ApiClient Constructor Debug:', {
			API_BASE_URL,
			envValue: import.meta.env.VITE_API_BASE_URL,
			finalBaseURL: this.baseURL,
			baseURLType: typeof this.baseURL,
			rawBaseURL: JSON.stringify(this.baseURL)
		});
	}

	getToken() {
		if (!browser) return null;
		return localStorage.getItem('access_token');
	}

	async request(endpoint, options = {}) {
		// Ensure we have valid base URL and endpoint
		const baseURL = this.baseURL || 'http://localhost:8000';
		const cleanEndpoint = String(endpoint || '').trim();
		
		// Construct URL properly - ensure endpoint starts with /
		const url = `${baseURL}${cleanEndpoint.startsWith('/') ? cleanEndpoint : '/' + cleanEndpoint}`;
		
		console.log('API Request:', { 
			baseURL,
			endpoint: cleanEndpoint,
			constructedURL: url,
			method: options.method || 'GET'
		});
		
		const token = this.getToken();

		const config = {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options.headers
			}
		};

		// Add auth token if available and not explicitly skipped
		if (token && !options.skipAuth) {
			config.headers.Authorization = `Bearer ${token}`;
		}

		try {
			const response = await fetch(url, config);
			
			if (!response.ok) {
				let errorData;
				try {
					errorData = await response.json();
				} catch (jsonError) {
					errorData = { message: `HTTP ${response.status} ${response.statusText}` };
				}
				
				console.error('API Error:', {
					url,
					status: response.status,
					statusText: response.statusText,
					errorData
				});
				
				// Create a structured error with status code and response data
				const error = new Error(errorData.detail || errorData.message || errorData.error?.message || `HTTP ${response.status}`);
				error.status = response.status;
				error.data = errorData;
				error.response = { data: errorData, status: response.status };
				throw error;
			}

			const data = await response.json();
			return data;
		} catch (error) {
			if (error.name === 'TypeError' && error.message.includes('fetch')) {
				console.error('Network Error:', error);
				const networkError = new Error('Network error - please check your connection');
				networkError.isNetworkError = true;
				throw networkError;
			}
			
			// Don't log 401 errors as they're handled by auth store
			if (error.status !== 401) {
				console.error('API Error:', error);
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
				// Don't set Content-Type for FormData
			}
		};
		delete config.headers['Content-Type'];
		return this.request(endpoint, config);
	}
}

export const api = new ApiClient();

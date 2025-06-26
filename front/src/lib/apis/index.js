// front/src/lib/apis/index.js
import { browser } from '$app/environment';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    getToken() {
        if (!browser) return null;
        return localStorage.getItem('access_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = this.getToken();
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            }
        };

        // Add auth token if available and not explicitly skipped
        if (token && !options.skipAuth) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);
            
            // Handle 401 - token expired/invalid
            if (response.status === 401 && browser && !options.skipAuth) {
                // Clear invalid tokens
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                
                // Redirect to login if not already on auth page
                if (!window.location.pathname.includes('/login')) {
                    window.location.href = '/login';
                }
                throw new Error('Unauthorized');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error?.message || data.message || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
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
                ...options.headers,
                // Don't set Content-Type for FormData
            }
        };
        delete config.headers['Content-Type'];
        return this.request(endpoint, config);
    }
}

export const api = new ApiClient();
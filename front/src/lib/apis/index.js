// front/src/lib/apis/index.js
import { browser } from '$app/environment';
import { tokenManager } from '$lib/utils/token.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * @typedef {Object} RequestOptions
 * @property {string} [method]
 * @property {Object<string, string>} [headers]
 * @property {any} [body]
 * @property {boolean} [skipAuth]
 */

class ApiClient {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    /**
     * @param {string} endpoint
     * @param {RequestOptions} [options]
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            }
        };

        // Add auth token if available
        const token = tokenManager.getAccessToken();
        if (token && !options.skipAuth) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401 && browser) {
                // Let the caller handle auth errors
                throw new Error('Unauthorized');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error?.message || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * @param {string} endpoint
     * @param {RequestOptions} [options]
     */
    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    /**
     * @param {string} endpoint
     * @param {any} data
     * @param {RequestOptions} [options]
     */
    post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * @param {string} endpoint
     * @param {any} data
     * @param {RequestOptions} [options]
     */
    put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * @param {string} endpoint
     * @param {any} data
     * @param {RequestOptions} [options]
     */
    patch(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    /**
     * @param {string} endpoint
     * @param {RequestOptions} [options]
     */
    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    /**
     * @param {string} endpoint
     * @param {FormData} formData
     * @param {RequestOptions} [options]
     */
    upload(endpoint, formData, options = {}) {
        const config = {
            ...options,
            method: 'POST',
            body: formData,
            headers: {
                ...options.headers,
                // Don't set Content-Type, let browser set it with boundary
            }
        };
        delete config.headers['Content-Type'];
        return this.request(endpoint, config);
    }
}

export const api = new ApiClient();
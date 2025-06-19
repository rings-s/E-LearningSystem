// front/src/lib/apis/index.js
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { authStore } from '../stores/auth.store.js';
import { get } from 'svelte/store';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const auth = get(authStore);
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            }
        };

        // Add auth token if available
        if (auth.token && !options.skipAuth) {
            config.headers.Authorization = `Bearer ${auth.token}`;
        }

        try {
            const response = await fetch(url, config);
            
            // Handle auth errors
            if (response.status === 401 && browser) {
                authStore.logout();
                goto('/login');
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

    put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
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
                // Don't set Content-Type, let browser set it with boundary
            }
        };
        delete config.headers['Content-Type'];
        return this.request(endpoint, config);
    }
}

export const api = new ApiClient();
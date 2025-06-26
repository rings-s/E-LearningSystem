// front/src/lib/services/auth.service.js
import { authStore, currentUser, isAuthenticated, userRole, isLoading, isInitialized } from '$lib/stores/auth.store.js';

// Re-export store values for backward compatibility
export { authStore, currentUser, isAuthenticated, userRole, isLoading, isInitialized };

// You can add additional service functions here if needed
export const authService = {
  async login(credentials) {
    return authStore.login(credentials);
  },
  
  async register(userData) {
    return authStore.register(userData);
  },
  
  async logout() {
    return authStore.logout();
  },
  
  async init() {
    return authStore.init();
  }
};
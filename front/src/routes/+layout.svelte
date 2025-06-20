<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  import { authStore, isAuthenticated, isLoading } from '$lib/services/auth.service.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { goto } from '$app/navigation';
  
  // Components
  import NotificationToast from '$lib/components/common/NotificationToast.svelte';
  
  // Global styles
  import '../app.css';

  let { children } = $props();
  let isInitialized = $state(false);

  // Get translation function
  const translate = $derived($t);

  // Routes that don't require authentication
  const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email'];
  const isPublicRoute = $derived(publicRoutes.includes($page.url.pathname));

  onMount(async () => {
      // Initialize UI store first
      uiStore.init();
      
      // Initialize auth store
      await authStore.init();
      isInitialized = true;

      // Redirect logic
      if (browser) {
          if (!$isAuthenticated && !isPublicRoute) {
              goto('/login');
          } else if ($isAuthenticated && $page.url.pathname === '/') {
              goto('/dashboard');
          }
      }
  });

  // Watch for auth changes and redirect
  $effect(() => {
      if (isInitialized && browser) {
          if (!$isAuthenticated && !isPublicRoute) {
              goto('/login');
          } else if ($isAuthenticated && isPublicRoute) {
              goto('/dashboard');
          }
      }
  });
</script>

<svelte:head>
  <title>{translate('common.appName')}</title>
  <meta name="description" content="Modern e-learning platform" />
</svelte:head>

{#if !isInitialized || $isLoading}
  <!-- Loading State -->
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div class="text-center">
          <div class="inline-flex items-center justify-center w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-full mb-6 shadow-lg">
              <div class="w-12 h-12 border-4 border-primary-600 dark:border-primary-400 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Loading</h2>
          <p class="text-gray-600 dark:text-gray-400">Preparing your experience...</p>
      </div>
  </div>
{:else}
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
      {@render children()}
      
      <!-- Global Components -->
      <NotificationToast />
  </div>
{/if}
<!-- front/src/routes/+layout.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { browser } from '$app/environment';
    import { authStore, isAuthenticated, isLoading } from '$lib/services/auth.service.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import { goto } from '$app/navigation';
    import { fade } from 'svelte/transition';
    
    // Components
    import NotificationToast from '$lib/components/common/NotificationToast.svelte';
    import ModernHeader from '$lib/components/layout/Header.svelte';
    import Sidebar from '$lib/components/layout/Sidebar.svelte';
    
    // Global styles
    import '../app.css';
  
    let { children } = $props();
    let isInitialized = $state(false);
  
    // Routes that don't require authentication
    const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email', '/', '/courses'];
    const authRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email'];
    
    const isPublicRoute = $derived(publicRoutes.some(route => $page.url.pathname.startsWith(route)));
    const isAuthRoute = $derived(authRoutes.some(route => $page.url.pathname.startsWith(route)));
    const showSidebar = $derived($isAuthenticated && !isAuthRoute && false); // Set to false to disable sidebar for now
  
    onMount(async () => {
      // Initialize stores
      uiStore.init();
      await authStore.init();
      isInitialized = true;
  
      // Handle initial routing
      if (browser && isInitialized) {
        if (!$isAuthenticated && !isPublicRoute) {
          goto('/login');
        } else if ($isAuthenticated && ($page.url.pathname === '/' || authRoutes.includes($page.url.pathname))) {
          goto('/dashboard');
        }
      }
    });
  
    // Watch for auth changes
    $effect(() => {
      if (isInitialized && browser) {
        if (!$isAuthenticated && !isPublicRoute) {
          goto('/login');
        } else if ($isAuthenticated && isAuthRoute) {
          goto('/dashboard');
        }
      }
    });
  </script>
  
  <svelte:head>
    <title>{$t('common.appName')}</title>
    <meta name="description" content="Modern e-learning platform for everyone" />
  </svelte:head>
  
  {#if !isInitialized || $isLoading}
    <!-- Enhanced Loading State -->
    <div class="min-h-screen flex items-center justify-center animated-gradient">
      <div class="text-center" transition:fade>
        <div class="relative">
          <div class="inline-flex items-center justify-center w-24 h-24 glass rounded-3xl shadow-2xl">
            <div class="w-16 h-16 rounded-2xl overflow-hidden">
              <div class="w-16 h-16 bg-gradient-to-br from-aurora-500 to-nebula-600 rounded-2xl flex items-center justify-center">
                <div class="text-3xl font-bold text-white animate-pulse">E</div>
              </div>
            </div>
          </div>
          <div class="absolute -inset-4 bg-gradient-to-r from-aurora-400 to-nebula-400 rounded-3xl opacity-20 blur-xl animate-pulse"></div>
        </div>
        <h2 class="text-2xl font-display font-bold bg-gradient-to-r from-aurora-600 to-nebula-600 bg-clip-text text-transparent mt-8 mb-2">
          Loading EduVerse
        </h2>
        <p class="text-gray-600 dark:text-gray-400">Preparing your learning experience...</p>
      </div>
    </div>
  {:else}
    <div class="min-h-screen">
      <!-- Always show header -->
      <ModernHeader />
      
      <!-- Main Content Area -->
      <main class="pt-24 min-h-screen">
        {#if showSidebar}
          <!-- With Sidebar Layout (currently disabled) -->
          <div class="flex">
            <Sidebar />
            <div class="flex-1 p-6">
              <div transition:fade={{ duration: 300 }}>
                {@render children()}
              </div>
            </div>
          </div>
        {:else}
          <!-- Without Sidebar Layout -->
          <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div transition:fade={{ duration: 300 }}>
              {@render children()}
            </div>
          </div>
        {/if}
      </main>
      
      <!-- Global Components -->
      <NotificationToast />
    </div>
  {/if}
  
  <style>
    :global(html) {
      scroll-behavior: smooth;
    }
    
    :global(body) {
      overflow-x: hidden;
    }
  </style>
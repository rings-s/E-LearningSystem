<!-- front/src/routes/+layout.svelte -->
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  import { authStore, isAuthenticated, isLoading, isInitialized } from '$lib/services/auth.service.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { goto } from '$app/navigation';
  import { fade } from 'svelte/transition';
  import '../app.css';
  
  // Components
  import Header from '$lib/components/layout/Header.svelte';
  import NotificationToast from '$lib/components/common/NotificationToast.svelte';
  
  let { children } = $props();
  
  // Routes that don't require authentication
  const publicRoutes = ['/', '/login', '/register', '/forgot-password', '/reset-password', '/verify-email', '/courses'];
  const authRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email'];
  
  const isPublicRoute = (path) => publicRoutes.some(route => path === route || path.startsWith(route + '/'));
  const isAuthRoute = (path) => authRoutes.some(route => path === route || path.startsWith(route + '/'));
  
  onMount(async () => {
      // Initialize stores
      uiStore.init();
      await authStore.init();
  });
  
  // Handle routing after initialization
  $effect(() => {
      if ($isInitialized && browser) {
          const currentPath = $page.url.pathname;
          
          // If not authenticated and trying to access protected route
          if (!$isAuthenticated && !isPublicRoute(currentPath)) {
              goto('/login');
          }
          // If authenticated and trying to access auth pages
          else if ($isAuthenticated && isAuthRoute(currentPath)) {
              goto('/dashboard');
          }
      }
  });
</script>

<svelte:head>
  <title>244SCHOOL - Modern E-Learning Platform</title>
  <meta name="description" content="244SCHOOL - Your gateway to quality online education" />
  <meta name="theme-color" content="#6366f1" />
</svelte:head>

{#if !$isInitialized}
  <!-- Loading State -->
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div class="text-center" transition:fade>
          <div class="relative">
              <div class="inline-flex items-center justify-center w-24 h-24 bg-white dark:bg-gray-800 rounded-3xl shadow-2xl">
                  <div class="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-600 rounded-2xl flex items-center justify-center">
                      <span class="text-3xl font-bold text-white">244</span>
                  </div>
              </div>
              <div class="absolute -inset-4 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-3xl opacity-20 blur-xl animate-pulse"></div>
          </div>
          <h2 class="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mt-8 mb-2">
              244SCHOOL
          </h2>
          <p class="text-gray-600 dark:text-gray-400">Preparing your learning experience...</p>
      </div>
  </div>
{:else}
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/20 dark:from-gray-900 dark:via-gray-800 dark:to-primary-900/20">
      <!-- Header -->
      <Header />
      
      <!-- Main Content -->
      <main class="pt-16">
          <div transition:fade={{ duration: 200 }}>
              {@render children()}
          </div>
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
  
  :global(.min-h-screen) {
      min-height: 100vh;
      min-height: 100dvh;
  }
</style>
<!-- front/src/routes/+layout.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { browser } from '$app/environment';
    import { authStore } from '$lib/stores/auth.store.js';
    import { isAuthenticated } from '$lib/services/auth.service.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { notificationStore } from '$lib/stores/notification.store.js';
    import { courseStore } from '$lib/stores/course.store.js';
    import { t, setLocale } from '$lib/i18n/index.js';
    import { loading, theme, language, isRTL } from '$lib/stores/ui.store.js';
    
    // Layout Components
    import Sidebar from '$lib/components/layout/Sidebar.svelte';
    import Header from '$lib/components/layout/Header.svelte';
    import MobileMenu from '$lib/components/layout/MobileMenu.svelte';
    import NotificationToast from '$lib/components/common/NotificationToast.svelte';
    
    // Global styles
    import '../app.css';
  
    let { children } = $props();
    let isInitialized = $state(false);
  
    // Routes that don't require authentication
    const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email'];
    const authRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email'];
    
    const isPublicRoute = $derived(publicRoutes.includes($page.url.pathname));
    const isAuthRoute = $derived(authRoutes.includes($page.url.pathname));
    const showSidebar = $derived($isAuthenticated && !isAuthRoute);
  
    onMount(async () => {
      // Initialize UI store
      uiStore.init();
      
      try {
        // Attempt to load user profile which will validate the session
        const user = await authStore.loadProfile();
        
        if (user && $isAuthenticated) {
          // Initialize other stores for authenticated users
          await notificationStore.init(user.uuid);
          
          // Load initial data
          courseStore.loadMyEnrollments().catch(console.error);
        }
      } catch (error) {
        // This is expected if the user is not logged in.
        // console.error("Authentication check failed:", error.message);
      } finally {
        isInitialized = true;
      }
    });
  
    // Handle theme changes
    $effect(() => {
      if (browser) {
        document.documentElement.classList.toggle('dark', $theme === 'dark');
      }
    });
  
    // Handle language changes
    $effect(() => {
      if (browser) {
        document.documentElement.lang = $language;
        document.documentElement.dir = $isRTL ? 'rtl' : 'ltr';
      }
    });
  
    // Cleanup on unmount
    $effect(() => {
      return () => {
        if ($isAuthenticated) {
          notificationStore.disconnect();
        }
      };
    });
  </script>
  
  <svelte:head>
    <title>{$t('common.appName')}</title>
    <meta name="description" content={$t('common.appDescription')} />
  </svelte:head>
  
  {#if !isInitialized}
    <!-- Loading State -->
    <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-full mb-4">
          <div class="w-10 h-10 border-4 border-primary-600 dark:border-primary-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <p class="text-gray-600 dark:text-gray-400">{$t('common.loading')}</p>
      </div>
    </div>
  {:else}
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900" class:rtl={$isRTL}>
      {#if showSidebar}
        <!-- Authenticated Layout with Sidebar -->
        <div class="flex h-screen overflow-hidden">
          <!-- Sidebar -->
          <Sidebar />
          
          <!-- Main Content Area -->
          <div class="flex-1 flex flex-col overflow-hidden">
            <!-- Header -->
            <Header />
            
            <!-- Page Content -->
            <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900">
              <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {@render children()}
              </div>
            </main>
          </div>
        </div>
        
        <!-- Mobile Menu -->
        <MobileMenu />
      {:else}
        <!-- Public/Auth Layout -->
        <div class="min-h-screen flex flex-col">
          <!-- Minimal Header for public pages -->
          {#if !isAuthRoute}
            <Header minimal />
          {/if}
          
          <!-- Page Content -->
          <main class="flex-1 flex items-center justify-center">
            {@render children()}
          </main>
        </div>
      {/if}
      
      <!-- Global UI Components -->
      <NotificationToast />
      
      <!-- Global Loading Overlay -->
      {#if $loading}
        <div class="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 border-4 border-primary-600 dark:border-primary-400 border-t-transparent rounded-full animate-spin"></div>
              <span class="text-gray-900 dark:text-white font-medium">
                {$t('common.loading')}
              </span>
            </div>
          </div>
        </div>
      {/if}
    </div>
  {/if}
  

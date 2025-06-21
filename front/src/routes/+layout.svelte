<!-- front/src/routes/+layout.svelte -->
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
    import Navbar from '$lib/components/layout/Navbar.svelte';
    import Sidebar from '$lib/components/layout/Sidebar.svelte';
    import { classNames } from '$lib/utils/helpers.js';
    
    // Global styles
    import '../app.css';
  
    let { children } = $props();
    let isInitialized = $state(false);
  
    // Routes that don't require authentication
    const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email', '/', '/courses'];
    const authRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email'];
    
    const isPublicRoute = $derived(publicRoutes.some(route => $page.url.pathname.startsWith(route)));
    const isAuthRoute = $derived(authRoutes.some(route => $page.url.pathname.startsWith(route)));
    const showSidebar = $derived($isAuthenticated && !isAuthRoute);
  
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
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div class="text-center">
            <div class="relative">
                <div class="inline-flex items-center justify-center w-24 h-24 bg-white dark:bg-gray-800 rounded-3xl shadow-2xl">
                    <div class="w-16 h-16 rounded-2xl overflow-hidden">
                        <img 
                            src="/logo.png" 
                            alt="Loading"
                            class="w-full h-full object-cover animate-pulse"
                            on:error={event => event.target.style.display = 'none'}
                        />
                        <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center">
                            <div class="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
                        </div>
                    </div>
                </div>
                <div class="absolute -inset-4 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-3xl opacity-20 blur-xl animate-pulse"></div>
            </div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mt-8 mb-2">Loading EduVerse</h2>
            <p class="text-gray-600 dark:text-gray-400">Preparing your learning experience...</p>
        </div>
    </div>
  {:else}
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
        {#if showSidebar}
            <!-- App Layout with Sidebar -->
            <div class="flex h-screen">
                <Sidebar />
                <div class="flex-1 flex flex-col">
                    <Navbar />
                    <main class="flex-1 overflow-y-auto pt-16">
                        <div class="p-6">
                            {@render children()}
                        </div>
                    </main>
                </div>
            </div>
        {:else}
            <!-- Public/Auth Layout -->
            <Navbar />
            <main class={classNames(
                'min-h-screen',
                !isAuthRoute && 'pt-16'
            )}>
                {@render children()}
            </main>
        {/if}
        
        <!-- Global Components -->
        <NotificationToast />
    </div>
  {/if}
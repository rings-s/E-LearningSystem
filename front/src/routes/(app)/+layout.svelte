// front/src/routes/(app)/+layout.svelte
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { authStore, isAuthenticated } from '$lib/stores/auth.store.js';
    import { uiStore, theme, language, isRTL } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import Sidebar from '$lib/components/layout/Sidebar.svelte';
    import Header from '$lib/components/layout/Header.svelte';
    import MobileMenu from '$lib/components/layout/MobileMenu.svelte';
    import NotificationToast from '$lib/components/common/NotificationToast.svelte';

    let { children } = $props();

    onMount(() => {
        authStore.init();
        uiStore.init();
    });
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 {$isRTL ? 'rtl' : 'ltr'}">
    {#if $isAuthenticated}
        <!-- Authenticated Layout -->
        <div class="flex h-screen overflow-hidden">
            <!-- Sidebar -->
            <Sidebar />
            
            <!-- Main Content -->
            <div class="flex-1 flex flex-col overflow-hidden">
                <!-- Header -->
                <Header />
                
                <!-- Page Content -->
                <main class="flex-1 overflow-x-hidden overflow-y-auto">
                    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
                        {@render children()}
                    </div>
                </main>
            </div>
        </div>
        
        <!-- Mobile Menu -->
        <MobileMenu />
    {:else}
        <!-- Public Layout -->
        <div class="min-h-screen flex flex-col">
            <Header minimal />
            <main class="flex-1">
                {@render children()}
            </main>
        </div>
    {/if}
    
    <!-- Global Components -->
    <NotificationToast />
</div>

<style>
    :global(body) {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                     'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        line-height: 1.5;
    }
    
    :global(.rtl) {
        direction: rtl;
        font-family: 'Cairo', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    :global(h1) { @apply text-2xl font-bold; }
    :global(h2) { @apply text-xl font-semibold; }
    :global(h3) { @apply text-lg font-semibold; }
    :global(h4) { @apply text-base font-medium; }
    
    :global(.container) {
        @apply max-w-7xl;
    }
    
    /* Scrollbar Styling */
    :global(::-webkit-scrollbar) {
        width: 6px;
        height: 6px;
    }
    
    :global(::-webkit-scrollbar-track) {
        @apply bg-gray-100 dark:bg-gray-800;
    }
    
    :global(::-webkit-scrollbar-thumb) {
        @apply bg-gray-400 dark:bg-gray-600 rounded;
    }
    
    :global(::-webkit-scrollbar-thumb:hover) {
        @apply bg-gray-500 dark:bg-gray-500;
    }
</style>
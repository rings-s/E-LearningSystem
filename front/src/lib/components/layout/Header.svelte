<!-- front/src/lib/components/layout/Header.svelte -->
<script>
    import { uiStore, theme, language } from '$lib/stores/ui.store.js';
    import { authStore } from '$lib/stores/auth.store.js';
    import { t } from '$lib/i18n/index.js';
    import { goto } from '$app/navigation';
    import NotificationBell from '../common/NotificationBell.svelte';
    import UserMenu from '../common/UserMenu.svelte';
  
    let { minimal = false } = $props();
    
    const toggleSidebar = () => uiStore.toggleSidebar();
    const toggleTheme = () => uiStore.toggleTheme();
    const toggleLanguage = () => {
      const newLang = $language === 'en' ? 'ar' : 'en';
      uiStore.setLanguage(newLang);
    };
  </script>
  
  <header class="sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
      <div class="flex items-center space-x-4">
        {#if !minimal}
          <button
            onclick={toggleSidebar}
            class="lg:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle sidebar"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        {/if}
        
        {#if minimal}
          <button onclick={() => goto('/')} class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center text-white font-bold">
              E
            </div>
            <span class="text-lg font-semibold text-gray-900 dark:text-white">
              {$t('common.appName')}
            </span>
          </button>
        {/if}
      </div>
  
      <div class="flex items-center space-x-2 sm:space-x-4">
        <!-- Language Toggle -->
        <button
          onclick={toggleLanguage}
          class="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors"
          aria-label="Toggle language"
        >
          <span class="text-sm font-medium">{$language === 'en' ? 'AR' : 'EN'}</span>
        </button>
  
        <!-- Theme Toggle -->
        <button
          onclick={toggleTheme}
          class="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors"
          aria-label="Toggle theme"
        >
          {#if $theme === 'light'}
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          {:else}
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          {/if}
        </button>
  
        {#if !minimal}
          <!-- Notifications -->
          <NotificationBell />
          
          <!-- User Menu -->
          <UserMenu />
        {:else}
          <!-- Auth Links -->
          <div class="flex items-center space-x-4">
            <a href="/login" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400">
              {$t('auth.login')}
            </a>
            <a href="/register" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors">
              {$t('auth.register')}
            </a>
          </div>
        {/if}
      </div>
    </div>
  </header>
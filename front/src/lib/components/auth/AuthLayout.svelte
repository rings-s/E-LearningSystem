<!-- front/src/lib/components/auth/AuthLayout.svelte -->
<script>
  import { t } from '$lib/i18n/index.js';
  import Card from '$lib/components/common/Card.svelte';
  import { uiStore, theme, language } from '$lib/stores/ui.store.js';

  let { 
    title = '',
    subtitle = '',
    showLogo = true,
    class: className = '',
    children,
    footer
  } = $props();

  const toggleTheme = () => uiStore.toggleTheme();
  const toggleLanguage = () => {
    const newLang = $language === 'en' ? 'ar' : 'en';
    uiStore.setLanguage(newLang);
  };
</script>

<div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
  <!-- Minimal Header -->
  <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <a href="/" class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center text-white font-bold">
            E
          </div>
          <span class="text-lg font-semibold text-gray-900 dark:text-white">
            {$t('common.appName')}
          </span>
        </a>
        
        <!-- Right side controls -->
        <div class="flex items-center space-x-4">
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

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-4">
            <a href="/" class="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors">
              Home
            </a>
            <a href="/courses" class="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors">
              Courses
            </a>
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <div class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 {className}">
      {#if showLogo}
        <div class="text-center">
          <a href="/" class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl text-white text-2xl font-bold mb-4 hover:shadow-lg transition-shadow">
            E
          </a>
          <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
            {title}
          </h2>
          {#if subtitle}
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {@html subtitle}
            </p>
          {/if}
        </div>
      {/if}
  
      <Card variant="bordered" padding="large">
        {@render children()}
      </Card>

      {#if footer}
        <div class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          {@render footer()}
        </div>
      {/if}
    </div>
  </div>
</div>
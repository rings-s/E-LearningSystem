<!-- front/src/lib/components/layout/Header.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { uiStore, theme, language } from '$lib/stores/ui.store.js';
  import { authStore, isAuthenticated, currentUser } from '$lib/stores/auth.store.js';
  import { notificationStore, unreadCount } from '$lib/stores/notification.store.js';
  import { t } from '$lib/i18n/index.js';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { clickOutside } from '$lib/utils/helpers.js';
  
  let scrolled = $state(false);
  let mobileMenuOpen = $state(false);
  let userMenuOpen = $state(false);
  let notificationsOpen = $state(false);
  
  const navigation = [
    { name: 'dashboard', href: '/dashboard', auth: true },
    { name: 'courses', href: '/courses', auth: false },
    { name: 'myCourses', href: '/my-courses', auth: true },
    { name: 'forum', href: '/forum', auth: true },
    { name: 'certificates', href: '/certificates', auth: true },
  ];
  
  const filteredNavigation = $derived(
    navigation.filter(item => !item.auth || $isAuthenticated)
  );
  
  onMount(() => {
    const handleScroll = () => {
      scrolled = window.scrollY > 10;
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });
  
  const toggleTheme = () => uiStore.toggleTheme();
  const toggleLanguage = () => {
    const newLang = $language === 'en' ? 'ar' : 'en';
    uiStore.setLanguage(newLang);
  };
  
  const isActive = (href) => $page.url.pathname.startsWith(href);
  
  const handleLogout = async () => {
    await authStore.logout();
    goto('/login');
  };
</script>

<header class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 {scrolled ? 'bg-white/95 dark:bg-gray-900/95 backdrop-blur-md shadow-sm' : 'bg-white dark:bg-gray-900'}">
  <nav class="container mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <div class="flex items-center">
        <a href="/" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
            E
          </div>
          <span class="text-xl font-bold text-gray-900 dark:text-white hidden sm:block">
            {$t('common.appName')}
          </span>
        </a>
      </div>
      
      <!-- Desktop Navigation -->
      <div class="hidden lg:flex items-center space-x-1">
        {#each filteredNavigation as item}
          <a
            href={item.href}
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 {
              isActive(item.href)
                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
            }"
          >
            {$t(`navigation.${item.name}`)}
          </a>
        {/each}
      </div>
      
      <!-- Right Actions -->
      <div class="flex items-center space-x-3">
        <!-- Theme Toggle -->
        <button
          onclick={toggleTheme}
          class="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-all"
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
        
        <!-- Language Toggle -->
        <button
          onclick={toggleLanguage}
          class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
        >
          {$language === 'en' ? 'عربي' : 'EN'}
        </button>
        
        {#if $isAuthenticated}
          <!-- Notifications -->
          <div class="relative">
            <button
              onclick={() => notificationsOpen = !notificationsOpen}
              class="relative p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-all"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {#if $unreadCount > 0}
                <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              {/if}
            </button>
            
            {#if notificationsOpen}
              <div
                use:clickOutside={() => notificationsOpen = false}
                transition:fly={{ y: 10, duration: 200 }}
                class="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
              >
                <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 class="font-semibold text-gray-900 dark:text-white">
                    {$t('notifications.notifications')}
                  </h3>
                </div>
                <div class="max-h-96 overflow-y-auto">
                  <p class="p-4 text-sm text-gray-500 dark:text-gray-400 text-center">
                    {$t('notifications.noNotifications')}
                  </p>
                </div>
              </div>
            {/if}
          </div>
          
          <!-- User Menu -->
          <div class="relative">
            <button
              onclick={() => userMenuOpen = !userMenuOpen}
              class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
            >
              {#if $currentUser?.avatar}
                <img src={$currentUser.avatar} alt="" class="w-8 h-8 rounded-lg object-cover" />
              {:else}
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-sm font-bold">
                  {$currentUser?.first_name?.[0] || 'U'}
                </div>
              {/if}
              <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {#if userMenuOpen}
              <div
                use:clickOutside={() => userMenuOpen = false}
                transition:fly={{ y: 10, duration: 200 }}
                class="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2"
              >
                <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {$currentUser?.full_name || $currentUser?.email}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {$t(`auth.${$currentUser?.role}`)}
                  </p>
                </div>
                <a
                
                  href="/profile"
                  onclick={() => userMenuOpen = false}
                  class="flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span>{$t('profile.profile')}</span>
                </a>
                
                
                {#if $currentUser?.role === 'teacher'}
                  <a
                    href="/courses/create"
                    onclick={() => userMenuOpen = false}
                    class="flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Create Course</span>
                  </a>
                {/if}
                
                <button
                  onclick={handleLogout}
                  class="w-full flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>{$t('auth.logout')}</span>
                </button>
              </div>
            {/if}
          </div>
          
          <!-- Mobile Menu Toggle -->
          <button
            onclick={() => mobileMenuOpen = !mobileMenuOpen}
            class="lg:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {#if !mobileMenuOpen}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              {:else}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              {/if}
            </svg>
          </button>
        {:else}
          <div class="flex items-center space-x-2">
            <a href="/login" class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              {$t('auth.login')}
            </a>
            <a href="/register" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-all">
              {$t('auth.register')}
            </a>
          </div>
        {/if}
      </div>
    </div>
  </nav>
  
  <!-- Mobile Menu -->
  {#if mobileMenuOpen}
    <div
      transition:fly={{ y: -20, duration: 200 }}
      class="lg:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800"
    >
      <div class="px-4 py-3 space-y-1">
        {#each filteredNavigation as item}
          <a
            href={item.href}
            onclick={() => mobileMenuOpen = false}
            class="block px-4 py-2 rounded-lg text-base font-medium {
              isActive(item.href)
                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
            }"
          >
            {$t(`navigation.${item.name}`)}
          </a>
        {/each}
        
        {#if $isAuthenticated}
          <div class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
            <a
              href="/profile"
              onclick={() => mobileMenuOpen = false}
              class="block px-4 py-2 rounded-lg text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              {$t('profile.profile')}
            </a>
            <button
              onclick={handleLogout}
              class="w-full text-left px-4 py-2 rounded-lg text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              {$t('auth.logout')}
            </button>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</header>
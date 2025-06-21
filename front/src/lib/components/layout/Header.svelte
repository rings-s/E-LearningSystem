<!-- front/src/lib/components/layout/Header.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { uiStore, theme, language } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { page } from '$app/stores';
  import { isAuthenticated, currentUser, userRole } from '$lib/services/auth.service.js';
  import { goto } from '$app/navigation';
  
  let scrolled = $state(false);
  let mobileMenuOpen = $state(false);
  
  // Complete navigation with all pages
  const navigation = [
    { name: 'dashboard', href: '/dashboard', icon: 'home', auth: true },
    { name: 'courses', href: '/courses', icon: 'book', auth: false },
    { name: 'myCourses', href: '/my-courses', icon: 'bookmark', auth: true },
    { name: 'teaching', href: '/teaching', icon: 'academic', auth: true, role: 'teacher' },
    { name: 'forum', href: '/forum', icon: 'chat', auth: true },
    { name: 'certificates', href: '/certificates', icon: 'award', auth: true },
  ];
  
  const filteredNavigation = $derived(
    navigation.filter(item => {
      if (item.auth && !$isAuthenticated) return false;
      if (item.role && $userRole !== item.role) return false;
      return true;
    })
  );
  
  onMount(() => {
    const handleScroll = () => {
      scrolled = window.scrollY > 20;
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });
  
  const toggleTheme = () => uiStore.toggleTheme();
  const toggleLanguage = () => {
    const newLang = $language === 'en' ? 'ar' : 'en';
    uiStore.setLanguage(newLang);
    document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
  };
  
  const isActive = (href) => $page.url.pathname.startsWith(href);
  
  // Complete icon set
  const icons = {
    home: {
      paths: [
        { d: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6", class: "home-roof" }
      ]
    },
    book: {
      paths: [
        { d: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253", class: "book-pages" }
      ]
    },
    bookmark: {
      paths: [
        { d: "M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z", class: "bookmark-icon" }
      ]
    },
    academic: {
      paths: [
        { d: "M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z M12 14v7", class: "academic-cap" }
      ]
    },
    chat: {
      paths: [
        { d: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z", class: "chat-bubble" }
      ]
    },
    award: {
      paths: [
        { d: "M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z", class: "award-star" }
      ]
    }
  };
</script>



<header 
  class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
  class:scrolled
>
  <nav class="glass mx-4 mt-4 rounded-2xl transition-all duration-300 {scrolled ? 'py-2' : 'py-4'}">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between">
        <!-- Logo with proper contrast -->
        <div class="flex items-center space-x-3 rtl:space-x-reverse">
          <div class="relative group">
            <div class="absolute inset-0 bg-primary rounded-xl blur-lg group-hover:blur-xl transition-all duration-300 opacity-30"></div>
            <div class="relative w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold shadow-lg transform transition-transform group-hover:scale-110">
              E
            </div>
          </div>
          <span class="text-xl font-display font-bold gradient-primary">
            {$t('common.appName')}
          </span>
        </div>
        
        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-1 rtl:space-x-reverse">
          {#each filteredNavigation as item}
            <a
              href={item.href}
              class="nav-item nav-link group {isActive(item.href) ? 'active' : ''}"
            >
              <div class="relative flex items-center space-x-2 rtl:space-x-reverse">
                <svg class="nav-icon w-5 h-5 {isActive(item.href) ? 'icon-primary' : 'icon-muted group-hover:icon-primary'}" 
                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {#each icons[item.icon].paths as path}
                    <path 
                      stroke-linecap="round" 
                      stroke-linejoin="round" 
                      stroke-width="2" 
                      d={path.d}
                      class={path.class}
                    />
                  {/each}
                </svg>
                <span class="font-medium">{$t(`navigation.${item.name}`)}</span>
              </div>
              
              {#if isActive(item.href)}
                <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-primary rounded-full animate-pulse"></div>
              {/if}
            </a>
          {/each}
        </div>
        
        <!-- Right Actions with proper contrast -->
        <div class="flex items-center space-x-2 rtl:space-x-reverse">
          <!-- Language Toggle -->
          <button
            onclick={toggleLanguage}
            class="relative p-2 rounded-xl neu-flat hover:neu-pressed transition-all duration-300 group focus-primary"
            aria-label="Toggle language"
          >
            <span class="relative text-sm font-bold gradient-primary">
              {$language === 'en' ? 'عربي' : 'EN'}
            </span>
          </button>
          
          <!-- Theme Toggle -->
          <button
            onclick={toggleTheme}
            class="relative p-2 rounded-xl neu-flat hover:neu-pressed transition-all duration-300 group focus-primary"
            aria-label="Toggle theme"
          >
            {#if $theme === 'light'}
              <svg class="relative w-5 h-5 text-accent transition-transform duration-300 group-hover:rotate-180" 
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            {:else}
              <svg class="relative w-5 h-5 text-accent transition-transform duration-300 group-hover:rotate-90" 
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            {/if}
          </button>
          
          <!-- User Actions -->
          {#if $isAuthenticated}
            <div class="flex items-center space-x-2 rtl:space-x-reverse">
              <button class="relative p-2 rounded-xl neu-flat hover:neu-pressed transition-all duration-300 focus-primary">
                <svg class="w-5 h-5 icon-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span class="absolute top-1 right-1 w-2 h-2 bg-error rounded-full"></span>
              </button>
              
              <button class="relative focus-primary rounded-xl">
                {#if $currentUser?.avatar}
                  <img src={$currentUser.avatar} alt="" class="w-8 h-8 rounded-xl object-cover" />
                {:else}
                  <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-400 to-secondary-400 flex items-center justify-center text-white text-sm font-bold">
                    {$currentUser?.first_name?.[0] || 'U'}
                  </div>
                {/if}
              </button>
            </div>
          {:else}
            <div class="flex items-center space-x-2 rtl:space-x-reverse">
              <a href="/login" class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary dark:hover:text-primary transition-colors">
                {$t('auth.login')}
              </a>
              <a href="/register" class="px-4 py-2 text-sm font-medium btn-primary rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105">
                {$t('auth.register')}
              </a>
            </div>
          {/if}
          
          <!-- Mobile Menu Toggle -->
          <button
            onclick={() => mobileMenuOpen = !mobileMenuOpen}
            class="md:hidden relative p-2 rounded-xl neu-flat hover:neu-pressed transition-all duration-300 focus-primary"
          >
            <svg class="w-6 h-6 icon-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {#if !mobileMenuOpen}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              {:else}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              {/if}
            </svg>
          </button>
        </div>
      </div>
    </div>
  </nav>
  
  <!-- Mobile Menu with proper contrast -->
  {#if mobileMenuOpen}
    <div 
      class="md:hidden glass mx-4 mt-2 rounded-2xl overflow-hidden"
      transition:fly={{ y: -20, duration: 300, easing: quintOut }}
    >
      <div class="p-4 space-y-2">
        {#each filteredNavigation as item}
          <a
            href={item.href}
            onclick={() => mobileMenuOpen = false}
            class="flex items-center space-x-3 rtl:space-x-reverse px-4 py-3 rounded-xl transition-all duration-300 
                   {isActive(item.href) 
                     ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300' 
                     : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'}"
          >
            <svg class="w-5 h-5 {isActive(item.href) ? 'icon-primary' : 'icon-muted'}" 
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {#each icons[item.icon].paths as path}
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d={path.d}
                />
              {/each}
            </svg>
            <span class="font-medium">{$t(`navigation.${item.name}`)}</span>
          </a>
        {/each}
      </div>
    </div>
  {/if}
</header>


<style>
  /* Animated Icon Styles */
  .nav-icon {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .nav-item:hover .nav-icon {
    transform: translateY(-2px) scale(1.1);
  }
  
  .nav-item:hover .home-roof {
    animation: float 2s ease-in-out infinite;
  }
  
  .nav-item:hover .book-pages {
    animation: book-flip 1s ease-in-out;
  }
  
  .nav-item:hover .bookmark-icon {
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  .nav-item:hover .academic-cap {
    animation: tip 1s ease-in-out;
  }
  
  .nav-item:hover .chat-bubble {
    animation: bounce 0.5s ease-out;
  }
  
  .nav-item:hover .award-star {
    animation: spin 1s ease-in-out;
  }
  
  @keyframes book-flip {
    0%, 100% { transform: rotateY(0); }
    50% { transform: rotateY(10deg); }
  }
  
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes tip {
    0%, 100% { transform: rotate(0); }
    25% { transform: rotate(-5deg); }
    75% { transform: rotate(5deg); }
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
  }
</style>
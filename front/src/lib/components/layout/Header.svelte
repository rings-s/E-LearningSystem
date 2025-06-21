<!-- front/src/lib/components/layout/ModernHeader.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { uiStore, theme, language } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { page } from '$app/stores';
  
  let scrolled = $state(false);
  let mobileMenuOpen = $state(false);
  
  const navigation = [
    { name: 'home', href: '/dashboard', icon: 'home' },
    { name: 'courses', href: '/courses', icon: 'book' },
    { name: 'forum', href: '/forum', icon: 'chat' },
    { name: 'certificates', href: '/certificates', icon: 'award' },
  ];
  
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
  
  const isActive = (href) => $page.url.pathname === href;
  
  // Animated SVG Icons
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
</style>

<header 
  class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
  class:scrolled
>
  <nav class="glass mx-4 mt-4 rounded-2xl transition-all duration-300 {scrolled ? 'py-2' : 'py-4'}">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center space-x-3">
          <div class="relative group">
            <div class="absolute inset-0 bg-gradient-to-r from-aurora-500 to-nebula-500 rounded-xl blur-lg group-hover:blur-xl transition-all duration-300 opacity-75"></div>
            <div class="relative w-10 h-10 bg-gradient-to-br from-aurora-500 to-nebula-500 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
              E
            </div>
          </div>
          <span class="text-xl font-display font-bold bg-gradient-to-r from-aurora-600 to-nebula-600 bg-clip-text text-transparent">
            {$t('common.appName')}
          </span>
        </div>
        
        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-1">
          {#each navigation as item}
            <a
              href={item.href}
              class="nav-item relative px-4 py-2 rounded-xl transition-all duration-300 group {isActive(item.href) ? 'text-aurora-600 dark:text-aurora-400' : 'text-gray-700 dark:text-gray-300 hover:text-aurora-600 dark:hover:text-aurora-400'}"
            >
              {#if isActive(item.href)}
                <div class="absolute inset-0 bg-gradient-to-r from-aurora-500/10 to-nebula-500/10 rounded-xl" 
                     transition:fade={{ duration: 300 }}></div>
              {/if}
              
              <div class="relative flex items-center space-x-2">
                <svg class="nav-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-aurora-500 rounded-full animate-pulse-glow"></div>
              {/if}
            </a>
          {/each}
        </div>
        
        <!-- Right Actions -->
        <div class="flex items-center space-x-2">
          <!-- Language Toggle -->
          <button
            onclick={toggleLanguage}
            class="relative p-2 rounded-xl neu-flat hover:neu-pressed transition-all duration-300 group"
            aria-label="Toggle language"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-aurora-500/0 to-nebula-500/0 group-hover:from-aurora-500/10 group-hover:to-nebula-500/10 rounded-xl transition-all duration-300"></div>
            <span class="relative text-sm font-bold bg-gradient-to-r from-aurora-600 to-nebula-600 bg-clip-text text-transparent">
              {$language === 'en' ? 'عربي' : 'EN'}
            </span>
          </button>
          
          <!-- Theme Toggle -->
          <button
            onclick={toggleTheme}
            class="relative p-2 rounded-xl neu-flat hover:neu-pressed transition-all duration-300 group"
            aria-label="Toggle theme"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-cosmic-500/0 to-stellar-500/0 group-hover:from-cosmic-500/10 group-hover:to-stellar-500/10 rounded-xl transition-all duration-300"></div>
            {#if $theme === 'light'}
              <svg class="relative w-5 h-5 text-cosmic-600 transition-transform duration-300 group-hover:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            {:else}
              <svg class="relative w-5 h-5 text-cosmic-400 transition-transform duration-300 group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            {/if}
          </button>
          
          <!-- Mobile Menu Toggle -->
          <button
            onclick={() => mobileMenuOpen = !mobileMenuOpen}
            class="md:hidden relative p-2 rounded-xl neu-flat hover:neu-pressed transition-all duration-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
  
  <!-- Mobile Menu -->
  {#if mobileMenuOpen}
    <div 
      class="md:hidden glass mx-4 mt-2 rounded-2xl overflow-hidden"
      transition:fly={{ y: -20, duration: 300, easing: quintOut }}
    >
      <div class="p-4 space-y-2">
        {#each navigation as item}
          <a
            href={item.href}
            onclick={() => mobileMenuOpen = false}
            class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 {isActive(item.href) ? 'bg-gradient-to-r from-aurora-500/20 to-nebula-500/20 text-aurora-600 dark:text-aurora-400' : 'hover:bg-gray-100/50 dark:hover:bg-gray-800/50'}"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
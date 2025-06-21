<!-- front/src/lib/components/layout/Navbar.svelte -->
<script>
    import { page } from '$app/stores';
    import { fade, fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { authStore, currentUser, isAuthenticated } from '$lib/stores/auth.store.js';
    import { uiStore, theme, language } from '$lib/stores/ui.store.js';
    import { t, setLocale, availableLanguages } from '$lib/i18n/index.js';
    import { classNames, clickOutside } from '$lib/utils/helpers.js';
    import Logo from '$lib/components/common/Logo.svelte';
    import NotificationBell from '../common/NotificationBell.svelte';
    import UserMenu from '../common/UserMenu.svelte';

    let mobileMenuOpen = $state(false);
    let scrolled = $state(false);
    
    // Handle scroll effect
    $effect(() => {
        if (typeof window !== 'undefined') {
            const handleScroll = () => {
                scrolled = window.scrollY > 20;
            };
            window.addEventListener('scroll', handleScroll);
            return () => window.removeEventListener('scroll', handleScroll);
        }
    });

    const navigation = [
        { name: $t('navigation.dashboard'), href: '/dashboard' },
        { name: $t('navigation.courses'), href: '/courses' },
        { name: $t('navigation.myCourses'), href: '/my-courses' },
        { name: $t('navigation.forum'), href: '/forum' }
    ];

    const isActive = (href) => $page.url.pathname === href;
</script>

<nav class={classNames(
    'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
    scrolled ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl shadow-lg' : 'bg-white dark:bg-gray-900'
)}>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <!-- Left side -->
            <div class="flex items-center gap-8">
                <Logo />
                
                <!-- Desktop Navigation -->
                <div class="hidden lg:flex items-center gap-1">
                    {#each navigation as item}
                        <a 
                            href={item.href}
                            class={classNames(
                                'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                                isActive(item.href)
                                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400'
                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                            )}
                        >
                            {item.name}
                        </a>
                    {/each}
                </div>
            </div>

            <!-- Right side -->
            <div class="flex items-center gap-2">
                {#if $isAuthenticated}
                    <!-- Theme Toggle -->
                    <button
                        onclick={() => uiStore.toggleTheme()}
                        class="relative p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-all duration-300 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                        aria-label="Toggle theme"
                    >
                        <div class="relative w-5 h-5">
                            <svg 
                                class={classNames(
                                    'absolute inset-0 w-5 h-5 transition-all duration-500 transform',
                                    $theme === 'light' ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-90'
                                )}
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24"
                            >
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                            <svg 
                                class={classNames(
                                    'absolute inset-0 w-5 h-5 transition-all duration-500 transform',
                                    $theme === 'dark' ? 'opacity-100 rotate-0' : 'opacity-0 rotate-90'
                                )}
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24"
                            >
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                            </svg>
                        </div>
                    </button>

                    <!-- Language Toggle -->
                    <button
                        onclick={() => setLocale($language === 'en' ? 'ar' : 'en')}
                        class="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-all duration-300 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                        aria-label="Toggle language"
                    >
                        <span class="text-sm font-bold">
                            {availableLanguages[$language]?.flag} {$language.toUpperCase()}
                        </span>
                    </button>

                    <div class="hidden md:flex items-center gap-2">
                        <NotificationBell />
                        <UserMenu />
                    </div>

                    <!-- Mobile menu button -->
                    <button
                        onclick={() => mobileMenuOpen = !mobileMenuOpen}
                        class="lg:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-all duration-300"
                    >
                        <div class="relative w-6 h-6">
                            <span class={classNames(
                                'absolute top-1 left-0 w-6 h-0.5 bg-current transition-all duration-300 transform',
                                mobileMenuOpen ? 'rotate-45 translate-y-2' : ''
                            )}></span>
                            <span class={classNames(
                                'absolute top-3 left-0 w-6 h-0.5 bg-current transition-all duration-300',
                                mobileMenuOpen ? 'opacity-0' : ''
                            )}></span>
                            <span class={classNames(
                                'absolute top-5 left-0 w-6 h-0.5 bg-current transition-all duration-300 transform',
                                mobileMenuOpen ? '-rotate-45 -translate-y-2' : ''
                            )}></span>
                        </div>
                    </button>
                {:else}
                    <div class="flex items-center gap-4">
                        <a href="/login" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                            {$t('auth.login')}
                        </a>
                        <a href="/register" class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 rounded-lg transition-all duration-300 transform hover:scale-105">
                            {$t('auth.register')}
                        </a>
                    </div>
                {/if}
            </div>
        </div>
    </div>

    <!-- Mobile menu -->
    {#if mobileMenuOpen}
        <div 
            class="lg:hidden absolute top-16 left-0 right-0 bg-white dark:bg-gray-900 shadow-xl border-t border-gray-200 dark:border-gray-800"
            transition:fly={{ y: -20, duration: 300, easing: quintOut }}
            use:clickOutside={() => mobileMenuOpen = false}
        >
            <div class="px-4 py-6 space-y-1">
                {#each navigation as item}
                    <a 
                        href={item.href}
                        onclick={() => mobileMenuOpen = false}
                        class={classNames(
                            'block px-4 py-3 rounded-lg text-base font-medium transition-all duration-200',
                            isActive(item.href)
                                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400'
                                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                        )}
                    >
                        {item.name}
                    </a>
                {/each}
                
                {#if $isAuthenticated}
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <NotificationBell />
                        <UserMenu />
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</nav>
<!-- front/src/lib/components/layout/Navbar.svelte -->
<script>
	import { page } from '$app/stores';
	import { fade, fly } from 'svelte/transition';
	import { authStore, currentUser, isAuthenticated } from '$lib/stores/auth.store.js';
	import { uiStore, theme, language } from '$lib/stores/ui.store.js';
	import { t, setLocale, availableLanguages } from '$lib/i18n/index.js';
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

<nav
	class="fixed top-0 right-0 left-0 z-50 border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 {scrolled
		? 'shadow-sm'
		: ''}"
>
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<div class="flex h-16 items-center justify-between">
			<!-- Left side -->
			<div class="flex items-center gap-8">
				<Logo />

				<!-- Desktop Navigation -->
				<div class="hidden items-center gap-1 lg:flex">
					{#each navigation as item}
						<a
							href={item.href}
							class="rounded-md px-3 py-2 text-sm font-medium transition-colors {isActive(item.href)
								? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
								: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}"
						>
							{item.name}
						</a>
					{/each}
				</div>
			</div>

			<!-- Right side -->
			<div class="flex items-center gap-3">
				{#if $isAuthenticated}
					<!-- Theme Toggle -->
					<button
						onclick={() => uiStore.toggleTheme()}
						class="rounded-md p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
						aria-label="Toggle theme"
					>
						{#if $theme === 'light'}
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
								/>
							</svg>
						{:else}
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
								/>
							</svg>
						{/if}
					</button>

					<!-- Language Toggle -->
					<button
						onclick={() => setLocale($language === 'en' ? 'ar' : 'en')}
						class="rounded-md p-2 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
						aria-label="Toggle language"
					>
						{$language === 'en' ? 'عربي' : 'EN'}
					</button>

					<div class="hidden items-center gap-2 md:flex">
						<NotificationBell />
						<UserMenu />
					</div>

					<!-- Mobile menu button -->
					<button
						onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
						class="rounded-md p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 lg:hidden dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
					>
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							{#if mobileMenuOpen}
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							{:else}
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 6h16M4 12h16M4 18h16"
								/>
							{/if}
						</svg>
					</button>
				{:else}
					<div class="flex items-center gap-4">
						<a
							href="/login"
							class="text-sm font-medium text-gray-700 transition-colors hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400"
						>
							{$t('auth.login')}
						</a>
						<a
							href="/register"
							class="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
						>
							{$t('auth.register')}
						</a>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<!-- Mobile menu -->
	{#if mobileMenuOpen}
		<div class="border-t border-gray-200 bg-white lg:hidden dark:border-gray-800 dark:bg-gray-900">
			<div class="space-y-1 px-4 py-3">
				{#each navigation as item}
					<a
						href={item.href}
						onclick={() => (mobileMenuOpen = false)}
						class="block rounded-md px-3 py-2 text-base font-medium transition-colors {isActive(
							item.href
						)
							? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
							: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}"
					>
						{item.name}
					</a>
				{/each}

				{#if $isAuthenticated}
					<div class="border-t border-gray-200 pt-4 md:hidden dark:border-gray-700">
						<NotificationBell />
						<UserMenu />
					</div>
				{/if}
			</div>
		</div>
	{/if}
</nav>

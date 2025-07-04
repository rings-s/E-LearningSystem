<!-- front/src/lib/components/layout/Header.svelte -->
<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { fade, fly, slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { authStore, isAuthenticated, currentUser } from '$lib/services/auth.service.js';
	import { uiStore, theme } from '$lib/stores/ui.store.js';
	import { t, locale } from '$lib/i18n/index.js';
	import { clickOutside } from '$lib/utils/helpers.js';
	import Logo from '$lib/components/common/Logo.svelte';
	import NotificationBell from '$lib/components/common/NotificationBell.svelte';

	let scrolled = $state(false);
	let mobileMenuOpen = $state(false);
	let userMenuOpen = $state(false);

	const navigation = [
		{ name: 'dashboard', href: '/dashboard', auth: true },
		{ name: 'courses', href: '/courses', auth: false },
		{ name: 'myCourses', href: '/my-courses', auth: true },
		{ name: 'forum', href: '/forum', auth: true },
		{ name: 'certificates', href: '/certificates', auth: true }
	];

	const filteredNavigation = $derived(navigation.filter((item) => !item.auth || $isAuthenticated));

	$effect(() => {
		const handleScroll = () => {
			scrolled = window.scrollY > 10;
		};

		if (typeof window !== 'undefined') {
			window.addEventListener('scroll', handleScroll);
			return () => window.removeEventListener('scroll', handleScroll);
		}
	});

	const toggleTheme = () => uiStore.toggleTheme();
	const toggleLanguage = () => {
		const newLang = $locale === 'en' ? 'ar' : 'en';
		uiStore.setLanguage(newLang);
	};

	const isActive = (href) => $page.url.pathname.startsWith(href);

	const handleLogout = async () => {
		authStore.logout();
		goto('/login');
	};

	const getInitials = (name) => {
		if (!name) return '';
		return name
			.split(' ')
			.map((n) => n[0])
			.join('')
			.toUpperCase()
			.slice(0, 2);
	};
</script>

<header
	class="fixed top-0 right-0 left-0 z-50 transition-all duration-300 {scrolled
		? 'bg-white/95 shadow-lg backdrop-blur-md dark:bg-gray-900/95'
		: 'bg-white/80 backdrop-blur-sm dark:bg-gray-900/80'}"
>
	<nav class="container mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex h-16 items-center justify-between">
			<!-- Logo -->
			<div class="flex items-center">
				<Logo href="/" showText={true} />
			</div>

			<!-- Desktop Navigation -->
			<div class="hidden items-center space-x-1 lg:flex">
				{#each filteredNavigation as item}
					<a
						href={item.href}
						class="rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 {isActive(
							item.href
						)
							? 'from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 text-primary-700 dark:text-primary-300 bg-gradient-to-r'
							: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}"
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
					class="rounded-lg p-2 text-gray-500 transition-all hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
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
					onclick={toggleLanguage}
					class="hidden rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 transition-all hover:bg-gray-100 sm:block dark:text-gray-300 dark:hover:bg-gray-800"
				>
					{$locale === 'en' ? 'عربي' : 'EN'}
				</button>

				{#if $isAuthenticated}
					<!-- Notifications (Desktop) -->
					<div class="hidden md:block">
						<NotificationBell />
					</div>

					<!-- User Menu -->
					<div class="relative">
						<button
							onclick={() => (userMenuOpen = !userMenuOpen)}
							class="flex items-center space-x-2 rounded-lg p-1.5 transition-all hover:bg-gray-100 dark:hover:bg-gray-800"
						>
							{#if $currentUser?.avatar}
								<img src={$currentUser.avatar} alt="" class="h-8 w-8 rounded-full object-cover" />
							{:else}
								<div
									class="from-primary-400 to-secondary-500 flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br text-sm font-bold text-white"
								>
									{getInitials($currentUser?.full_name || $currentUser?.email)}
								</div>
							{/if}
							<svg
								class="hidden h-4 w-4 text-gray-500 sm:block dark:text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M19 9l-7 7-7-7"
								/>
							</svg>
						</button>

						{#if userMenuOpen}
							<div
								use:clickOutside={() => (userMenuOpen = false)}
								transition:fly={{ y: 10, duration: 200 }}
								class="absolute right-0 mt-2 w-56 overflow-hidden rounded-xl border border-gray-200 bg-white py-2 shadow-lg dark:border-gray-700 dark:bg-gray-800"
							>
								<div class="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
									<p class="truncate text-sm font-medium text-gray-900 dark:text-white">
										{$currentUser?.full_name || $currentUser?.email}
									</p>
									<p class="text-xs text-gray-500 capitalize dark:text-gray-400">
										{$t(`auth.${$currentUser?.role}`)}
									</p>
								</div>
								<a
									href="/profile"
									onclick={() => (userMenuOpen = false)}
									class="flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
										/>
									</svg>
									<span>{$t('navigation.profile')}</span>
								</a>

								<button
									onclick={handleLogout}
									class="flex w-full items-center space-x-3 px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
										/>
									</svg>
									<span>{$t('auth.logout')}</span>
								</button>
							</div>
						{/if}
					</div>
				{:else}
					<div class="hidden items-center space-x-2 sm:flex">
						<a
							href="/login"
							class="px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
						>
							{$t('auth.login')}
						</a>
						<a
							href="/register"
							class="from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 transform rounded-lg bg-gradient-to-r px-4 py-2 text-sm font-medium text-white transition-all hover:scale-105"
						>
							{$t('auth.register')}
						</a>
					</div>
				{/if}

				<!-- Mobile Menu Toggle -->
				<button
					onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
					class="rounded-lg p-2 text-gray-500 transition-all hover:bg-gray-100 hover:text-gray-700 lg:hidden dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
					aria-label="Toggle menu"
				>
					<div class="relative h-6 w-6">
						<span class="absolute inset-0 flex flex-col justify-center">
							<span
								class="block h-0.5 w-6 transform bg-current transition-all duration-300 {mobileMenuOpen
									? 'translate-y-0 rotate-45'
									: '-translate-y-1.5'}"
							></span>
							<span
								class="block h-0.5 w-6 bg-current transition-all duration-300 {mobileMenuOpen
									? 'opacity-0'
									: 'opacity-100'}"
							></span>
							<span
								class="block h-0.5 w-6 transform bg-current transition-all duration-300 {mobileMenuOpen
									? 'translate-y-0 -rotate-45'
									: 'translate-y-1.5'}"
							></span>
						</span>
					</div>
				</button>
			</div>
		</div>
	</nav>

	<!-- Mobile Menu -->
	{#if mobileMenuOpen}
		<div
			transition:slide={{ duration: 300, easing: quintOut }}
			class="border-t border-gray-200 bg-white lg:hidden dark:border-gray-800 dark:bg-gray-900"
		>
			<div class="space-y-1 px-4 py-3">
				{#each filteredNavigation as item}
					<a
						href={item.href}
						onclick={() => (mobileMenuOpen = false)}
						class="block rounded-lg px-4 py-2 text-base font-medium transition-all {isActive(
							item.href
						)
							? 'from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 text-primary-700 dark:text-primary-300 bg-gradient-to-r'
							: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}"
					>
						{$t(`navigation.${item.name}`)}
					</a>
				{/each}

				{#if !$isAuthenticated}
					<div class="mt-2 space-y-1 border-t border-gray-200 pt-2 dark:border-gray-700">
						<a
							href="/login"
							onclick={() => (mobileMenuOpen = false)}
							class="block rounded-lg px-4 py-2 text-base font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
						>
							{$t('auth.login')}
						</a>
						<a
							href="/register"
							onclick={() => (mobileMenuOpen = false)}
							class="from-primary-600 to-secondary-600 block rounded-lg bg-gradient-to-r px-4 py-2 text-base font-medium text-white"
						>
							{$t('auth.register')}
						</a>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</header>

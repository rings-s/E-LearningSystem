<script>
	import { t } from '#lib/i18n/index.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { browser } from '$app/env';
	import {
		authStore,
		isAuthenticated,
		isLoading,
		isInitialized
	} from '#lib/services/auth.service.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { goto } from '$app/navigation';
	import '../app.css';

	// Components
	import Header from '#lib/components/layout/Header.svelte';
	import AppShell from '#lib/components/layout/AppShell.svelte';
	import Logo from '#lib/components/common/Logo.svelte';
	import NotificationToast from '#lib/components/common/NotificationToast.svelte';

	let { children } = $props();

	// Routes that don't require authentication
	const publicRoutes = [
		'/',
		'/login',
		'/register',
		'/forgot-password',
		'/reset-password',
		'/verify-email',
		'/courses'
	];
	const authRoutes = [
		'/login',
		'/register',
		'/forgot-password',
		'/reset-password',
		'/verify-email'
	];

	const isPublicRoute = (path) =>
		publicRoutes.some((route) => path === route || path.startsWith(route + '/'));
	const isAuthRoute = (path) =>
		authRoutes.some((route) => path === route || path.startsWith(route + '/'));

	// Learn pages are full-screen "focus mode" with their own navigation
	const isFocusRoute = $derived(/\/learn\/?$/.test(page.url.pathname));
	const useAppShell = $derived(
		$isAuthenticated && !isAuthRoute(page.url.pathname) && page.url.pathname !== '/'
	);

	onMount(async () => {
		// Initialize stores
		if (browser) {
			uiStore.init();
			await authStore.init();
		}
	});

	// Handle routing after initialization
	$effect(() => {
		if ($isInitialized && browser) {
			const currentPath = page.url.pathname;

			// Redirect to login if not authenticated and accessing protected routes
			if (!$isAuthenticated && !isPublicRoute(currentPath)) {
				goto('/login');
			} else if ($isAuthenticated && isAuthRoute(currentPath)) {
				// Redirect to dashboard if authenticated and on auth pages
				goto('/dashboard');
			}
		}
	});
</script>

<!-- front/src/routes/+layout.svelte -->

<svelte:head>
	<title>{$t('ui.appTitle')}</title>
	<meta name="description" content="Ilmora - Your gateway to quality online education" />
	<meta name="theme-color" content="#6366f1" />
</svelte:head>

{#if !$isInitialized}
	<div
		class="flex min-h-dvh flex-col items-center justify-center gap-6 bg-gray-50 dark:bg-gray-950"
	>
		<Logo size="large" />
		<div
			class="border-primary-200 border-t-primary-600 dark:border-primary-900 dark:border-t-primary-400 size-6 animate-spin rounded-full border-2"
			role="status"
			aria-label={$t('ui.loading')}
		></div>
	</div>
{:else if isFocusRoute || isAuthRoute(page.url.pathname)}
	{@render children()}
{:else if useAppShell}
	<AppShell>
		{@render children()}
	</AppShell>
{:else}
	<Header />
	<main class="pt-16">
		{#if page.url.pathname === '/'}
			{@render children()}
		{:else}
			<div class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
				{@render children()}
			</div>
		{/if}
	</main>
{/if}

<NotificationToast />

<style>
	:global(html) {
		scroll-behavior: smooth;
	}

	:global(body) {
		overflow-x: hidden;
	}

	:global(.min-h-screen) {
		min-height: 100vh;
		min-height: 100dvh;
	}
</style>

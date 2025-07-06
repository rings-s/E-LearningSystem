<!-- front/src/routes/+layout.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { browser } from '$app/environment';
	import {
		authStore,
		isAuthenticated,
		isLoading,
		isInitialized
	} from '$lib/services/auth.service.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import '../app.css';

	// Components
	import Header from '$lib/components/layout/Header.svelte';
	import NotificationToast from '$lib/components/common/NotificationToast.svelte';

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
			const currentPath = $page.url.pathname;

			// Redirect to login if not authenticated and accessing protected routes
			if (!$isAuthenticated && !isPublicRoute(currentPath)) {
				goto('/login');
			}
			// Redirect to dashboard if authenticated and on auth pages
			else if ($isAuthenticated && isAuthRoute(currentPath)) {
				goto('/dashboard');
			}
		}
	});
</script>

<svelte:head>
	<title>244SCHOOL - Modern E-Learning Platform</title>
	<meta name="description" content="244SCHOOL - Your gateway to quality online education" />
	<meta name="theme-color" content="#6366f1" />
</svelte:head>

{#if !$isInitialized}
	<!-- Loading State -->
	<div
		class="from-primary-50 to-secondary-50 flex min-h-screen items-center justify-center bg-gradient-to-br via-white dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
	>
		<div class="text-center" transition:fade>
			<div class="relative">
				<div
					class="inline-flex h-24 w-24 items-center justify-center rounded-3xl bg-white shadow-2xl dark:bg-gray-800"
				>
					<div
						class="from-primary-500 to-secondary-600 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br"
					>
						<span class="text-3xl font-bold text-white">244</span>
					</div>
				</div>
				<div
					class="from-primary-400 to-secondary-400 absolute -inset-4 animate-pulse rounded-3xl bg-gradient-to-r opacity-20 blur-xl"
				></div>
			</div>
			<h2
				class="from-primary-600 to-secondary-600 mt-8 mb-2 bg-gradient-to-r bg-clip-text text-2xl font-bold text-transparent"
			>
				244SCHOOL
			</h2>
			<p class="text-gray-600 dark:text-gray-400">Preparing your learning experience...</p>
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
		<!-- Header -->
		<Header />

		<!-- Main Content -->
		<main class="pt-16">
			<div transition:fade={{ duration: 200 }}>
				{@render children()}
			</div>
		</main>

		<!-- Global Components -->
		<NotificationToast />
	</div>
{/if}

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

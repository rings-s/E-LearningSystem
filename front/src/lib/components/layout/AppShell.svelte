<!-- front/src/lib/components/layout/AppShell.svelte -->
<!-- Signed-in layout: fixed sidebar on desktop, slide-in drawer on mobile, sticky top bar. -->
<script>
	import { page } from '$app/state';
	import { fade, fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { locale, t } from '#lib/i18n/index.js';
	import { scrollLock } from '#lib/utils/helpers.js';
	import Sidebar from './Sidebar.svelte';
	import PreferenceToggles from './PreferenceToggles.svelte';
	import Logo from '#lib/components/common/Logo.svelte';
	import NotificationBell from '#lib/components/common/NotificationBell.svelte';
	import UserMenu from '#lib/components/common/UserMenu.svelte';

	let { children } = $props();

	let drawerOpen = $state(false);
	const drawerFrom = $derived($locale === 'ar' ? 288 : -288);

	// Close the drawer whenever the route changes
	$effect(() => {
		page.url.pathname;
		drawerOpen = false;
	});

	$effect(() => {
		if (!drawerOpen) return;
		scrollLock(true);
		const onKey = (e) => e.key === 'Escape' && (drawerOpen = false);
		document.addEventListener('keydown', onKey);
		return () => {
			scrollLock(false);
			document.removeEventListener('keydown', onKey);
		};
	});
</script>

<!-- Desktop sidebar -->
<aside
	class="fixed inset-y-0 start-0 z-30 hidden w-64 border-e border-gray-200/80 bg-white lg:block dark:border-white/10 dark:bg-gray-900"
>
	<Sidebar />
</aside>

<!-- Mobile drawer -->
{#if drawerOpen}
	<div class="fixed inset-0 z-50 lg:hidden">
		<div
			class="absolute inset-0 bg-gray-950/40 backdrop-blur-sm"
			transition:fade={{ duration: 150 }}
			onclick={() => (drawerOpen = false)}
			aria-hidden="true"
		></div>
		<aside
			class="absolute inset-y-0 start-0 w-72 max-w-[85vw] bg-white shadow-xl dark:bg-gray-900"
			transition:fly={{ x: drawerFrom, duration: 200, easing: cubicOut }}
			aria-label={$t('ui.mainNavigation')}
		>
			<Sidebar onNavigate={() => (drawerOpen = false)}>
				{#snippet footer()}
					<PreferenceToggles />
				{/snippet}
			</Sidebar>
		</aside>
	</div>
{/if}

<div class="lg:ps-64">
	<header
		class="sticky top-0 z-20 flex h-16 items-center gap-2 border-b border-gray-200/80 bg-white/80 px-4 backdrop-blur-md sm:px-6 lg:px-8 dark:border-white/10 dark:bg-gray-950/80"
	>
		<button
			type="button"
			onclick={() => (drawerOpen = true)}
			class="-ms-2 flex size-10 items-center justify-center rounded-xl text-gray-600 hover:bg-gray-100 lg:hidden dark:text-gray-300 dark:hover:bg-white/10"
			aria-label={$t('ui.openNavigation')}
		>
			<svg class="size-6" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5"
				/>
			</svg>
		</button>
		<div class="lg:hidden">
			<Logo href="/dashboard" size="small" showText={false} />
		</div>

		<div class="ms-auto flex items-center gap-1">
			<div class="hidden items-center gap-1 sm:flex">
				<PreferenceToggles />
			</div>
			<NotificationBell />
			<div class="ms-1">
				<UserMenu />
			</div>
		</div>
	</header>

	<main class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
		{@render children()}
	</main>
</div>

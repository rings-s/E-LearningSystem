<!-- front/src/lib/components/layout/Header.svelte -->
<!-- Public header for the landing page, course catalog and auth pages. -->
<script>
	import { page } from '$app/state';
	import { slide } from 'svelte/transition';
	import { isAuthenticated } from '#lib/services/auth.service.js';
	import { t } from '#lib/i18n/index.js';
	import { classNames } from '#lib/utils/helpers.js';
	import Logo from '#lib/components/common/Logo.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import PreferenceToggles from './PreferenceToggles.svelte';

	let scrolled = $state(false);
	let menuOpen = $state(false);

	const links = [{ label: 'navigation.courses', href: '/courses' }];

	$effect(() => {
		const onScroll = () => (scrolled = window.scrollY > 8);
		onScroll();
		window.addEventListener('scroll', onScroll, { passive: true });
		return () => window.removeEventListener('scroll', onScroll);
	});

	$effect(() => {
		page.url.pathname;
		menuOpen = false;
	});

	const isActive = (href) => page.url.pathname.startsWith(href);
</script>

<header
	class={classNames(
		'fixed inset-x-0 top-0 z-40 border-b transition-[background-color,border-color] duration-200',
		scrolled || menuOpen
			? 'border-gray-200/80 bg-white/85 backdrop-blur-md dark:border-white/10 dark:bg-gray-950/85'
			: 'border-transparent bg-transparent'
	)}
>
	<nav class="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 sm:px-6 lg:px-8">
		<Logo href="/" />

		<div class="hidden items-center gap-1 md:flex">
			{#each links as link}
				<a
					href={link.href}
					class={classNames(
						'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
						isActive(link.href)
							? 'text-gray-900 dark:text-white'
							: 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
					)}
				>
					{$t(link.label)}
				</a>
			{/each}
		</div>

		<div class="ms-auto flex items-center gap-1">
			<div class="hidden items-center gap-1 sm:flex">
				<PreferenceToggles />
			</div>

			<div class="ms-2 hidden items-center gap-2 md:flex">
				{#if $isAuthenticated}
					<Button href="/dashboard" size="small">{$t('navigation.dashboard')}</Button>
				{:else}
					<Button href="/login" variant="ghost" size="small">{$t('auth.login')}</Button>
					<Button href="/register" size="small">{$t('auth.register')}</Button>
				{/if}
			</div>

			<button
				type="button"
				onclick={() => (menuOpen = !menuOpen)}
				class="-me-2 flex size-10 items-center justify-center rounded-xl text-gray-600 hover:bg-gray-100 md:hidden dark:text-gray-300 dark:hover:bg-white/10"
				aria-label={$t('ui.toggleMenu')}
				aria-expanded={menuOpen}
			>
				<svg
					class="size-6"
					fill="none"
					stroke="currentColor"
					stroke-width="1.75"
					viewBox="0 0 24 24"
				>
					{#if menuOpen}
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
					{:else}
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5"
						/>
					{/if}
				</svg>
			</button>
		</div>
	</nav>

	{#if menuOpen}
		<div
			transition:slide={{ duration: 200 }}
			class="border-t border-gray-200/80 px-4 pt-2 pb-4 md:hidden dark:border-white/10"
		>
			{#each links as link}
				<a
					href={link.href}
					class="block rounded-xl px-3 py-2.5 text-base font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-white/5"
				>
					{$t(link.label)}
				</a>
			{/each}
			<div class="mt-2 flex items-center gap-1 sm:hidden">
				<PreferenceToggles />
			</div>
			<div class="mt-3 grid grid-cols-2 gap-2">
				{#if $isAuthenticated}
					<Button href="/dashboard" class="col-span-2">{$t('navigation.dashboard')}</Button>
				{:else}
					<Button href="/login" variant="outline">{$t('auth.login')}</Button>
					<Button href="/register">{$t('auth.register')}</Button>
				{/if}
			</div>
		</div>
	{/if}
</header>

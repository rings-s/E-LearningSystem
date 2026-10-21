<!-- front/src/lib/components/common/UserMenu.svelte -->
<script>
	import { fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { authStore, currentUser } from '#lib/services/auth.service.js';
	import { t } from '#lib/i18n/index.js';
	import { clickOutside, getInitials } from '#lib/utils/helpers.js';

	let open = $state(false);

	const displayName = $derived(
		$currentUser?.full_name || $currentUser?.username || $currentUser?.email || ''
	);

	const handleLogout = () => {
		open = false;
		authStore.logout();
		goto('/login');
	};
</script>

<div class="relative" use:clickOutside={() => (open = false)}>
	<button
		type="button"
		onclick={() => (open = !open)}
		class="flex items-center gap-2 rounded-xl p-1 transition-colors hover:bg-gray-100 dark:hover:bg-white/10"
		aria-label={$t('ui.accountMenu')}
		aria-expanded={open}
	>
		{#if $currentUser?.avatar}
			<img src={$currentUser.avatar} alt="" class="size-8 rounded-full object-cover" />
		{:else}
			<span
				class="brand-gradient flex size-8 items-center justify-center rounded-full text-xs font-semibold text-white"
			>
				{getInitials(displayName)}
			</span>
		{/if}
	</button>

	{#if open}
		<div
			transition:fly={{ y: -6, duration: 150 }}
			class="absolute end-0 top-full z-50 mt-2 w-64 overflow-hidden rounded-2xl bg-white p-1.5 shadow-xl ring-1 ring-gray-200/80 dark:bg-gray-900 dark:ring-white/10"
		>
			<div class="px-3 py-2.5">
				<p class="truncate text-sm font-semibold text-gray-900 dark:text-white">{displayName}</p>
				{#if $currentUser?.email && $currentUser.email !== displayName}
					<p class="truncate text-xs text-gray-500 dark:text-gray-400">{$currentUser.email}</p>
				{/if}
			</div>
			<div class="my-1 h-px bg-gray-100 dark:bg-white/5"></div>
			<a
				href="/profile"
				onclick={() => (open = false)}
				class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5"
			>
				<svg class="size-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
					/>
				</svg>
				{$t('navigation.profile')}
			</a>
			<button
				type="button"
				onclick={handleLogout}
				class="text-danger-600 hover:bg-danger-50 dark:text-danger-400 dark:hover:bg-danger-400/10 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
			>
				<svg class="size-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"
					/>
				</svg>
				{$t('auth.logout')}
			</button>
		</div>
	{/if}
</div>

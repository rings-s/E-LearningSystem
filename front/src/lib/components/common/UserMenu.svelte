<!-- front/src/lib/components/common/UserMenu.svelte -->
<script>
	import { fade } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.store.js';
	import { currentUser } from '$lib/services/auth.service.js';
	import { t } from '$lib/i18n/index.js';
	import { clickOutside, getInitials } from '$lib/utils/helpers.js';

	let showDropdown = $state(false);

	const menuItems = [
		{ label: $t('navigation.profile'), href: '/profile', icon: 'user' },
		{ label: $t('navigation.settings'), href: '/settings', icon: 'cog' },
		{ label: $t('navigation.help'), href: '/help', icon: 'question' },
		{ divider: true },
		{ label: $t('auth.logout'), action: handleLogout, icon: 'logout', variant: 'danger' }
	];

	async function handleLogout() {
		authStore.logout();
		goto('/login');
	}

	const icons = {
		user: '<path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />',
		cog: '<path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />',
		question:
			'<path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />',
		logout:
			'<path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />'
	};
</script>

<div class="relative">
	<button
		onclick={() => (showDropdown = !showDropdown)}
		class="flex items-center gap-2 rounded-lg p-1.5 transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
	>
		{#if $currentUser?.avatar}
			<img
				src={$currentUser.avatar}
				alt={$currentUser.full_name}
				class="h-8 w-8 rounded-full object-cover"
			/>
		{:else}
			<div
				class="from-primary-400 to-primary-600 flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br text-sm font-medium text-white"
			>
				{getInitials($currentUser?.full_name || $currentUser?.email || '')}
			</div>
		{/if}

		<svg
			class="h-4 w-4 text-gray-500 dark:text-gray-400"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	{#if showDropdown}
		<div
			class="absolute right-0 z-50 mt-2 w-56 rounded-xl border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
			transition:fade={{ duration: 200 }}
			use:clickOutside={() => (showDropdown = false)}
		>
			<!-- User Info -->
			<div class="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
				<p class="text-sm font-medium text-gray-900 dark:text-white">
					{$currentUser?.full_name || $currentUser?.email}
				</p>
				{#if $currentUser?.email}
					<p class="mt-0.5 truncate text-xs text-gray-500 dark:text-gray-400">
						{$currentUser.email}
					</p>
				{/if}
			</div>

			<!-- Menu Items -->
			<div class="py-1">
				{#each menuItems as item}
					{#if item.divider}
						<hr class="my-1 border-gray-200 dark:border-gray-700" />
					{:else if item.href}
						<a
							href={item.href}
							onclick={() => (showDropdown = false)}
							class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
						>
							<svg
								class="h-5 w-5 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								{@html icons[item.icon]}
							</svg>
							{item.label}
						</a>
					{:else}
						<button
							onclick={() => {
								item.action();
								showDropdown = false;
							}}
							class="flex w-full items-center gap-3 px-4 py-2 text-left text-sm transition-colors hover:bg-gray-100 dark:hover:bg-gray-700 {item.variant ===
							'danger'
								? 'text-red-600 dark:text-red-400'
								: 'text-gray-700 dark:text-gray-300'}"
						>
							<svg
								class="h-5 w-5 {item.variant === 'danger'
									? 'text-red-500 dark:text-red-400'
									: 'text-gray-400'}"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								{@html icons[item.icon]}
							</svg>
							{item.label}
						</button>
					{/if}
				{/each}
			</div>
		</div>
	{/if}
</div>

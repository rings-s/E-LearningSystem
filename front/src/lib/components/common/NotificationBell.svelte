<!-- front/src/lib/components/common/NotificationBell.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import { coreApi } from '#lib/apis/core.js';
	import { formatters } from '#lib/utils/formatters.js';
	import { t, locale } from '#lib/i18n/index.js';
	import { clickOutside } from '#lib/utils/helpers.js';

	let showDropdown = $state(false);
	let notifications = $state([]);
	let unreadCount = $state(0);
	let loading = $state(false);

	onMount(async () => {
		await fetchUnreadCount();
	});

	const fetchUnreadCount = async () => {
		try {
			const response = await coreApi.getUnreadCount();
			unreadCount = response.unread_count;
		} catch (error) {
			console.error('Failed to fetch unread count:', error);
		}
	};

	const fetchNotifications = async () => {
		loading = true;
		try {
			const response = await coreApi.getNotifications({ is_read: false });
			notifications = response.results || response;
		} catch (error) {
			console.error('Failed to fetch notifications:', error);
		} finally {
			loading = false;
		}
	};

	const toggleDropdown = async () => {
		showDropdown = !showDropdown;
		if (showDropdown && notifications.length === 0) {
			await fetchNotifications();
		}
	};

	const markAsRead = async (notification) => {
		try {
			await coreApi.markNotificationRead(notification.uuid);
			notification.is_read = true;
			unreadCount = Math.max(0, unreadCount - 1);
		} catch (error) {
			console.error('Failed to mark notification as read:', error);
		}
	};

	const markAllAsRead = async () => {
		try {
			await coreApi.markAllNotificationsRead();
			notifications = notifications.map((n) => ({ ...n, is_read: true }));
			unreadCount = 0;
		} catch (error) {
			console.error('Failed to mark all as read:', error);
		}
	};

	const getNotificationIcon = (type) => {
		const icons = {
			enrollment:
				'<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />',
			course_update:
				'<path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />',
			quiz_result:
				'<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />',
			forum_reply:
				'<path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />',
			certificate_ready:
				'<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />'
		};
		return icons[type] || icons.enrollment;
	};
</script>

<div class="relative">
	<button
		type="button"
		onclick={toggleDropdown}
		class="relative flex size-10 items-center justify-center rounded-xl text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-white/10 dark:hover:text-white"
		aria-label={$t('notifications.notifications')}
		aria-expanded={showDropdown}
	>
		<svg class="size-5" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"
			/>
		</svg>
		{#if unreadCount > 0}
			<span
				class="bg-danger-500 absolute end-1.5 top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px] font-semibold text-white ring-2 ring-white dark:ring-gray-950"
				transition:scale
			>
				{unreadCount > 9 ? '9+' : unreadCount}
			</span>
		{/if}
	</button>

	{#if showDropdown}
		<div
			class="fixed inset-x-3 top-16 z-50 overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-gray-200/80 sm:absolute sm:inset-x-auto sm:end-0 sm:top-full sm:mt-2 sm:w-96 dark:bg-gray-900 dark:ring-white/10"
			transition:fade={{ duration: 150 }}
			use:clickOutside={() => (showDropdown = false)}
		>
			<div class="flex items-center justify-between px-4 py-3">
				<h3 class="text-sm font-semibold text-gray-900 dark:text-white">
					{$t('notifications.notifications')}
				</h3>
				{#if unreadCount > 0}
					<button
						type="button"
						onclick={markAllAsRead}
						class="text-primary-600 hover:text-primary-700 dark:text-primary-400 text-xs font-medium"
					>
						{$t('notifications.markAllRead')}
					</button>
				{/if}
			</div>

			<div
				class="max-h-[60dvh] scrollbar-thin overflow-y-auto border-t border-gray-100 dark:border-white/5"
			>
				{#if loading}
					<div class="space-y-3 p-4">
						{#each Array(3) as _}
							<div class="flex gap-3">
								<div class="skeleton size-9 rounded-full"></div>
								<div class="flex-1 space-y-2">
									<div class="skeleton h-3 w-2/3"></div>
									<div class="skeleton h-3 w-full"></div>
								</div>
							</div>
						{/each}
					</div>
				{:else if notifications.length === 0}
					<div class="px-4 py-10 text-center">
						<p class="text-sm font-medium text-gray-900 dark:text-white">{$t('ui.allCaughtUp')}</p>
						<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
							{$t('notifications.noNotifications')}
						</p>
					</div>
				{:else}
					{#each notifications as notification}
						<button
							type="button"
							onclick={() => markAsRead(notification)}
							class="flex w-full gap-3 px-4 py-3 text-start transition-colors hover:bg-gray-50 dark:hover:bg-white/5"
						>
							<span
								class="bg-primary-50 text-primary-600 dark:bg-primary-400/10 dark:text-primary-400 flex size-9 shrink-0 items-center justify-center rounded-full"
							>
								<svg
									class="size-4"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									viewBox="0 0 24 24"
								>
									{@html getNotificationIcon(notification.notification_type)}
								</svg>
							</span>
							<span class="min-w-0 flex-1">
								<span class="block text-sm font-medium text-gray-900 dark:text-white">
									{notification.title}
								</span>
								<span class="line-clamp-2 block text-xs text-gray-500 dark:text-gray-400">
									{notification.message}
								</span>
								<span class="mt-1 block text-xs text-gray-400 dark:text-gray-500">
									{formatters.relativeTime(notification.created_at, $locale)}
								</span>
							</span>
							{#if !notification.is_read}
								<span class="bg-primary-500 mt-1.5 size-2 shrink-0 rounded-full"></span>
							{/if}
						</button>
					{/each}
				{/if}
			</div>
		</div>
	{/if}
</div>

<!-- front/src/lib/components/common/NotificationBell.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import { coreApi } from '$lib/apis/core.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { t, locale } from '$lib/i18n/index.js';
	import { clickOutside } from '$lib/utils/helpers.js';

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
		onclick={toggleDropdown}
		class="relative rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200"
		aria-label="Notifications"
	>
		<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
			/>
		</svg>

		{#if unreadCount > 0}
			<span
				class="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white"
				transition:scale
			>
				{unreadCount > 9 ? '9+' : unreadCount}
			</span>
		{/if}
	</button>

	{#if showDropdown}
		<div
			class="absolute right-0 z-50 mt-2 w-80 rounded-xl border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
			transition:fade={{ duration: 200 }}
			use:clickOutside={() => (showDropdown = false)}
		>
			<!-- Header -->
			<div class="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
				<div class="flex items-center justify-between">
					<h3 class="text-base font-semibold text-gray-900 dark:text-white">
						{$t('notifications.notifications')}
					</h3>
					{#if unreadCount > 0}
						<button
							onclick={markAllAsRead}
							class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-xs"
						>
							{$t('notifications.markAllRead')}
						</button>
					{/if}
				</div>
			</div>

			<!-- Notifications List -->
			<div class="max-h-96 overflow-y-auto">
				{#if loading}
					<div class="px-4 py-8 text-center">
						<div
							class="inline-flex h-8 w-8 animate-pulse items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700"
						>
							<div class="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600"></div>
						</div>
						<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
							{$t('common.loading')}
						</p>
					</div>
				{:else if notifications.length === 0}
					<div class="px-4 py-8 text-center">
						<svg
							class="mx-auto h-12 w-12 text-gray-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
							/>
						</svg>
						<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
							{$t('notifications.noNotifications')}
						</p>
					</div>
				{:else}
					{#each notifications as notification}
						<button
							onclick={() => markAsRead(notification)}
							class="w-full border-b border-gray-100 px-4 py-3 transition-colors last:border-b-0 hover:bg-gray-50 dark:border-gray-700/50 dark:hover:bg-gray-700/50"
						>
							<div class="flex gap-3">
								<div
									class="bg-primary-100 dark:bg-primary-900/30 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full"
								>
									<svg
										class="text-primary-600 dark:text-primary-400 h-5 w-5"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										{@html getNotificationIcon(notification.notification_type)}
									</svg>
								</div>
								<div class="flex-1 text-left">
									<p class="text-sm font-medium text-gray-900 dark:text-white">
										{notification.title}
									</p>
									<p class="line-clamp-2 text-xs text-gray-500 dark:text-gray-400">
										{notification.message}
									</p>
									<p class="mt-1 text-xs text-gray-400 dark:text-gray-500">
										{formatters.relativeTime(notification.created_at, $locale)}
									</p>
								</div>
								{#if !notification.is_read}
									<div class="bg-primary-500 mt-2 h-2 w-2 flex-shrink-0 rounded-full"></div>
								{/if}
							</div>
						</button>
					{/each}
				{/if}
			</div>

			<!-- Footer -->
			<div class="border-t border-gray-200 px-4 py-3 dark:border-gray-700">
				<a
					href="/notifications"
					class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 block text-center text-sm"
				>
					{$t('actions.viewAll')}
				</a>
			</div>
		</div>
	{/if}
</div>

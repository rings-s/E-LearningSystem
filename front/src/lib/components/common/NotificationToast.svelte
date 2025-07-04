<!-- front/src/lib/components/common/NotificationToast.svelte -->
<script>
	import { fade, fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { notificationStore } from '$lib/stores/notification.store.js';

	const typeStyles = {
		success: {
			bg: 'from-green-500/20 to-green-600/20',
			border: 'border-green-500/30',
			icon: 'text-green-600 dark:text-green-400',
			iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
		},
		error: {
			bg: 'from-red-500/20 to-red-600/20',
			border: 'border-red-500/30',
			icon: 'text-red-600 dark:text-red-400',
			iconPath: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
		},
		warning: {
			bg: 'from-yellow-500/20 to-yellow-600/20',
			border: 'border-yellow-500/30',
			icon: 'text-yellow-600 dark:text-yellow-400',
			iconPath:
				'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
		},
		info: {
			bg: 'from-blue-500/20 to-blue-600/20',
			border: 'border-blue-500/30',
			icon: 'text-blue-600 dark:text-blue-400',
			iconPath: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
		}
	};
</script>

<div
	class="toast-container fixed top-4 right-4 z-50 space-y-3"
	aria-live="polite"
	aria-atomic="true"
>
	{#each $notificationStore as notification (notification.id)}
		<div
			class="glass mb-3 rounded-xl border p-4 {typeStyles[notification.type]
				.border} bg-gradient-to-r {typeStyles[notification.type].bg} max-w-sm shadow-lg"
			transition:fly={{ x: 300, duration: 300, easing: quintOut }}
		>
			<div class="flex items-start space-x-3">
				<div class="flex-shrink-0">
					<svg
						class="h-6 w-6 {typeStyles[notification.type].icon}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d={typeStyles[notification.type].iconPath}
						/>
					</svg>
				</div>
				<div class="min-w-0 flex-1">
					<p class="text-sm font-medium text-gray-900 dark:text-white">
						{notification.title}
					</p>
					{#if notification.message}
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{notification.message}
						</p>
					{/if}
				</div>
				<button
					onclick={() => notificationStore.remove(notification.id)}
					class="ml-4 flex-shrink-0 rounded-lg p-1 transition-colors hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
					aria-label="Close notification"
				>
					<svg class="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>
		</div>
	{/each}
</div>

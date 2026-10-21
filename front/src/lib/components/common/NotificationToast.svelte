<!-- front/src/lib/components/common/NotificationToast.svelte -->
<!-- Renders toasts queued with uiStore.showNotification({ type, title, message }) -->
<script>
	import { t } from '#lib/i18n/index.js';
	import { fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { uiStore } from '#lib/stores/ui.store.js';

	const types = {
		success: {
			icon: 'text-success-600 dark:text-success-400',
			path: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
		},
		error: {
			icon: 'text-danger-600 dark:text-danger-400',
			path: 'M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z'
		},
		warning: {
			icon: 'text-warning-600 dark:text-warning-400',
			path: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z'
		},
		info: {
			icon: 'text-primary-600 dark:text-primary-400',
			path: 'M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z'
		}
	};

	const toasts = $derived($uiStore.notifications ?? []);
</script>

<div
	class="pointer-events-none fixed inset-x-4 top-4 z-[60] flex flex-col items-center gap-3 sm:inset-x-auto sm:end-4 sm:items-end"
	aria-live="polite"
>
	{#each toasts as toast (toast.id)}
		{@const style = types[toast.type] ?? types.info}
		<div
			class="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-2xl bg-white/95 p-4 shadow-lg ring-1 ring-gray-200/80 backdrop-blur dark:bg-gray-900/95 dark:ring-white/10"
			role={toast.type === 'error' ? 'alert' : 'status'}
			transition:fly={{ y: -12, duration: 200, easing: cubicOut }}
		>
			<svg
				class="size-5 shrink-0 {style.icon}"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				viewBox="0 0 24 24"
				aria-hidden="true"
			>
				<path stroke-linecap="round" stroke-linejoin="round" d={style.path} />
			</svg>
			<div class="min-w-0 flex-1">
				{#if toast.title}
					<p class="text-sm font-semibold text-gray-900 dark:text-white">{toast.title}</p>
				{/if}
				{#if toast.message}
					<p class="mt-0.5 text-sm text-gray-600 dark:text-gray-400">{toast.message}</p>
				{/if}
			</div>
			<button
				type="button"
				onclick={() => uiStore.removeNotification(toast.id)}
				class="-m-1 shrink-0 rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-white/10 dark:hover:text-gray-200"
				aria-label={$t('ui.dismiss')}
			>
				<svg class="size-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>
	{/each}
</div>

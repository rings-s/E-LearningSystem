<!-- front/src/lib/components/common/Modal.svelte -->
<script>
	import { t } from '#lib/i18n/index.js';
	import { fade, fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { classNames, portal, focusTrap, scrollLock } from '#lib/utils/helpers.js';

	let {
		open = false,
		onClose = () => {},
		title = '',
		size = 'medium', // 'small' | 'medium' | 'large' | 'xl' | 'full'
		closeOnBackdrop = true,
		closeOnEscape = true,
		class: className = '',
		children
	} = $props();

	const titleId = `modal-${Math.random().toString(36).slice(2, 11)}`;

	const sizes = {
		small: 'sm:max-w-md',
		medium: 'sm:max-w-lg',
		large: 'sm:max-w-2xl',
		xl: 'sm:max-w-4xl',
		full: 'sm:max-w-[calc(100vw-2rem)]'
	};

	$effect(() => {
		if (!open) return;
		scrollLock(true);
		const handleKeydown = (e) => {
			if (e.key === 'Escape' && closeOnEscape) onClose();
		};
		document.addEventListener('keydown', handleKeydown);
		return () => {
			scrollLock(false);
			document.removeEventListener('keydown', handleKeydown);
		};
	});
</script>

{#if open}
	<div class="fixed inset-0 z-50" use:portal>
		<div
			class="fixed inset-0 bg-gray-950/40 backdrop-blur-sm dark:bg-black/60"
			transition:fade={{ duration: 150 }}
			onclick={() => closeOnBackdrop && onClose()}
			aria-hidden="true"
		></div>

		<!-- Bottom sheet on phones, centered dialog from sm: up -->
		<div class="fixed inset-0 flex items-end justify-center sm:items-center sm:p-6">
			<div
				class={classNames(
					'relative flex max-h-[92dvh] w-full flex-col overflow-hidden bg-white shadow-xl ring-1 ring-gray-200/80',
					'rounded-t-3xl sm:rounded-2xl dark:bg-gray-900 dark:ring-white/10',
					sizes[size] ?? sizes.medium,
					className
				)}
				transition:fly={{ y: 24, duration: 200, easing: cubicOut }}
				use:focusTrap
				role="dialog"
				aria-modal="true"
				aria-labelledby={title ? titleId : undefined}
			>
				<div class="flex items-center justify-between gap-4 px-5 pt-5 pb-3 sm:px-6">
					<h2 id={titleId} class="text-lg font-semibold text-gray-900 dark:text-white">
						{title}
					</h2>
					<button
						type="button"
						onclick={onClose}
						class="-me-2 rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-white/10 dark:hover:text-gray-200"
						aria-label={$t('ui.close')}
					>
						<svg
							class="size-5"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							viewBox="0 0 24 24"
						>
							<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>

				<div class="overflow-y-auto px-5 pb-6 sm:px-6">
					{@render children?.()}
				</div>
			</div>
		</div>
	</div>
{/if}

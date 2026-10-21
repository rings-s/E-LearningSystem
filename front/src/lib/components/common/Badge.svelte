<!-- front/src/lib/components/common/Badge.svelte -->
<script>
	import { t } from '#lib/i18n/index.js';
	import { classNames } from '#lib/utils/helpers.js';

	let {
		variant = 'default',
		size = 'medium', // 'small' | 'medium' | 'large'
		dot = false,
		removable = false,
		onRemove = () => {},
		class: className = '',
		children
	} = $props();

	const variants = {
		default:
			'bg-gray-100 text-gray-700 ring-gray-500/10 dark:bg-white/10 dark:text-gray-300 dark:ring-white/10',
		primary:
			'bg-primary-50 text-primary-700 ring-primary-600/15 dark:bg-primary-400/10 dark:text-primary-300 dark:ring-primary-400/20',
		info: 'bg-primary-50 text-primary-700 ring-primary-600/15 dark:bg-primary-400/10 dark:text-primary-300 dark:ring-primary-400/20',
		secondary:
			'bg-secondary-50 text-secondary-700 ring-secondary-600/15 dark:bg-secondary-400/10 dark:text-secondary-300 dark:ring-secondary-400/20',
		success:
			'bg-success-50 text-success-700 ring-success-600/20 dark:bg-success-400/10 dark:text-success-300 dark:ring-success-400/20',
		warning:
			'bg-warning-50 text-warning-800 ring-warning-600/20 dark:bg-warning-400/10 dark:text-warning-300 dark:ring-warning-400/20',
		danger:
			'bg-danger-50 text-danger-700 ring-danger-600/15 dark:bg-danger-400/10 dark:text-danger-300 dark:ring-danger-400/20',
		accent:
			'bg-accent-50 text-accent-800 ring-accent-600/20 dark:bg-accent-400/10 dark:text-accent-300 dark:ring-accent-400/20',
		outline: 'bg-transparent text-gray-700 ring-gray-300 dark:text-gray-300 dark:ring-white/20',
		white:
			'bg-white/90 text-gray-900 ring-black/5 shadow-xs backdrop-blur dark:bg-gray-900/80 dark:text-white dark:ring-white/10'
	};

	const sizes = {
		small: 'px-2 py-0.5 text-xs gap-1',
		medium: 'px-2.5 py-0.5 text-xs gap-1.5',
		large: 'px-3 py-1 text-sm gap-1.5'
	};
</script>

<span
	class={classNames(
		'inline-flex items-center rounded-full font-medium whitespace-nowrap ring-1 ring-inset',
		variants[variant] ?? variants.default,
		sizes[size] ?? sizes.medium,
		className
	)}
>
	{#if dot}
		<span class="size-1.5 rounded-full bg-current" aria-hidden="true"></span>
	{/if}

	{@render children?.()}

	{#if removable}
		<button
			type="button"
			onclick={onRemove}
			class="-me-1 inline-flex size-4 items-center justify-center rounded-full transition-colors hover:bg-black/10 dark:hover:bg-white/10"
			aria-label={$t('ui.remove')}
		>
			<svg class="size-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
			</svg>
		</button>
	{/if}
</span>

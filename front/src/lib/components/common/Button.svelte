<!-- front/src/lib/components/common/Button.svelte -->
<script>
	import { classNames } from '#lib/utils/helpers.js';

	let {
		variant = 'primary', // 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'warning'
		size = 'medium', // 'small' | 'medium' | 'large'
		fullWidth = false,
		loading = false,
		disabled = false,
		type = 'button',
		href = null,
		onclick = () => {},
		class: className = '',
		children,
		iconLeft = null,
		iconRight = null,
		...rest
	} = $props();

	const variants = {
		primary:
			'bg-primary-600 text-white shadow-xs inset-ring inset-ring-white/10 hover:bg-primary-700 active:bg-primary-800 dark:bg-primary-500 dark:hover:bg-primary-400',
		secondary:
			'bg-gray-100 text-gray-900 hover:bg-gray-200 active:bg-gray-300 dark:bg-white/10 dark:text-white dark:hover:bg-white/15',
		outline:
			'bg-white text-gray-800 shadow-xs ring-1 ring-gray-200 ring-inset hover:bg-gray-50 hover:ring-gray-300 dark:bg-white/5 dark:text-gray-100 dark:ring-white/10 dark:hover:bg-white/10',
		ghost:
			'text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-white/10 dark:hover:text-white',
		danger:
			'bg-danger-600 text-white shadow-xs hover:bg-danger-700 active:bg-danger-800 dark:bg-danger-500 dark:hover:bg-danger-400',
		success:
			'bg-success-600 text-white shadow-xs hover:bg-success-700 active:bg-success-800 dark:bg-success-500 dark:hover:bg-success-400',
		warning:
			'bg-warning-500 text-gray-950 shadow-xs hover:bg-warning-400 active:bg-warning-600 dark:bg-warning-400 dark:hover:bg-warning-300'
	};

	const sizes = {
		small: 'h-8 px-3 text-sm gap-1.5 rounded-lg',
		medium: 'h-10 px-4 text-sm gap-2 rounded-xl',
		large: 'h-12 px-6 text-base gap-2 rounded-xl'
	};

	const iconSize = size === 'large' ? 'size-5' : 'size-4';

	const classes = $derived(
		classNames(
			'inline-flex shrink-0 items-center justify-center font-medium whitespace-nowrap select-none',
			'transition-[background-color,color,box-shadow] duration-150',
			'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500',
			'disabled:pointer-events-none disabled:opacity-50 aria-disabled:pointer-events-none aria-disabled:opacity-50',
			variants[variant] ?? variants.primary,
			sizes[size] ?? sizes.medium,
			fullWidth && 'w-full',
			className
		)
	);

	const handleClick = (e) => {
		if (!disabled && !loading) onclick(e);
	};
</script>

{#snippet content()}
	{#if loading}
		<svg class="{iconSize} animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
			></circle>
			<path class="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
		</svg>
	{:else if iconLeft}
		<svg
			class={iconSize}
			fill="none"
			stroke="currentColor"
			stroke-width="2"
			viewBox="0 0 24 24"
			aria-hidden="true"
		>
			{@html iconLeft}
		</svg>
	{/if}
	{@render children?.()}
	{#if iconRight && !loading}
		<svg
			class={iconSize}
			fill="none"
			stroke="currentColor"
			stroke-width="2"
			viewBox="0 0 24 24"
			aria-hidden="true"
		>
			{@html iconRight}
		</svg>
	{/if}
{/snippet}

{#if href && !disabled}
	<a {href} class={classes} aria-busy={loading} {...rest}>
		{@render content()}
	</a>
{:else}
	<button
		{type}
		disabled={disabled || loading}
		class={classes}
		aria-busy={loading}
		onclick={handleClick}
		{...rest}
	>
		{@render content()}
	</button>
{/if}

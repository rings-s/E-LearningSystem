<!-- front/src/lib/components/common/Card.svelte -->
<script>
	import { classNames } from '#lib/utils/helpers.js';

	let {
		children,
		variant = 'default', // 'default' | 'bordered' | 'elevated' | 'subtle'
		padding = 'default', // 'none' | 'small' | 'default' | 'large'
		hoverable = false,
		onclick = null,
		class: className = '',
		...restProps
	} = $props();

	const variants = {
		default: 'bg-white ring-1 ring-gray-200/80 shadow-xs dark:bg-gray-900 dark:ring-white/10',
		bordered: 'bg-white ring-1 ring-gray-200/80 shadow-xs dark:bg-gray-900 dark:ring-white/10',
		elevated: 'bg-white ring-1 ring-gray-200/60 shadow-lg dark:bg-gray-900 dark:ring-white/10',
		subtle: 'bg-gray-50 ring-1 ring-gray-200/60 dark:bg-white/5 dark:ring-white/5'
	};

	const paddings = {
		none: '',
		small: 'p-4',
		default: 'p-5 sm:p-6',
		large: 'p-6 sm:p-8'
	};

	const classes = $derived(
		classNames(
			'rounded-2xl transition-[box-shadow,transform] duration-200',
			variants[variant] ?? variants.default,
			paddings[padding] ?? paddings.default,
			(hoverable || onclick) && 'hover:-translate-y-0.5 hover:shadow-md',
			className
		)
	);
</script>

{#if onclick}
	<button
		type="button"
		{onclick}
		class={classNames(
			classes,
			'focus-visible:outline-primary-500 w-full text-start focus-visible:outline-2 focus-visible:outline-offset-2'
		)}
		{...restProps}
	>
		{@render children?.()}
	</button>
{:else}
	<div class={classes} {...restProps}>
		{@render children?.()}
	</div>
{/if}

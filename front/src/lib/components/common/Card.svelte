<!-- front/src/lib/components/common/Card.svelte -->
<script>
	import { classNames } from '$lib/utils/helpers.js';

	let {
		children,
		variant = 'default', // 'default', 'bordered', 'elevated'
		padding = 'default', // 'none', 'small', 'default', 'large'
		hoverable = false,
		onclick = null,
		class: className = '',
		...restProps
	} = $props();

	const variants = {
		default: 'bg-white dark:bg-gray-800',
		bordered: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
		elevated: 'bg-white dark:bg-gray-800 shadow-lg'
	};

	const paddings = {
		none: '',
		small: 'p-4',
		default: 'p-6',
		large: 'p-8'
	};

	const isInteractive = onclick !== null;
</script>

{#if isInteractive}
	<button
		{onclick}
		class={classNames(
			'w-full rounded-xl text-left transition-all duration-200',
			variants[variant],
			paddings[padding],
			hoverable && 'transform hover:scale-[1.01] hover:shadow-md dark:hover:shadow-lg',
			isInteractive && 'focus:ring-primary-500 cursor-pointer focus:ring-2 focus:outline-none',
			className
		)}
		{...restProps}
	>
		{@render children()}
	</button>
{:else}
	<div
		class={classNames(
			'rounded-xl transition-all duration-200',
			variants[variant],
			paddings[padding],
			hoverable && 'hover:shadow-md dark:hover:shadow-lg',
			className
		)}
		{...restProps}
	>
		{@render children()}
	</div>
{/if}

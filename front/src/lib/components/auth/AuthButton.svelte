<script>
	import { classNames } from '$lib/utils/helpers.js';

	let {
		variant = 'primary',
		size = 'large',
		fullWidth = true,
		loading = false,
		disabled = false,
		type = 'button',
		onclick = () => {},
		children,
		...rest
	} = $props();

	const variants = {
		primary:
			'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white shadow-lg shadow-primary-500/25',
		secondary:
			'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700',
		ghost:
			'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
	};

	const sizes = {
		medium: 'px-6 py-3 text-sm',
		large: 'px-8 py-4 text-base'
	};
</script>

<button
	{type}
	{disabled}
	class={classNames(
		'focus:ring-primary-500 inline-flex transform items-center justify-center rounded-2xl font-semibold transition-all duration-200 focus:ring-2 focus:ring-offset-2 focus:outline-none dark:focus:ring-offset-gray-800',
		'hover:scale-[1.02] active:scale-[0.98]',
		variants[variant],
		sizes[size],
		fullWidth && 'w-full',
		(disabled || loading) && 'cursor-not-allowed opacity-50 hover:scale-100'
	)}
	{onclick}
	{...rest}
>
	{#if loading}
		<svg class="mr-3 -ml-1 h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
			></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			></path>
		</svg>
		Loading...
	{:else}
		{@render children()}
	{/if}
</button>

<script>
	import { fade } from 'svelte/transition';
	import { classNames } from '$lib/utils/helpers.js';

	let {
		type = 'text',
		name = '',
		label = '',
		placeholder = '',
		value = '',
		error = '',
		hint = '',
		disabled = false,
		required = false,
		icon = null,
		class: className = '',
		...rest
	} = $props();

	let focused = $state(false);
	let inputElement;
	const id = `input-${Math.random().toString(36).substr(2, 9)}`;
</script>

<div class={classNames('form-group space-y-2', className)}>
	{#if label}
		<label for={id} class="block text-sm font-semibold text-gray-700 dark:text-gray-300">
			{label}
			{#if required}
				<span class="ml-1 text-red-500">*</span>
			{/if}
		</label>
	{/if}

	<div class="relative">
		{#if icon}
			<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
				<svg
					class="h-5 w-5 text-gray-400 {focused ? 'text-primary-500' : ''} transition-colors"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					{@html icon}
				</svg>
			</div>
		{/if}

		<input
			bind:this={inputElement}
			{id}
			{type}
			{name}
			{value}
			{placeholder}
			{disabled}
			{required}
			class={classNames(
				'block w-full rounded-2xl border-0 px-4 py-4 text-gray-900 placeholder-gray-400 shadow-sm ring-1 transition-all duration-200 ring-inset dark:text-white dark:placeholder-gray-500',
				'bg-gray-50/50 backdrop-blur-sm dark:bg-gray-700/50',
				'focus:ring-primary-500 focus:bg-white focus:ring-2 focus:ring-inset dark:focus:bg-gray-700',
				icon && 'pl-12',
				error
					? 'ring-red-300 focus:ring-red-500 dark:ring-red-600'
					: 'ring-gray-200 dark:ring-gray-600',
				disabled && 'cursor-not-allowed opacity-50',
				'text-sm'
			)}
			onfocus={() => (focused = true)}
			onblur={() => (focused = false)}
			oninput={(e) => (value = e.target.value)}
			{...rest}
		/>
	</div>

	{#if hint && !error}
		<p class="text-xs text-gray-500 dark:text-gray-400" transition:fade>
			{hint}
		</p>
	{/if}

	{#if error}
		<p class="flex items-center gap-1 text-xs text-red-600 dark:text-red-400" transition:fade>
			<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			{error}
		</p>
	{/if}
</div>

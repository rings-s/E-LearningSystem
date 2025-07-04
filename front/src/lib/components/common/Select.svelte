<!-- front/src/lib/components/common/Select.svelte -->
<script>
	import { classNames } from '$lib/utils/helpers.js';

	let {
		name = '',
		label = '',
		value = $bindable(''),
		options = [],
		placeholder = 'Select an option',
		error = '',
		disabled = false,
		required = false,
		class: className = '',
		onchange = () => {},
		...rest
	} = $props();

	const id = `select-${Math.random().toString(36).substr(2, 9)}`;
</script>

<div class={classNames('form-group', className)}>
	{#if label}
		<label for={id} class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
			{label}
			{#if required}
				<span class="text-red-500">*</span>
			{/if}
		</label>
	{/if}

	<div class="relative">
		<select
			{id}
			{name}
			bind:value
			{disabled}
			{required}
			class={classNames(
				'block w-full rounded-lg border transition-colors duration-200',
				'text-sm text-gray-900 dark:text-white',
				'bg-white dark:bg-gray-800',
				'focus:ring-primary-500 focus:border-primary-500 focus:ring-2',
				error ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600',
				disabled && 'cursor-not-allowed opacity-50',
				'px-3 py-2 pr-8'
			)}
			{onchange}
			{...rest}
		>
			{#if placeholder}
				<option value="" disabled selected={!value}>
					{placeholder}
				</option>
			{/if}

			{#each options as option}
				{#if typeof option === 'object'}
					<option value={option.value} disabled={option.disabled}>
						{option.label}
					</option>
				{:else}
					<option value={option}>
						{option}
					</option>
				{/if}
			{/each}
		</select>

		<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
			<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</div>
	</div>

	{#if error}
		<p class="mt-1 text-xs text-red-600 dark:text-red-400">
			{error}
		</p>
	{/if}
</div>

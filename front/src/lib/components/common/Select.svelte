<!-- front/src/lib/components/common/Select.svelte -->
<script>
	import { classNames } from '#lib/utils/helpers.js';

	let {
		id = `select-${Math.random().toString(36).slice(2, 11)}`,
		name = '',
		label = '',
		value = $bindable(null),
		options = [],
		placeholder = 'Select an option',
		error = '',
		disabled = false,
		required = false,
		allowNull = false,
		class: className = '',
		...rest
	} = $props();
</script>

<div class={classNames('space-y-1.5', className)}>
	{#if label}
		<label for={id} class="block text-sm font-medium text-gray-800 dark:text-gray-200">
			{label}
			{#if required}<span class="text-danger-500">*</span>{/if}
		</label>
	{/if}

	<div class="relative">
		<select
			{id}
			{name}
			bind:value
			{disabled}
			{required}
			aria-invalid={error ? 'true' : undefined}
			class={classNames(
				'block h-11 w-full appearance-none rounded-xl border-0 bg-white ps-3.5 pe-10 text-sm text-gray-900 shadow-xs ring-1 ring-inset',
				'focus:ring-2 focus:outline-none dark:bg-white/5 dark:text-white',
				'disabled:cursor-not-allowed disabled:opacity-60',
				error
					? 'ring-danger-400 focus:ring-danger-500'
					: 'focus:ring-primary-500 ring-gray-200 dark:ring-white/10'
			)}
			{...rest}
		>
			{#if placeholder}
				<option value={allowNull ? null : ''} disabled={!allowNull}>{placeholder}</option>
			{/if}
			{#each options as option}
				{#if typeof option === 'object'}
					<option value={option.value} disabled={option.disabled}>{option.label}</option>
				{:else}
					<option value={option}>{option}</option>
				{/if}
			{/each}
		</select>

		<svg
			class="pointer-events-none absolute inset-y-0 end-3 my-auto size-4 text-gray-400"
			fill="none"
			stroke="currentColor"
			stroke-width="2"
			viewBox="0 0 24 24"
			aria-hidden="true"
		>
			<path stroke-linecap="round" stroke-linejoin="round" d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
		</svg>
	</div>

	{#if error}
		<p class="text-danger-600 dark:text-danger-400 text-xs">{error}</p>
	{/if}
</div>

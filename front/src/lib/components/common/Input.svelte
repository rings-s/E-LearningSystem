<!-- front/src/lib/components/common/Input.svelte -->
<script>
	import { t } from '#lib/i18n/index.js';
	import { classNames } from '#lib/utils/helpers.js';
	import { slide } from 'svelte/transition';

	let {
		type = 'text',
		id = `input-${Math.random().toString(36).slice(2, 11)}`,
		name = '',
		label = '',
		placeholder = '',
		value = $bindable(''),
		error = '',
		disabled = false,
		required = false,
		readonly = false,
		icon = null, // SVG path markup, e.g. "<path d='...' />"
		hint = '',
		helperText = '',
		size = 'medium', // 'small' | 'medium' | 'large'
		showPasswordToggle = false,
		class: className = '',
		...rest
	} = $props();

	let showPassword = $state(false);

	const actualType = $derived(type === 'password' && showPassword ? 'text' : type);
	const helper = $derived(helperText || hint);
	const hasToggle = $derived(showPasswordToggle && type === 'password');

	const sizes = {
		small: 'h-9 text-sm',
		medium: 'h-11 text-sm',
		large: 'h-12 text-base'
	};
</script>

<div class={classNames('space-y-1.5', className)}>
	{#if label}
		<label for={id} class="block text-sm font-medium text-gray-800 dark:text-gray-200">
			{label}
			{#if required}<span class="text-danger-500">*</span>{/if}
		</label>
	{/if}

	<div class="group relative">
		{#if icon}
			<svg
				class="group-focus-within:text-primary-600 dark:group-focus-within:text-primary-400 pointer-events-none absolute inset-y-0 start-3.5 my-auto size-5 text-gray-400 transition-colors"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				viewBox="0 0 24 24"
				aria-hidden="true"
			>
				{@html icon}
			</svg>
		{/if}

		<input
			{id}
			type={actualType}
			{name}
			bind:value
			{placeholder}
			{disabled}
			{required}
			{readonly}
			aria-invalid={error ? 'true' : undefined}
			aria-describedby={error || helper ? `${id}-help` : undefined}
			class={classNames(
				'block w-full rounded-xl border-0 bg-white px-3.5 text-gray-900 shadow-xs ring-1 ring-gray-200 transition-shadow ring-inset',
				'placeholder:text-gray-400 focus:ring-2 focus:outline-none',
				'dark:bg-white/5 dark:text-white dark:ring-white/10 dark:placeholder:text-gray-500',
				'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:opacity-60 dark:disabled:bg-white/5',
				error
					? 'ring-danger-400 focus:ring-danger-500 dark:ring-danger-500/60'
					: 'focus:ring-primary-500 dark:focus:ring-primary-400',
				sizes[size] ?? sizes.medium,
				icon && 'ps-11',
				hasToggle && 'pe-11'
			)}
			{...rest}
		/>

		{#if hasToggle}
			<button
				type="button"
				onclick={() => (showPassword = !showPassword)}
				class="absolute inset-y-0 end-0 flex items-center px-3.5 text-gray-400 transition-colors hover:text-gray-600 dark:hover:text-gray-300"
				aria-label={showPassword ? $t('ui.hidePassword') : $t('ui.showPassword')}
			>
				<svg class="size-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
					{#if showPassword}
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
						/>
					{:else}
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
						/>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
						/>
					{/if}
				</svg>
			</button>
		{/if}
	</div>

	{#if error}
		<p
			id="{id}-help"
			class="text-danger-600 dark:text-danger-400 text-xs"
			transition:slide={{ duration: 150 }}
		>
			{error}
		</p>
	{:else if helper}
		<p id="{id}-help" class="text-xs text-gray-500 dark:text-gray-400">{helper}</p>
	{/if}
</div>

<!-- front/src/lib/components/common/EmptyState.svelte -->
<script>
	import { classNames } from '#lib/utils/helpers.js';

	let {
		title,
		description = '',
		icon = '<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />',
		actions,
		class: className = ''
	} = $props();
</script>

<div
	class={classNames(
		'flex flex-col items-center rounded-2xl border border-dashed border-gray-300 px-6 py-12 text-center sm:py-16 dark:border-white/10',
		className
	)}
>
	<div
		class="bg-primary-50 text-primary-600 dark:bg-primary-400/10 dark:text-primary-400 mb-4 flex size-12 items-center justify-center rounded-2xl"
	>
		<svg class="size-6" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
			{@html icon}
		</svg>
	</div>
	<h3 class="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
	{#if description}
		<p class="mt-1 max-w-sm text-sm text-gray-600 dark:text-gray-400">{description}</p>
	{/if}
	{#if actions}
		<div class="mt-6 flex flex-wrap justify-center gap-2">
			{@render actions()}
		</div>
	{/if}
</div>

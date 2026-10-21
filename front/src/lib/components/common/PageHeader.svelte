<!-- front/src/lib/components/common/PageHeader.svelte -->
<!-- Consistent page title block: eyebrow, title, description and an actions slot. -->
<script>
	import { classNames } from '#lib/utils/helpers.js';

	let { title, description = '', eyebrow = '', actions, class: className = '' } = $props();
</script>

<header
	class={classNames('flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between', className)}
>
	<div class="min-w-0">
		{#if eyebrow}
			<p class="text-primary-600 dark:text-primary-400 mb-1 text-sm font-medium">{eyebrow}</p>
		{/if}
		<h1 class="text-2xl font-semibold text-gray-900 sm:text-3xl dark:text-white">{title}</h1>
		{#if description}
			<p class="mt-1.5 max-w-2xl text-sm text-gray-600 sm:text-base dark:text-gray-400">
				{description}
			</p>
		{/if}
	</div>
	{#if actions}
		<div class="flex flex-wrap items-center gap-2 sm:shrink-0">
			{@render actions()}
		</div>
	{/if}
</header>

<!-- front/src/lib/components/common/Skeleton.svelte -->
<!-- Loading placeholders. variant="card" renders a course-card-shaped block. -->
<script>
	import { classNames } from '#lib/utils/helpers.js';

	let { variant = 'line', count = 1, class: className = '' } = $props();
</script>

{#each Array(count) as _}
	{#if variant === 'card'}
		<div
			class={classNames(
				'overflow-hidden rounded-2xl bg-white ring-1 ring-gray-200/80 dark:bg-gray-900 dark:ring-white/10',
				className
			)}
			aria-hidden="true"
		>
			<div class="skeleton aspect-video rounded-none"></div>
			<div class="space-y-3 p-5">
				<div class="skeleton h-4 w-3/4"></div>
				<div class="skeleton h-3 w-full"></div>
				<div class="skeleton h-3 w-2/3"></div>
			</div>
		</div>
	{:else}
		<div class={classNames('skeleton h-4 w-full', className)} aria-hidden="true"></div>
	{/if}
{/each}

<script>
	let {
		title,
		value,
		icon = '',
		trend = '',
		trendDirection = 'neutral', // 'up', 'down', 'neutral'
		size = 'medium' // 'small', 'medium', 'large'
	} = $props();

	let trendColorClass = $derived(
		{
			up: 'text-success-600 dark:text-success-400',
			down: 'text-danger-600 dark:text-danger-400',
			neutral: 'text-gray-500 dark:text-gray-400'
		}[trendDirection]
	);

	let trendIcon = $derived(
		{
			up: '↗',
			down: '↘',
			neutral: ''
		}[trendDirection]
	);
</script>

<div
	class="rounded-2xl bg-white p-4 shadow-xs ring-1 ring-gray-200/80 sm:p-5 dark:bg-gray-900 dark:ring-white/10"
>
	<div class="flex items-start justify-between gap-3">
		<p class="text-xs font-medium text-gray-500 sm:text-sm dark:text-gray-400">{title}</p>
		{#if icon}
			<span
				class="hidden size-8 shrink-0 items-center justify-center rounded-lg bg-gray-50 text-base sm:flex dark:bg-white/5"
				aria-hidden="true"
			>
				{icon}
			</span>
		{/if}
	</div>
	<p
		class="mt-2 font-semibold tracking-tight text-gray-900 tabular-nums dark:text-white {size ===
		'large'
			? 'text-3xl'
			: 'text-2xl'}"
	>
		{value}
	</p>
	{#if trend}
		<p class="mt-1 truncate text-xs {trendColorClass}">
			{#if trendIcon}<span aria-hidden="true">{trendIcon}</span>{/if}
			{trend}
		</p>
	{/if}
</div>

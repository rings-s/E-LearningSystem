<!-- front/src/lib/components/dashboard/StatsCard.svelte -->
<script>
	import { classNames } from '$lib/utils/helpers.js';
	import { formatters } from '$lib/utils/formatters.js';

	let {
		title = '',
		value = 0,
		icon = null,
		trend = null, // { value: 10, direction: 'up' }
		format = 'number', // 'number', 'percent', 'duration'
		color = 'primary',
		class: className = ''
	} = $props();

	const colors = {
		primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400',
		success: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
		warning: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
		danger: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
		info: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
	};

	const formattedValue = $derived(() => {
		switch (format) {
			case 'percent':
				return formatters.percent(value);
			case 'duration':
				return formatters.duration(value);
			default:
				return formatters.number(value);
		}
	});
</script>

<div
	class={classNames(
		'rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800',
		className
	)}
>
	<div class="flex items-start justify-between">
		<div class="flex-1">
			<p class="text-sm text-gray-500 dark:text-gray-400">
				{title}
			</p>
			<p class="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">
				{formattedValue()}
			</p>

			{#if trend}
				<div class="mt-2 flex items-center gap-1 text-sm">
					<svg
						class={classNames(
							'h-4 w-4',
							trend.direction === 'up' ? 'text-green-500' : 'text-red-500',
							trend.direction === 'down' && 'rotate-180'
						)}
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
						/>
					</svg>
					<span
						class={classNames(
							'font-medium',
							trend.direction === 'up'
								? 'text-green-600 dark:text-green-400'
								: 'text-red-600 dark:text-red-400'
						)}
					>
						{trend.value}%
					</span>
					<span class="text-gray-500 dark:text-gray-400"> vs last month </span>
				</div>
			{/if}
		</div>

		{#if icon}
			<div
				class={classNames(
					'flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg',
					colors[color]
				)}
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					{@html icon}
				</svg>
			</div>
		{/if}
	</div>
</div>

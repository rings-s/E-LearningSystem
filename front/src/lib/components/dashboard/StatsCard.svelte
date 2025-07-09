<script>
	export let title;
	export let value;
	export let icon = '';
	export let trend = '';
	export let trendDirection = 'neutral'; // 'up', 'down', 'neutral'
	export let size = 'medium'; // 'small', 'medium', 'large'
	
	$: trendColorClass = {
		'up': 'text-green-600 dark:text-green-400',
		'down': 'text-red-600 dark:text-red-400',
		'neutral': 'text-gray-600 dark:text-gray-400'
	}[trendDirection];
	
	$: trendIcon = {
		'up': '↗',
		'down': '↘',
		'neutral': ''
	}[trendDirection];
</script>

<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm hover:shadow-md transition-shadow">
	<div class="flex items-start justify-between">
		<div class="flex-1">
			<div class="flex items-center space-x-3 mb-2">
				{#if icon}
					<span class="text-2xl">{icon}</span>
				{/if}
				<h3 class="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
					{title}
				</h3>
			</div>
			
			<div class="flex items-baseline space-x-2">
				<span class="text-{size === 'large' ? '3xl' : size === 'small' ? 'xl' : '2xl'} font-bold text-gray-900 dark:text-white">
					{value}
				</span>
			</div>
			
			{#if trend}
				<div class="mt-2 flex items-center space-x-1">
					{#if trendIcon}
						<span class="{trendColorClass} text-sm">{trendIcon}</span>
					{/if}
					<span class="text-sm {trendColorClass}">
						{trend}
					</span>
				</div>
			{/if}
		</div>
	</div>
</div>
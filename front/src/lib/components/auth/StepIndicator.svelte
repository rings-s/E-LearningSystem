<script>
	let { steps = [], currentStep = 0 } = $props();
</script>

<div class="mb-8 flex items-center justify-center">
	{#each steps as step, index}
		<div class="flex items-center">
			<div
				class="flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300 {index <
				currentStep
					? 'bg-primary-600 border-primary-600 text-white'
					: index === currentStep
						? 'border-primary-600 text-primary-600 bg-primary-50 dark:bg-primary-900/20'
						: 'border-gray-300 text-gray-400 dark:border-gray-600'}"
			>
				{#if index < currentStep}
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M5 13l4 4L19 7"
						/>
					</svg>
				{:else}
					<span class="text-sm font-semibold">{index + 1}</span>
				{/if}
			</div>

			{#if index < steps.length - 1}
				<div
					class="mx-4 h-0.5 w-16 {index < currentStep
						? 'bg-primary-600'
						: 'bg-gray-300 dark:bg-gray-600'} transition-colors duration-300"
				></div>
			{/if}
		</div>
	{/each}
</div>

<div class="mb-6 text-center">
	<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
		{steps[currentStep]?.title}
	</h3>
	<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
		{steps[currentStep]?.description}
	</p>
</div>

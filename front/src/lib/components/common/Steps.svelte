<!-- front/src/lib/components/common/Steps.svelte -->
<!-- Progress indicator for multi-step forms. `currentStep` is 1-based. -->
<script>
	import { t } from '#lib/i18n/index.js';
	import { classNames } from '#lib/utils/helpers.js';

	let {
		steps = [], // [{ title, description?, completed? }]
		currentStep = 1,
		onStepClick = null,
		compact = false, // always use the condensed label + progress bar
		class: className = ''
	} = $props();

	const stepNumber = (index) => index + 1;
	const isDone = (index) => stepNumber(index) < currentStep || steps[index]?.completed;
	const isCurrent = (index) => stepNumber(index) === currentStep;
	const canClick = (index) => onStepClick && (isDone(index) || isCurrent(index));
	const progress = $derived(steps.length ? (currentStep / steps.length) * 100 : 0);
</script>

<nav aria-label={$t('ui.progress')} class={className}>
	<!-- Phones: compact label + progress bar -->
	<div class={compact ? '' : 'sm:hidden'}>
		<p class="text-sm font-medium text-gray-900 dark:text-white">
			{$t('ui.stepOf', { current: currentStep, total: steps.length })}
			<span class="text-gray-500 dark:text-gray-400">· {steps[currentStep - 1]?.title}</span>
		</p>
		<div class="mt-3 h-1.5 overflow-hidden rounded-full bg-gray-200 dark:bg-white/10">
			<div
				class="bg-primary-600 dark:bg-primary-400 h-full rounded-full transition-[width] duration-300"
				style="width: {progress}%"
			></div>
		</div>
	</div>

	<!-- Tablet and up: full stepper -->
	<ol class="hidden items-center {compact ? '' : 'sm:flex'}">
		{#each steps as step, index}
			<li class={classNames('flex items-center', index < steps.length - 1 && 'flex-1')}>
				<button
					type="button"
					disabled={!canClick(index)}
					onclick={() => onStepClick?.(stepNumber(index))}
					aria-current={isCurrent(index) ? 'step' : undefined}
					class="group flex items-center gap-3 rounded-lg text-start disabled:cursor-default"
				>
					<span
						class={classNames(
							'flex size-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold transition-colors',
							isDone(index) && !isCurrent(index)
								? 'bg-primary-600 dark:bg-primary-500 text-white'
								: isCurrent(index)
									? 'bg-primary-50 text-primary-700 ring-primary-600 dark:bg-primary-400/10 dark:text-primary-300 dark:ring-primary-400 ring-2'
									: 'bg-white text-gray-500 ring-1 ring-gray-300 dark:bg-transparent dark:text-gray-400 dark:ring-white/15'
						)}
					>
						{#if isDone(index) && !isCurrent(index)}
							<svg
								class="size-4"
								fill="none"
								stroke="currentColor"
								stroke-width="3"
								viewBox="0 0 24 24"
							>
								<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
							</svg>
						{:else}
							{stepNumber(index)}
						{/if}
					</span>
					<span class="hidden flex-col md:flex">
						<span
							class={classNames(
								'text-sm font-medium',
								isCurrent(index) || isDone(index)
									? 'text-gray-900 dark:text-white'
									: 'text-gray-500 dark:text-gray-400'
							)}
						>
							{step.title}
						</span>
						{#if step.description}
							<span class="text-xs text-gray-500 dark:text-gray-400">{step.description}</span>
						{/if}
					</span>
				</button>

				{#if index < steps.length - 1}
					<div
						class={classNames(
							'mx-3 h-0.5 flex-1 rounded-full transition-colors lg:mx-4',
							isDone(index) ? 'bg-primary-600 dark:bg-primary-500' : 'bg-gray-200 dark:bg-white/10'
						)}
						aria-hidden="true"
					></div>
				{/if}
			</li>
		{/each}
	</ol>
</nav>

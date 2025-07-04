<!-- front/src/lib/components/course/CourseProgress.svelte -->
<script>
	import { onMount } from 'svelte';
	import { classNames } from '$lib/utils/helpers.js';

	let {
		progress = 0,
		showLabel = true,
		size = 'medium',
		variant = 'auto',
		animated = true,
		class: className = ''
	} = $props();

	let displayProgress = $state(0);

	const sizes = {
		small: 'h-1.5',
		medium: 'h-2.5',
		large: 'h-4'
	};

	const variants = {
		primary: 'bg-gradient-to-r from-primary-600 to-primary-500',
		success: 'bg-gradient-to-r from-green-600 to-emerald-500',
		warning: 'bg-gradient-to-r from-yellow-600 to-orange-500',
		info: 'bg-gradient-to-r from-blue-600 to-cyan-500'
	};

	const getVariant = (progressValue) => {
		if (progressValue >= 100) return 'success';
		if (progressValue >= 75) return 'primary';
		if (progressValue >= 50) return 'info';
		return 'warning';
	};

	const currentVariant = $derived(() => {
		return variant === 'auto' ? getVariant(progress) : variant;
	});

	onMount(() => {
		if (animated) {
			animateProgress();
		} else {
			displayProgress = progress;
		}
	});

	function animateProgress() {
		const startProgress = displayProgress;
		const endProgress = Math.min(100, Math.max(0, progress));
		const duration = 1000;
		const startTime = Date.now();

		function updateProgress() {
			const elapsed = Date.now() - startTime;
			const progressRatio = Math.min(elapsed / duration, 1);
			const easedProgress = 1 - Math.pow(1 - progressRatio, 3);
			
			displayProgress = startProgress + (endProgress - startProgress) * easedProgress;

			if (progressRatio < 1) {
				requestAnimationFrame(updateProgress);
			} else {
				displayProgress = endProgress;
			}
		}

		requestAnimationFrame(updateProgress);
	}

	$effect(() => {
		if (animated) {
			animateProgress();
		} else {
			displayProgress = progress;
		}
	});
</script>

<div class={classNames('course-progress', className)}>
	{#if showLabel}
		<div class="mb-2 flex items-center justify-between">
			<span class="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
			<span class="text-sm font-semibold text-gray-900 dark:text-white">
				{Math.round(displayProgress)}%
			</span>
		</div>
	{/if}

	<div
		class={classNames(
			'w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700 relative',
			sizes[size]
		)}
		role="progressbar"
		aria-valuenow={Math.round(displayProgress)}
		aria-valuemin="0"
		aria-valuemax="100"
	>
		<div
			class={classNames(
				'h-full rounded-full transition-all duration-500 ease-out relative overflow-hidden',
				variants[currentVariant]
			)}
			style="width: {displayProgress}%"
		>
			{#if animated && displayProgress > 0}
				<div class="absolute inset-0 bg-white bg-opacity-20 rounded-full animate-pulse"></div>
			{/if}
		</div>
	</div>

	{#if showLabel && size === 'large'}
		<div class="mt-2 flex justify-between text-xs text-gray-500 dark:text-gray-400">
			<span class={displayProgress >= 25 ? 'text-green-600 font-medium' : ''}>25%</span>
			<span class={displayProgress >= 50 ? 'text-green-600 font-medium' : ''}>50%</span>
			<span class={displayProgress >= 75 ? 'text-green-600 font-medium' : ''}>75%</span>
			<span class={displayProgress >= 100 ? 'text-green-600 font-medium' : ''}>Complete</span>
		</div>
	{/if}
</div>
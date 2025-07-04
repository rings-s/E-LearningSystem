<!-- front/src/lib/components/course/CourseProgress.svelte -->
<script>
	import { classNames } from '$lib/utils/helpers.js';

	let {
		progress = 0,
		showLabel = true,
		size = 'medium', // 'small', 'medium', 'large'
		variant = 'primary', // 'primary', 'success', 'warning'
		class: className = ''
	} = $props();

	const sizes = {
		small: 'h-1',
		medium: 'h-2',
		large: 'h-3'
	};

	const variants = {
		primary: 'bg-gradient-to-r from-primary-600 to-primary-500 dark:from-primary-500 dark:to-primary-400',
		success: 'bg-gradient-to-r from-green-600 to-emerald-500 dark:from-green-500 dark:to-emerald-400',
		warning: 'bg-gradient-to-r from-yellow-600 to-orange-500 dark:from-yellow-500 dark:to-orange-400',
		info: 'bg-gradient-to-r from-blue-600 to-cyan-500 dark:from-blue-500 dark:to-cyan-400'
	};

	const getVariant = () => {
		if (progress >= 100) return 'success';
		if (progress >= 50) return 'primary';
		return 'warning';
	};

	const currentVariant = variant === 'auto' ? getVariant() : variant;
</script>

<div class={classNames('course-progress', className)}>
	{#if showLabel}
		<div class="mb-1 flex items-center justify-between">
			<span class="text-sm font-medium text-gray-700 dark:text-gray-300"> Progress </span>
			<span class="text-sm font-medium text-gray-700 dark:text-gray-300">
				{Math.round(progress)}%
			</span>
		</div>
	{/if}

	<div
		class={classNames(
			'w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700',
			sizes[size]
		)}
	>
		<div
			class={classNames(
				'h-full rounded-full transition-all duration-500 ease-out shadow-sm',
				variants[currentVariant]
			)}
			style="width: {Math.min(100, Math.max(0, progress))}%"
		>
			<!-- Progress shine effect -->
			<div class="h-full w-full rounded-full bg-white bg-opacity-20 animate-pulse"></div>
		</div>
	</div>
</div>

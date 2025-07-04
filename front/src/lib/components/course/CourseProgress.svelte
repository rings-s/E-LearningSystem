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
		primary: 'bg-primary-600 dark:bg-primary-500',
		success: 'bg-green-600 dark:bg-green-500',
		warning: 'bg-yellow-600 dark:bg-yellow-500'
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
				'h-full rounded-full transition-all duration-500 ease-out',
				variants[currentVariant]
			)}
			style="width: {Math.min(100, Math.max(0, progress))}%"
		></div>
	</div>
</div>

<!-- front/src/lib/components/common/Logo.svelte -->
<script>
	import { classNames } from '$lib/utils/helpers.js';

	let { size = 'medium', showText = true, href = '/', class: className = '' } = $props();

	const sizes = {
		small: { logo: 'w-8 h-8', text: 'text-lg' },
		medium: { logo: 'w-10 h-10', text: 'text-xl' },
		large: { logo: 'w-16 h-16', text: 'text-2xl' }
	};
</script>

<a {href} class={classNames('group inline-flex items-center gap-3', className)}>
	<div
		class={classNames(
			'relative overflow-hidden rounded-xl transition-all duration-300 group-hover:scale-105',
			sizes[size].logo
		)}
	>
		<div
			class="from-primary-500 to-secondary-600 flex h-full w-full items-center justify-center bg-gradient-to-br"
		>
			<span class="font-bold text-white {sizes[size].text}">244</span>
		</div>
	</div>

	{#if showText}
		<span
			class={classNames(
				'bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text font-bold text-transparent transition-all duration-300 dark:from-white dark:to-gray-300',
				sizes[size].text
			)}
		>
			244SCHOOL
		</span>
	{/if}
</a>

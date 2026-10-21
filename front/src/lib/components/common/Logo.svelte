<!-- front/src/lib/components/common/Logo.svelte -->
<script>
	import { classNames } from '#lib/utils/helpers.js';

	let { size = 'medium', showText = true, href = '/', class: className = '' } = $props();

	const sizes = {
		small: { mark: 'h-8 w-8 rounded-lg', icon: 'h-5 w-5', text: 'text-lg' },
		medium: { mark: 'h-9 w-9 rounded-xl', icon: 'h-5 w-5', text: 'text-xl' },
		large: { mark: 'h-14 w-14 rounded-2xl', icon: 'h-8 w-8', text: 'text-3xl' }
	};
</script>

<a
	{href}
	class={classNames('group inline-flex items-center gap-2.5', className)}
	aria-label="Ilmora"
>
	<span
		class={classNames(
			'brand-gradient shadow-glow flex shrink-0 items-center justify-center ring-1 ring-white/20 transition-transform duration-200 ring-inset group-hover:-rotate-3',
			sizes[size].mark
		)}
	>
		<!-- Open book with a point of light: "the glow of knowledge" -->
		<svg class={sizes[size].icon} viewBox="0 0 24 24" fill="none" aria-hidden="true">
			<path
				d="M12 8.5C9.6 7 6.6 6.6 3.5 7.4v11c3.1-.8 6.1-.4 8.5 1.1m0-11c2.4-1.5 5.4-1.9 8.5-1.1v11c-3.1-.8-6.1-.4-8.5 1.1m0-11v11"
				stroke="white"
				stroke-width="1.8"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>
			<circle cx="12" cy="3.6" r="1.7" class="fill-accent-300" />
		</svg>
	</span>

	{#if showText}
		<span
			class={classNames('font-bold tracking-tight text-gray-900 dark:text-white', sizes[size].text)}
		>
			Ilm<span class="text-primary-600 dark:text-primary-400">ora</span>
		</span>
	{/if}
</a>

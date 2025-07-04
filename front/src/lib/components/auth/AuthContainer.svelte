<script>
	import { fade, fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	let { title = '', subtitle = '', showLogo = true, maxWidth = 'md', children, footer } = $props();

	const maxWidthClasses = {
		sm: 'max-w-sm',
		md: 'max-w-md',
		lg: 'max-w-lg',
		xl: 'max-w-xl'
	};
</script>

<div
	class="from-primary-50 to-secondary-50 flex min-h-screen items-center justify-center bg-gradient-to-br via-white px-4 py-12 sm:px-6 lg:px-8 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
>
	<!-- Background Pattern -->
	<div class="bg-grid-pattern absolute inset-0 opacity-5 dark:opacity-10"></div>

	<div
		class="relative w-full {maxWidthClasses[maxWidth]} space-y-8"
		in:fly={{ y: 20, duration: 600, easing: quintOut }}
	>
		{#if showLogo}
			<div class="text-center" in:fade={{ delay: 200, duration: 400 }}>
				<div
					class="from-primary-500 to-primary-600 shadow-primary-500/25 mb-6 inline-flex h-20 w-20 transform items-center justify-center rounded-3xl bg-gradient-to-br text-3xl font-bold text-white shadow-xl transition-transform duration-200 hover:scale-105"
				>
					E
				</div>

				<h1
					class="mb-2 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-4xl font-bold text-transparent dark:from-white dark:to-gray-300"
				>
					{title}
				</h1>

				{#if subtitle}
					<p class="text-lg text-gray-600 dark:text-gray-400">
						{@html subtitle}
					</p>
				{/if}
			</div>
		{/if}

		<!-- Main Content Card -->
		<div
			class="rounded-3xl border border-gray-200/20 bg-white/80 p-8 shadow-2xl shadow-gray-500/10 backdrop-blur-xl sm:p-10 dark:border-gray-700/20 dark:bg-gray-800/80"
			in:fly={{ y: 20, delay: 300, duration: 600, easing: quintOut }}
		>
			{@render children()}
		</div>

		{#if footer}
			<div
				class="text-center text-sm text-gray-600 dark:text-gray-400"
				in:fade={{ delay: 400, duration: 400 }}
			>
				{@render footer()}
			</div>
		{/if}
	</div>
</div>

<style>
	.bg-grid-pattern {
		background-image: radial-gradient(circle, #e5e7eb 1px, transparent 1px);
		background-size: 20px 20px;
	}

	:global(.dark) .bg-grid-pattern {
		background-image: radial-gradient(circle, #374151 1px, transparent 1px);
	}
</style>

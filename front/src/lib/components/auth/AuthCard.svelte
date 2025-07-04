<!-- front/src/lib/components/auth/AuthCard.svelte -->
<script>
	import { fade } from 'svelte/transition';

	let { title = '', subtitle = '', children, footer = null } = $props();
</script>

<div class="space-y-8">
	<!-- Header -->
	{#if title || subtitle}
		<div class="space-y-2 text-center" in:fade={{ delay: 100, duration: 400 }}>
			{#if title}
				<h1
					class="bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-3xl font-bold text-transparent dark:from-white dark:to-gray-300"
				>
					{title}
				</h1>
			{/if}
			{#if subtitle}
				<p class="text-gray-600 dark:text-gray-400">
					{subtitle}
				</p>
			{/if}
		</div>
	{/if}

	<!-- Main Card -->
	<div
		class="space-y-6 rounded-2xl border border-gray-100 bg-white p-8 shadow-xl shadow-gray-200/50 dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/50"
		in:fade={{ delay: 200, duration: 400 }}
	>
		{@render children()}
	</div>

	<!-- Footer -->
	{#if footer}
		<div
			class="text-center text-sm text-gray-600 dark:text-gray-400"
			in:fade={{ delay: 300, duration: 400 }}
		>
			{@render footer()}
		</div>
	{/if}
</div>

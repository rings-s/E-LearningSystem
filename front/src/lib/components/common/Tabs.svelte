<!-- front/src/lib/components/common/Tabs.svelte -->
<script>
	import { fade } from 'svelte/transition';
	import { classNames } from '#lib/utils/helpers.js';

	let {
		tabs = [], // [{ label, icon?, badge?, disabled?, content? }]
		defaultTab = 0,
		variant = 'underline', // 'underline' | 'pills'
		fullWidth = false,
		class: className = '',
		activeTab = $bindable(defaultTab),
		content
	} = $props();

	const isSvgMarkup = (icon) => typeof icon === 'string' && icon.trim().startsWith('<');
	const hasPanels = $derived(!!content || tabs.some((t) => t.content));
</script>

<div class={className}>
	<!-- Scrolls sideways on small screens instead of wrapping -->
	<div
		class={classNames(
			'-mx-4 scrollbar-thin overflow-x-auto px-4 sm:mx-0 sm:px-0',
			variant === 'underline' && 'border-b border-gray-200 dark:border-white/10'
		)}
	>
		<div
			role="tablist"
			class={classNames(
				'flex min-w-max',
				variant === 'pills' ? 'gap-1 rounded-xl bg-gray-100 p-1 dark:bg-white/5' : '-mb-px gap-6',
				fullWidth && 'w-full'
			)}
		>
			{#each tabs as tab, index}
				{@const active = activeTab === index}
				<button
					type="button"
					role="tab"
					aria-selected={active}
					disabled={tab.disabled}
					onclick={() => (activeTab = index)}
					class={classNames(
						'inline-flex items-center justify-center gap-2 text-sm font-medium whitespace-nowrap transition-colors disabled:cursor-not-allowed disabled:opacity-50',
						variant === 'pills'
							? classNames(
									'rounded-lg px-3.5 py-2',
									active
										? 'bg-white text-gray-900 shadow-xs dark:bg-white/10 dark:text-white'
										: 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
								)
							: classNames(
									'border-b-2 px-1 py-3',
									active
										? 'border-primary-600 text-primary-700 dark:border-primary-400 dark:text-primary-300'
										: 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
								),
						fullWidth && 'flex-1'
					)}
				>
					{#if tab.icon}
						{#if isSvgMarkup(tab.icon)}
							<svg
								class="size-4"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								viewBox="0 0 24 24"
							>
								{@html tab.icon}
							</svg>
						{:else}
							<span aria-hidden="true">{tab.icon}</span>
						{/if}
					{/if}
					{tab.label}
					{#if tab.badge}
						<span
							class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-white/10 dark:text-gray-300"
						>
							{tab.badge}
						</span>
					{/if}
				</button>
			{/each}
		</div>
	</div>

	{#if hasPanels}
		<div class="mt-6" role="tabpanel">
			{#key activeTab}
				<div in:fade={{ duration: 150 }}>
					{#if content && tabs[activeTab]}
						{@render content(tabs[activeTab])}
					{:else if tabs[activeTab]?.content}
						{@render tabs[activeTab].content()}
					{/if}
				</div>
			{/key}
		</div>
	{/if}
</div>

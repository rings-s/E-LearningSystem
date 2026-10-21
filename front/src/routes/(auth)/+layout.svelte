<!-- front/src/routes/(auth)/+layout.svelte -->
<!-- Split-screen layout shared by every auth page: brand panel on desktop, form on the right. -->
<script>
	import { t } from '#lib/i18n/index.js';
	import Logo from '#lib/components/common/Logo.svelte';
	import PreferenceToggles from '#lib/components/layout/PreferenceToggles.svelte';

	let { children } = $props();

	const points = ['ui.authPoint1', 'ui.authPoint2', 'ui.authPoint3'];
</script>

<div class="grid min-h-dvh lg:grid-cols-2">
	<!-- Brand panel -->
	<aside class="brand-gradient relative hidden overflow-hidden p-12 text-white lg:flex lg:flex-col">
		<div
			class="absolute -end-24 -top-24 size-96 rounded-full bg-white/10 blur-3xl"
			aria-hidden="true"
		></div>
		<div
			class="bg-accent-400/20 absolute -start-16 bottom-0 size-80 rounded-full blur-3xl"
			aria-hidden="true"
		></div>

		<a href="/" class="relative flex items-center gap-2.5 text-xl font-semibold">
			<span
				class="flex size-9 items-center justify-center rounded-xl bg-white/15 ring-1 ring-white/25"
			>
				<svg class="size-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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
			{$t('ui.brand')}
		</a>

		<div class="relative mt-auto max-w-md">
			<h2 class="text-4xl font-semibold tracking-tight">{$t('ui.authHeadline')}</h2>
			<p class="mt-4 text-lg text-white/80">
				{$t('ui.authText')}
			</p>
			<ul class="mt-8 space-y-3">
				{#each points as point}
					<li class="flex items-center gap-3 text-white/90">
						<span class="flex size-6 items-center justify-center rounded-full bg-white/15">
							<svg
								class="size-3.5"
								fill="none"
								stroke="currentColor"
								stroke-width="3"
								viewBox="0 0 24 24"
							>
								<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
							</svg>
						</span>
						{$t(point)}
					</li>
				{/each}
			</ul>
		</div>
		<p class="relative mt-12 text-sm text-white/60">
			© {new Date().getFullYear()}
			{$t('ui.brand')}
		</p>
	</aside>

	<!-- Form panel -->
	<main class="flex flex-col bg-white dark:bg-gray-950">
		<div class="flex h-16 items-center justify-between px-4 sm:px-8">
			<div class="lg:invisible">
				<Logo size="small" />
			</div>
			<div class="flex items-center gap-1">
				<PreferenceToggles />
			</div>
		</div>
		<div class="flex flex-1 items-center justify-center px-4 py-10 sm:px-8">
			<div class="w-full max-w-sm">
				{@render children()}
			</div>
		</div>
	</main>
</div>

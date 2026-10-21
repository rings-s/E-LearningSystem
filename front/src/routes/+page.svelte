<!-- front/src/routes/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '#lib/services/auth.service.js';
	import { t } from '#lib/i18n/index.js';
	import Button from '#lib/components/common/Button.svelte';
	import Logo from '#lib/components/common/Logo.svelte';

	$effect(() => {
		if ($isAuthenticated) {
			goto('/dashboard');
		}
	});

	const features = [
		{
			title: 'landing.feature1Title',
			text: 'landing.feature1Text',
			icon: 'M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342'
		},
		{
			title: 'landing.feature2Title',
			text: 'landing.feature2Text',
			icon: 'M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z'
		},
		{
			title: 'landing.feature3Title',
			text: 'landing.feature3Text',
			icon: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z'
		},
		{
			title: 'landing.feature4Title',
			text: 'landing.feature4Text',
			icon: 'M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z'
		},
		{
			title: 'landing.feature5Title',
			text: 'landing.feature5Text',
			icon: 'M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155'
		},
		{
			title: 'landing.feature6Title',
			text: 'landing.feature6Text',
			icon: 'M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802'
		}
	];

	const steps = [1, 2, 3].map((n) => ({
		title: `landing.step${n}Title`,
		text: `landing.step${n}Text`
	}));
</script>

<svelte:head>
	<title>{$t('landing.pageTitle')}</title>
</svelte:head>

<!-- Hero -->
<section class="relative isolate overflow-hidden">
	<div
		class="from-primary-100/70 dark:from-primary-500/10 absolute inset-x-0 top-0 -z-10 h-[36rem] bg-radial-[ellipse_at_top] to-transparent"
		aria-hidden="true"
	></div>

	<div
		class="mx-auto grid max-w-7xl items-center gap-12 px-4 pt-12 pb-16 sm:px-6 sm:pt-20 lg:grid-cols-2 lg:px-8 lg:pt-24 lg:pb-24"
	>
		<div class="text-center lg:text-start">
			<span
				class="text-primary-700 ring-primary-600/15 dark:text-primary-300 dark:ring-primary-400/20 inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-medium ring-1 backdrop-blur dark:bg-white/5"
			>
				<span class="bg-accent-400 size-1.5 rounded-full"></span>
				{$t('landing.badge')}
			</span>
			<h1
				class="mt-6 text-4xl font-semibold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl dark:text-white"
			>
				{$t('landing.heroTitle')}
				<span class="text-brand-gradient block">{$t('landing.heroHighlight')}</span>
			</h1>
			<p
				class="mx-auto mt-6 max-w-xl text-base text-gray-600 sm:text-lg lg:mx-0 dark:text-gray-400"
			>
				{$t('landing.heroText')}
			</p>
			<div class="mt-8 flex flex-col justify-center gap-3 sm:flex-row lg:justify-start">
				<Button href="/register" size="large">{$t('actions.getStarted')}</Button>
				<Button href="/courses" variant="outline" size="large">{$t('landing.browseCourses')}</Button
				>
			</div>
		</div>

		<!-- Product preview -->
		<div class="relative mx-auto w-full max-w-lg lg:max-w-none" aria-hidden="true">
			<div
				class="rounded-3xl bg-white/60 p-2 shadow-xl ring-1 ring-gray-200/80 backdrop-blur dark:bg-white/5 dark:ring-white/10"
			>
				<div
					class="overflow-hidden rounded-2xl bg-white ring-1 ring-gray-200/60 dark:bg-gray-900 dark:ring-white/10"
				>
					<div class="brand-gradient relative aspect-video">
						<div class="absolute inset-0 flex items-center justify-center">
							<span
								class="flex size-14 items-center justify-center rounded-full bg-white/20 ring-1 ring-white/40 backdrop-blur"
							>
								<svg class="ms-1 size-6 text-white" viewBox="0 0 24 24" fill="currentColor">
									<path
										d="M8 5.14v13.72a1 1 0 001.5.86l11-6.86a1 1 0 000-1.72l-11-6.86A1 1 0 008 5.14z"
									/>
								</svg>
							</span>
						</div>
						<div class="absolute inset-x-4 bottom-4 h-1 overflow-hidden rounded-full bg-white/25">
							<div class="h-full w-2/3 rounded-full bg-white"></div>
						</div>
					</div>
					<div class="space-y-3 p-5">
						<p class="text-sm font-semibold text-gray-900 dark:text-white">
							{$t('landing.previewLesson')}
						</p>
						<div class="flex items-center gap-3">
							<div class="h-2 flex-1 overflow-hidden rounded-full bg-gray-100 dark:bg-white/10">
								<div class="bg-primary-600 h-full w-2/3 rounded-full"></div>
							</div>
							<span class="text-xs font-medium text-gray-500 dark:text-gray-400">68%</span>
						</div>
					</div>
				</div>
			</div>
			<div
				class="absolute -end-3 -top-5 hidden items-center gap-3 rounded-2xl bg-white p-3 pe-5 shadow-lg ring-1 ring-gray-200/80 sm:flex dark:bg-gray-900 dark:ring-white/10"
			>
				<span
					class="bg-success-50 text-success-600 dark:bg-success-400/10 dark:text-success-400 flex size-10 items-center justify-center rounded-xl"
				>
					<svg
						class="size-5"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
					</svg>
				</span>
				<span>
					<span class="block text-sm font-semibold text-gray-900 dark:text-white"
						>{$t('landing.certificateEarned')}</span
					>
					<span class="block text-xs text-gray-500 dark:text-gray-400"
						>{$t('landing.certificateCourse')}</span
					>
				</span>
			</div>
		</div>
	</div>
</section>

<!-- Features -->
<section
	class="border-t border-gray-200/80 bg-white py-16 sm:py-24 dark:border-white/10 dark:bg-gray-900/40"
>
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<div class="mx-auto max-w-2xl text-center">
			<p class="text-primary-600 dark:text-primary-400 text-sm font-semibold">
				{$t('landing.featuresEyebrow')}
			</p>
			<h2
				class="mt-2 text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl dark:text-white"
			>
				{$t('landing.featuresTitle')}
			</h2>
		</div>
		<div class="mt-12 grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
			{#each features as feature}
				<div>
					<span
						class="bg-primary-50 text-primary-600 ring-primary-600/10 dark:bg-primary-400/10 dark:text-primary-400 flex size-11 items-center justify-center rounded-xl ring-1"
					>
						<svg
							class="size-5"
							fill="none"
							stroke="currentColor"
							stroke-width="1.75"
							viewBox="0 0 24 24"
						>
							<path stroke-linecap="round" stroke-linejoin="round" d={feature.icon} />
						</svg>
					</span>
					<h3 class="mt-4 text-base font-semibold text-gray-900 dark:text-white">
						{$t(feature.title)}
					</h3>
					<p class="mt-1.5 text-sm leading-relaxed text-gray-600 dark:text-gray-400">
						{$t(feature.text)}
					</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- How it works -->
<section class="py-16 sm:py-24">
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<h2
			class="text-center text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl dark:text-white"
		>
			{$t('landing.howTitle')}
		</h2>
		<ol class="mt-12 grid gap-6 md:grid-cols-3">
			{#each steps as step, i}
				<li
					class="rounded-2xl bg-white p-6 shadow-xs ring-1 ring-gray-200/80 dark:bg-gray-900 dark:ring-white/10"
				>
					<span
						class="bg-primary-600 flex size-8 items-center justify-center rounded-full text-sm font-semibold text-white"
					>
						{i + 1}
					</span>
					<h3 class="mt-4 text-base font-semibold text-gray-900 dark:text-white">
						{$t(step.title)}
					</h3>
					<p class="mt-1.5 text-sm text-gray-600 dark:text-gray-400">{$t(step.text)}</p>
				</li>
			{/each}
		</ol>
	</div>
</section>

<!-- Call to action -->
<section class="px-4 pb-16 sm:px-6 sm:pb-24 lg:px-8">
	<div
		class="brand-gradient relative mx-auto max-w-5xl overflow-hidden rounded-3xl px-6 py-12 text-center shadow-xl sm:px-12 sm:py-16"
	>
		<h2 class="text-2xl font-semibold tracking-tight text-white sm:text-4xl">
			{$t('landing.ctaTitle')}
		</h2>
		<p class="mx-auto mt-3 max-w-xl text-white/80">
			{$t('landing.ctaText')}
		</p>
		<div class="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
			<a
				href="/register"
				class="text-primary-700 inline-flex h-12 items-center justify-center rounded-xl bg-white px-6 font-medium shadow-sm transition-colors hover:bg-white/90"
			>
				{$t('landing.ctaPrimary')}
			</a>
			<a
				href="/courses"
				class="inline-flex h-12 items-center justify-center rounded-xl px-6 font-medium text-white ring-1 ring-white/30 transition-colors hover:bg-white/10"
			>
				{$t('landing.ctaSecondary')}
			</a>
		</div>
	</div>
</section>

<footer class="border-t border-gray-200/80 dark:border-white/10">
	<div
		class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row sm:px-6 lg:px-8"
	>
		<Logo size="small" />
		<p class="text-sm text-gray-500 dark:text-gray-400">
			{$t('landing.copyright', { year: new Date().getFullYear() })}
		</p>
	</div>
</footer>

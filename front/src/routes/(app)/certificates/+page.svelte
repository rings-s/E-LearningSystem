<!-- front/src/routes/(app)/certificates/+page.svelte -->
<script>
	import { t, locale } from '#lib/i18n/index.js';
	import { onMount } from 'svelte';
	import { coursesApi } from '#lib/apis/courses.js';
	import { formatters } from '#lib/utils/formatters.js';
	import PageHeader from '#lib/components/common/PageHeader.svelte';
	import EmptyState from '#lib/components/common/EmptyState.svelte';
	import Skeleton from '#lib/components/common/Skeleton.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';

	let certificates = $state([]);
	let courseTitles = $state({});
	let loading = $state(true);
	let error = $state('');

	const toList = (res) => (Array.isArray(res) ? res : res?.results || []);

	async function load() {
		loading = true;
		error = '';
		try {
			// Certificates only reference the course id, so map ids to titles via enrollments
			const [certs, enrollments] = await Promise.all([
				coursesApi.getMyCertificates(),
				coursesApi.getMyEnrollments().catch(() => [])
			]);
			certificates = toList(certs);
			courseTitles = Object.fromEntries(
				toList(enrollments)
					.filter((e) => e.course)
					.map((e) => [e.course.id, e.course.title])
			);
		} catch (err) {
			error = err.message || $t('certificatesPage.loadFailed');
		} finally {
			loading = false;
		}
	}

	onMount(load);
</script>

<svelte:head>
	<title>{$t('certificatesPage.pageTitle')}</title>
</svelte:head>

<div class="space-y-6">
	<PageHeader
		title={$t('certificatesPage.title')}
		description={$t('certificatesPage.description')}
	/>

	{#if loading}
		<div class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
			{#each Array(3) as _}
				<Skeleton class="h-56 rounded-2xl" />
			{/each}
		</div>
	{:else if error}
		<EmptyState title={$t('certificatesPage.loadError')} description={error}>
			{#snippet actions()}
				<Button onclick={load}>{$t('certificatesPage.tryAgain')}</Button>
			{/snippet}
		</EmptyState>
	{:else if certificates.length === 0}
		<EmptyState
			title={$t('certificatesPage.empty')}
			description={$t('certificatesPage.emptyDesc')}
			icon={'<path stroke-linecap="round" stroke-linejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.492a46.32 46.32 0 012.916.52 6.003 6.003 0 01-5.395 4.972m0 0a6.726 6.726 0 01-2.749 1.35m0 0a6.772 6.772 0 01-3.044 0" />'}
		>
			{#snippet actions()}
				<Button href="/my-courses">{$t('certificatesPage.continueLearning')}</Button>
			{/snippet}
		</EmptyState>
	{:else}
		<div class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
			{#each certificates as cert (cert.uuid)}
				<article
					class="relative flex flex-col overflow-hidden rounded-2xl bg-white shadow-xs ring-1 ring-gray-200/80 dark:bg-gray-900 dark:ring-white/10"
				>
					<div class="brand-gradient relative px-5 py-6 text-white">
						<div
							class="absolute -end-8 -top-8 size-32 rounded-full bg-white/10"
							aria-hidden="true"
						></div>
						<p class="text-xs font-medium tracking-wider text-white/70 uppercase">
							{$t('certificatesPage.ofCompletion')}
						</p>
						<h2 dir="auto" class="mt-2 line-clamp-2 text-lg font-semibold">
							{courseTitles[cert.course] || $t('certificatesPage.course')}
						</h2>
					</div>

					<dl class="grid flex-1 grid-cols-2 gap-4 p-5 text-sm">
						<div>
							<dt class="text-gray-500 dark:text-gray-400">{$t('certificatesPage.completed')}</dt>
							<dd class="font-medium text-gray-900 dark:text-white">
								{formatters.date(cert.completion_date || cert.issue_date, $locale)}
							</dd>
						</div>
						{#if cert.final_score != null}
							<div>
								<dt class="text-gray-500 dark:text-gray-400">{$t('certificatesPage.score')}</dt>
								<dd class="font-medium text-gray-900 dark:text-white">
									{Math.round(cert.final_score)}%
								</dd>
							</div>
						{/if}
						<div class="col-span-2">
							<dt class="text-gray-500 dark:text-gray-400">{$t('certificatesPage.number')}</dt>
							<dd class="font-mono text-xs text-gray-900 dark:text-white">
								{cert.certificate_number}
							</dd>
						</div>
					</dl>

					<div
						class="flex items-center justify-between gap-2 border-t border-gray-100 px-5 py-3 dark:border-white/5"
					>
						<Badge variant={cert.is_valid ? 'success' : 'danger'} size="small" dot>
							{cert.is_valid ? $t('certificatesPage.valid') : $t('certificatesPage.revoked')}
						</Badge>
						{#if cert.pdf_file}
							<Button
								href={cert.pdf_file}
								variant="ghost"
								size="small"
								target="_blank"
								rel="noopener"
							>
								{$t('certificatesPage.download')}
							</Button>
						{/if}
					</div>
				</article>
			{/each}
		</div>
	{/if}
</div>

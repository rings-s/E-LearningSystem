<!-- front/src/lib/components/dashboard/DashboardHeader.svelte -->
<script>
	import { t, locale } from '#lib/i18n/index.js';
	import Button from '#lib/components/common/Button.svelte';

	let { userName, userRole, refreshing = false, onRefresh = () => {} } = $props();

	const hour = new Date().getHours();
	const greeting = $derived(
		hour < 12
			? $t('dashboardHome.goodMorning')
			: hour < 17
				? $t('dashboardHome.goodAfternoon')
				: $t('dashboardHome.goodEvening')
	);
	const today = $derived(
		new Date().toLocaleDateString($locale, { weekday: 'long', month: 'long', day: 'numeric' })
	);

	const subtitle = $derived(
		{
			student: $t('dashboardHome.subStudent'),
			teacher: $t('dashboardHome.subTeacher'),
			manager: $t('dashboardHome.subManager'),
			admin: $t('dashboardHome.subManager')
		}[userRole] ?? $t('dashboardHome.subDefault')
	);
</script>

<header class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
	<div class="min-w-0">
		<p class="text-sm font-medium text-gray-500 dark:text-gray-400">{today}</p>
		<h1 class="mt-1 text-2xl font-semibold text-gray-900 sm:text-3xl dark:text-white">
			{$t('dashboardHome.greeting', { greeting, name: userName })}
		</h1>
		<p class="mt-1.5 text-sm text-gray-600 sm:text-base dark:text-gray-400">{subtitle}</p>
	</div>

	<div class="flex items-center gap-2">
		<Button
			onclick={onRefresh}
			variant="outline"
			loading={refreshing}
			aria-label={$t('dashboardHome.refreshDashboard')}
			iconLeft={refreshing
				? null
				: '<path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />'}
		>
			<span class="hidden sm:inline">{$t('dashboardHome.refresh')}</span>
		</Button>
		{#if userRole === 'teacher'}
			<Button
				href="/teacher/courses/create"
				iconLeft={'<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />'}
			>
				{$t('dashboardHome.newCourse')}
			</Button>
		{:else}
			<Button
				href="/courses"
				iconLeft={'<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />'}
			>
				{$t('dashboardHome.exploreCourses')}
			</Button>
		{/if}
	</div>
</header>

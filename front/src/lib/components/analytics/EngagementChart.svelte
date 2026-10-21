<!-- front/src/lib/components/analytics/EngagementChart.svelte -->
<script>
	import { t } from '#lib/i18n/index.js';
	import ChartWrapper from '#lib/components/charts/ChartWrapper.svelte';
	import { formatters } from '#lib/utils/formatters.js';

	let {
		data = [],
		title = $t('analyticsPage.studentEngagementPlain'),
		timeRange = '30d',
		height = '300px',
		class: className = ''
	} = $props();

	// Process engagement data for chart display
	const chartData = $derived.by(() => {
		if (!data || data.length === 0) {
			return {
				labels: [],
				datasets: [
					{
						label: $t('analyticsPage.activeStudents'),
						data: [],
						borderColor: '#5b4ff5',
						backgroundColor: 'rgba(91, 79, 245, 0.12)',
						fill: true,
						tension: 0.4
					}
				]
			};
		}

		const labels = data.map((point) => {
			if (timeRange === '7d') {
				return formatters.shortDay(point.date);
			} else if (timeRange === '30d') {
				return formatters.shortDate(point.date);
			} else {
				return formatters.monthYear(point.date);
			}
		});

		return {
			labels,
			datasets: [
				{
					label: $t('analyticsPage.activeStudents'),
					data: data.map((point) => point.active_students || 0),
					borderColor: '#5b4ff5',
					backgroundColor: 'rgba(91, 79, 245, 0.12)',
					fill: true,
					tension: 0.4,
					pointRadius: 4,
					pointHoverRadius: 6
				},
				{
					label: $t('analyticsPage.totalStudents'),
					data: data.map((point) => point.total_students || 0),
					borderColor: '#6b7280',
					backgroundColor: 'rgba(107, 114, 128, 0.1)',
					fill: false,
					tension: 0.4,
					pointRadius: 3,
					pointHoverRadius: 5,
					borderDash: [5, 5]
				}
			]
		};
	});

	const chartOptions = {
		responsive: true,
		maintainAspectRatio: false,
		interaction: {
			intersect: false,
			mode: 'index'
		},
		plugins: {
			legend: {
				position: 'top',
				align: 'end'
			},
			tooltip: {
				backgroundColor: 'rgba(0, 0, 0, 0.8)',
				titleColor: '#ffffff',
				bodyColor: '#ffffff',
				borderColor: '#5b4ff5',
				borderWidth: 1,
				callbacks: {
					title: (context) => {
						const dataPoint = data[context[0].dataIndex];
						return formatters.fullDate(dataPoint.date);
					},
					label: (context) => {
						const value = context.parsed.y;
						return `${context.dataset.label}: ${value} students`;
					},
					afterBody: (context) => {
						const dataPoint = data[context[0].dataIndex];
						if (dataPoint.engagement_rate !== undefined) {
							return $t('analyticsPage.engagementRateValue', {
								rate: Math.round(dataPoint.engagement_rate || 0) || 0
							});
						}
						return '';
					}
				}
			}
		},
		scales: {
			x: {
				grid: {
					display: false
				},
				ticks: {
					maxTicksLimit: 8
				}
			},
			y: {
				beginAtZero: true,
				grid: {
					color: 'rgba(0, 0, 0, 0.1)'
				},
				ticks: {
					callback: (value) => Math.round(value)
				}
			}
		}
	};

	// Calculate summary statistics
	const summaryStats = $derived.by(() => {
		if (!data || data.length === 0) {
			return {
				avgActive: 0,
				maxActive: 0,
				engagementTrend: 0,
				totalSessions: 0
			};
		}

		const activeStudents = data.map((d) => d.active_students || 0);
		const avgActive =
			activeStudents.length > 0
				? Math.round(activeStudents.reduce((sum, val) => sum + val, 0) / activeStudents.length) || 0
				: 0;
		const maxActive = Math.max(...activeStudents);

		// Calculate trend (simple linear regression slope)
		const n = data.length;
		if (n < 2) {
			return { avgActive, maxActive, engagementTrend: 0, totalSessions: 0 };
		}

		const sumX = data.reduce((sum, _, i) => sum + i, 0);
		const sumY = activeStudents.reduce((sum, val) => sum + val, 0);
		const sumXY = data.reduce((sum, _, i) => sum + i * activeStudents[i], 0);
		const sumXX = data.reduce((sum, _, i) => sum + i * i, 0);

		const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
		const engagementTrend = Math.round(slope * 100) / 100;

		const totalSessions = data.reduce((sum, d) => sum + (d.total_sessions || 0), 0);

		return { avgActive, maxActive, engagementTrend, totalSessions };
	});
</script>

<div class="space-y-4 {className}">
	<!-- Chart Header -->
	<div class="flex items-center justify-between">
		<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
			{title}
		</h3>
		{#if summaryStats.engagementTrend !== 0}
			<div class="flex items-center space-x-2">
				<span class="text-sm text-gray-500 dark:text-gray-400">{$t('analyticsPage.trend')}</span>
				<div
					class="flex items-center {summaryStats.engagementTrend > 0
						? 'text-green-600'
						: 'text-red-600'}"
				>
					{#if summaryStats.engagementTrend > 0}
						<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
							/>
						</svg>
						<span class="text-sm font-medium">+{summaryStats.engagementTrend}</span>
					{:else}
						<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"
							/>
						</svg>
						<span class="text-sm font-medium">{summaryStats.engagementTrend}</span>
					{/if}
				</div>
			</div>
		{/if}
	</div>

	<!-- Summary Stats -->
	{#if data && data.length > 0}
		<div class="mb-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
			<div class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-3">
				<div class="text-primary-600 dark:text-primary-400 text-2xl font-bold">
					{summaryStats.avgActive}
				</div>
				<div class="text-primary-800 dark:text-primary-200 text-sm">
					{$t('analyticsPage.avgActive')}
				</div>
			</div>
			<div class="rounded-lg bg-green-50 p-3 dark:bg-green-900/20">
				<div class="text-2xl font-bold text-green-600 dark:text-green-400">
					{summaryStats.maxActive}
				</div>
				<div class="text-sm text-green-800 dark:text-green-200">
					{$t('analyticsPage.peakActivity')}
				</div>
			</div>
			<div class="bg-secondary-50 dark:bg-secondary-900/20 rounded-lg p-3">
				<div class="text-secondary-600 dark:text-secondary-400 text-2xl font-bold">
					{summaryStats.totalSessions}
				</div>
				<div class="text-secondary-800 dark:text-secondary-200 text-sm">
					{$t('analyticsPage.totalSessions')}
				</div>
			</div>
			<div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
				<div class="text-2xl font-bold text-gray-600 dark:text-gray-400">
					{data.length}
				</div>
				<div class="text-sm text-gray-800 dark:text-gray-200">{$t('analyticsPage.dataPoints')}</div>
			</div>
		</div>
	{/if}

	<!-- Chart -->
	<div class="relative">
		{#if data && data.length > 0}
			<ChartWrapper type="line" data={chartData} options={chartOptions} {height} />
		{:else}
			<div
				class="flex items-center justify-center rounded-lg bg-gray-50 dark:bg-gray-800"
				style="height: {height}"
			>
				<div class="text-center text-gray-500 dark:text-gray-400">
					<svg class="mx-auto mb-2 h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
						/>
					</svg>
					<p class="mb-1 text-lg font-medium">{$t('analyticsPage.noEngagementLower')}</p>
					<p class="text-sm">{$t('analyticsPage.dataWillAppearPlural')}</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- Data Insights -->
	{#if data && data.length > 2}
		<div
			class="rounded-lg bg-gray-50 p-3 text-sm text-gray-600 dark:bg-gray-800/50 dark:text-gray-400"
		>
			<strong>{$t('analyticsPage.insights')}</strong>
			{#if summaryStats.engagementTrend > 0}
				📈 Student engagement is trending upward ({summaryStats.engagementTrend > 1
					? 'strongly'
					: 'slightly'}).
			{:else if summaryStats.engagementTrend < 0}
				📉 Student engagement is declining ({summaryStats.engagementTrend < -1
					? 'significantly'
					: 'slightly'}). Consider engaging with students or updating content.
			{:else}
				📊 Student engagement remains stable across the selected period.
			{/if}

			{#if summaryStats.maxActive > summaryStats.avgActive * 1.5}
				{$t('analyticsPage.peakNote', {
					percent:
						summaryStats.avgActive > 0
							? Math.round((summaryStats.maxActive / summaryStats.avgActive - 1) * 100) || 0
							: 0
				})}
			{/if}
		</div>
	{/if}
</div>

<!-- front/src/lib/components/analytics/EngagementChart.svelte -->
<script>
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';
	import { formatters } from '$lib/utils/formatters.js';

	let { 
		data = [], 
		title = 'Student Engagement', 
		timeRange = '30d',
		height = '300px', 
		class: className = '' 
	} = $props();

	// Process engagement data for chart display
	const chartData = $derived(() => {
		if (!data || data.length === 0) {
			return {
				labels: [],
				datasets: [{
					label: 'Active Students',
					data: [],
					borderColor: '#3b82f6',
					backgroundColor: 'rgba(59, 130, 246, 0.1)',
					fill: true,
					tension: 0.4
				}]
			};
		}

		const labels = data.map(point => {
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
					label: 'Active Students',
					data: data.map(point => point.active_students || 0),
					borderColor: '#3b82f6',
					backgroundColor: 'rgba(59, 130, 246, 0.1)',
					fill: true,
					tension: 0.4,
					pointRadius: 4,
					pointHoverRadius: 6
				},
				{
					label: 'Total Students',
					data: data.map(point => point.total_students || 0),
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
				borderColor: '#3b82f6',
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
							return `Engagement Rate: ${Math.round(dataPoint.engagement_rate || 0) || 0}%`;
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
	const summaryStats = $derived(() => {
		if (!data || data.length === 0) {
			return {
				avgActive: 0,
				maxActive: 0,
				engagementTrend: 0,
				totalSessions: 0
			};
		}

		const activeStudents = data.map(d => d.active_students || 0);
		const avgActive = activeStudents.length > 0 ? Math.round(activeStudents.reduce((sum, val) => sum + val, 0) / activeStudents.length) || 0 : 0;
		const maxActive = Math.max(...activeStudents);
		
		// Calculate trend (simple linear regression slope)
		const n = data.length;
		if (n < 2) {
			return { avgActive, maxActive, engagementTrend: 0, totalSessions: 0 };
		}

		const sumX = data.reduce((sum, _, i) => sum + i, 0);
		const sumY = activeStudents.reduce((sum, val) => sum + val, 0);
		const sumXY = data.reduce((sum, _, i) => sum + (i * activeStudents[i]), 0);
		const sumXX = data.reduce((sum, _, i) => sum + (i * i), 0);
		
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
				<span class="text-sm text-gray-500 dark:text-gray-400">Trend:</span>
				<div class="flex items-center {summaryStats.engagementTrend > 0 ? 'text-green-600' : 'text-red-600'}">
					{#if summaryStats.engagementTrend > 0}
						<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
						</svg>
						<span class="text-sm font-medium">+{summaryStats.engagementTrend}</span>
					{:else}
						<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
						</svg>
						<span class="text-sm font-medium">{summaryStats.engagementTrend}</span>
					{/if}
				</div>
			</div>
		{/if}
	</div>

	<!-- Summary Stats -->
	{#if data && data.length > 0}
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
			<div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
				<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
					{summaryStats.avgActive}
				</div>
				<div class="text-sm text-blue-800 dark:text-blue-200">
					Avg Active Students
				</div>
			</div>
			<div class="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
				<div class="text-2xl font-bold text-green-600 dark:text-green-400">
					{summaryStats.maxActive}
				</div>
				<div class="text-sm text-green-800 dark:text-green-200">
					Peak Activity
				</div>
			</div>
			<div class="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg">
				<div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
					{summaryStats.totalSessions}
				</div>
				<div class="text-sm text-purple-800 dark:text-purple-200">
					Total Sessions
				</div>
			</div>
			<div class="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
				<div class="text-2xl font-bold text-gray-600 dark:text-gray-400">
					{data.length}
				</div>
				<div class="text-sm text-gray-800 dark:text-gray-200">
					Data Points
				</div>
			</div>
		</div>
	{/if}

	<!-- Chart -->
	<div class="relative">
		{#if data && data.length > 0}
			<ChartWrapper 
				type="line" 
				data={chartData} 
				options={chartOptions} 
				{height} 
			/>
		{:else}
			<div class="flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg" style="height: {height}">
				<div class="text-center text-gray-500 dark:text-gray-400">
					<svg class="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
					</svg>
					<p class="text-lg font-medium mb-1">No engagement data</p>
					<p class="text-sm">Data will appear as students interact with your courses</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- Data Insights -->
	{#if data && data.length > 2}
		<div class="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg">
			<strong>Insights:</strong>
			{#if summaryStats.engagementTrend > 0}
				📈 Student engagement is trending upward ({summaryStats.engagementTrend > 1 ? 'strongly' : 'slightly'}).
			{:else if summaryStats.engagementTrend < 0}
				📉 Student engagement is declining ({summaryStats.engagementTrend < -1 ? 'significantly' : 'slightly'}). Consider engaging with students or updating content.
			{:else}
				📊 Student engagement remains stable across the selected period.
			{/if}
			
			{#if summaryStats.maxActive > summaryStats.avgActive * 1.5}
				Peak activity was {summaryStats.avgActive > 0 ? Math.round((summaryStats.maxActive / summaryStats.avgActive - 1) * 100) || 0 : 0}% above average - analyze what drove this spike.
			{/if}
		</div>
	{/if}
</div>
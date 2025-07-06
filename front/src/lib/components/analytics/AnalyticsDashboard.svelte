<!-- front/src/lib/components/analytics/AnalyticsDashboard.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { fade, slide } from 'svelte/transition';
	import { analyticsService } from '$lib/services/analytics.service.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { debounce } from '$lib/utils/helpers.js';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';
	import EngagementChart from '$lib/components/analytics/EngagementChart.svelte';

	let {
		type = 'teacher', // 'teacher', 'student', 'platform'
		courseId = null,
		timeRange = '30d',
		autoRefresh = true,
		showExport = true,
		class: className = ''
	} = $props();

	// State
	let analytics = $state(null);
	let loading = $state(true);
	let error = $state('');
	let refreshing = $state(false);
	let selectedMetric = $state('overview');

	// Auto-refresh
	let refreshInterval;

	// Time range options
	const timeRanges = [
		{ value: '7d', label: 'Last 7 days' },
		{ value: '30d', label: 'Last 30 days' },
		{ value: '90d', label: 'Last 3 months' },
		{ value: '6m', label: 'Last 6 months' },
		{ value: 'all', label: 'All time' }
	];

	// Metric options based on type
	const metrics = $derived(() => {
		if (type === 'teacher') {
			return [
				{ id: 'overview', label: 'Overview', icon: '📊' },
				{ id: 'engagement', label: 'Engagement', icon: '⚡' },
				{ id: 'progress', label: 'Progress', icon: '📈' },
				{ id: 'performance', label: 'Performance', icon: '🎯' },
				{ id: 'revenue', label: 'Revenue', icon: '💰' }
			];
		} else if (type === 'student') {
			return [
				{ id: 'overview', label: 'Overview', icon: '📊' },
				{ id: 'progress', label: 'Progress', icon: '📈' },
				{ id: 'study_time', label: 'Study Time', icon: '⏱️' },
				{ id: 'performance', label: 'Performance', icon: '🎯' },
				{ id: 'goals', label: 'Goals', icon: '🏆' }
			];
		} else {
			return [
				{ id: 'overview', label: 'Overview', icon: '📊' },
				{ id: 'users', label: 'Users', icon: '👥' },
				{ id: 'courses', label: 'Courses', icon: '📚' },
				{ id: 'engagement', label: 'Engagement', icon: '⚡' },
				{ id: 'growth', label: 'Growth', icon: '📈' }
			];
		}
	});

	// Derived analytics data
	let summary = $derived(() => analytics?.summary || {});
	let charts = $derived(() => analytics?.charts || {});
	let insights = $derived(() => analytics?.insights || []);

	// Key metrics based on type
	let keyMetrics = $derived(() => {
		if (!analytics?.summary) return [];

		if (type === 'teacher') {
			return [
				{
					title: 'Total Courses',
					value: summary.total_courses || 0,
					change: '+2',
					trend: 'up',
					icon: '📚',
					color: 'blue'
				},
				{
					title: 'Active Students',
					value: summary.active_students_7d || 0,
					change: '+12%',
					trend: 'up',
					icon: '👥',
					color: 'green'
				},
				{
					title: 'Avg Progress',
					value: `${Math.round(summary.avg_progress || 0)}%`,
					change: '+5%',
					trend: 'up',
					icon: '📈',
					color: 'purple'
				},
				{
					title: 'Course Rating',
					value: (summary.avg_course_rating || 0).toFixed(1),
					change: '+0.2',
					trend: 'up',
					icon: '⭐',
					color: 'yellow'
				}
			];
		} else if (type === 'student') {
			return [
				{
					title: 'Courses Enrolled',
					value: summary.total_courses || 0,
					change: '+1',
					trend: 'up',
					icon: '📚',
					color: 'blue'
				},
				{
					title: 'Completed',
					value: summary.completed_courses || 0,
					change: '+1',
					trend: 'up',
					icon: '✅',
					color: 'green'
				},
				{
					title: 'Study Hours',
					value: Math.round(summary.study_hours_30d || 0),
					change: '+3h',
					trend: 'up',
					icon: '⏱️',
					color: 'purple'
				},
				{
					title: 'Learning Streak',
					value: summary.learning_streak || 0,
					change: '+2',
					trend: 'up',
					icon: '🔥',
					color: 'orange'
				}
			];
		} else {
			return [
				{
					title: 'Total Users',
					value: formatters.number(summary.total_users || 0),
					change: '+12%',
					trend: 'up',
					icon: '👥',
					color: 'blue'
				},
				{
					title: 'Active Courses',
					value: summary.active_courses || 0,
					change: '+8',
					trend: 'up',
					icon: '📚',
					color: 'green'
				},
				{
					title: 'Enrollments',
					value: formatters.number(summary.total_enrollments || 0),
					change: '+25%',
					trend: 'up',
					icon: '📈',
					color: 'purple'
				},
				{
					title: 'Engagement Rate',
					value: `${Math.round(summary.engagement_rate || 0) || 0}%`,
					change: '+3%',
					trend: 'up',
					icon: '⚡',
					color: 'yellow'
				}
			];
		}
	});

	onMount(async () => {
		await loadAnalytics();
		if (autoRefresh) {
			startAutoRefresh();
		}
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadAnalytics() {
		loading = true;
		error = '';

		try {
			if (type === 'teacher') {
				analytics = await analyticsService.getTeacherAnalytics();
			} else if (type === 'student') {
				analytics = await analyticsService.getStudentAnalytics();
			} else {
				analytics = await analyticsService.getPlatformAnalytics();
			}
		} catch (err) {
			console.error('Failed to load analytics:', err);
			error = err.message || 'Failed to load analytics data';
		} finally {
			loading = false;
		}
	}

	function startAutoRefresh() {
		refreshInterval = setInterval(async () => {
			if (!refreshing) {
				await refreshAnalytics();
			}
		}, 5 * 60 * 1000); // Refresh every 5 minutes
	}

	async function refreshAnalytics() {
		refreshing = true;
		try {
			await loadAnalytics();
		} catch (err) {
			console.error('Failed to refresh analytics:', err);
		} finally {
			refreshing = false;
		}
	}

	const debouncedTimeRangeChange = debounce(async (newRange) => {
		timeRange = newRange;
		await loadAnalytics();
	}, 300);

	function exportAnalytics() {
		if (!analytics) return;

		const exportData = {
			type,
			courseId,
			timeRange,
			exportDate: new Date().toISOString(),
			analytics: analytics,
			summary: summary
		};

		const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.href = url;
		link.download = `${type}-analytics-${timeRange}-${new Date().toISOString().split('T')[0]}.json`;
		link.click();
		URL.revokeObjectURL(url);
	}

	function handleMetricChange(metricId) {
		selectedMetric = metricId;
	}
</script>

<div class="space-y-6 {className}">
	<!-- Header Controls -->
	<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
		<div>
			<h2 class="text-2xl font-bold text-gray-900 dark:text-white capitalize">
				{type} Analytics
			</h2>
			<p class="text-gray-600 dark:text-gray-400">
				{#if courseId}
					Course-specific analytics for the selected time period
				{:else}
					Comprehensive analytics dashboard for the selected time period
				{/if}
			</p>
		</div>

		<div class="flex flex-col sm:flex-row gap-3">
			<!-- Time Range Selector -->
			<select
				bind:value={timeRange}
				onchange={(e) => debouncedTimeRangeChange(e.target.value)}
				class="px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
			>
				{#each timeRanges as range}
					<option value={range.value}>{range.label}</option>
				{/each}
			</select>

			<!-- Action Buttons -->
			<div class="flex gap-2">
				<Button
					onclick={refreshAnalytics}
					variant="outline"
					size="medium"
					disabled={refreshing}
					loading={refreshing}
				>
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
					</svg>
					Refresh
				</Button>

				{#if showExport}
					<Button
						onclick={exportAnalytics}
						variant="primary"
						size="medium"
						disabled={!analytics}
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						Export
					</Button>
				{/if}
			</div>
		</div>
	</div>

	<!-- Metric Navigation -->
	<div class="border-b border-gray-200 dark:border-gray-700">
		<nav class="flex space-x-8 overflow-x-auto">
			{#each metrics as metric}
				<button
					onclick={() => handleMetricChange(metric.id)}
					class="py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors {selectedMetric === metric.id
						? 'border-blue-500 text-blue-600 dark:text-blue-400'
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}"
				>
					<span class="mr-2">{metric.icon}</span>
					{metric.label}
				</button>
			{/each}
		</nav>
	</div>

	<!-- Error State -->
	{#if error}
		<div class="text-center py-12" in:fade={{ duration: 300 }}>
			<div class="mb-4">
				<svg class="mx-auto h-16 w-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
			</div>
			<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Analytics Error</h3>
			<p class="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
			<Button onclick={loadAnalytics} variant="primary" size="medium">
				Try Again
			</Button>
		</div>
	{:else if loading}
		<!-- Loading State -->
		<div class="space-y-6">
			<!-- Key Metrics Loading -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				{#each Array(4) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="h-4 bg-gray-200 rounded w-1/2 mb-2 dark:bg-gray-700"></div>
							<div class="h-8 bg-gray-200 rounded w-3/4 mb-2 dark:bg-gray-700"></div>
							<div class="h-3 bg-gray-200 rounded w-1/3 dark:bg-gray-700"></div>
						</Card>
					</div>
				{/each}
			</div>

			<!-- Charts Loading -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				{#each Array(2) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="h-6 bg-gray-200 rounded w-1/3 mb-4 dark:bg-gray-700"></div>
							<div class="h-64 bg-gray-200 rounded dark:bg-gray-700"></div>
						</Card>
					</div>
				{/each}
			</div>
		</div>
	{:else if analytics}
		<!-- Analytics Content -->
		<div in:fade={{ duration: 300 }}>
			<!-- Key Metrics -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
				{#each keyMetrics as metric}
					<StatsCard
						title={metric.title}
						value={metric.value}
						trend={metric.change}
						trendDirection={metric.trend}
						icon={metric.icon}
						color={metric.color}
					/>
				{/each}
			</div>

			<!-- Charts Section -->
			{#if selectedMetric === 'overview'}
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
					{#if charts.progressChart}
						<Card class="p-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
								{charts.progressChart.title || 'Progress Overview'}
							</h3>
							<ChartWrapper
								type={charts.progressChart.type}
								data={charts.progressChart.data}
								options={charts.progressChart.options}
								height="300px"
							/>
						</Card>
					{/if}

					{#if charts.studyTimeChart}
						<Card class="p-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
								{charts.studyTimeChart.title || 'Activity Overview'}
							</h3>
							<ChartWrapper
								type={charts.studyTimeChart.type}
								data={charts.studyTimeChart.data}
								options={charts.studyTimeChart.options}
								height="300px"
							/>
						</Card>
					{/if}
				</div>
			{:else if selectedMetric === 'engagement'}
				<div class="mb-6">
					<EngagementChart
						data={analytics.engagementData || []}
						title="Student Engagement Trends"
						{timeRange}
						height="400px"
					/>
				</div>
			{:else}
				<!-- Other metric views -->
				<Card class="p-8 text-center mb-6">
					<div class="mb-4">
						<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
						</svg>
					</div>
					<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
						{metrics.find(m => m.id === selectedMetric)?.label} Analytics
					</h3>
					<p class="text-gray-600 dark:text-gray-400">
						Detailed {selectedMetric} analytics will be displayed here.
					</p>
				</Card>
			{/if}

			<!-- Insights -->
			{#if insights && insights.length > 0}
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
						Key Insights
					</h3>
					<div class="space-y-3">
						{#each insights as insight}
							<div class="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg" in:slide>
								<div class="flex-shrink-0">
									<svg class="h-5 w-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
								</div>
								<div class="flex-1">
									<p class="text-sm text-blue-800 dark:text-blue-200 font-medium">
										{insight.title}
									</p>
									<p class="text-sm text-blue-700 dark:text-blue-300 mt-1">
										{insight.description}
									</p>
								</div>
							</div>
						{/each}
					</div>
				</Card>
			{/if}
		</div>
	{:else}
		<!-- No Data State -->
		<div class="text-center py-12">
			<div class="mb-4">
				<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
				</svg>
			</div>
			<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
				No Analytics Data
			</h3>
			<p class="text-gray-600 dark:text-gray-400">
				Analytics data will appear here once you have activity to track.
			</p>
		</div>
	{/if}
</div>
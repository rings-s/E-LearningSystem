<!-- front/src/lib/components/dashboard/ManagerDashboard.svelte -->
<script>
	import { fade, fly } from 'svelte/transition';
	import { formatters } from '$lib/utils/formatters.js';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';

	let { data, analytics, courses = [], onAction = () => {} } = $props();

	// Derived data from backend analytics
	const platformHealth = $derived(analytics?.platform_health || {});
	const userGrowth = $derived(analytics?.user_growth || []);
	const categoryInsights = $derived(analytics?.category_insights || []);
	const charts = $derived(analytics?.charts || {});

	// Platform calculations
	const growthRate = $derived(() => {
		if (!userGrowth || userGrowth.length < 2) return 0;
		const current = userGrowth[userGrowth.length - 1]?.new_users || 0;
		const previous = userGrowth[userGrowth.length - 2]?.new_users || 0;
		if (previous === 0) return 0;
		return Math.round(((current - previous) / previous) * 100);
	});

	const systemHealth = $derived(() => {
		const engagementRate = platformHealth.user_engagement_rate || 0;
		if (engagementRate >= 80) return { status: 'excellent', color: 'green' };
		if (engagementRate >= 60) return { status: 'good', color: 'blue' };
		if (engagementRate >= 40) return { status: 'fair', color: 'yellow' };
		return { status: 'needs attention', color: 'red' };
	});

	// Chart data for user growth
	const userGrowthChart = $derived(() => ({
		labels: userGrowth.map(item => item.month || ''),
		datasets: [{
			label: 'New Users',
			data: userGrowth.map(item => item.new_users || 0),
			borderColor: '#3b82f6',
			backgroundColor: 'rgba(59, 130, 246, 0.1)',
			fill: true,
			tension: 0.4
		}]
	}));

	// Chart data for category distribution
	const categoryChart = $derived(() => ({
		labels: categoryInsights.map(cat => cat.category || ''),
		datasets: [{
			label: 'Courses',
			data: categoryInsights.map(cat => cat.courses || 0),
			backgroundColor: [
				'#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#10b981',
				'#06b6d4', '#f97316', '#84cc16', '#ec4899', '#6366f1'
			]
		}]
	}));
</script>

<div class="space-y-8">
	<!-- Platform Metrics -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" in:fly={{ y: 20, duration: 600 }}>
		<StatsCard
			title="Total Users"
			value={formatters.number(platformHealth.total_users || 0)}
			trend="{growthRate > 0 ? '+' : ''}{growthRate}%"
			trendDirection={growthRate > 0 ? 'up' : 'down'}
			icon="👥"
			color="blue"
		/>
		<StatsCard
			title="Active Users"
			value={formatters.number(platformHealth.active_users_30d || 0)}
			trend="{formatters.safeRound(platformHealth.user_engagement_rate)}% engagement"
			trendDirection="up"
			icon="⚡"
			color="green"
		/>
		<StatsCard
			title="Total Courses"
			value={platformHealth.total_courses || 0}
			trend="{platformHealth.published_courses || 0} published"
			trendDirection="up"
			icon="📚"
			color="purple"
		/>
		<StatsCard
			title="Total Enrollments"
			value={formatters.number(platformHealth.total_enrollments || 0)}
			trend="Active learning"
			trendDirection="up"
			icon="📈"
			color="orange"
		/>
	</div>

	<!-- System Health Overview -->
	<Card class="p-6 bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 border-slate-200 dark:border-slate-700">
		<div class="flex items-center justify-between mb-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Platform Health</h3>
			<Badge
				variant={systemHealth.color === 'green' ? 'success' : systemHealth.color === 'blue' ? 'primary' : systemHealth.color === 'yellow' ? 'warning' : 'danger'}
				class="capitalize"
			>
				{systemHealth.status}
			</Badge>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<div class="text-center">
				<div class="text-3xl font-bold text-blue-600 dark:text-blue-400">
					{formatters.safeRound(platformHealth.user_engagement_rate)}%
				</div>
				<div class="text-sm text-gray-600 dark:text-gray-400">User Engagement</div>
			</div>
			<div class="text-center">
				<div class="text-3xl font-bold text-green-600 dark:text-green-400">
					{platformHealth.active_users_30d || 0}
				</div>
				<div class="text-sm text-gray-600 dark:text-gray-400">Active Users (30d)</div>
			</div>
			<div class="text-center">
				<div class="text-3xl font-bold text-purple-600 dark:text-purple-400">
					{Math.round(((platformHealth.published_courses || 0) / (platformHealth.total_courses || 1)) * 100)}%
				</div>
				<div class="text-sm text-gray-600 dark:text-gray-400">Course Publish Rate</div>
			</div>
		</div>
	</Card>

	<!-- Analytics Charts -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
		<!-- User Growth Chart -->
		<Card class="p-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">User Growth Trend</h3>
			{#if userGrowth && userGrowth.length > 0}
				<ChartWrapper
					type="line"
					data={userGrowthChart}
					options={{
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: { display: false }
						},
						scales: {
							y: { 
								beginAtZero: true,
								title: { display: true, text: 'New Users' }
							},
							x: { 
								title: { display: true, text: 'Month' }
							}
						}
					}}
					height="300px"
				/>
			{:else}
				<div class="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
					<div class="text-center">
						<svg class="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
						</svg>
						<p>No growth data available</p>
					</div>
				</div>
			{/if}
		</Card>

		<!-- Category Distribution -->
		<Card class="p-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">Course Categories</h3>
			{#if categoryInsights && categoryInsights.length > 0}
				<ChartWrapper
					type="doughnut"
					data={categoryChart}
					options={{
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: { 
								position: 'bottom',
								labels: { padding: 20 }
							}
						}
					}}
					height="300px"
				/>
			{:else}
				<div class="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
					<div class="text-center">
						<svg class="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
						</svg>
						<p>No category data available</p>
					</div>
				</div>
			{/if}
		</Card>
	</div>

	<!-- Category Performance Table -->
	{#if categoryInsights && categoryInsights.length > 0}
		<Card class="p-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">Category Performance</h3>
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
					<thead class="bg-gray-50 dark:bg-gray-800">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
								Category
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
								Courses
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
								Enrollments
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
								Avg. Enrollment
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
						{#each categoryInsights as category}
							<tr class="hover:bg-gray-50 dark:hover:bg-gray-800">
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="font-medium text-gray-900 dark:text-white">
										{category.category}
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-gray-500 dark:text-gray-400">
									{category.courses}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-gray-500 dark:text-gray-400">
									{formatters.number(category.enrollments)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										<div class="text-gray-900 dark:text-white font-medium">
											{category.courses > 0 ? Math.round(category.enrollments / category.courses) : 0}
										</div>
										<div class="ml-2">
											{#if category.courses > 0 && (category.enrollments / category.courses) > 50}
												<Badge variant="success" size="small">High</Badge>
											{:else if category.courses > 0 && (category.enrollments / category.courses) > 20}
												<Badge variant="warning" size="small">Medium</Badge>
											{:else}
												<Badge variant="secondary" size="small">Low</Badge>
											{/if}
										</div>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</Card>
	{/if}

	<!-- Management Quick Actions -->
	<Card class="p-6">
		<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">
			Platform Management
		</h3>
		
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<Button
				href="/admin/users"
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-blue-50 dark:hover:bg-blue-900/20"
			>
				<svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
				</svg>
				<span>Manage Users</span>
			</Button>

			<Button
				href="/admin/courses"
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-green-50 dark:hover:bg-green-900/20"
			>
				<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
				</svg>
				<span>Manage Courses</span>
			</Button>

			<Button
				href="/admin/analytics"
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-purple-50 dark:hover:bg-purple-900/20"
			>
				<svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
				</svg>
				<span>View Analytics</span>
			</Button>

			<Button
				href="/admin/settings"
				variant="outline"
				class="h-20 flex-col space-y-2 hover:bg-orange-50 dark:hover:bg-orange-900/20"
			>
				<svg class="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
				</svg>
				<span>Platform Settings</span>
			</Button>
		</div>
	</Card>
</div>
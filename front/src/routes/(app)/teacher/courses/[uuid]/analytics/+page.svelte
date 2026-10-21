<script>
	import { page } from '$app/state';
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { coursesApi } from '#lib/apis/courses.js';
	import { coreApi } from '#lib/apis/core.js';
	import { analyticsService } from '#lib/services/analytics.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t, locale } from '#lib/i18n/index.js';
	import { formatters } from '#lib/utils/formatters.js';
	import { debounce } from '#lib/utils/helpers.js';

	// Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import StatsCard from '#lib/components/dashboard/StatsCard.svelte';
	import ChartWrapper from '#lib/components/charts/ChartWrapper.svelte';
	import ProgressChart from '#lib/components/charts/ProgressChart.svelte';
	import ActivityChart from '#lib/components/charts/ActivityChart.svelte';

	// Route params
	let courseId = page.params.uuid;

	// State variables
	let course = $state(null);
	let analytics = $state(null);
	let loading = $state(true);
	let error = $state('');
	let refreshing = $state(false);
	let selectedTimeRange = $state('30d');
	let selectedTab = $state('overview');

	// Analytics data
	let studentsData = $state([]);
	let progressData = $state([]);
	let engagementData = $state([]);
	let performanceMetrics = $state(null);

	// Auto-refresh interval
	let refreshInterval;

	// Time range options
	const timeRanges = $derived([
		{ value: '7d', label: $t('analyticsPage.last7') },
		{ value: '30d', label: $t('analyticsPage.last30') },
		{ value: '90d', label: $t('analyticsPage.last90') },
		{ value: 'all', label: $t('analyticsPage.allTime') }
	]);

	// Tab options
	const tabs = $derived([
		{ id: 'overview', label: $t('analyticsPage.overview'), icon: '📊' },
		{ id: 'students', label: $t('analyticsPage.students'), icon: '👥' },
		{ id: 'progress', label: $t('analyticsPage.progress'), icon: '📈' },
		{ id: 'engagement', label: $t('analyticsPage.engagement'), icon: '⚡' },
		{ id: 'performance', label: $t('analyticsPage.performance'), icon: '🎯' }
	]);

	// Derived analytics with better error handling
	let progressDistribution = $derived.by(() => {
		if (!analytics?.studentActivity?.progress_distribution) {
			return { not_started: 0, in_progress: 0, completed: 0 };
		}
		const dist = analytics.studentActivity.progress_distribution;
		return {
			not_started: Number(dist.not_started) || 0,
			in_progress: Number(dist.in_progress) || 0,
			completed: Number(dist.completed) || 0
		};
	});

	let averageProgress = $derived.by(() => {
		if (!studentsData || !Array.isArray(studentsData) || studentsData.length === 0) return 0;

		const validProgresses = studentsData
			.map((student) => Number(student.progress) || 0)
			.filter((progress) => !isNaN(progress));

		if (validProgresses.length === 0) return 0;
		const total = validProgresses.reduce((sum, progress) => sum + progress, 0);
		return Math.round(total / validProgresses.length);
	});

	let completionRate = $derived.by(() => {
		if (!progressDistribution) return 0;
		const notStarted = Number(progressDistribution.not_started) || 0;
		const inProgress = Number(progressDistribution.in_progress) || 0;
		const completed = Number(progressDistribution.completed) || 0;
		const total = notStarted + inProgress + completed;
		if (total === 0 || isNaN(total)) return 0;
		const rate = (completed / total) * 100;
		return isNaN(rate) ? 0 : Math.round(rate);
	});

	let engagementRate = $derived.by(() => {
		if (!analytics?.summary) return 0;
		const total = Number(analytics.summary.total_students) || 0;
		const active = Number(analytics.summary.active_students_7d) || 0;
		if (total === 0 || isNaN(total) || isNaN(active)) return 0;
		const rate = (active / total) * 100;
		return isNaN(rate) ? 0 : Math.round(rate);
	});

	// Chart configurations
	let progressChartData = $derived.by(() => ({
		labels: [
			$t('analyticsPage.notStarted'),
			$t('analyticsPage.inProgress'),
			$t('analyticsPage.completed')
		],
		datasets: [
			{
				label: $t('analyticsPage.students'),
				data: [
					progressDistribution.not_started,
					progressDistribution.in_progress,
					progressDistribution.completed
				],
				backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
				borderWidth: 2,
				borderColor: '#ffffff'
			}
		]
	}));

	let engagementChartData = $derived.by(() => {
		if (!engagementData || engagementData.length === 0) {
			return {
				labels: [],
				datasets: [
					{
						label: $t('analyticsPage.activeStudents'),
						data: [],
						borderColor: '#3b82f6',
						backgroundColor: 'rgba(59, 130, 246, 0.1)',
						fill: true,
						tension: 0.4
					}
				]
			};
		}

		return {
			labels: engagementData.map((d) => formatters.shortDate(d.date)),
			datasets: [
				{
					label: $t('analyticsPage.activeStudents'),
					data: engagementData.map((d) => d.active_students),
					borderColor: '#3b82f6',
					backgroundColor: 'rgba(59, 130, 246, 0.1)',
					fill: true,
					tension: 0.4
				}
			]
		};
	});

	onMount(async () => {
		// Check if user is authorized to view analytics
		if (!$currentUser || ($currentUser.role !== 'teacher' && !$currentUser.is_staff)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('errors.unauthorized'),
				message: $t('analyticsPage.teacherOnly')
			});
			return;
		}

		await loadCourseAnalytics();
		startAutoRefresh();
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadCourseAnalytics() {
		loading = true;
		error = '';

		try {
			// Load course details first
			const courseResponse = await coursesApi.getCourse(courseId);
			course = courseResponse;

			// Verify user is the instructor
			if (course.instructor?.id !== $currentUser.id && !$currentUser.is_staff) {
				throw new Error('You are not authorized to view analytics for this course');
			}

			// Load course analytics
			const analyticsResponse = await coursesApi.getCourseAnalytics(courseId);
			analytics = analyticsResponse;

			// Load detailed student data
			await loadStudentsData();
			await loadProgressData();
			await loadEngagementData();
			await loadPerformanceMetrics();
		} catch (err) {
			console.error('Failed to load course analytics:', err);
			error = err.message || $t('analyticsPage.loadFailed');

			uiStore.showNotification({
				type: 'error',
				title: $t('analyticsPage.analyticsError'),
				message: error
			});
		} finally {
			loading = false;
		}
	}

	async function loadStudentsData() {
		try {
			const response = await coursesApi.getCourseStudents(courseId, {
				time_range: selectedTimeRange,
				include_progress: true
			});
			studentsData = response.students || response.results || [];
		} catch (err) {
			console.error('Failed to load students data:', err);
			studentsData = [];
		}
	}

	async function loadProgressData() {
		try {
			const response = await coursesApi.getCourseAnalytics(courseId);
			progressData = response.progress_data || response.enrollments || [];
		} catch (err) {
			console.error('Failed to load progress data:', err);
			progressData = [];
		}
	}

	async function loadEngagementData() {
		try {
			const response = await coursesApi.getCourseAnalytics(courseId);
			engagementData = response.engagement_data || response.student_activity || [];
		} catch (err) {
			console.error('Failed to load engagement data:', err);
			engagementData = [];
		}
	}

	async function loadPerformanceMetrics() {
		try {
			const response = await coursesApi.getCourseAnalytics(courseId);
			performanceMetrics = response.performance_metrics || response;
		} catch (err) {
			console.error('Failed to load performance metrics:', err);
			performanceMetrics = null;
		}
	}

	function startAutoRefresh() {
		// Refresh analytics every 5 minutes
		refreshInterval = setInterval(
			async () => {
				if (!refreshing) {
					await refreshAnalytics();
				}
			},
			5 * 60 * 1000
		);
	}

	async function refreshAnalytics() {
		refreshing = true;
		try {
			await loadCourseAnalytics();
		} catch (err) {
			console.error('Failed to refresh analytics:', err);
		} finally {
			refreshing = false;
		}
	}

	const debouncedTimeRangeChange = debounce(async (newRange) => {
		selectedTimeRange = newRange;
		await loadCourseAnalytics();
	}, 300);

	function handleTabChange(tabId) {
		selectedTab = tabId;
	}

	function exportAnalytics() {
		if (!analytics) return;

		// Generate PDF report
		generatePDFReport();
	}

	function generatePDFReport() {
		// Create a new window for the PDF content
		const printWindow = window.open('', '_blank');
		if (!printWindow) {
			uiStore.showNotification({
				type: 'error',
				title: $t('analyticsPage.exportError'),
				message: $t('analyticsPage.allowPopups')
			});
			return;
		}

		const currentDate = new Date().toLocaleDateString();
		const currentTime = new Date().toLocaleTimeString();

		// Generate comprehensive PDF content
		const pdfContent = `
		<!DOCTYPE html>
		<html>
		<head>
			<title>Course Analytics Report - ${course?.title || 'Course'}</title>
			<style>
				body {
					font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
					line-height: 1.6;
					color: #333;
					max-width: 800px;
					margin: 0 auto;
					padding: 20px;
				}
				.header {
					text-align: center;
					border-bottom: 3px solid #3b82f6;
					padding-bottom: 20px;
					margin-bottom: 30px;
				}
				.header h1 {
					color: #3b82f6;
					margin: 0 0 10px 0;
					font-size: 28px;
				}
				.header .subtitle {
					color: #6b7280;
					font-size: 16px;
					margin: 5px 0;
				}
				.stats-grid {
					display: grid;
					grid-template-columns: repeat(4, 1fr);
					gap: 20px;
					margin: 30px 0;
				}
				.stat-card {
					background: #f8fafc;
					border: 1px solid #e2e8f0;
					border-radius: 8px;
					padding: 20px;
					text-align: center;
				}
				.stat-value {
					font-size: 24px;
					font-weight: bold;
					color: #1f2937;
					margin-bottom: 5px;
				}
				.stat-label {
					font-size: 14px;
					color: #6b7280;
				}
				.section {
					margin: 40px 0;
				}
				.section h2 {
					color: #1f2937;
					font-size: 20px;
					border-bottom: 2px solid #e5e7eb;
					padding-bottom: 10px;
					margin-bottom: 20px;
				}
				.table {
					width: 100%;
					border-collapse: collapse;
					margin: 20px 0;
				}
				.table th, .table td {
					border: 1px solid #e5e7eb;
					padding: 12px;
					text-align: left;
				}
				.table th {
					background: #f3f4f6;
					font-weight: 600;
				}
				.progress-bar {
					width: 100px;
					height: 6px;
					background: #e5e7eb;
					border-radius: 3px;
					overflow: hidden;
				}
				.progress-fill {
					height: 100%;
					background: #3b82f6;
				}
				.footer {
					margin-top: 50px;
					padding-top: 20px;
					border-top: 1px solid #e5e7eb;
					text-align: center;
					color: #6b7280;
					font-size: 12px;
				}
				@media print {
					body { margin: 0; padding: 15px; }
					.stats-grid { grid-template-columns: repeat(2, 1fr); }
				}
			</style>
		</head>
		<body>
			<div class="header">
				<h1>Course Analytics Report</h1>
				<div class="subtitle">${course?.title || 'Course Title'}</div>
				<div class="subtitle">Instructor: ${course?.instructor?.name || 'Unknown'}</div>
				<div class="subtitle">Report Generated: ${currentDate} at ${currentTime}</div>
				<div class="subtitle">Time Period: ${timeRanges.find((r) => r.value === selectedTimeRange)?.label || selectedTimeRange}</div>
			</div>

			<div class="stats-grid">
				<div class="stat-card">
					<div class="stat-value">${analytics.summary?.total_students || 0}</div>
					<div class="stat-label">{$t('analyticsPage.totalStudents')}</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">${averageProgress}%</div>
					<div class="stat-label">{$t('analyticsPage.averageProgress')}</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">${completionRate}%</div>
					<div class="stat-label">{$t('analyticsPage.completionRate')}</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">${engagementRate}%</div>
					<div class="stat-label">{$t('analyticsPage.engagementRate')}</div>
				</div>
			</div>

			<div class="section">
				<h2>Progress Distribution</h2>
				<table class="table">
					<tr>
						<th>{$t('analyticsPage.status')}</th>
						<th>{$t('analyticsPage.students')}</th>
						<th>Percentage</th>
					</tr>
					<tr>
						<td>{$t('analyticsPage.notStarted')}</td>
						<td>${progressDistribution.not_started}</td>
						<td>${Math.round((progressDistribution.not_started / (progressDistribution.not_started + progressDistribution.in_progress + progressDistribution.completed || 1)) * 100)}%</td>
					</tr>
					<tr>
						<td>{$t('analyticsPage.inProgress')}</td>
						<td>${progressDistribution.in_progress}</td>
						<td>${Math.round((progressDistribution.in_progress / (progressDistribution.not_started + progressDistribution.in_progress + progressDistribution.completed || 1)) * 100)}%</td>
					</tr>
					<tr>
						<td>{$t('analyticsPage.completed')}</td>
						<td>${progressDistribution.completed}</td>
						<td>${Math.round((progressDistribution.completed / (progressDistribution.not_started + progressDistribution.in_progress + progressDistribution.completed || 1)) * 100)}%</td>
					</tr>
				</table>
			</div>

			${
				studentsData && studentsData.length > 0
					? `
			<div class="section">
				<h2>Student Details</h2>
				<table class="table">
					<tr>
						<th>{$t('analyticsPage.student')}</th>
						<th>{$t('analyticsPage.progress')}</th>
						<th>{$t('analyticsPage.lastActive')}</th>
						<th>{$t('analyticsPage.status')}</th>
					</tr>
					${studentsData
						.slice(0, 20)
						.map(
							(student) => `
					<tr>
						<td>${student.name || 'Anonymous'}</td>
						<td>
							<div class="progress-bar">
								<div class="progress-fill" style="width: ${student.progress || 0}%"></div>
							</div>
							${student.progress || 0}%
						</td>
						<td>${student.last_active ? new Date(student.last_active).toLocaleDateString() : 'Never'}</td>
						<td>${student.status || 'Active'}</td>
					</tr>
					`
						)
						.join('')}
					${
						studentsData.length > 20
							? `
					<tr>
						<td colspan="4" style="text-align: center; font-style: italic; color: #6b7280;">
							... and ${studentsData.length - 20} more students
						</td>
					</tr>
					`
							: ''
					}
				</table>
			</div>
			`
					: ''
			}

			<div class="section">
				<h2>Summary</h2>
				<p><strong>Total Students:</strong> ${analytics.summary?.total_students || 0}</p>
				<p><strong>Active Students (Last 7 days):</strong> ${analytics.summary?.active_students_7d || 0}</p>
				<p><strong>Average Course Rating:</strong> ${(analytics.summary?.avg_course_rating || 0).toFixed(1)}/5.0</p>
				<p><strong>Course Status:</strong> ${course?.status || 'Draft'}</p>
				<p><strong>Last Updated:</strong> ${course?.updated_at ? new Date(course.updated_at).toLocaleDateString() : 'Unknown'}</p>
			</div>

			<div class="footer">
				<p>Generated by E-Learning Platform Analytics System</p>
				<p>This report contains confidential student data and should be handled according to privacy policies.</p>
			</div>
		</body>
		</html>
		`;

		printWindow.document.write(pdfContent);
		printWindow.document.close();

		// Wait for content to load then trigger print
		setTimeout(() => {
			printWindow.focus();
			printWindow.print();
		}, 500);

		uiStore.showNotification({
			type: 'success',
			title: $t('analyticsPage.pdfReady'),
			message: "PDF report has been generated. Use your browser's print dialog to save as PDF."
		});
	}
</script>

<!-- front/src/routes/(app)/teacher/courses/[uuid]/analytics/+page.svelte -->

<svelte:head>
	<title
		>{course?.title
			? $t('analyticsPage.pageTitle', { title: course.title })
			: $t('analyticsPage.courseAnalytics')}</title
	>
</svelte:head>

<div>
	<div>
		<!-- Header -->
		{#if loading}
			<div class="mb-8" in:fade={{ duration: 300 }}>
				<div class="animate-pulse">
					<div class="mb-4 h-8 w-1/3 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-1/2 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>
		{:else if course}
			<div class="mb-8" in:fade={{ duration: 600 }}>
				<div class="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
					<div>
						<div class="mb-2 flex items-center gap-4">
							<Button
								href="/my-courses"
								variant="ghost"
								size="medium"
								class="hover:text-primary-600 dark:hover:text-primary-400 text-gray-600 dark:text-gray-400"
							>
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 19l-7-7 7-7"
									></path>
								</svg>
								{$t('analyticsPage.backToMyCourses')}
							</Button>
						</div>
						<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
							{course.title}
						</h1>
						<p class="text-gray-600 dark:text-gray-400">
							{$t('analyticsPage.dashboardUpdated', {
								time: formatters.relativeTime(Date.now(), $locale)
							})}
						</p>
					</div>

					<div class="flex flex-col gap-3 sm:flex-row">
						<!-- Time Range Selector -->
						<select
							bind:value={selectedTimeRange}
							onchange={(e) => debouncedTimeRangeChange(e.target.value)}
							class="focus:border-primary-500 focus:ring-primary-500 rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
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
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
									></path>
								</svg>
								{$t('analyticsPage.refresh')}
							</Button>

							<Button
								onclick={exportAnalytics}
								variant="primary"
								size="medium"
								disabled={!analytics}
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
									></path>
								</svg>
								{$t('analyticsPage.exportPdf')}
							</Button>
						</div>
					</div>
				</div>

				<!-- Tab Navigation -->
				<div class="border-b border-gray-200 dark:border-gray-700">
					<nav class="-mb-px flex scrollbar-thin gap-6 overflow-x-auto sm:gap-8">
						{#each tabs as tab}
							<button
								onclick={() => handleTabChange(tab.id)}
								class="shrink-0 border-b-2 px-1 py-4 text-sm font-medium whitespace-nowrap transition-colors {selectedTab ===
								tab.id
									? 'border-primary-500 text-primary-600 dark:text-primary-400'
									: 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}"
							>
								<span class="mr-2">{tab.icon}</span>
								{tab.label}
							</button>
						{/each}
					</nav>
				</div>
			</div>
		{/if}

		<!-- Error State -->
		{#if error}
			<div class="py-12 text-center" in:fade={{ duration: 300 }}>
				<div class="mb-4">
					<svg
						class="mx-auto h-16 w-16 text-red-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						></path>
					</svg>
				</div>
				<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
					{$t('analyticsPage.analyticsError')}
				</h3>
				<p class="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
				<Button onclick={loadCourseAnalytics} variant="primary" size="medium"
					>{$t('analyticsPage.tryAgain')}</Button
				>
			</div>
		{:else if loading}
			<div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				{#each Array(4) as _}
					<div class="animate-pulse">
						<Card class="p-6">
							<div class="mb-2 h-4 w-1/2 rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="mb-2 h-8 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-3 w-1/3 rounded bg-gray-200 dark:bg-gray-700"></div>
						</Card>
					</div>
				{/each}
			</div>
		{:else if analytics && selectedTab === 'overview'}
			<!-- Overview Tab -->
			<div in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<!-- Key Metrics -->
				<div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
					<StatsCard
						title={$t('analyticsPage.totalStudents')}
						value={analytics.summary?.total_students || 0}
						trend="+12%"
						trendDirection="up"
						icon="👥"
						color="blue"
					/>
					<StatsCard
						title={$t('analyticsPage.averageProgress')}
						value="{averageProgress}%"
						trend="+5%"
						trendDirection="up"
						icon="📈"
						color="green"
					/>
					<StatsCard
						title={$t('analyticsPage.completionRate')}
						value="{completionRate}%"
						trend="+8%"
						trendDirection="up"
						icon="✅"
						color="purple"
					/>
					<StatsCard
						title={$t('analyticsPage.engagementRate')}
						value="{engagementRate}%"
						trend="-2%"
						trendDirection="down"
						icon="⚡"
						color="yellow"
					/>
				</div>

				<!-- Charts -->
				<div class="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
					<!-- Progress Distribution -->
					<Card
						class="to-primary-50 dark:to-primary-900/20 border-primary-200 dark:border-primary-800 bg-gradient-to-br from-white p-6 dark:from-gray-800"
					>
						<div class="mb-4 flex items-center justify-between">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
								{$t('analyticsPage.progressDistribution')}
							</h3>
							<div class="text-sm text-gray-500 dark:text-gray-400">
								{progressDistribution.not_started +
									progressDistribution.in_progress +
									progressDistribution.completed} total students
							</div>
						</div>
						{#if progressDistribution.not_started + progressDistribution.in_progress + progressDistribution.completed > 0}
							<ChartWrapper
								type="doughnut"
								data={progressChartData}
								options={{
									responsive: true,
									maintainAspectRatio: false,
									plugins: {
										legend: {
											position: 'bottom',
											labels: {
												padding: 20,
												usePointStyle: true,
												font: {
													size: 14
												}
											}
										},
										tooltip: {
											backgroundColor: 'rgba(0, 0, 0, 0.8)',
											titleColor: '#ffffff',
											bodyColor: '#ffffff',
											callbacks: {
												label: function (context) {
													const label = context.label || '';
													const value = context.parsed;
													const total = context.dataset.data.reduce((a, b) => a + b, 0);
													const percentage = ((value / total) * 100).toFixed(1);
													return `${label}: ${value} students (${percentage}%)`;
												}
											}
										}
									},
									cutout: '50%',
									animation: {
										animateRotate: true,
										animateScale: true
									}
								}}
								height="300px"
							/>
						{:else}
							<div class="flex h-64 items-center justify-center text-gray-500 dark:text-gray-400">
								<div class="text-center">
									<svg
										class="mx-auto mb-2 h-12 w-12"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
										></path>
									</svg>
									<p class="font-medium">{$t('analyticsPage.noStudentData')}</p>
									<p class="text-sm">{$t('analyticsPage.studentsWillAppear')}</p>
								</div>
							</div>
						{/if}
					</Card>

					<!-- Engagement Over Time -->
					<Card
						class="border-green-200 bg-gradient-to-br from-white to-green-50 p-6 dark:border-green-800 dark:from-gray-800 dark:to-green-900/20"
					>
						<div class="mb-4 flex items-center justify-between">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
								{$t('analyticsPage.studentEngagement')}
							</h3>

							<div class="text-sm text-gray-500 dark:text-gray-400">
								{timeRanges.find((r) => r.value === selectedTimeRange)?.label || selectedTimeRange}
							</div>
						</div>

						{#if engagementData && engagementData.length > 0}
							<ChartWrapper
								type="line"
								data={engagementChartData}
								options={{
									responsive: true,
									maintainAspectRatio: false,
									interaction: {
										intersect: false,
										mode: 'index'
									},
									plugins: {
										legend: {
											display: false
										},
										tooltip: {
											backgroundColor: 'rgba(0, 0, 0, 0.8)',
											titleColor: '#ffffff',
											bodyColor: '#ffffff',
											borderColor: '#3b82f6',
											borderWidth: 1,
											callbacks: {
												title: (context) => {
													return formatters.fullDate(engagementData[context[0].dataIndex]?.date);
												},
												label: (context) => {
													return $t('analyticsPage.activeStudentsValue', {
														count: context.parsed.y
													});
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
									},
									animation: {
										duration: 1000,
										easing: 'easeInOutQuart'
									}
								}}
								height="300px"
							/>
						{:else}
							<div class="flex h-64 items-center justify-center text-gray-500 dark:text-gray-400">
								<div class="text-center">
									<svg
										class="mx-auto mb-2 h-12 w-12"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
										></path>
									</svg>
									<p class="font-medium">{$t('analyticsPage.noEngagement')}</p>
									<p class="text-sm">{$t('analyticsPage.dataWillAppear')}</p>
								</div>
							</div>
						{/if}
					</Card>
				</div>

				<!-- Recent Activity -->
				<Card class="p-6">
					<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
						{$t('analyticsPage.recentActivity')}
					</h3>
					{#if studentsData && studentsData.length > 0}
						<div class="space-y-4">
							{#each studentsData.slice(0, 5) as student}
								<div
									class="flex items-center justify-between rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50"
								>
									<div class="flex items-center space-x-4">
										<div
											class="bg-primary-100 dark:bg-primary-900 flex h-10 w-10 items-center justify-center rounded-full"
										>
											<span class="text-primary-600 dark:text-primary-400 font-medium">
												{student.name?.charAt(0)?.toUpperCase() || '?'}
											</span>
										</div>
										<div>
											<p class="font-medium text-gray-900 dark:text-white">
												{student.name || $t('analyticsPage.anonymousStudent')}
											</p>
											<p class="text-sm text-gray-500 dark:text-gray-400">
												{$t('analyticsPage.lastActiveValue', {
													time: formatters.relativeTime(student.last_active, $locale)
												})}
											</p>
										</div>
									</div>
									<div class="flex items-center space-x-4">
										<div class="text-right">
											<p class="text-sm font-medium text-gray-900 dark:text-white">
												{student.progress || 0}% Complete
											</p>
											<div class="h-2 w-24 rounded-full bg-gray-200 dark:bg-gray-700">
												<div
													class="bg-primary-600 h-2 rounded-full"
													style="width: {student.progress || 0}%"
												></div>
											</div>
										</div>
										<Badge
											variant={student.status === 'active' ? 'success' : 'warning'}
											size="small"
										>
											{student.status || 'inactive'}
										</Badge>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="py-8 text-center text-gray-500 dark:text-gray-400">
							{$t('analyticsPage.noActivity')}
						</div>
					{/if}
				</Card>
			</div>
		{:else if selectedTab === 'students'}
			<!-- Students Tab -->
			<div in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<Card class="p-6">
					<div class="mb-6 flex items-center justify-between">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
							{$t('analyticsPage.studentManagement')}
						</h3>
						<p class="text-sm text-gray-500 dark:text-gray-400">
							{studentsData.length} students enrolled
						</p>
					</div>

					{#if studentsData && studentsData.length > 0}
						<div class="overflow-x-auto">
							<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
								<thead class="bg-gray-50 dark:bg-gray-800">
									<tr>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
										>
											{$t('analyticsPage.student')}
										</th>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
										>
											{$t('analyticsPage.progress')}
										</th>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
										>
											{$t('analyticsPage.lastActive')}
										</th>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
										>
											{$t('analyticsPage.status')}
										</th>
									</tr>
								</thead>
								<tbody
									class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-900"
								>
									{#each studentsData as student}
										<tr class="hover:bg-gray-50 dark:hover:bg-gray-800">
											<td class="px-6 py-4 whitespace-nowrap">
												<div class="flex items-center">
													<div
														class="bg-primary-100 dark:bg-primary-900 flex h-10 w-10 items-center justify-center rounded-full"
													>
														<span class="text-primary-600 dark:text-primary-400 font-medium">
															{student.name?.charAt(0)?.toUpperCase() || '?'}
														</span>
													</div>
													<div class="ml-4">
														<div class="text-sm font-medium text-gray-900 dark:text-white">
															{student.name || $t('analyticsPage.anonymousStudent')}
														</div>
														<div class="text-sm text-gray-500 dark:text-gray-400">
															{student.email || $t('analyticsPage.noEmail')}
														</div>
													</div>
												</div>
											</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<div class="flex items-center">
													<div class="mr-3 h-2 w-16 rounded-full bg-gray-200 dark:bg-gray-700">
														<div
															class="bg-primary-600 h-2 rounded-full"
															style="width: {student.progress || 0}%"
														></div>
													</div>
													<span class="text-sm text-gray-900 dark:text-white">
														{student.progress || 0}%
													</span>
												</div>
											</td>
											<td
												class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400"
											>
												{formatters.relativeTime(student.last_active, $locale)}
											</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<Badge
													variant={student.status === 'active' ? 'success' : 'warning'}
													size="small"
												>
													{student.status || 'inactive'}
												</Badge>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{:else}
						<div class="py-8 text-center text-gray-500 dark:text-gray-400">
							{$t('analyticsPage.noStudents')}
						</div>
					{/if}
				</Card>
			</div>
		{:else}
			<!-- Other tabs placeholder -->
			<div in:fly={{ y: 20, delay: 100, duration: 600 }}>
				<Card class="p-8 text-center">
					<div class="mb-4">
						<svg
							class="mx-auto h-16 w-16 text-gray-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							></path>
						</svg>
					</div>

					<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
						{tabs.find((t) => t.id === selectedTab)?.label} Analytics
					</h3>

					<p class="text-gray-600 dark:text-gray-400">
						This section is coming soon with advanced {selectedTab} analytics.
					</p>
				</Card>
			</div>
		{/if}
	</div>
</div>

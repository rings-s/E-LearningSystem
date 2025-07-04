<script>
	import { onMount, onDestroy } from 'svelte';
	import Chart from 'chart.js/auto';
	import { theme } from '$lib/stores/ui.store.js';

	let { type = 'bar', data = {}, options = {}, height = '300px', class: className = '' } = $props();

	let canvasElement;
	let chartInstance = null;

	const defaultOptions = {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
			legend: {
				labels: {
					color: $theme === 'dark' ? '#e5e7eb' : '#374151',
					font: {
						size: 12
					}
				}
			},
			tooltip: {
				backgroundColor: $theme === 'dark' ? '#1f2937' : '#ffffff',
				titleColor: $theme === 'dark' ? '#f3f4f6' : '#111827',
				bodyColor: $theme === 'dark' ? '#e5e7eb' : '#374151',
				borderColor: $theme === 'dark' ? '#374151' : '#e5e7eb',
				borderWidth: 1,
				padding: 12,
				cornerRadius: 8,
				displayColors: false,
				titleFont: {
					size: 13,
					weight: 600
				},
				bodyFont: {
					size: 12
				}
			}
		},
		scales:
			type !== 'pie' && type !== 'doughnut' && type !== 'radar'
				? {
						x: {
							grid: {
								color: $theme === 'dark' ? '#374151' : '#e5e7eb',
								drawBorder: false
							},
							ticks: {
								color: $theme === 'dark' ? '#9ca3af' : '#6b7280',
								font: {
									size: 11
								}
							}
						},
						y: {
							grid: {
								color: $theme === 'dark' ? '#374151' : '#e5e7eb',
								drawBorder: false
							},
							ticks: {
								color: $theme === 'dark' ? '#9ca3af' : '#6b7280',
								font: {
									size: 11
								}
							}
						}
					}
				: undefined
	};

	onMount(() => {
		createChart();
	});

	onDestroy(() => {
		destroyChart();
	});

	$effect(() => {
		// Recreate chart when data or theme changes
		if (chartInstance) {
			destroyChart();
			createChart();
		}
	});

	function createChart() {
		if (!canvasElement) return;

		const ctx = canvasElement.getContext('2d');
		chartInstance = new Chart(ctx, {
			type,
			data: {
				...data,
				datasets: data.datasets?.map((dataset) => ({
					...dataset,
					borderWidth: dataset.borderWidth || 2,
					tension: dataset.tension || 0.4
				}))
			},
			options: {
				...defaultOptions,
				...options,
				plugins: {
					...defaultOptions.plugins,
					...options.plugins
				}
			}
		});
	}

	function destroyChart() {
		if (chartInstance) {
			chartInstance.destroy();
			chartInstance = null;
		}
	}
</script>

// front/src/lib/components/charts/ChartWrapper.svelte
<div class="chart-container {className}" style="height: {height}">
	<canvas bind:this={canvasElement}></canvas>
</div>

<style>
	.chart-container {
		position: relative;
		width: 100%;
	}
</style>

<script>
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';
	import { formatters } from '$lib/utils/formatters.js';

	let { courses = [], height = '300px', class: className = '' } = $props();

	const chartData = $derived({
		labels: courses.map((c) => (c.title.length > 20 ? c.title.substring(0, 20) + '...' : c.title)),
		datasets: [
			{
				label: 'Progress %',
				data: courses.map((c) => c.progress_percentage || 0),
				backgroundColor: courses.map((c) => {
					const progress = c.progress_percentage || 0;
					if (progress >= 80) return '#10b981';
					if (progress >= 50) return '#f59e0b';
					return '#3b82f6';
				}),
				borderRadius: 6,
				barThickness: 30
			}
		]
	});

	const chartOptions = {
		indexAxis: 'y',
		plugins: {
			legend: { display: false },
			tooltip: {
				callbacks: {
					label: (context) => `Progress: ${context.parsed.x}%`
				}
			}
		},
		scales: {
			x: {
				beginAtZero: true,
				max: 100,
				ticks: {
					callback: (value) => `${value}%`,
					stepSize: 25
				}
			}
		}
	};
</script>

<ChartWrapper type="bar" data={chartData} options={chartOptions} {height} class={className} />

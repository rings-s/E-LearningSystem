<script>
	import { t } from '#lib/i18n/index.js';
	import ChartWrapper from '#lib/components/charts/ChartWrapper.svelte';

	let {
		metrics = {
			quizzes: 0,
			assignments: 0,
			participation: 0,
			completion: 0,
			consistency: 0
		},
		height = '300px',
		class: className = ''
	} = $props();

	const chartData = $derived({
		labels: [
			$t('analyticsPage.quizzes'),
			$t('analyticsPage.assignments'),
			$t('analyticsPage.participation'),
			$t('analyticsPage.completion'),
			$t('analyticsPage.consistency')
		],
		datasets: [
			{
				label: $t('analyticsPage.performance'),
				data: [
					metrics.quizzes,
					metrics.assignments,
					metrics.participation,
					metrics.completion,
					metrics.consistency
				],
				borderColor: '#5b4ff5',
				backgroundColor: 'rgba(91, 79, 245, 0.15)',
				pointBackgroundColor: '#5b4ff5',
				pointBorderColor: '#fff',
				pointHoverBackgroundColor: '#fff',
				pointHoverBorderColor: '#5b4ff5',
				pointRadius: 5,
				pointHoverRadius: 7
			}
		]
	});

	const chartOptions = {
		scales: {
			r: {
				beginAtZero: true,
				max: 100,
				ticks: {
					stepSize: 20,
					callback: (value) => `${value}%`
				},
				pointLabels: {
					font: {
						size: 12
					}
				}
			}
		},
		plugins: {
			legend: { display: false }
		}
	};
</script>

<ChartWrapper type="radar" data={chartData} options={chartOptions} {height} class={className} />

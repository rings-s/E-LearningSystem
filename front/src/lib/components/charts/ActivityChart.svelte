<script>
	import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';
	import { formatters } from '$lib/utils/formatters.js';

	let { activities = [], days = 7, height = '250px', class: className = '' } = $props();

	const getLast7Days = () => {
		const result = [];
		for (let i = days - 1; i >= 0; i--) {
			const date = new Date();
			date.setDate(date.getDate() - i);
			result.push({
				date: date.toISOString().split('T')[0],
				label: date.toLocaleDateString('en', { weekday: 'short' })
			});
		}
		return result;
	};

	const countActivitiesByDay = (activities, days) => {
		const counts = {};
		days.forEach((day) => (counts[day.date] = 0));

		if (!activities || !Array.isArray(activities)) {
			return days.map(() => 0);
		}

		activities.forEach((activity) => {
			if (!activity || !activity.created_at) {
				return;
			}
			
			try {
				// Validate the date string first
				if (typeof activity.created_at !== 'string' || activity.created_at.trim() === '') {
					return;
				}
				
				const activityDate = new Date(activity.created_at);
				if (isNaN(activityDate.getTime()) || !isFinite(activityDate.getTime())) {
					return;
				}
				
				const date = activityDate.toISOString().split('T')[0];
				if (counts[date] !== undefined) {
					counts[date]++;
				}
			} catch (error) {
				console.warn('Invalid date in activity:', activity.created_at, error);
				return;
			}
		});

		return days.map((day) => counts[day.date]);
	};

	const dayData = getLast7Days();

	const chartData = $derived({
		labels: dayData.map((d) => d.label),
		datasets: [
			{
				label: 'Activities',
				data: countActivitiesByDay(activities, dayData),
				borderColor: '#6366f1',
				backgroundColor: 'rgba(99, 102, 241, 0.1)',
				tension: 0.4,
				fill: true,
				pointBackgroundColor: '#6366f1',
				pointBorderColor: '#fff',
				pointBorderWidth: 2,
				pointRadius: 4,
				pointHoverRadius: 6
			}
		]
	});

	const chartOptions = {
		plugins: {
			legend: { display: false }
		},
		scales: {
			y: {
				beginAtZero: true,
				ticks: {
					stepSize: 1,
					precision: 0
				}
			}
		}
	};
</script>

<ChartWrapper type="line" data={chartData} options={chartOptions} {height} class={className} />

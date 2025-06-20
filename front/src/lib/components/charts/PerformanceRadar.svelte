// front/src/lib/components/charts/PerformanceRadar.svelte
<script>
  import ChartWrapper from '$lib/components/charts/ChartWrapper.svelte';

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
    labels: ['Quizzes', 'Assignments', 'Participation', 'Completion', 'Consistency'],
    datasets: [{
      label: 'Performance',
      data: [
        metrics.quizzes,
        metrics.assignments,
        metrics.participation,
        metrics.completion,
        metrics.consistency
      ],
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139, 92, 246, 0.2)',
      pointBackgroundColor: '#8b5cf6',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#8b5cf6',
      pointRadius: 5,
      pointHoverRadius: 7
    }]
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

<ChartWrapper 
  type="radar"
  data={chartData}
  options={chartOptions}
  {height}
  class={className}
/>
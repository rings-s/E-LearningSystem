<script>
	import Chart from 'chart.js/auto';
	import { theme } from '#lib/stores/ui.store.js';

	let { type = 'bar', data = {}, options = {}, height = '300px', class: className = '' } = $props();

	let canvasElement = $state();

	const palette = (dark) => ({
		text: dark ? '#a1a1aa' : '#71717a',
		grid: dark ? 'rgba(255,255,255,0.06)' : 'rgba(24,24,27,0.06)',
		tooltipBg: dark ? '#18181b' : '#ffffff',
		tooltipTitle: dark ? '#fafafa' : '#18181b',
		tooltipBody: dark ? '#d4d4d8' : '#3f3f46',
		tooltipBorder: dark ? 'rgba(255,255,255,0.1)' : '#e4e4e7'
	});

	function buildOptions(dark) {
		const c = palette(dark);
		const axis = {
			grid: { color: c.grid },
			border: { display: false },
			ticks: { color: c.text, font: { size: 11 } }
		};
		const base = {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: { labels: { color: c.text, font: { size: 12 }, usePointStyle: true } },
				tooltip: {
					backgroundColor: c.tooltipBg,
					titleColor: c.tooltipTitle,
					bodyColor: c.tooltipBody,
					borderColor: c.tooltipBorder,
					borderWidth: 1,
					padding: 10,
					cornerRadius: 10,
					displayColors: false,
					titleFont: { size: 12, weight: 600 },
					bodyFont: { size: 12 }
				}
			},
			scales:
				type === 'radar'
					? {
							r: {
								grid: { color: c.grid },
								angleLines: { color: c.grid },
								pointLabels: { color: c.text, font: { size: 11 } },
								ticks: { color: c.text, backdropColor: 'transparent', font: { size: 10 } }
							}
						}
					: type === 'pie' || type === 'doughnut'
						? undefined
						: { x: axis, y: axis }
		};

		// Shallow-merge per section so callers can override individual keys
		return {
			...base,
			...options,
			plugins: { ...base.plugins, ...options.plugins },
			scales: base.scales
				? Object.fromEntries(
						Object.keys({ ...base.scales, ...options.scales }).map((k) => [
							k,
							{ ...base.scales?.[k], ...options.scales?.[k] }
						])
					)
				: options.scales
		};
	}

	// Rebuild whenever the data, options or theme change
	$effect(() => {
		if (!canvasElement) return;
		const chart = new Chart(canvasElement, {
			type,
			data: JSON.parse(JSON.stringify(data)),
			options: buildOptions($theme === 'dark')
		});
		return () => chart.destroy();
	});
</script>

<div class="relative w-full {className}" style="height: {height}">
	<canvas bind:this={canvasElement}></canvas>
</div>

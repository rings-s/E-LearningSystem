<!-- front/src/lib/components/course/CourseCover.svelte -->
<!-- Course thumbnail with YouTube and gradient fallbacks. Fills its parent. -->
<script>
	import { getInitials } from '#lib/utils/helpers.js';

	let { course, class: className = '' } = $props();

	const extractVideoId = (url) => {
		if (!url) return '';
		if (url.length === 11) return url;
		const match = url.match(
			/(?:youtube\.com\/(?:[^/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?/\s]{11})/
		);
		return match ? match[1] : '';
	};

	const src = $derived.by(() => {
		if (course?.thumbnail) return course.thumbnail;
		const videoId = extractVideoId(course?.preview_video);
		return videoId ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg` : null;
	});

	// Stable gradient picked from the title
	const covers = [
		'from-primary-600 to-secondary-600',
		'from-sky-500 to-primary-600',
		'from-emerald-500 to-teal-700',
		'from-amber-500 to-rose-600',
		'from-fuchsia-500 to-secondary-700',
		'from-slate-700 to-slate-900'
	];
	const cover = $derived(
		covers[[...(course?.title ?? '')].reduce((h, ch) => h + ch.charCodeAt(0), 0) % covers.length]
	);

	let failed = $state(false);
</script>

{#if src && !failed}
	<img
		{src}
		alt=""
		loading="lazy"
		onerror={() => (failed = true)}
		class="size-full object-cover {className}"
	/>
{:else}
	<div class="flex size-full items-center justify-center bg-linear-to-br {cover} {className}">
		<span class="text-3xl font-semibold tracking-tight text-white/90">
			{getInitials(course?.title)}
		</span>
	</div>
{/if}

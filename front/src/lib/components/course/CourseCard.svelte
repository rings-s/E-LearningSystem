<!-- front/src/lib/components/course/CourseCard.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { formatters } from '$lib/utils/formatters.js';
	import { classNames } from '$lib/utils/helpers.js';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Button from '$lib/components/common/Button.svelte';

	let { course, variant = 'default' } = $props();

	const handleClick = () => {
		goto(`/courses/${course.uuid}`);
	};

	const levelConfig = {
		beginner: { color: 'success', icon: '🟢' },
		intermediate: { color: 'warning', icon: '🟡' },
		advanced: { color: 'danger', icon: '🔴' }
	};

	const getThumbnailUrl = (course) => {
		if (course.thumbnail) return course.thumbnail;

		// Generate YouTube thumbnail if preview_video exists
		if (course.preview_video) {
			const videoId = extractVideoId(course.preview_video);
			if (videoId) {
				return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
			}
		}

		return null;
	};

	const extractVideoId = (url) => {
		if (!url) return '';
		if (url.length === 11) return url;

		const regex =
			/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
		const match = url.match(regex);
		return match ? match[1] : '';
	};

	const thumbnailUrl = getThumbnailUrl(course);

	// Fixed image error handler
	function handleImageError(event) {
		const img = event.target;
		img.style.display = 'none';
		// Show fallback div
		const fallback = img.nextElementSibling;
		if (fallback) {
			fallback.style.display = 'flex';
		}
	}
</script>

<Card
	variant="bordered"
	hoverable
	onclick={handleClick}
	class={classNames(
		'group flex h-full flex-col overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl',
		variant === 'featured' && 'ring-primary-500 ring-2'
	)}
>
	<!-- Thumbnail -->
	<div class="relative -m-6 mb-4 overflow-hidden">
		{#if thumbnailUrl}
			<img
				src={thumbnailUrl}
				alt={course.title}
				class="h-48 w-full object-cover transition-transform duration-300 group-hover:scale-105"
				loading="lazy"
				onerror={handleImageError}
			/>
			<!-- Fallback div (hidden by default) -->
			<div
				class="from-primary-400 to-primary-600 flex h-48 w-full items-center justify-center bg-gradient-to-br"
				style="display: none;"
			>
				<svg class="h-16 w-16 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
					/>
				</svg>
			</div>
		{:else}
			<div
				class="from-primary-400 to-primary-600 flex h-48 w-full items-center justify-center bg-gradient-to-br"
			>
				<svg class="h-16 w-16 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
					/>
				</svg>
			</div>
		{/if}

		<!-- Overlays -->
		<div
			class="absolute inset-0 bg-black/0 transition-colors duration-300 group-hover:bg-black/10"
		></div>

		<!-- Badges -->
		<div class="absolute top-3 left-3 flex gap-2">
			{#if course.is_featured}
				<Badge
					variant="accent"
					size="small"
					class="bg-gradient-to-r from-yellow-400 to-orange-500 text-white"
				>
					⭐ Featured
				</Badge>
			{/if}
			<Badge variant={levelConfig[course.level].color} size="small">
				{levelConfig[course.level].icon}
			</Badge>
		</div>

		<!-- Play Button Overlay -->
		{#if course.preview_video}
			<div
				class="absolute inset-0 flex items-center justify-center opacity-0 transition-opacity duration-300 group-hover:opacity-100"
			>
				<div class="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 shadow-lg">
					<svg class="text-primary-600 ml-1 h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
						<path d="M8 5v14l11-7z" />
					</svg>
				</div>
			</div>
		{/if}
	</div>

	<!-- Content -->
	<div class="flex flex-1 flex-col p-6">
		<!-- Category -->
		<div class="mb-2">
			<span
				class="text-primary-600 dark:text-primary-400 text-xs font-medium tracking-wide uppercase"
			>
				{course.category_name || 'General'}
			</span>
		</div>

		<!-- Title -->
		<h3
			class="group-hover:text-primary-600 dark:group-hover:text-primary-400 mb-2 line-clamp-2 text-lg font-bold text-gray-900 transition-colors dark:text-white"
		>
			{course.title}
		</h3>

		<!-- Description -->
		<p class="mb-4 line-clamp-2 flex-1 text-sm text-gray-600 dark:text-gray-400">
			{course.short_description}
		</p>

		<!-- Instructor -->
		<div class="mb-4 flex items-center gap-2">
			<div
				class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700"
			>
				{#if course.instructor_avatar}
					<img
						src={course.instructor_avatar}
						alt={course.instructor_name}
						class="h-full w-full object-cover"
						loading="lazy"
					/>
				{:else}
					<span class="text-xs font-medium text-gray-600 dark:text-gray-300">
						{course.instructor_name?.[0] || '?'}
					</span>
				{/if}
			</div>
			<span class="text-sm font-medium text-gray-700 dark:text-gray-300">
				{course.instructor_name || 'Unknown Instructor'}
			</span>
		</div>

		<!-- Stats -->
		<div class="mb-4 flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
			<div class="flex items-center gap-4">
				<div class="flex items-center gap-1">
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					<span>{course.duration_hours}h</span>
				</div>

				<div class="flex items-center gap-1">
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
						/>
					</svg>
					<span>{formatters.number(course.enrolled_count || 0)}</span>
				</div>
			</div>

			{#if course.average_rating > 0}
				<div class="flex items-center gap-1">
					<svg class="h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
						<path
							d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
						/>
					</svg>
					<span class="font-medium text-gray-700 dark:text-gray-300">
						{course.average_rating.toFixed(1)}
					</span>
				</div>
			{/if}
		</div>

		<!-- Action Button -->
		<div class="mt-auto">
			{#if course.is_enrolled}
				<Button href={`/courses/${course.uuid}/learn`} variant="primary" fullWidth size="small">
					Continue Learning
				</Button>
			{:else}
				<Button
					onclick={(e) => {
						e.stopPropagation();
						goto(`/courses/${course.uuid}`);
					}}
					variant="outline"
					fullWidth
					size="small"
					class="group-hover:bg-primary-600 group-hover:border-primary-600 transition-all duration-300 group-hover:text-white"
				>
					View Course
				</Button>
			{/if}
		</div>
	</div>
</Card>

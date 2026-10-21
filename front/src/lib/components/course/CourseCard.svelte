<!-- front/src/lib/components/course/CourseCard.svelte -->
<script>
	import { t } from '#lib/i18n/index.js';
	import { getInitials } from '#lib/utils/helpers.js';
	import Badge from '#lib/components/common/Badge.svelte';
	import CourseCover from './CourseCover.svelte';

	let { course } = $props();

	const levelVariant = { beginner: 'success', intermediate: 'warning', advanced: 'danger' };

	const rating = $derived(Number(course.average_rating ?? course.avg_rating ?? 0));
	const students = $derived(course.enrolled_count ?? course.enrollment_count ?? 0);
	const href = $derived(
		course.is_enrolled ? `/my-courses/${course.uuid}/learn` : `/courses/${course.uuid}`
	);
</script>

<a
	{href}
	class="group focus-visible:outline-primary-500 flex h-full flex-col overflow-hidden rounded-2xl bg-white shadow-xs ring-1 ring-gray-200/80 transition-[box-shadow,transform] duration-200 hover:-translate-y-0.5 hover:shadow-lg focus-visible:outline-2 focus-visible:outline-offset-2 dark:bg-gray-900 dark:ring-white/10"
>
	<!-- Thumbnail -->
	<div class="relative aspect-video overflow-hidden bg-gray-100 dark:bg-white/5">
		<CourseCover {course} class="transition-transform duration-500 group-hover:scale-[1.03]" />

		<div class="absolute inset-x-3 top-3 flex items-start justify-between gap-2">
			{#if course.category_name}
				<Badge variant="white" size="small">{course.category_name}</Badge>
			{:else}
				<span></span>
			{/if}
			{#if course.is_featured}
				<Badge variant="accent" size="small">{$t('ui.featured')}</Badge>
			{/if}
		</div>
	</div>

	<!-- Body -->
	<div class="flex flex-1 flex-col p-5">
		{#if course.level}
			<Badge
				variant={levelVariant[course.level] ?? 'default'}
				size="small"
				dot
				class="mb-3 self-start">{$t(`catalog.${course.level}`)}</Badge
			>
		{/if}

		<!-- Course text comes from the backend in any language, so let it pick its own direction -->
		<h3
			dir="auto"
			class="group-hover:text-primary-700 dark:group-hover:text-primary-300 line-clamp-2 text-base leading-snug font-semibold text-gray-900 transition-colors dark:text-white"
		>
			{course.title}
		</h3>
		{#if course.short_description}
			<p dir="auto" class="mt-1.5 line-clamp-2 text-sm text-gray-600 dark:text-gray-400">
				{course.short_description}
			</p>
		{/if}

		{#if course.instructor_name}
			<div class="mt-4 flex items-center gap-2">
				{#if course.instructor_avatar}
					<img src={course.instructor_avatar} alt="" class="size-6 rounded-full object-cover" />
				{:else}
					<span
						class="flex size-6 items-center justify-center rounded-full bg-gray-100 text-[10px] font-semibold text-gray-600 dark:bg-white/10 dark:text-gray-300"
					>
						{getInitials(course.instructor_name)}
					</span>
				{/if}
				<span class="truncate text-sm text-gray-700 dark:text-gray-300"
					>{course.instructor_name}</span
				>
			</div>
		{/if}

		<div class="min-h-5 flex-1"></div>

		<!-- Meta -->
		<div
			class="flex items-center gap-4 border-t border-gray-100 pt-4 text-xs text-gray-500 dark:border-white/5 dark:text-gray-400"
		>
			{#if rating > 0}
				<span class="flex items-center gap-1 font-medium text-gray-900 dark:text-white">
					<svg
						class="text-accent-500 size-4"
						viewBox="0 0 20 20"
						fill="currentColor"
						aria-hidden="true"
					>
						<path
							d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
						/>
					</svg>
					{rating.toFixed(1)}
				</span>
			{/if}
			<span class="flex items-center gap-1">
				<svg
					class="size-4"
					fill="none"
					stroke="currentColor"
					stroke-width="1.75"
					viewBox="0 0 24 24"
					aria-hidden="true"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z"
					/>
				</svg>
				{students.toLocaleString()}
			</span>
			{#if course.duration_hours}
				<span class="flex items-center gap-1">
					<svg
						class="size-4"
						fill="none"
						stroke="currentColor"
						stroke-width="1.75"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					{$t('ui.hoursShort', { count: course.duration_hours })}
				</span>
			{/if}
			{#if course.is_enrolled}
				<span class="text-primary-600 dark:text-primary-400 ms-auto font-medium"
					>{$t('ui.continue')}</span
				>
			{/if}
		</div>
	</div>
</a>

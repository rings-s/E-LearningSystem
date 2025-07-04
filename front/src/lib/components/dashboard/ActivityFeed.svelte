<!-- front/src/lib/components/dashboard/ActivityFeed.svelte -->
<script>
	import { formatters } from '$lib/utils/formatters.js';
	import { t, locale } from '$lib/i18n/index.js';
	import { classNames } from '$lib/utils/helpers.js';

	let {
		activities = [],
		maxItems = 10,
		showViewAll = true,
		onViewAll = () => {},
		class: className = ''
	} = $props();

	const activityIcons = {
		course_view:
			'<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />',
		lesson_complete:
			'<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />',
		quiz_submit:
			'<path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />',
		forum_post:
			'<path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />',
		certificate_earned:
			'<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />'
	};

	const getActivityColor = (type) => {
		const colors = {
			course_view: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
			lesson_complete: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
			quiz_submit: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
			forum_post: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
			certificate_earned:
				'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
		};
		return colors[type] || colors.course_view;
	};

	const displayedActivities = $derived(activities.slice(0, maxItems));
</script>

<div class={classNames('activity-feed', className)}>
	<div class="space-y-4">
		{#each displayedActivities as activity, index}
			<div class="flex gap-3">
				<!-- Icon -->
				<div
					class={classNames(
						'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full',
						getActivityColor(activity.activity_type)
					)}
				>
					<svg
						class="h-5 w-5"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
					>
						{@html activityIcons[activity.activity_type] || activityIcons.course_view}
					</svg>
				</div>

				<!-- Content -->
				<div class="min-w-0 flex-1">
					<p class="text-sm text-gray-900 dark:text-white">
						<span class="font-medium">{activity.user_name}</span>
						{' '}
						<span class="text-gray-600 dark:text-gray-400">
							{activity.description}
						</span>
					</p>
					{#if activity.metadata?.course_title}
						<p class="mt-1 truncate text-sm text-gray-500 dark:text-gray-400">
							{activity.metadata.course_title}
						</p>
					{/if}
					<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
						{formatters.relativeTime(activity.created_at, $locale)}
					</p>
				</div>
			</div>

			{#if index < displayedActivities.length - 1}
				<div class="ml-5 h-4 border-l-2 border-gray-200 dark:border-gray-700"></div>
			{/if}
		{/each}
	</div>

	{#if showViewAll && activities.length > maxItems}
		<button
			onclick={onViewAll}
			class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 mt-6 w-full py-2 text-sm font-medium transition-colors"
		>
			View all activities ({activities.length})
		</button>
	{/if}
</div>

<script>
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import { coursesApi } from '#lib/apis/courses.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { formatters } from '#lib/utils/formatters.js';
	import { getInitials, validateUUID, isValidUUID } from '#lib/utils/helpers.js';
	import { t, locale } from '#lib/i18n/index.js';

	// Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import YouTubePlayer from '#lib/components/course/YouTubePlayer.svelte';
	import LessonList from '#lib/components/course/LessonList.svelte';
	import ShareModal from '#lib/components/course/ShareModal.svelte';
	import CourseCover from '#lib/components/course/CourseCover.svelte';
	import Tabs from '#lib/components/common/Tabs.svelte';
	import Skeleton from '#lib/components/common/Skeleton.svelte';
	import EmptyState from '#lib/components/common/EmptyState.svelte';

	const courseId = page.params.uuid;
	/** @type {any} */
	let course = $state(null);
	let loading = $state(true);
	let enrolling = $state(false);
	let activeTab = $state('overview');
	let isFavorite = $state(false);
	let showShareModal = $state(false);
	let favoriteLoading = $state(false);
	let validationError = $state(null);

	const tabs = $derived([
		{ id: 'overview', label: $t('course.overview'), icon: 'info' },
		{ id: 'curriculum', label: $t('course.curriculum'), icon: 'list' },
		{ id: 'instructor', label: $t('course.instructor'), icon: 'user' },
		{ id: 'reviews', label: $t('course.reviews'), icon: 'star' }
	]);

	onMount(async () => {
		// Validate UUID before making API calls
		const validation = validateUUID(courseId, 'Course ID');
		if (!validation.isValid) {
			validationError = validation.error;
			loading = false;
			return;
		}

		await Promise.all([fetchCourse(), checkFavoriteStatus()]);
	});

	const fetchCourse = async () => {
		try {
			course = await coursesApi.getCourse(courseId);
		} catch (error) {
			console.error('Failed to fetch course:', error);
			uiStore.showNotification({
				type: 'error',
				title: $t('courseDetail.error'),
				message: $t('courseDetail.loadFailed')
			});
			goto('/courses');
		} finally {
			loading = false;
		}
	};

	const handleEnroll = async () => {
		if (!$currentUser) {
			goto('/login');
			return;
		}

		// Validate UUID before enrollment
		if (!isValidUUID(courseId)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('courseDetail.invalidCourse'),
				message: $t('courseDetail.invalidCourseId')
			});
			return;
		}

		enrolling = true;
		try {
			await coursesApi.enrollInCourse(courseId);
			if (course) {
				course.is_enrolled = true;
			}
			uiStore.showNotification({
				type: 'success',
				title: $t('courseDetail.enrolledSuccess'),
				message: $t('courseDetail.welcomeTo', {
					title: course?.title || $t('courseDetail.theCourse')
				})
			});
			goto(`/courses/${courseId}/learn`);
		} catch (error) {
			uiStore.showNotification({
				type: 'error',
				title: $t('courseDetail.enrollFailed'),
				message: error.message || $t('courseDetail.enrollFailedMsg')
			});
		} finally {
			enrolling = false;
		}
	};

	const checkFavoriteStatus = async () => {
		try {
			isFavorite = await coursesApi.isFavorite(courseId);
		} catch (error) {
			console.error('Failed to check favorite status:', error);
		}
	};

	const handleFavoriteToggle = async () => {
		if (!$currentUser) {
			goto('/login');
			return;
		}

		// Validate UUID before favorite operation
		if (!isValidUUID(courseId)) {
			uiStore.showNotification({
				type: 'error',
				title: $t('courseDetail.invalidCourse'),
				message: $t('courseDetail.invalidCourseId')
			});
			return;
		}

		favoriteLoading = true;
		try {
			if (isFavorite) {
				await coursesApi.removeFromFavorites(courseId);
				isFavorite = false;
				uiStore.showNotification({
					type: 'success',
					title: $t('course.removeFromFavorites'),
					message: `${course?.title} ${$t('course.removeFromFavorites')}`
				});
			} else {
				await coursesApi.addToFavorites(courseId);
				isFavorite = true;
				uiStore.showNotification({
					type: 'success',
					title: $t('course.addToFavorites'),
					message: `${course?.title} ${$t('course.addToFavorites')}`
				});
			}
		} catch (error) {
			console.error('Failed to toggle favorite:', error);
			uiStore.showNotification({
				type: 'error',
				title: $t('courseDetail.error'),
				message: error.message || $t('courseDetail.favoritesFailed')
			});
		} finally {
			favoriteLoading = false;
		}
	};

	const handleShare = () => {
		showShareModal = true;
	};

	const levelConfig = {
		beginner: { color: 'success', icon: '🟢' },
		intermediate: { color: 'warning', icon: '🟡' },
		advanced: { color: 'danger', icon: '🔴' }
	};

	const icons = {
		info: '<path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />',
		list: '<path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />',
		user: '<path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />',
		star: '<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />'
	};
</script>

<svelte:head>
	<title>{course?.title || $t('course.course')} · Ilmora</title>
	<meta name="description" content={course?.short_description || $t('courseDetail.metaFallback')} />
</svelte:head>

{#snippet star(cls = 'size-4')}
	<svg class="{cls} text-accent-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
		<path
			d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
		/>
	</svg>
{/snippet}

{#if loading}
	<div class="space-y-8" aria-busy="true">
		<div class="grid gap-8 lg:grid-cols-2">
			<div class="space-y-4">
				<Skeleton class="h-5 w-40" />
				<Skeleton class="h-10 w-full" />
				<Skeleton class="h-10 w-2/3" />
				<Skeleton class="h-4 w-full" />
			</div>
			<Skeleton class="aspect-video rounded-2xl" />
		</div>
		<div class="grid gap-8 lg:grid-cols-3">
			<Skeleton class="h-80 rounded-2xl lg:col-span-2" />
			<Skeleton class="h-80 rounded-2xl" />
		</div>
	</div>
{:else if course}
	<div class="space-y-8" in:fade={{ duration: 200 }}>
		<a
			href="/courses"
			class="inline-flex items-center gap-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
		>
			<svg
				class="size-4 rtl:rotate-180"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
			</svg>
			{$t('course.browseAllCourses')}
		</a>

		<!-- Hero -->
		<section class="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
			<div>
				<div class="flex flex-wrap items-center gap-2">
					{#if course.category_name}
						<Badge variant="primary">{course.category_name}</Badge>
					{/if}
					{#if course.level}
						<Badge variant={levelConfig[course.level]?.color ?? 'default'} dot class="capitalize">
							{$t(`catalog.${course.level}`)}
						</Badge>
					{/if}
					{#if course.is_featured}
						<Badge variant="accent">{$t('courseDetail.featured')}</Badge>
					{/if}
				</div>
				<h1
					dir="auto"
					class="mt-4 text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl dark:text-white"
				>
					{course.title}
				</h1>
				{#if course.short_description}
					<p dir="auto" class="mt-4 text-base text-gray-600 sm:text-lg dark:text-gray-400">
						{course.short_description}
					</p>
				{/if}

				<div class="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm">
					<span class="flex items-center gap-2 text-gray-900 dark:text-white">
						<span
							class="brand-gradient flex size-8 items-center justify-center rounded-full text-xs font-semibold text-white"
						>
							{getInitials(course.instructor?.full_name || course.instructor_name)}
						</span>
						{course.instructor?.full_name || course.instructor_name}
					</span>
					{#if (course.average_rating || 0) > 0}
						<span class="flex items-center gap-1 text-gray-600 dark:text-gray-400">
							{@render star()}
							<span class="font-medium text-gray-900 dark:text-white"
								>{Number(course.average_rating).toFixed(1)}</span
							>
							{#if course.reviews_count || course.reviews?.length}({formatters.number(
									course.reviews_count || course.reviews.length
								)}){/if}
						</span>
					{/if}
					<span class="text-gray-600 dark:text-gray-400">
						{formatters.number(course.enrolled_count || 0)}
						{$t('course.students')}
					</span>
					{#if course.duration_hours}
						<span class="text-gray-600 dark:text-gray-400">
							{course.duration_hours}
							{$t('course.hours')}
						</span>
					{/if}
				</div>
			</div>

			<div
				class="overflow-hidden rounded-2xl bg-gray-100 shadow-lg ring-1 ring-gray-200/80 dark:bg-white/5 dark:ring-white/10"
			>
				{#if course.preview_video}
					<YouTubePlayer
						videoId={course.preview_video}
						class="aspect-video w-full"
						modestBranding={true}
						rel={0}
						showInfo={false}
					/>
				{:else}
					<div class="aspect-video"><CourseCover {course} /></div>
				{/if}
			</div>
		</section>

		<div class="grid items-start gap-8 lg:grid-cols-3">
			<!-- Main -->
			<div class="min-w-0 lg:col-span-2">
				<Tabs
					tabs={tabs.map((tab) => ({ label: tab.label }))}
					bind:activeTab={
						() => tabs.findIndex((tab) => tab.id === activeTab), (i) => (activeTab = tabs[i].id)
					}
				/>

				<div class="mt-6">
					{#key activeTab}
						<div in:fade={{ duration: 150 }}>
							{#if activeTab === 'overview'}
								<div class="space-y-8">
									{#if course.description}
										<section>
											<h2 class="text-lg font-semibold text-gray-900 dark:text-white">
												{$t('course.aboutThisCourse')}
											</h2>
											<p
												dir="auto"
												class="mt-3 leading-relaxed whitespace-pre-line text-gray-700 dark:text-gray-300"
											>
												{course.description}
											</p>
										</section>
									{/if}

									{#if course.learning_outcomes}
										<Card>
											<h2 class="text-lg font-semibold text-gray-900 dark:text-white">
												{$t('course.whatYoullLearn')}
											</h2>
											<ul class="mt-4 grid gap-3 sm:grid-cols-2">
												{#each course.learning_outcomes.split('\n').filter(Boolean) as outcome}
													<li
														dir="auto"
														class="flex gap-3 text-sm text-gray-700 dark:text-gray-300"
													>
														<svg
															class="text-success-600 dark:text-success-400 mt-0.5 size-4 shrink-0"
															fill="none"
															stroke="currentColor"
															stroke-width="2.5"
															viewBox="0 0 24 24"
														>
															<path
																stroke-linecap="round"
																stroke-linejoin="round"
																d="M4.5 12.75l6 6 9-13.5"
															/>
														</svg>
														{outcome.trim()}
													</li>
												{/each}
											</ul>
										</Card>
									{/if}

									{#if course.prerequisites}
										<section>
											<h2 class="text-lg font-semibold text-gray-900 dark:text-white">
												{$t('course.prerequisites')}
											</h2>
											<p
												dir="auto"
												class="mt-3 leading-relaxed whitespace-pre-line text-gray-700 dark:text-gray-300"
											>
												{course.prerequisites}
											</p>
										</section>
									{/if}
								</div>
							{:else if activeTab === 'curriculum'}
								<p class="mb-4 text-sm text-gray-600 dark:text-gray-400">
									{course.modules?.length || 0}
									{$t('course.modules')} · {course.total_lessons || 0}
									{$t('course.lessons')} · {course.duration_hours || 0}h {$t('course.totalLength')}
								</p>
								<LessonList modules={course.modules || []} isEnrolled={course.is_enrolled} />
							{:else if activeTab === 'instructor'}
								<Card>
									<div class="flex flex-col gap-5 sm:flex-row sm:items-start">
										{#if course.instructor?.avatar}
											<img
												src={course.instructor.avatar}
												alt=""
												class="size-20 rounded-2xl object-cover"
											/>
										{:else}
											<span
												class="brand-gradient flex size-20 shrink-0 items-center justify-center rounded-2xl text-2xl font-semibold text-white"
											>
												{getInitials(course.instructor?.full_name || course.instructor_name)}
											</span>
										{/if}
										<div>
											<h2 class="text-lg font-semibold text-gray-900 dark:text-white">
												{course.instructor?.full_name || course.instructor_name}
											</h2>
											<p class="text-primary-600 dark:text-primary-400 text-sm font-medium">
												{$t('course.instructor')}
											</p>
											{#if course.instructor?.bio}
												<p class="mt-3 leading-relaxed text-gray-700 dark:text-gray-300">
													{course.instructor.bio}
												</p>
											{/if}
										</div>
									</div>
								</Card>
							{:else if activeTab === 'reviews'}
								{#if course.reviews?.length > 0}
									<ul class="space-y-4">
										{#each course.reviews as review}
											<li>
												<Card padding="small">
													<div class="flex gap-4">
														<span
															class="flex size-10 shrink-0 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold text-gray-700 dark:bg-white/10 dark:text-gray-200"
														>
															{getInitials(review.student_name)}
														</span>
														<div class="min-w-0 flex-1">
															<div class="flex flex-wrap items-center justify-between gap-2">
																<p class="font-medium text-gray-900 dark:text-white">
																	{review.student_name}
																</p>
																<span
																	class="flex"
																	aria-label={$t('courseDetail.outOf5', { rating: review.rating })}
																>
																	{#each Array(5) as _, i}
																		{@render star(
																			i < review.rating ? 'size-4' : 'size-4 opacity-25'
																		)}
																	{/each}
																</span>
															</div>
															<p
																class="mt-2 text-sm leading-relaxed text-gray-700 dark:text-gray-300"
															>
																{review.comment}
															</p>
															<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
																{formatters.relativeTime(review.created_at, $locale)}
															</p>
														</div>
													</div>
												</Card>
											</li>
										{/each}
									</ul>
								{:else}
									<EmptyState
										title={$t('course.noReviewsYet')}
										description={$t('course.beFirstToReview')}
										icon={'<path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />'}
									/>
								{/if}
							{/if}
						</div>
					{/key}
				</div>
			</div>

			<!-- Enroll card -->
			<aside class="order-first lg:sticky lg:top-24 lg:order-none">
				<Card variant="elevated">
					<p class="text-2xl font-semibold text-gray-900 dark:text-white">{$t('course.free')}</p>

					<div class="mt-5 space-y-2">
						{#if course.is_enrolled}
							<Badge variant="success" dot class="mb-2">{$t('course.enrolled')}</Badge>
							<Button href={`/courses/${courseId}/learn`} size="large" fullWidth>
								{$t('course.continueLearning')}
							</Button>
							<Button href="/my-courses" variant="outline" fullWidth>
								{$t('course.viewMyCourses')}
							</Button>
						{:else}
							<Button onclick={handleEnroll} size="large" fullWidth loading={enrolling}>
								{enrolling ? $t('course.enrolling') : $t('course.enrollNow')}
							</Button>
						{/if}
					</div>

					<div class="mt-3 grid grid-cols-2 gap-2">
						<Button
							variant="outline"
							size="small"
							onclick={handleFavoriteToggle}
							loading={favoriteLoading}
							aria-pressed={isFavorite}
							iconLeft={favoriteLoading
								? null
								: `<path stroke-linecap="round" stroke-linejoin="round" ${isFavorite ? 'fill="currentColor"' : ''} d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />`}
						>
							{isFavorite ? $t('courseDetail.saved') : $t('courseDetail.save')}
						</Button>
						<Button
							variant="outline"
							size="small"
							onclick={handleShare}
							iconLeft={'<path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" />'}
						>
							{$t('actions.share')}
						</Button>
					</div>

					<dl
						class="mt-6 divide-y divide-gray-100 border-t border-gray-100 text-sm dark:divide-white/5 dark:border-white/5"
					>
						{#each [[$t('course.level'), course.level ? $t(`catalog.${course.level}`) : null], [$t('course.duration'), course.duration_hours ? `${course.duration_hours} ${$t('course.hours')}` : null], [$t('course.language'), course.language?.toUpperCase()], [$t('course.students'), formatters.number(course.enrolled_count || 0)], [$t('course.certificate'), $t('course.yes')], [$t('course.lifetimeAccess'), $t('course.yes')]].filter(([, v]) => v) as [label, value]}
							<div class="flex justify-between gap-4 py-3">
								<dt class="text-gray-500 first-letter:uppercase dark:text-gray-400">{label}</dt>
								<dd class="font-medium text-gray-900 capitalize dark:text-white">{value}</dd>
							</div>
						{/each}
					</dl>
				</Card>
			</aside>
		</div>
	</div>
{:else}
	<EmptyState
		title={validationError ? $t('courseDetail.invalidLink') : $t('course.courseNotFound')}
		description={validationError || $t('course.courseNotFoundDesc')}
	>
		{#snippet actions()}
			<Button href="/courses">{$t('course.browseAllCourses')}</Button>
		{/snippet}
	</EmptyState>
{/if}

<ShareModal isOpen={showShareModal} {course} onClose={() => (showShareModal = false)} />

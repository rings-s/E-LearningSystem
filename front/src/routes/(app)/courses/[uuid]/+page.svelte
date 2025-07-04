<!-- front/src/routes/(app)/courses/[uuid]/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { classNames } from '$lib/utils/helpers.js';
	import { t } from '$lib/i18n';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import YouTubePlayer from '$lib/components/course/YouTubePlayer.svelte';
	import LessonList from '$lib/components/course/LessonList.svelte';
	import ShareModal from '$lib/components/course/ShareModal.svelte';

	const courseId = $page.params.uuid;
	/** @type {any} */
	let course = $state(null);
	let loading = $state(true);
	let enrolling = $state(false);
	let activeTab = $state('overview');
	let isFavorite = $state(false);
	let showShareModal = $state(false);
	let favoriteLoading = $state(false);

	const tabs = $derived([
		{ id: 'overview', label: $t('course.overview'), icon: 'info' },
		{ id: 'curriculum', label: $t('course.curriculum'), icon: 'list' },
		{ id: 'instructor', label: $t('course.instructor'), icon: 'user' },
		{ id: 'reviews', label: $t('course.reviews'), icon: 'star' }
	]);

	onMount(async () => {
		await Promise.all([fetchCourse(), checkFavoriteStatus()]);
	});

	const fetchCourse = async () => {
		try {
			course = await coursesApi.getCourse(courseId);
		} catch (error) {
			console.error('Failed to fetch course:', error);
			uiStore.showNotification({
				type: 'error',
				title: 'Error',
				message: 'Failed to load course'
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

		enrolling = true;
		try {
			await coursesApi.enrollInCourse(courseId);
			if (course) {
				course.is_enrolled = true;
			}
			uiStore.showNotification({
				type: 'success',
				title: 'Enrolled Successfully',
				message: `Welcome to ${course?.title || 'the course'}!`
			});
			goto(`/courses/${courseId}/learn`);
		} catch (error) {
			uiStore.showNotification({
				type: 'error',
				title: 'Enrollment Failed',
				message: error.message || 'Failed to enroll'
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
				title: 'Error',
				message: 'Failed to update favorites'
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
	<title>{course?.title || $t('course.course')} - {$t('common.appName')}</title>
	<meta name="description" content={course?.short_description || $t('common.appName')} />
</svelte:head>

{#if loading}
	<div class="container mx-auto px-4 py-8">
		<div class="animate-pulse space-y-6">
			<div class="h-64 rounded-2xl bg-gray-200 dark:bg-gray-700"></div>
			<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
				<div class="space-y-4 lg:col-span-2">
					<div class="h-8 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-2/3 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
				<div class="h-96 rounded-xl bg-gray-200 dark:bg-gray-700"></div>
			</div>
		</div>
	</div>
{:else if course}
	<div
		class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800"
	>
		<!-- Hero Section -->
		<div
			class="from-primary-600 via-primary-700 to-secondary-600 relative overflow-hidden bg-gradient-to-r"
		>
			<div class="absolute inset-0 bg-black/20"></div>
			<div class="relative container mx-auto px-4 py-16">
				<div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
					<!-- Content -->
					<div class="space-y-6 text-white">
						<div class="flex flex-wrap items-center gap-3">
							{#if course?.level}
								<Badge variant="white" class="border-white/30 bg-white/20 text-white">
									{levelConfig[course.level]?.icon || ''}
									{course.level}
								</Badge>
							{/if}
							{#if course?.category_name}
								<Badge variant="white" class="border-white/30 bg-white/20 text-white">
									{course.category_name}
								</Badge>
							{/if}
							{#if course?.is_featured}
								<Badge variant="accent" class="bg-gradient-to-r from-yellow-400 to-orange-500">
									⭐ Featured
								</Badge>
							{/if}
						</div>

						<h1 class="text-4xl leading-tight font-bold lg:text-5xl">
							{course?.title || 'Course Title'}
						</h1>

						{#if course?.short_description}
							<p class="text-xl leading-relaxed text-white/90">
								{course.short_description}
							</p>
						{/if}

						<div class="flex flex-wrap items-center gap-6 text-white/80">
							<div class="flex items-center gap-2">
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
									/>
								</svg>
								<span class="font-medium">{course?.instructor?.full_name || 'Instructor'}</span>
							</div>

							{#if course?.average_rating > 0}
								<div class="flex items-center gap-2">
									<div class="flex items-center">
										{#each Array(5) as _, i}
											<svg
												class="h-5 w-5 {i < Math.round(course?.average_rating || 0)
													? 'text-yellow-400'
													: 'text-white/30'}"
												fill="currentColor"
												viewBox="0 0 20 20"
											>
												<path
													d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
												/>
											</svg>
										{/each}
									</div>
									<span class="font-medium">{course?.average_rating?.toFixed(1) || '0.0'}</span>
									<span class="text-white/60"
										>({formatters.number(course?.reviews_count || 0)} reviews)</span
									>
								</div>
							{/if}

							<div class="flex items-center gap-2">
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
									/>
								</svg>
								<span class="font-medium">{formatters.number(course?.enrolled_count || 0)}</span>
								<span class="text-white/60">students</span>
							</div>

							<div class="flex items-center gap-2">
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								<span class="font-medium">{course?.duration_hours || 0}h</span>
							</div>
						</div>
					</div>

					<!-- Preview Video -->
					<div class="relative">
						{#if course?.preview_video}
							<YouTubePlayer
								videoId={course?.preview_video}
								class="overflow-hidden rounded-2xl shadow-2xl"
								modestBranding={true}
								rel={0}
								showInfo={false}
							/>
						{:else}
							<div
								class="flex aspect-video items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm"
							>
								<div class="text-center text-white">
									<svg
										class="mx-auto mb-4 h-20 w-20 opacity-60"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
									<p class="text-lg opacity-80">{$t('course.previewComingSoon')}</p>
								</div>
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Main Content -->
		<div class="container mx-auto px-4 py-12">
			<div class="grid grid-cols-1 gap-12 lg:grid-cols-3">
				<!-- Content Area -->
				<div class="space-y-8 lg:col-span-2">
					<!-- Tab Navigation -->
					<div
						class="rounded-2xl border border-gray-200 bg-white p-2 shadow-sm dark:border-gray-700 dark:bg-gray-800"
					>
						<nav class="flex space-x-1">
							{#each tabs as tab}
								<button
									onclick={() => (activeTab = tab.id)}
									class={classNames(
										'flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200',
										activeTab === tab.id
											? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400'
											: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
									)}
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										{@html icons[tab.icon]}
									</svg>
									{tab.label}
								</button>
							{/each}
						</nav>
					</div>

					<!-- Tab Content -->
					<Card variant="bordered" padding="large">
						{#if activeTab === 'overview'}
							<div class="prose prose-gray dark:prose-invert max-w-none">
								<h3 class="mb-6 text-2xl font-bold">{$t('course.aboutThisCourse')}</h3>
								{#if course?.description}
									<div class="leading-relaxed text-gray-700 dark:text-gray-300">
										{course.description}
									</div>
								{/if}

								{#if course?.learning_outcomes}
									<h3 class="mt-8 mb-4 text-xl font-semibold">{$t('course.whatYoullLearn')}</h3>
									<div class="grid grid-cols-1 gap-3 md:grid-cols-2">
										{#each course.learning_outcomes.split('\n').filter(Boolean) as outcome}
											<div
												class="flex items-start gap-3 rounded-lg bg-green-50 p-3 dark:bg-green-900/20"
											>
												<svg
													class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-600 dark:text-green-400"
													fill="none"
													stroke="currentColor"
													viewBox="0 0 24 24"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M5 13l4 4L19 7"
													/>
												</svg>
												<span class="text-sm text-green-800 dark:text-green-200"
													>{outcome.trim()}</span
												>
											</div>
										{/each}
									</div>
								{/if}

								{#if course.prerequisites}
									<h3 class="mt-8 mb-4 text-xl font-semibold">{$t('course.prerequisites')}</h3>
									<div class="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
										<p class="text-blue-800 dark:text-blue-200">{course.prerequisites}</p>
									</div>
								{/if}
							</div>
						{:else if activeTab === 'curriculum'}
							<div>
								<h3 class="mb-6 text-2xl font-bold">{$t('course.courseCurriculum')}</h3>
								<div class="mb-6 flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
									<span>{course.modules?.length || 0} {$t('course.modules')}</span>
									<span>{course.total_lessons || 0} {$t('course.lessons')}</span>
									<span>{course.duration_hours}{$t('course.hours')} {$t('course.totalLength')}</span>
								</div>
								<LessonList modules={course.modules || []} isEnrolled={course.is_enrolled} />
							</div>
						{:else if activeTab === 'instructor'}
							<div>
								<h3 class="mb-6 text-2xl font-bold">{$t('course.meetYourInstructor')}</h3>
								<div class="flex items-start gap-6">
									{#if course.instructor.avatar}
										<img
											src={course.instructor.avatar}
											alt={course.instructor.full_name}
											class="h-24 w-24 rounded-full object-cover"
										/>
									{:else}
										<div
											class="from-primary-400 to-secondary-600 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br text-3xl font-bold text-white"
										>
											{course.instructor.full_name?.[0]}
										</div>
									{/if}

									<div class="flex-1">
										<h4 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">
											{course.instructor.full_name}
										</h4>
										<p class="text-primary-600 dark:text-primary-400 mb-4 font-medium">
											{course.instructor.role === 'teacher' ? $t('course.instructor') : course.instructor.role}
										</p>

										{#if course.instructor.bio}
											<p class="leading-relaxed text-gray-700 dark:text-gray-300">
												{course.instructor.bio}
											</p>
										{/if}
									</div>
								</div>
							</div>
						{:else if activeTab === 'reviews'}
							<div>
								<h3 class="mb-6 text-2xl font-bold">{$t('course.studentReviews')}</h3>
								{#if course.reviews?.length > 0}
									<div class="space-y-6">
										{#each course.reviews as review}
											<div class="flex gap-4 rounded-xl bg-gray-50 p-6 dark:bg-gray-800/50">
												<div class="flex-shrink-0">
													{#if review.student_avatar}
														<img
															src={review.student_avatar}
															alt={review.student_name}
															class="h-12 w-12 rounded-full object-cover"
														/>
													{:else}
														<div
															class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-300 font-medium text-white dark:bg-gray-600"
														>
															{review.student_name?.[0]}
														</div>
													{/if}
												</div>

												<div class="flex-1">
													<div class="mb-2 flex items-center justify-between">
														<h5 class="font-semibold text-gray-900 dark:text-white">
															{review.student_name}
														</h5>
														<div class="flex items-center">
															{#each Array(5) as _, i}
																<svg
																	class="h-4 w-4 {i < review.rating
																		? 'text-yellow-400'
																		: 'text-gray-300 dark:text-gray-600'}"
																	fill="currentColor"
																	viewBox="0 0 20 20"
																>
																	<path
																		d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
																	/>
																</svg>
															{/each}
														</div>
													</div>

													<p class="mb-2 text-gray-700 dark:text-gray-300">
														{review.comment}
													</p>

													<p class="text-xs text-gray-500 dark:text-gray-400">
														{formatters.relativeTime(review.created_at)}
													</p>
												</div>
											</div>
										{/each}
									</div>
								{:else}
									<div class="py-12 text-center">
										<svg
											class="mx-auto mb-4 h-16 w-16 text-gray-400"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
											/>
										</svg>
										<h4 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
											{$t('course.noReviewsYet')}
										</h4>
										<p class="text-gray-500 dark:text-gray-400">{$t('course.beFirstToReview')}</p>
									</div>
								{/if}
							</div>
						{/if}
					</Card>
				</div>

				<!-- Sidebar -->
				<div class="space-y-6">
					<!-- Enrollment Card -->
					<Card variant="elevated" padding="large" class="sticky top-24">
						<div class="space-y-6">
							<div class="text-center">
								{#if course.is_enrolled}
									<div class="mb-4">
										<Badge variant="success" size="large" class="mb-2">✓ {$t('course.enrolled')}</Badge>
									</div>
									<Button
										href={`/courses/${courseId}/learn`}
										variant="primary"
										size="large"
										fullWidth
										class="mb-4"
									>
										{$t('course.continueLearning')}
									</Button>
									<Button href={`/my-courses`} variant="outline" size="medium" fullWidth>
										{$t('course.viewMyCourses')}
									</Button>
								{:else}
									<Button
										onclick={handleEnroll}
										variant="primary"
										size="large"
										fullWidth
										loading={enrolling}
										class="mb-4"
									>
										{enrolling ? $t('course.enrolling') : $t('course.enrollNow')}
									</Button>
									<p class="text-sm text-gray-500 dark:text-gray-400">
										{$t('course.free')} • {$t('course.lifetimeAccess')} • {$t('course.certificateIncluded')}
									</p>
								{/if}
							</div>

							<!-- Course Details -->
							<div class="space-y-4 border-t border-gray-200 pt-6 dark:border-gray-700">
								<h4 class="mb-4 font-semibold text-gray-900 dark:text-white">{$t('course.courseDetails')}</h4>

								<div class="space-y-3">
									<div class="flex items-center justify-between text-sm">
										<span class="text-gray-600 dark:text-gray-400">{$t('course.level')}</span>
										<Badge variant={levelConfig[course.level].color} size="small">
											{levelConfig[course.level].icon}
											{course.level}
										</Badge>
									</div>

									<div class="flex items-center justify-between text-sm">
										<span class="text-gray-600 dark:text-gray-400">{$t('course.duration')}</span>
										<span class="font-medium text-gray-900 dark:text-white">
											{course.duration_hours} {$t('course.hours')}
										</span>
									</div>

									<div class="flex items-center justify-between text-sm">
										<span class="text-gray-600 dark:text-gray-400">{$t('course.language')}</span>
										<span class="font-medium text-gray-900 dark:text-white">
											{course.language === 'ar' ? 'العربية' : 'English'}
										</span>
									</div>

									<div class="flex items-center justify-between text-sm">
										<span class="text-gray-600 dark:text-gray-400">{$t('course.students')}</span>
										<span class="font-medium text-gray-900 dark:text-white">
											{formatters.number(course.enrolled_count)}
										</span>
									</div>

									<div class="flex items-center justify-between text-sm">
										<span class="text-gray-600 dark:text-gray-400">{$t('course.certificate')}</span>
										<div class="flex items-center gap-1">
											<svg
												class="h-4 w-4 text-green-500"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M5 13l4 4L19 7"
												/>
											</svg>
											<span class="font-medium text-gray-900 dark:text-white">{$t('course.yes')}</span>
										</div>
									</div>
								</div>
							</div>

							<!-- Share Course -->
							<div class="border-t border-gray-200 pt-6 dark:border-gray-700">
								<h4 class="mb-3 font-semibold text-gray-900 dark:text-white">{$t('course.shareCourse')}</h4>
								<div class="flex items-center gap-2">
									<Button 
										onclick={handleShare}
										variant="outline" 
										size="small" 
										class="flex-1"
									>
										<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
											/>
										</svg>
										{$t('actions.share')}
									</Button>
									<Button 
										onclick={handleFavoriteToggle}
										variant="outline" 
										size="small" 
										class="flex-1"
										loading={favoriteLoading}
										disabled={favoriteLoading}
									>
										<svg class="mr-2 h-4 w-4" fill={isFavorite ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
											/>
										</svg>
										{isFavorite ? $t('course.removeFromFavorites') : $t('course.addToFavorites')}
									</Button>
								</div>
							</div>
						</div>
					</Card>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="container mx-auto px-4 py-16 text-center">
		<svg
			class="mx-auto mb-6 h-20 w-20 text-gray-400"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
			/>
		</svg>
		<h2 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">{$t('course.courseNotFound')}</h2>
		<p class="mb-8 text-gray-600 dark:text-gray-400">
			{$t('course.courseNotFoundDesc')}
		</p>
		<Button href="/courses" variant="primary">{$t('course.browseAllCourses')}</Button>
	</div>
{/if}

<!-- Share Modal -->
<ShareModal bind:isOpen={showShareModal} {course} onClose={() => (showShareModal = false)} />

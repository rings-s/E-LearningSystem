<!-- front/src/routes/(app)/courses/[uuid]/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade, fly, scale } from 'svelte/transition';
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

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
	{#if loading}
		<!-- Enhanced Loading State -->
		<div class="container mx-auto px-4 py-8">
			<div class="animate-pulse space-y-8" in:fade={{ duration: 500 }}>
				<!-- Hero skeleton -->
				<div class="h-96 rounded-3xl bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600"></div>
				
				<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
					<div class="space-y-6 lg:col-span-2">
						<!-- Tab navigation skeleton -->
						<Card variant="bordered" class="p-2">
							<div class="flex space-x-1">
								{#each Array(4) as _}
									<div class="h-12 flex-1 rounded-xl bg-gray-200 dark:bg-gray-700"></div>
								{/each}
							</div>
						</Card>
						
						<!-- Content skeleton -->
						<Card variant="bordered" padding="large">
							<div class="space-y-4">
								<div class="h-8 w-1/2 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-4 rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-4 w-2/3 rounded bg-gray-200 dark:bg-gray-700"></div>
							</div>
						</Card>
					</div>
					
					<!-- Sidebar skeleton -->
					<Card variant="bordered" padding="large" class="h-96">
						<div class="space-y-4">
							<div class="h-6 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-12 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
							<div class="space-y-2">
								{#each Array(5) as _}
									<div class="flex justify-between">
										<div class="h-4 w-1/3 rounded bg-gray-200 dark:bg-gray-700"></div>
										<div class="h-4 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
									</div>
								{/each}
							</div>
						</div>
					</Card>
				</div>
			</div>
		</div>
	{:else if course}
		<!-- Enhanced Hero Section -->
		<div class="relative overflow-hidden" in:fade={{ duration: 800 }}>
			<!-- Animated Background -->
			<div class="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600">
				<!-- Animated geometric pattern -->
				<div class="absolute inset-0 opacity-10">
					<svg class="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
						<defs>
							<pattern id="hero-grid" width="10" height="10" patternUnits="userSpaceOnUse">
								<path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/>
							</pattern>
						</defs>
						<rect width="100%" height="100%" fill="url(#hero-grid)" />
					</svg>
				</div>
				
				<!-- Floating geometric shapes -->
				<div class="absolute inset-0 overflow-hidden">
					{#each Array(6) as _, i}
						<div 
							class="absolute rounded-full bg-white/5 animate-float-gentle"
							style="
								width: {15 + Math.random() * 25}px; 
								height: {15 + Math.random() * 25}px;
								left: {Math.random() * 100}%;
								top: {Math.random() * 100}%;
								animation-delay: {i * 0.8}s;
								animation-duration: {8 + Math.random() * 4}s;
							"
						></div>
					{/each}
				</div>

				<!-- Gradient overlay -->
				<div class="absolute inset-0 bg-gradient-to-r from-black/20 via-transparent to-black/20"></div>
			</div>
			
			<div class="relative container mx-auto px-4 py-16">
				<div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
					<!-- Content -->
					<div class="space-y-6 text-white" in:fly={{ x: -30, delay: 200, duration: 800 }}>
						<div class="flex flex-wrap items-center gap-3">
							{#if course?.level}
								<Badge variant="white" class="border-white/30 bg-white/20 text-white backdrop-blur-sm">
									{levelConfig[course.level]?.icon || ''}
									{course.level}
								</Badge>
							{/if}
							{#if course?.category_name}
								<Badge variant="white" class="border-white/30 bg-white/20 text-white backdrop-blur-sm">
									{course.category_name}
								</Badge>
							{/if}
							{#if course?.is_featured}
								<Badge variant="accent" class="bg-gradient-to-r from-yellow-400 to-orange-500 shadow-lg">
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

						<!-- Enhanced Meta Information -->
						<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
							<div class="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur-sm">
								<svg class="h-5 w-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
								</svg>
								<div>
									<div class="text-sm text-white/70">Instructor</div>
									<div class="font-medium">{course?.instructor?.full_name || 'Instructor'}</div>
								</div>
							</div>

							{#if course?.average_rating > 0}
								<div class="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur-sm">
									<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
										<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
									</svg>
									<div>
										<div class="text-sm text-white/70">Rating</div>
										<div class="font-medium">{course?.average_rating?.toFixed(1)} ({formatters.number(course?.reviews_count || 0)})</div>
									</div>
								</div>
							{/if}

							<div class="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur-sm">
								<svg class="h-5 w-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
								</svg>
								<div>
									<div class="text-sm text-white/70">Students</div>
									<div class="font-medium">{formatters.number(course?.enrolled_count || 0)}</div>
								</div>
							</div>

							<div class="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur-sm">
								<svg class="h-5 w-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<div>
									<div class="text-sm text-white/70">Duration</div>
									<div class="font-medium">{course?.duration_hours || 0} hours</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Enhanced Preview Video -->
					<div class="relative" in:fly={{ x: 30, delay: 400, duration: 800 }}>
						{#if course?.preview_video}
							<div class="group relative overflow-hidden rounded-3xl shadow-2xl transition-transform duration-300 hover:scale-105">
								<YouTubePlayer
									videoId={course?.preview_video}
									class="aspect-video w-full"
									modestBranding={true}
									rel={0}
									showInfo={false}
								/>
								<div class="absolute inset-0 rounded-3xl ring-1 ring-white/20"></div>
							</div>
						{:else}
							<div class="group relative aspect-video overflow-hidden rounded-3xl bg-white/10 backdrop-blur-sm transition-all duration-300 hover:scale-105">
								<div class="flex h-full items-center justify-center">
									<div class="text-center text-white">
										<div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-white/10 backdrop-blur-sm">
											<svg class="h-10 w-10 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
										</div>
										<p class="text-lg font-medium opacity-80">{$t('course.previewComingSoon')}</p>
									</div>
								</div>
								<div class="absolute inset-0 rounded-3xl ring-1 ring-white/20"></div>
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
				<div class="space-y-8 lg:col-span-2" in:fly={{ y: 30, delay: 600, duration: 800 }}>
					<!-- Enhanced Tab Navigation -->
					<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-xl dark:bg-gray-800/95">
						<nav class="flex space-x-1 p-2">
							{#each tabs as tab}
								<button
									onclick={() => (activeTab = tab.id)}
									class={classNames(
										'group flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300',
										activeTab === tab.id
											? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 shadow-sm scale-105'
											: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white hover:scale-105'
									)}
								>
									<svg class="h-4 w-4 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										{@html icons[tab.icon]}
									</svg>
									{tab.label}
								</button>
							{/each}
						</nav>
					</Card>

					<!-- Enhanced Tab Content -->
					<Card variant="bordered" padding="large" class="bg-white/95 backdrop-blur-sm shadow-xl dark:bg-gray-800/95">
						{#if activeTab === 'overview'}
							<div class="prose prose-gray dark:prose-invert max-w-none" in:fade={{ duration: 300 }}>
								<h3 class="mb-6 text-2xl font-bold text-gray-900 dark:text-white">{$t('course.aboutThisCourse')}</h3>
								{#if course?.description}
									<div class="leading-relaxed text-gray-700 dark:text-gray-300">
										{course.description}
									</div>
								{/if}

								{#if course?.learning_outcomes}
									<h3 class="mt-8 mb-6 text-xl font-semibold text-gray-900 dark:text-white">{$t('course.whatYoullLearn')}</h3>
									<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
										{#each course.learning_outcomes.split('\n').filter(Boolean) as outcome, i}
											<div 
												class="group flex items-start gap-3 rounded-xl bg-green-50 p-4 transition-all duration-300 hover:bg-green-100 hover:scale-105 dark:bg-green-900/20 dark:hover:bg-green-900/30"
												in:fly={{ x: -20, delay: i * 100, duration: 500 }}
											>
												<svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-600 dark:text-green-400 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
												</svg>
												<span class="text-sm font-medium text-green-800 dark:text-green-200">{outcome.trim()}</span>
											</div>
										{/each}
									</div>
								{/if}

								{#if course.prerequisites}
									<h3 class="mt-8 mb-4 text-xl font-semibold text-gray-900 dark:text-white">{$t('course.prerequisites')}</h3>
									<div class="rounded-xl bg-blue-50 p-6 dark:bg-blue-900/20">
										<p class="text-blue-800 dark:text-blue-200 leading-relaxed">{course.prerequisites}</p>
									</div>
								{/if}
							</div>
						{:else if activeTab === 'curriculum'}
							<div in:fade={{ duration: 300 }}>
								<h3 class="mb-6 text-2xl font-bold text-gray-900 dark:text-white">{$t('course.courseCurriculum')}</h3>
								<div class="mb-6 flex flex-wrap items-center gap-6">
									<div class="rounded-lg bg-gray-50 px-4 py-2 dark:bg-gray-800">
										<span class="text-sm font-medium text-gray-600 dark:text-gray-400">{course.modules?.length || 0} {$t('course.modules')}</span>
									</div>
									<div class="rounded-lg bg-gray-50 px-4 py-2 dark:bg-gray-800">
										<span class="text-sm font-medium text-gray-600 dark:text-gray-400">{course.total_lessons || 0} {$t('course.lessons')}</span>
									</div>
									<div class="rounded-lg bg-gray-50 px-4 py-2 dark:bg-gray-800">
										<span class="text-sm font-medium text-gray-600 dark:text-gray-400">{course.duration_hours}h {$t('course.totalLength')}</span>
									</div>
								</div>
								<LessonList modules={course.modules || []} isEnrolled={course.is_enrolled} />
							</div>
						{:else if activeTab === 'instructor'}
							<div in:fade={{ duration: 300 }}>
								<h3 class="mb-6 text-2xl font-bold text-gray-900 dark:text-white">{$t('course.meetYourInstructor')}</h3>
								<div class="flex items-start gap-6">
									{#if course.instructor.avatar}
										<img src={course.instructor.avatar} alt={course.instructor.full_name} class="h-24 w-24 rounded-full object-cover shadow-lg" />
									{:else}
										<div class="from-primary-400 to-secondary-600 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br text-3xl font-bold text-white shadow-lg">
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
							<div in:fade={{ duration: 300 }}>
								<h3 class="mb-6 text-2xl font-bold text-gray-900 dark:text-white">{$t('course.studentReviews')}</h3>
								{#if course.reviews?.length > 0}
									<div class="space-y-6">
										{#each course.reviews as review, i}
											<div 
												class="group flex gap-4 rounded-xl bg-gray-50 p-6 transition-all duration-300 hover:bg-gray-100 hover:shadow-md dark:bg-gray-800/50 dark:hover:bg-gray-800/80"
												in:fly={{ y: 20, delay: i * 100, duration: 500 }}
											>
												<div class="flex-shrink-0">
													{#if review.student_avatar}
														<img src={review.student_avatar} alt={review.student_name} class="h-12 w-12 rounded-full object-cover" />
													{:else}
														<div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-300 font-medium text-white dark:bg-gray-600">
															{review.student_name?.[0]}
														</div>
													{/if}
												</div>

												<div class="flex-1">
													<div class="mb-2 flex items-center justify-between">
														<h5 class="font-semibold text-gray-900 dark:text-white">{review.student_name}</h5>
														<div class="flex items-center">
															{#each Array(5) as _, i}
																<svg class="h-4 w-4 {i < review.rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}" fill="currentColor" viewBox="0 0 20 20">
																	<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
																</svg>
															{/each}
														</div>
													</div>

													<p class="mb-2 leading-relaxed text-gray-700 dark:text-gray-300">{review.comment}</p>

													<p class="text-xs text-gray-500 dark:text-gray-400">
														{formatters.relativeTime(review.created_at)}
													</p>
												</div>
											</div>
										{/each}
									</div>
								{:else}
									<div class="py-12 text-center">
										<div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
											<svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
											</svg>
										</div>
										<h4 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">{$t('course.noReviewsYet')}</h4>
										<p class="text-gray-500 dark:text-gray-400">{$t('course.beFirstToReview')}</p>
									</div>
								{/if}
							</div>
						{/if}
					</Card>
				</div>

				<!-- Enhanced Sidebar -->
				<div class="space-y-6" in:fly={{ y: 30, delay: 800, duration: 800 }}>
					<!-- Enhanced Enrollment Card -->
					<Card variant="elevated" padding="large" class="sticky top-24 bg-white/95 backdrop-blur-sm shadow-2xl dark:bg-gray-800/95">
						<div class="space-y-6">
							<div class="text-center">
								{#if course.is_enrolled}
									<div class="mb-6" in:scale={{ duration: 500 }}>
										<Badge variant="success" size="large" class="mb-4 shadow-lg">
											<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
											</svg>
											{$t('course.enrolled')}
										</Badge>
									</div>
									<Button href={`/courses/${courseId}/learn`} variant="primary" size="large" fullWidth class="mb-4 transition-all hover:scale-105">
										{$t('course.continueLearning')}
									</Button>
									<Button href={`/my-courses`} variant="outline" size="medium" fullWidth class="transition-all hover:scale-105">
										{$t('course.viewMyCourses')}
									</Button>
								{:else}
									<Button onclick={handleEnroll} variant="primary" size="large" fullWidth loading={enrolling} class="mb-4 transition-all hover:scale-105">
										{enrolling ? $t('course.enrolling') : $t('course.enrollNow')}
									</Button>
									<div class="flex flex-wrap justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
										<Badge variant="outline" size="small">
											<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
											</svg>
											{$t('course.free')}
										</Badge>
										<Badge variant="outline" size="small">
											<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											{$t('course.lifetimeAccess')}
										</Badge>
										<Badge variant="outline" size="small">
											<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											{$t('course.certificateIncluded')}
										</Badge>
									</div>
								{/if}
							</div>

							<!-- Enhanced Course Details -->
							<div class="space-y-4 border-t border-gray-200 pt-6 dark:border-gray-700">
								<h4 class="mb-4 font-semibold text-gray-900 dark:text-white">{$t('course.courseDetails')}</h4>

								<div class="space-y-3">
									<div class="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
										<span class="text-sm text-gray-600 dark:text-gray-400">{$t('course.level')}</span>
										<Badge variant={levelConfig[course.level].color} size="small">
											{levelConfig[course.level].icon}
											{course.level}
										</Badge>
									</div>

									<div class="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
										<span class="text-sm text-gray-600 dark:text-gray-400">{$t('course.duration')}</span>
										<span class="font-medium text-gray-900 dark:text-white">
											{course.duration_hours} {$t('course.hours')}
										</span>
									</div>

									<div class="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
										<span class="text-sm text-gray-600 dark:text-gray-400">{$t('course.language')}</span>
										<span class="font-medium text-gray-900 dark:text-white">
											{course.language === 'ar' ? 'العربية' : 'English'}
										</span>
									</div>

									<div class="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
										<span class="text-sm text-gray-600 dark:text-gray-400">{$t('course.students')}</span>
										<span class="font-medium text-gray-900 dark:text-white">
											{formatters.number(course.enrolled_count)}
										</span>
									</div>

									<div class="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
										<span class="text-sm text-gray-600 dark:text-gray-400">{$t('course.certificate')}</span>
										<div class="flex items-center gap-1">
											<svg class="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
											</svg>
											<span class="font-medium text-gray-900 dark:text-white">{$t('course.yes')}</span>
										</div>
									</div>
								</div>
							</div>

							<!-- Enhanced Share Course -->
							<div class="border-t border-gray-200 pt-6 dark:border-gray-700">
								<h4 class="mb-3 font-semibold text-gray-900 dark:text-white">{$t('course.shareCourse')}</h4>
								<div class="flex items-center gap-2">
									<Button onclick={handleShare} variant="outline" size="small" class="flex-1 transition-all hover:scale-105">
										<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
										</svg>
										{$t('actions.share')}
									</Button>
									<Button onclick={handleFavoriteToggle} variant="outline" size="small" class="flex-1 transition-all hover:scale-105" loading={favoriteLoading} disabled={favoriteLoading}>
										<svg class="mr-2 h-4 w-4" fill={isFavorite ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
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
	{:else}
		<!-- Enhanced Error State -->
		<div class="container mx-auto px-4 py-16 text-center" in:fade={{ duration: 500 }}>
			<div in:scale={{ duration: 600, start: 0.8 }}>
				<div class="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-red-100 to-red-200 dark:from-red-900 dark:to-red-800">
					<svg class="h-12 w-12 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h2 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">{$t('course.courseNotFound')}</h2>
				<p class="mb-8 text-gray-600 dark:text-gray-400">{$t('course.courseNotFoundDesc')}</p>
				<Button href="/courses" variant="primary" class="transition-all hover:scale-105">{$t('course.browseAllCourses')}</Button>
			</div>
		</div>
	{/if}
</div>

<!-- Share Modal -->
<ShareModal bind:isOpen={showShareModal} {course} onClose={() => (showShareModal = false)} />

<style>
	@keyframes float-gentle {
		0%, 100% {
			transform: translateY(0px) rotate(0deg);
		}
		33% {
			transform: translateY(-15px) rotate(1deg);
		}
		66% {
			transform: translateY(-8px) rotate(-1deg);
		}
	}

	.animate-float-gentle {
		animation: float-gentle 8s ease-in-out infinite;
	}
</style>
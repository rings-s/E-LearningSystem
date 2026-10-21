<!-- front/src/routes/(app)/my-courses/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { coursesApi } from '#lib/apis/courses.js';
	import { currentUser } from '#lib/stores/auth.store.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t, locale } from '#lib/i18n/index.js';
	import { formatters } from '#lib/utils/formatters.js';
	import { classNames, debounce } from '#lib/utils/helpers.js';

	// Components
	import CourseCover from '#lib/components/course/CourseCover.svelte';
	import StatsCard from '#lib/components/dashboard/StatsCard.svelte';
	import PageHeader from '#lib/components/common/PageHeader.svelte';
	import EmptyState from '#lib/components/common/EmptyState.svelte';
	import Skeleton from '#lib/components/common/Skeleton.svelte';
	import Select from '#lib/components/common/Select.svelte';
	import Tabs from '#lib/components/common/Tabs.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import Input from '#lib/components/common/Input.svelte';

	let courses = $state([]);
	let loading = $state(true);
	let searchQuery = $state('');
	let activeFilter = $state('all');
	let viewMode = $state('grid');
	let sortBy = $state('recent');
	let error = $state(null);

	// Convert reactive statements to derived runes
	const userRole = $derived($currentUser?.role || 'student');
	const isTeacher = $derived(userRole === 'teacher');

	// Debounced search function
	const debouncedSearch = debounce((query) => {
		searchQuery = query;
	}, 300);

	// Convert filtered courses to derived
	const filteredCourses = $derived(
		(() => {
			try {
				let filtered = [...courses];

				// Apply status filter
				if (activeFilter !== 'all') {
					if (isTeacher) {
						filtered = filtered.filter((c) => c.status === activeFilter);
					} else {
						filtered = filtered.filter((c) => c.enrollment?.status === activeFilter);
					}
				}

				// Apply search filter
				if (searchQuery.trim()) {
					const query = searchQuery.toLowerCase();
					filtered = filtered.filter((c) => {
						const title = c.title?.toLowerCase() || '';
						const instructor = c.instructor_name?.toLowerCase() || '';
						const category = c.category_name?.toLowerCase() || '';
						return title.includes(query) || instructor.includes(query) || category.includes(query);
					});
				}

				// Apply sorting
				filtered.sort((a, b) => {
					switch (sortBy) {
						case 'title':
							return a.title.localeCompare(b.title);
						case 'progress':
							if (isTeacher) return 0;
							return (
								(b.enrollment?.progress_percentage || 0) - (a.enrollment?.progress_percentage || 0)
							);
						case 'status':
							if (isTeacher) return a.status.localeCompare(b.status);
							return (a.enrollment?.status || '').localeCompare(b.enrollment?.status || '');
						case 'recent':
						default:
							const aDate = isTeacher ? a.updated_at : a.enrollment?.enrolled_at;
							const bDate = isTeacher ? b.updated_at : b.enrollment?.enrolled_at;
							return new Date(bDate || 0) - new Date(aDate || 0);
					}
				});

				return filtered;
			} catch (err) {
				console.error('Error filtering courses:', err);
				return [];
			}
		})()
	);

	// Convert stats to derived
	const stats = $derived(
		(() => {
			try {
				if (isTeacher) {
					const total = courses.length;
					const published = courses.filter((c) => c.status === 'published').length;
					const draft = courses.filter((c) => c.status === 'draft').length;
					const totalStudents = courses.reduce(
						(sum, c) => sum + (c.enrolled_students_count ?? c.enrollment_count ?? 0),
						0
					);

					return { total, published, draft, totalStudents };
				} else {
					const total = courses.length;
					const completed = courses.filter((c) => c.enrollment?.status === 'completed').length;
					const inProgress = courses.filter((c) => c.enrollment?.status === 'in_progress').length;
					const avgProgress =
						total > 0
							? Math.round(
									courses.reduce((sum, c) => sum + (c.enrollment?.progress_percentage || 0), 0) /
										total
								)
							: 0;

					return { total, completed, inProgress, avgProgress };
				}
			} catch (err) {
				console.error('Error calculating stats:', err);
				return { total: 0, completed: 0, inProgress: 0, avgProgress: 0 };
			}
		})()
	);

	// Convert filter options to derived
	const filterOptions = $derived(
		(() => {
			if (isTeacher) {
				return [
					{
						id: 'all',
						label: $t('myCourses.allCourses'),
						icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z'
					},
					{ id: 'published', label: $t('myCourses.published'), icon: 'M5 13l4 4L19 7' },
					{
						id: 'draft',
						label: $t('myCourses.drafts'),
						icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z'
					},
					{ id: 'archived', label: $t('myCourses.archived'), icon: 'M5 8l6 6M5 8l6 6m0-6L5 8' }
				];
			} else {
				return [
					{
						id: 'all',
						label: $t('myCourses.allCourses'),
						icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z'
					},
					{
						id: 'in_progress',
						label: $t('myCourses.inProgress'),
						icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
					},
					{
						id: 'completed',
						label: $t('myCourses.completed'),
						icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
					},
					{
						id: 'enrolled',
						label: $t('myCourses.recentlyEnrolled'),
						icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253'
					}
				];
			}
		})()
	);

	// Convert sort options to derived
	const sortOptions = $derived([
		{
			id: 'recent',
			label: isTeacher ? $t('myCourses.recentlyUpdated') : $t('myCourses.recentlyEnrolled')
		},
		{ id: 'title', label: $t('myCourses.titleAZ') },
		...(isTeacher ? [] : [{ id: 'progress', label: $t('myCourses.progress') }]),
		{ id: 'status', label: $t('myCourses.status') }
	]);

	onMount(async () => {
		await fetchCourses();
	});

	// Fixed: This should be fetchCourses (plural), not fetchCourse (singular)
	const fetchCourses = async () => {
		loading = true;
		error = null;

		try {
			console.log('Fetching courses for user:', $currentUser);
			console.log('Is teacher:', isTeacher);

			if (isTeacher) {
				// For teachers, get courses they created
				const response = await coursesApi.getMyCourses();
				console.log('Teacher courses response:', response);
				courses = Array.isArray(response.results)
					? response.results
					: Array.isArray(response)
						? response
						: [];
			} else {
				// For students, get their enrollments
				const enrollments = await coursesApi.getMyEnrollments();
				console.log('Student enrollments response:', enrollments);
				courses = Array.isArray(enrollments)
					? enrollments.map((e) => ({
							...e.course,
							enrollment: e
						}))
					: [];
			}
			console.log('Final courses:', courses);
		} catch (err) {
			console.error('Failed to fetch courses:', err);
			error = err.message || $t('myCourses.loadFailed');
			courses = [];

			uiStore.showNotification({
				type: 'error',
				title: $t('myCourses.error'),
				message: $t('myCourses.loadFailedToast')
			});
		} finally {
			loading = false;
		}
	};

	const handleSearchInput = (event) => {
		debouncedSearch(event.target.value);
	};

	const getStatusConfig = (status, isTeacherCourse = false) => {
		if (isTeacherCourse) {
			const configs = {
				published: {
					color: 'success',
					label: $t('myCourses.published'),
					bg: 'bg-green-50',
					text: 'text-green-700'
				},
				draft: {
					color: 'warning',
					label: $t('myCourses.draft'),
					bg: 'bg-amber-50',
					text: 'text-amber-700'
				},
				archived: {
					color: 'gray',
					label: $t('myCourses.archived'),
					bg: 'bg-gray-50',
					text: 'text-gray-700'
				}
			};
			return configs[status] || configs.draft;
		} else {
			const configs = {
				enrolled: {
					color: 'info',
					label: $t('myCourses.enrolled'),
					bg: 'bg-primary-50',
					text: 'text-primary-700'
				},
				in_progress: {
					color: 'warning',
					label: $t('myCourses.inProgress'),
					bg: 'bg-amber-50',
					text: 'text-amber-700'
				},
				completed: {
					color: 'success',
					label: $t('myCourses.completed'),
					bg: 'bg-green-50',
					text: 'text-green-700'
				},
				dropped: {
					color: 'danger',
					label: $t('myCourses.dropped'),
					bg: 'bg-red-50',
					text: 'text-red-700'
				}
			};
			return configs[status] || configs.enrolled;
		}
	};

	const getProgressColor = (progress) => {
		if (progress >= 80) return 'success';
		if (progress >= 50) return 'warning';
		return 'info';
	};

	const formatDate = (dateString) => {
		if (!dateString) return 'N/A';
		return formatters.date(dateString, $locale);
	};

	const getCourseActionUrl = (course) => {
		if (isTeacher) {
			return `/teacher/courses/${course.uuid}/manage`;
		} else {
			return `/courses/${course.uuid}/learn`;
		}
	};

	const getCourseActionLabel = (course) => {
		if (isTeacher) {
			return course.status === 'published'
				? $t('myCourses.manageCourse')
				: $t('myCourses.editCourse');
		} else {
			return course.enrollment?.status === 'completed'
				? $t('myCourses.reviewCourse')
				: $t('myCourses.continueLearning');
		}
	};
</script>

<svelte:head>
	<title>{$t('myCourses.pageTitle')}</title>
</svelte:head>

<div class="space-y-6">
	<PageHeader
		title={isTeacher ? $t('myCourses.teachingTitle') : $t('myCourses.learningTitle')}
		description={isTeacher ? $t('myCourses.teachingDesc') : $t('myCourses.learningDesc')}
	>
		{#snippet actions()}
			{#if isTeacher}
				<Button
					href="/teacher/courses/create"
					iconLeft={'<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />'}
				>
					{$t('myCourses.newCourse')}
				</Button>
			{:else}
				<Button href="/courses" variant="outline">{$t('myCourses.browseCourses')}</Button>
			{/if}
		{/snippet}
	</PageHeader>

	<!-- Stats -->
	{#if !loading && courses.length > 0}
		<div class="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
			{#each isTeacher ? [{ label: $t('myCourses.totalCourses'), value: stats.total }, { label: $t('myCourses.published'), value: stats.published }, { label: $t('myCourses.drafts'), value: stats.draft }, { label: $t('myCourses.students'), value: stats.totalStudents }] : [{ label: $t('myCourses.enrolled'), value: stats.total }, { label: $t('myCourses.inProgressLower'), value: stats.inProgress }, { label: $t('myCourses.completed'), value: stats.completed }, { label: $t('myCourses.avgProgress'), value: `${stats.avgProgress}%` }] as stat}
				<StatsCard title={stat.label} value={stat.value} />
			{/each}
		</div>
	{/if}

	<!-- Controls -->
	{#if !loading && courses.length > 0}
		<div class="space-y-4">
			<div class="flex flex-col gap-3 sm:flex-row">
				<Input
					type="search"
					class="flex-1"
					placeholder={$t('myCourses.searchPlaceholder')}
					oninput={handleSearchInput}
					icon="<path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z' />"
				/>
				<div class="flex gap-3">
					<Select
						bind:value={sortBy}
						options={sortOptions.map((o) => ({ value: o.id, label: o.label }))}
						placeholder=""
						class="flex-1 sm:w-48"
						aria-label={$t('myCourses.sortCourses')}
					/>
					<div
						class="hidden shrink-0 rounded-xl bg-gray-100 p-1 sm:flex dark:bg-white/5"
						role="group"
						aria-label={$t('myCourses.viewMode')}
					>
						{#each [{ id: 'grid', d: 'M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z' }, { id: 'list', d: 'M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM3.75 12h.007v.008H3.75V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm-.375 5.25h.007v.008H3.75v-.008zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z' }] as mode}
							<button
								type="button"
								onclick={() => (viewMode = mode.id)}
								aria-pressed={viewMode === mode.id}
								aria-label={mode.id === 'grid'
									? $t('myCourses.gridView')
									: $t('myCourses.listView')}
								class="flex size-9 items-center justify-center rounded-lg transition-colors {viewMode ===
								mode.id
									? 'bg-white text-gray-900 shadow-xs dark:bg-white/10 dark:text-white'
									: 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'}"
							>
								<svg
									class="size-5"
									fill="none"
									stroke="currentColor"
									stroke-width="1.75"
									viewBox="0 0 24 24"
								>
									<path stroke-linecap="round" stroke-linejoin="round" d={mode.d} />
								</svg>
							</button>
						{/each}
					</div>
				</div>
			</div>

			<Tabs
				variant="pills"
				tabs={filterOptions.map((f) => ({ label: f.label }))}
				bind:activeTab={
					() => filterOptions.findIndex((f) => f.id === activeFilter),
					(i) => (activeFilter = filterOptions[i].id)
				}
			/>
		</div>
	{/if}

	<!-- Content -->
	{#if error}
		<EmptyState
			title={$t('myCourses.loadError')}
			description={error}
			icon={'<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />'}
		>
			{#snippet actions()}
				<Button onclick={fetchCourses}>{$t('myCourses.tryAgain')}</Button>
			{/snippet}
		</EmptyState>
	{:else if loading}
		<div class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
			<Skeleton variant="card" count={6} />
		</div>
	{:else if courses.length === 0}
		<EmptyState
			title={isTeacher ? $t('myCourses.noTeaching') : $t('myCourses.noLearning')}
			description={isTeacher ? $t('myCourses.noTeachingDesc') : $t('myCourses.noLearningDesc')}
		>
			{#snippet actions()}
				{#if isTeacher}
					<Button href="/teacher/courses/create">{$t('myCourses.createCourse')}</Button>
				{:else}
					<Button href="/courses">{$t('myCourses.browseCourses')}</Button>
				{/if}
			{/snippet}
		</EmptyState>
	{:else if filteredCourses.length === 0}
		<EmptyState
			title={$t('myCourses.noMatches')}
			description={$t('myCourses.noMatchesDesc')}
			icon={'<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />'}
		>
			{#snippet actions()}
				<Button variant="outline" onclick={() => (activeFilter = 'all')}
					>{$t('myCourses.showAll')}</Button
				>
			{/snippet}
		</EmptyState>
	{:else}
		<div
			class={viewMode === 'list'
				? 'space-y-3'
				: 'grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3'}
		>
			{#each filteredCourses as course (course.uuid)}
				{@const status = getStatusConfig(
					isTeacher ? course.status : course.enrollment?.status,
					isTeacher
				)}
				{@const progress = Math.round(course.enrollment?.progress_percentage || 0)}
				<a
					href={getCourseActionUrl(course)}
					in:fade={{ duration: 150 }}
					class="group flex overflow-hidden rounded-2xl bg-white shadow-xs ring-1 ring-gray-200/80 transition-[box-shadow,transform] duration-200 hover:-translate-y-0.5 hover:shadow-lg dark:bg-gray-900 dark:ring-white/10 {viewMode ===
					'list'
						? 'flex-row items-stretch'
						: 'flex-col'}"
				>
					<div
						class="relative shrink-0 overflow-hidden bg-gray-100 dark:bg-white/5 {viewMode ===
						'list'
							? 'w-28 sm:w-48'
							: 'aspect-video'}"
					>
						<CourseCover {course} />
						<Badge
							variant="white"
							size="small"
							class="absolute start-3 top-3 {viewMode === 'list' ? 'hidden sm:inline-flex' : ''}"
						>
							{status.label}
						</Badge>
					</div>

					<div class="flex min-w-0 flex-1 flex-col p-4 sm:p-5">
						{#if course.category_name}
							<p class="text-primary-600 dark:text-primary-400 text-xs font-medium">
								{course.category_name}
							</p>
						{/if}
						<h3
							dir="auto"
							class="group-hover:text-primary-700 dark:group-hover:text-primary-300 mt-1 line-clamp-2 text-base font-semibold text-gray-900 transition-colors dark:text-white"
						>
							{course.title}
						</h3>
						{#if !isTeacher && course.instructor_name}
							<p class="mt-1 truncate text-sm text-gray-500 dark:text-gray-400">
								{course.instructor_name}
							</p>
						{/if}

						<div class="min-h-4 flex-1"></div>

						{#if isTeacher}
							<div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
								<span
									>{$t('myCourses.studentsCount', {
										count: course.enrolled_students_count ?? course.enrollment_count ?? 0
									})}</span
								>
								<span>{$t('myCourses.updated', { date: formatDate(course.updated_at) })}</span>
							</div>
						{:else}
							<div>
								<div class="flex items-center justify-between text-xs">
									<span class="text-gray-500 dark:text-gray-400">
										{progress === 100
											? $t('myCourses.completed')
											: $t('myCourses.percentComplete', { percent: progress })}
									</span>
									<span class="text-primary-600 dark:text-primary-400 font-medium">
										{getCourseActionLabel(course)}
									</span>
								</div>
								<div class="mt-2 h-1.5 overflow-hidden rounded-full bg-gray-100 dark:bg-white/10">
									<div
										class="h-full rounded-full transition-[width] duration-500 {progress === 100
											? 'bg-success-500'
											: 'bg-primary-600 dark:bg-primary-400'}"
										style="width: {progress}%"
									></div>
								</div>
							</div>
						{/if}
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>

<script>
	import { t, locale } from '#lib/i18n/index.js';
	import { isTeacher, isStudent, isAdmin } from '#lib/utils/helpers.js';
	import { formatters } from '#lib/utils/formatters.js';

	// Components
	import Card from '#lib/components/common/Card.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';
	import StatsCard from '#lib/components/dashboard/StatsCard.svelte';
	import EmptyState from '#lib/components/common/EmptyState.svelte';
	import ActivityChart from '#lib/components/charts/ActivityChart.svelte';
	import PerformanceRadar from '#lib/components/charts/PerformanceRadar.svelte';

	let { user, data = {}, analytics = {}, courses = [], onAction = () => {} } = $props();

	// Utility functions - defined first for proper hoisting
	function getUniqueStudentCount(coursesData) {
		if (!coursesData || !Array.isArray(coursesData)) {
			return 0;
		}

		// Get unique students across all courses
		const uniqueStudents = new Set();

		coursesData.forEach((course) => {
			if (course.enrolled_students && Array.isArray(course.enrolled_students)) {
				course.enrolled_students.forEach((student) => {
					uniqueStudents.add(student.id || student.uuid);
				});
			}
		});

		// Fallback to enrollment count sum if enrolled_students not available
		if (uniqueStudents.size === 0) {
			// Try both field names for compatibility
			return coursesData.reduce((sum, c) => {
				return sum + (c.enrollment_count || c.enrolled_count || 0);
			}, 0);
		}

		return uniqueStudents.size;
	}

	// Derived user role
	let userRole = $derived(user?.role || 'student');
	let userName = $derived(
		user?.name || user?.first_name || user?.username || $t('dashboardHome.user')
	);

	// Role-based data processing
	let stats = $derived(getStatsForRole(userRole, data, courses));
	let quickActions = $derived(getQuickActionsForRole(userRole));
	let recentItems = $derived(getRecentItemsForRole(userRole, courses, data));

	function getStatsForRole(role, dashboardData, coursesData) {
		if (isTeacher(user)) {
			return {
				primary: {
					title: $t('dashboardHome.totalCourses'),
					value: coursesData.length || 0,
					icon: '📚',
					trendDirection: 'up'
				},
				secondary: [
					{
						title: $t('dashboardHome.publishedCourses'),
						value: coursesData.filter((c) => c.status === 'published').length || 0,
						icon: '✅',
						trendDirection: 'up'
					},
					{
						title: $t('dashboardHome.totalStudents'),
						value: getUniqueStudentCount(coursesData),
						icon: '👥',
						trendDirection: 'up'
					},
					{
						title: $t('dashboardHome.averageRating'),
						value:
							coursesData.length > 0
								? (
										coursesData.reduce((sum, c) => sum + (c.average_rating || 0), 0) /
										coursesData.length
									).toFixed(1)
								: '0.0',
						icon: '⭐',
						trendDirection: 'up'
					}
				]
			};
		} else if (isStudent(user)) {
			return {
				primary: {
					title: $t('dashboardHome.enrolledCourses'),
					value: coursesData.length || 0,
					icon: '🎓',
					trendDirection: 'up'
				},
				secondary: [
					{
						title: $t('dashboardHome.completed'),
						value: coursesData.filter((c) => c.progress === 100).length || 0,
						icon: '✅',
						trendDirection: 'up'
					},
					{
						title: $t('dashboardHome.inProgress'),
						value: coursesData.filter((c) => c.progress > 0 && c.progress < 100).length || 0,
						icon: '📖',
						trendDirection: 'neutral'
					},
					{
						title: $t('dashboardHome.studyHours'),
						value: dashboardData.total_study_hours || 0,
						icon: '⏱️',
						trendDirection: 'up'
					}
				]
			};
		} else {
			// Admin/Manager stats
			return {
				primary: {
					title: $t('dashboardHome.totalUsers'),
					value: dashboardData.total_users || 0,
					icon: '👥',
					trendDirection: 'up'
				},
				secondary: [
					{
						title: $t('dashboardHome.activeCourses'),
						value: dashboardData.total_courses || 0,
						icon: '📚',
						trendDirection: 'up'
					},
					{
						title: $t('dashboardHome.totalEnrollments'),
						value: dashboardData.total_enrollments || 0,
						icon: '🎓',
						trendDirection: 'up'
					},
					{
						title: $t('dashboardHome.activeToday'),
						value: dashboardData.active_users_today || 0,
						icon: '🟢',
						trendDirection: 'neutral'
					}
				]
			};
		}
	}

	function getQuickActionsForRole(role) {
		if (isTeacher(user)) {
			return [
				{
					title: $t('dashboardHome.createNewCourse'),
					description: $t('dashboardHome.createNewCourseDesc'),
					icon: '➕',
					action: 'create_course',
					href: '/teacher/courses/create',
					primary: true
				},
				{
					title: $t('dashboardHome.manageStudents'),
					description: $t('dashboardHome.manageStudentsDesc'),
					icon: '👥',
					action: 'manage_students',
					href: '/teacher/students'
				},
				{
					title: $t('dashboardHome.viewAllCourses'),
					description: $t('dashboardHome.viewAllCoursesDesc'),
					icon: '📚',
					action: 'view_courses',
					href: '/teacher/courses'
				},
				{
					title: $t('dashboardHome.analytics'),
					description: $t('dashboardHome.analyticsDesc'),
					icon: '📊',
					action: 'view_analytics',
					href: '#'
				}
			];
		} else if (isStudent(user)) {
			return [
				{
					title: $t('dashboardHome.browseCourses'),
					description: $t('dashboardHome.browseCoursesDesc'),
					icon: '🔍',
					action: 'browse_courses',
					href: '/courses',
					primary: true
				},
				{
					title: $t('dashboardHome.myCourses'),
					description: $t('dashboardHome.myCoursesDesc'),
					icon: '📖',
					action: 'my_courses',
					href: '/my-courses'
				},
				{
					title: $t('dashboardHome.certificates'),
					description: $t('dashboardHome.certificatesDesc'),
					icon: '🏆',
					action: 'certificates',
					href: '/certificates'
				}
			];
		} else {
			return [
				{
					title: $t('dashboardHome.manageCourses'),
					description: $t('dashboardHome.manageCoursesDesc'),
					icon: '📚',
					action: 'manage_courses',
					href: '/admin/courses',
					primary: true
				},
				{
					title: $t('dashboardHome.userManagement'),
					description: $t('dashboardHome.userManagementDesc'),
					icon: '👤',
					action: 'manage_users',
					href: '/admin/users'
				},
				{
					title: $t('dashboardHome.analyticsDashboard'),
					description: $t('dashboardHome.analyticsDashboardDesc'),
					icon: '📊',
					action: 'platform_analytics',
					href: '/admin/analytics'
				},
				{
					title: $t('dashboardHome.systemSettings'),
					description: $t('dashboardHome.systemSettingsDesc'),
					icon: '⚙️',
					action: 'settings',
					href: '/admin/settings'
				}
			];
		}
	}

	function getRecentItemsForRole(role, coursesData, dashboardData) {
		if (isTeacher(user)) {
			return [...coursesData]
				.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
				.slice(0, 5)
				.map((course) => ({
					title: course.title,
					description: $t('dashboardHome.studentsCount', { count: course.enrollment_count || 0 }),
					status: course.status,
					href: `/teacher/courses/${course.uuid}/manage`,
					thumbnail: course.thumbnail,
					date: course.created_at
				}));
		} else if (isStudent(user)) {
			return [...coursesData]
				.sort(
					(a, b) =>
						new Date(b.last_accessed || b.enrolled_at) - new Date(a.last_accessed || a.enrolled_at)
				)
				.slice(0, 5)
				.map((course) => ({
					title: course.title,
					description: $t('dashboardHome.percentComplete', { percent: course.progress || 0 }),
					status: course.progress === 100 ? 'completed' : 'in_progress',
					href: `/my-courses/${course.uuid}/learn`,
					thumbnail: course.thumbnail,
					date: course.last_accessed || course.enrolled_at,
					progress: course.progress
				}));
		} else {
			return dashboardData.recent_activities || [];
		}
	}

	function handleActionClick(action) {
		onAction(action.action);
	}

	// Prepare analytics for the charts. Missing data shows an empty state instead of placeholder numbers.
	function processAnalyticsData(analyticsData) {
		const activity = Array.isArray(analyticsData?.activity)
			? analyticsData.activity.filter(
					(a) => a?.created_at && !isNaN(new Date(a.created_at).getTime())
				)
			: [];
		const performance =
			analyticsData?.performance && 'quizzes' in analyticsData.performance
				? analyticsData.performance
				: null;
		return { activity: activity.length ? activity : null, performance };
	}

	let processedAnalytics = $derived(processAnalyticsData(analytics));
</script>

<div class="space-y-6">
	<!-- Stats -->
	<div class="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
		{#each [stats.primary, ...stats.secondary] as stat}
			<StatsCard
				title={stat.title}
				value={stat.value}
				icon={stat.icon}
				trend={stat.trend}
				trendDirection={stat.trendDirection}
			/>
		{/each}
	</div>

	<!-- Charts -->
	<div class="grid gap-6 lg:grid-cols-5">
		<Card class="min-w-0 lg:col-span-3">
			<h2 class="text-base font-semibold text-gray-900 dark:text-white">
				{$t('dashboardHome.activity')}
			</h2>
			<p class="text-sm text-gray-500 dark:text-gray-400">{$t('dashboardHome.activityDesc')}</p>
			<div class="mt-6">
				{#if processedAnalytics?.activity}
					<ActivityChart activities={processedAnalytics.activity} />
				{:else}
					<p class="py-16 text-center text-sm text-gray-500">{$t('dashboardHome.noActivity')}</p>
				{/if}
			</div>
		</Card>
		<Card class="min-w-0 lg:col-span-2">
			<h2 class="text-base font-semibold text-gray-900 dark:text-white">
				{$t('dashboardHome.performance')}
			</h2>
			<p class="text-sm text-gray-500 dark:text-gray-400">{$t('dashboardHome.performanceDesc')}</p>
			<div class="mt-6">
				{#if processedAnalytics?.performance}
					<PerformanceRadar metrics={processedAnalytics.performance} />
				{:else}
					<p class="py-16 text-center text-sm text-gray-500">{$t('dashboardHome.noPerformance')}</p>
				{/if}
			</div>
		</Card>
	</div>

	<div class="grid gap-6 lg:grid-cols-5">
		<!-- Recent / continue learning -->
		<Card padding="none" class="min-w-0 lg:col-span-3">
			<div class="flex items-center justify-between px-5 pt-5 sm:px-6 sm:pt-6">
				<h2 class="text-base font-semibold text-gray-900 dark:text-white">
					{isTeacher(user)
						? $t('dashboardHome.recentCourses')
						: isStudent(user)
							? $t('dashboardHome.continueLearning')
							: $t('dashboardHome.recentActivity')}
				</h2>
				{#if recentItems.length > 0}
					<a
						href={isTeacher(user) ? '/teacher/courses' : '/my-courses'}
						class="text-primary-600 hover:text-primary-700 dark:text-primary-400 text-sm font-medium"
					>
						{$t('dashboardHome.viewAll')}
					</a>
				{/if}
			</div>

			{#if recentItems?.length > 0}
				<ul class="mt-3 divide-y divide-gray-100 pb-2 dark:divide-white/5">
					{#each recentItems as item}
						<li>
							<a
								href={item.href}
								class="flex items-center gap-4 px-5 py-3 transition-colors hover:bg-gray-50 sm:px-6 dark:hover:bg-white/5"
							>
								{#if item.thumbnail}
									<img
										src={item.thumbnail}
										alt=""
										class="size-12 shrink-0 rounded-xl object-cover"
									/>
								{:else}
									<span
										class="bg-primary-50 text-primary-700 dark:bg-primary-400/10 dark:text-primary-300 flex size-12 shrink-0 items-center justify-center rounded-xl text-base font-semibold"
									>
										{item.title?.charAt(0)?.toUpperCase() || '?'}
									</span>
								{/if}
								<span class="min-w-0 flex-1">
									<span
										dir="auto"
										class="block truncate text-sm font-medium text-gray-900 dark:text-white"
									>
										{item.title}
									</span>
									<span class="block truncate text-xs text-gray-500 dark:text-gray-400">
										{item.description}{#if item.date}
											· {formatters.relativeTime(item.date, $locale)}{/if}
									</span>
									{#if item.progress !== undefined && isStudent(user)}
										<span
											class="mt-2 block h-1.5 overflow-hidden rounded-full bg-gray-100 dark:bg-white/10"
										>
											<span
												class="bg-primary-600 dark:bg-primary-400 block h-full rounded-full"
												style="width: {item.progress}%"
											></span>
										</span>
									{/if}
								</span>
								{#if item.status}
									<Badge
										variant={item.status === 'published' || item.status === 'completed'
											? 'success'
											: 'warning'}
										size="small"
										class="hidden capitalize sm:inline-flex"
									>
										{$t(
											{
												completed: 'dashboardHome.completed',
												published: 'dashboardHome.published',
												draft: 'dashboardHome.draft'
											}[item.status] ?? 'dashboardHome.inProgress'
										)}
									</Badge>
								{/if}
							</a>
						</li>
					{/each}
				</ul>
			{:else}
				<div class="p-5 sm:p-6">
					<EmptyState
						title={isTeacher(user)
							? $t('dashboardHome.noCoursesYet')
							: $t('dashboardHome.noEnrolled')}
						description={isTeacher(user)
							? $t('dashboardHome.noCoursesDesc')
							: $t('dashboardHome.noEnrolledDesc')}
					>
						{#snippet actions()}
							{#if isTeacher(user)}
								<Button href="/teacher/courses/create">{$t('dashboardHome.createCourse')}</Button>
							{:else}
								<Button href="/courses">{$t('dashboardHome.browseCoursesLower')}</Button>
							{/if}
						{/snippet}
					</EmptyState>
				</div>
			{/if}
		</Card>

		<!-- Quick actions -->
		<Card class="min-w-0 lg:col-span-2">
			<h2 class="text-base font-semibold text-gray-900 dark:text-white">
				{$t('dashboardHome.quickActions')}
			</h2>
			<div class="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
				{#each quickActions as action}
					<button
						type="button"
						onclick={() => handleActionClick(action)}
						class="group flex items-start gap-3 rounded-xl p-3 text-start ring-1 ring-gray-200/80 transition-colors hover:bg-gray-50 hover:ring-gray-300 dark:ring-white/10 dark:hover:bg-white/5"
					>
						<span
							class="flex size-9 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-base dark:bg-white/10"
							aria-hidden="true"
						>
							{action.icon}
						</span>
						<span class="min-w-0">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>{action.title}</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400"
								>{action.description}</span
							>
						</span>
					</button>
				{/each}
			</div>
		</Card>
	</div>
</div>

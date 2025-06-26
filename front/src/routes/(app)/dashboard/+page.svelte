<!-- front/src/routes/(app)/dashboard/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { coreApi } from '$lib/apis/core.js';
  import { currentUser } from '$lib/stores/auth.store.js';
  import { t } from '$lib/i18n/index.js';
  import StatsCard from '$lib/components/dashboard/StatsCard.svelte';
  import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
  import Card from '$lib/components/common/Card.svelte';
  import Tabs from '$lib/components/common/Tabs.svelte';
  import Button from '$lib/components/common/Button.svelte';

  let dashboardData = $state(null);
  let loading = $state(true);

  onMount(async () => {
    try {
      const response = await coreApi.getDashboard();
      dashboardData = response.data || response;
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      // Set some default data if API fails
      dashboardData = {
        enrolled_courses: 0,
        completed_courses: 0,
        total_study_hours: 0,
        total_certificates: 0,
        in_progress_courses: 0,
        active_courses: [],
        recent_activities: [],
        // Teacher data
        total_courses: 0,
        total_students: 0,
        average_rating: 0,
        active_students: 0,
        course_analytics: []
      };
    } finally {
      loading = false;
    }
  });

  const studentTabs = [
    {
      label: $t('dashboard.overview') || 'Overview',
      content: () => StudentOverview
    },
    {
      label: $t('dashboard.myProgress') || 'My Progress',
      content: () => StudentProgress
    },
    {
      label: $t('dashboard.recentActivity') || 'Recent Activity',
      content: () => RecentActivity
    }
  ];

  const teacherTabs = [
    {
      label: $t('dashboard.overview') || 'Overview',
      content: () => TeacherOverview
    },
    {
      label: $t('course.courses') || 'Courses',
      content: () => TeacherCourses
    },
    {
      label: $t('dashboard.statistics') || 'Statistics',
      content: () => TeacherStats
    }
  ];

  const tabs = $derived($currentUser?.role === 'teacher' ? teacherTabs : studentTabs);
</script>

<svelte:head>
<title>Dashboard - 244SCHOOL</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
<div class="max-w-7xl mx-auto space-y-6">
  <!-- Header -->
  <div>
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      Dashboard
    </h1>
    <p class="mt-1 text-lg text-gray-600 dark:text-gray-400">
      Welcome back, {$currentUser?.first_name || 'Student'}!
    </p>
  </div>

  {#if loading}
    <div class="flex items-center justify-center h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
        <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">Loading...</p>
      </div>
    </div>
  {:else if dashboardData}
    <Tabs {tabs} variant="pills" />
  {/if}
</div>
</div>

{#snippet StudentOverview()}
<!-- Stats Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
  <StatsCard
    title="Total Courses"
    value={dashboardData?.enrolled_courses || 0}
    icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />'
    color="primary"
  />
  <StatsCard
    title="Completed Courses"
    value={dashboardData?.completed_courses || 0}
    icon='<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />'
    color="success"
  />
  <StatsCard
    title="Hours Learned"
    value={dashboardData?.total_study_hours || 0}
    format="duration"
    icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />'
    color="warning"
  />
  <StatsCard
    title="Certificates"
    value={dashboardData?.total_certificates || 0}
    icon='<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />'
    color="info"
  />
</div>

<!-- Continue Learning -->
{#if dashboardData?.in_progress_courses > 0 && dashboardData?.active_courses?.length > 0}
  <Card variant="bordered" class="mb-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      Continue Learning
    </h3>
    <div class="space-y-4">
      {#each dashboardData.active_courses as course}
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
          <div class="flex-1">
            <h4 class="font-medium text-gray-900 dark:text-white">
              {course.title}
            </h4>
            <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-primary-600 h-2 rounded-full" 
                style="width: {course.progress || 0}%"
              ></div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{course.progress || 0}% complete</p>
          </div>
          <Button href={`/courses/${course.uuid}/learn`} variant="primary" size="small">
            Continue
          </Button>
        </div>
      {/each}
    </div>
  </Card>
{/if}

<!-- Welcome Message -->
<Card variant="bordered">
  <div class="text-center py-8">
    <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
      Welcome to 244SCHOOL!
    </h3>
    <p class="text-gray-600 dark:text-gray-400 mb-4">
      Ready to start your learning journey?
    </p>
    <Button href="/courses" variant="primary">
      Browse Courses
    </Button>
  </div>
</Card>
{/snippet}

{#snippet StudentProgress()}
<Card variant="bordered">
  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
    My Progress
  </h3>
  <p class="text-gray-600 dark:text-gray-400">
    Your learning progress will appear here once you start taking courses.
  </p>
</Card>
{/snippet}

{#snippet RecentActivity()}
<Card variant="bordered">
  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
    Recent Activity
  </h3>
  <ActivityFeed activities={dashboardData?.recent_activities || []} />
</Card>
{/snippet}

{#snippet TeacherOverview()}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <StatsCard
    title="Total Courses"
    value={dashboardData?.total_courses || 0}
    icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />'
    color="primary"
  />
  <StatsCard
    title="Total Students"
    value={dashboardData?.total_students || 0}
    icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />'
    color="success"
  />
  <StatsCard
    title="Average Rating"
    value={dashboardData?.average_rating || 0}
    format="number"
    icon='<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />'
    color="warning"
  />
  <StatsCard
    title="Active Students"
    value={dashboardData?.active_students || 0}
    trend={{ value: 12, direction: 'up' }}
    icon='<path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />'
    color="info"
  />
</div>
{/snippet}

{#snippet TeacherCourses()}
<div class="space-y-4">
  {#if dashboardData?.course_analytics?.length > 0}
    {#each dashboardData.course_analytics as course}
      <Card variant="bordered" hoverable>
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
              {course.title}
            </h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {course.enrolled_count} students • {course.completion_rate}% completion rate
            </p>
          </div>
          <Button href={`/teaching/courses/${course.uuid}`} variant="outline">
            Manage Course
          </Button>
        </div>
      </Card>
    {/each}
  {:else}
    <Card variant="bordered">
      <div class="text-center py-8">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No courses yet
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Create your first course to start teaching
        </p>
        <Button href="/courses/create" variant="primary">
          Create Course
        </Button>
      </div>
    </Card>
  {/if}
</div>
{/snippet}

{#snippet TeacherStats()}
<Card variant="bordered">
  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
    Course Performance
  </h3>
  <p class="text-gray-600 dark:text-gray-400">
    Detailed analytics will appear here.
  </p>
</Card>
{/snippet}
<!-- front/src/routes/(app)/my-courses/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { coursesApi } from '$lib/apis/courses.js';
    import { t } from '$lib/i18n/index.js';
    import CourseProgress from '$lib/components/course/CourseProgress.svelte';
    import Card from '$lib/components/common/Card.svelte';
    import Button from '$lib/components/common/Button.svelte';
    import Tabs from '$lib/components/common/Tabs.svelte';
    import Badge from '$lib/components/common/Badge.svelte';
  
    let enrollments = $state([]);
    let loading = $state(true);
    let filter = $state('all');
  
    const tabs = [
      {
        label: 'All Courses',
        content: () => FilteredCourses('all')
      },
      {
        label: 'In Progress',
        content: () => FilteredCourses('in_progress')
      },
      {
        label: 'Completed',
        content: () => FilteredCourses('completed')
      }
    ];
  
    onMount(async () => {
      await fetchEnrollments();
    });
  
    const fetchEnrollments = async () => {
      try {
        const response = await coursesApi.getMyEnrollments();
        enrollments = response.results || response;
      } catch (error) {
        console.error('Failed to fetch enrollments:', error);
      } finally {
        loading = false;
      }
    };
  
    const getFilteredEnrollments = (status) => {
      if (status === 'all') return enrollments;
      return enrollments.filter(e => e.status === status);
    };
  
    const getStatusColor = (status) => {
      const colors = {
        enrolled: 'info',
        in_progress: 'warning',
        completed: 'success',
        dropped: 'danger'
      };
      return colors[status] || 'default';
    };
  </script>
  
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {$t('navigation.myCourses')}
        </h1>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Track your learning progress
        </p>
      </div>
      
      <Button href="/courses" variant="primary">
        Browse More Courses
      </Button>
    </div>
  
    {#if loading}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each Array(6) as _}
          <div class="animate-pulse">
            <div class="bg-gray-200 dark:bg-gray-700 rounded-xl h-48"></div>
            <div class="mt-4 space-y-2">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else if enrollments.length === 0}
      <Card variant="bordered" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No courses yet</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Start your learning journey by enrolling in a course
        </p>
        <div class="mt-6">
          <Button href="/courses" variant="primary">
            Browse Courses
          </Button>
        </div>
      </Card>
    {:else}
      <Tabs {tabs} />
    {/if}
  </div>
  
  {#snippet FilteredCourses(status)}
    {@const filtered = getFilteredEnrollments(status)}
    
    {#if filtered.length === 0}
      <div class="text-center py-12">
        <p class="text-gray-500 dark:text-gray-400">
          No {status === 'all' ? '' : status.replace('_', ' ')} courses
        </p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each filtered as enrollment}
          <Card variant="bordered" hoverable class="flex flex-col">
            <!-- Thumbnail -->
            <div class="relative -m-6 mb-4">
              {#if enrollment.course.thumbnail}
                <img
                  src={enrollment.course.thumbnail}
                  alt={enrollment.course.title}
                  class="w-full h-48 object-cover rounded-t-xl"
                />
              {:else}
                <div class="w-full h-48 bg-gradient-to-br from-primary-400 to-primary-600 rounded-t-xl"></div>
              {/if}
              
              <div class="absolute top-2 right-2">
                <Badge variant={getStatusColor(enrollment.status)}>
                  {enrollment.status.replace('_', ' ')}
                </Badge>
              </div>
            </div>
  
            <!-- Content -->
            <div class="flex-1 flex flex-col">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {enrollment.course.title}
              </h3>
              
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {enrollment.course.instructor_name}
              </p>
  
              <div class="mt-auto space-y-4">
                <CourseProgress progress={enrollment.progress_percentage} />
                
                <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                  <span>Enrolled {new Date(enrollment.enrolled_at).toLocaleDateString()}</span>
                  {#if enrollment.last_accessed}
                    <span>Last accessed {new Date(enrollment.last_accessed).toLocaleDateString()}</span>
                  {/if}
                </div>
  
                <Button
                  href={`/courses/${enrollment.course.uuid}/learn`}
                  variant="primary"
                  fullWidth
                >
                  {enrollment.status === 'completed' ? 'Review Course' : $t('course.continueLearning')}
                </Button>
              </div>
            </div>
          </Card>
        {/each}
      </div>
    {/if}
  {/snippet}
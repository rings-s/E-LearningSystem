<!-- front/src/routes/(app)/courses/[uuid]/+page.svelte -->
<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { coursesApi } from '$lib/apis/courses.js';
  import { currentUser } from '$lib/stores/auth.store.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { formatters } from '$lib/utils/formatters.js';
  import Card from '$lib/components/common/Card.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Badge from '$lib/components/common/Badge.svelte';
  import Tabs from '$lib/components/common/Tabs.svelte';
  import LessonList from '$lib/components/course/LessonList.svelte';

  const courseId = $page.params.uuid;
  let course = $state(null);
  let loading = $state(true);
  let enrolling = $state(false);

  // Define tabs as a derived value based on course state
  const tabs = $derived([
    {
      label: $t('course.overview'),
      content: () => Overview
    },
    {
      label: $t('course.curriculum'),
      content: () => Curriculum
    },
    {
      label: $t('course.instructor'),
      content: () => Instructor
    },
    {
      label: $t('course.reviews'),
      badge: course?.reviews_count,
      content: () => Reviews
    }
  ]);

  onMount(async () => {
    await fetchCourse();
  });

  const fetchCourse = async () => {
    try {
      course = await coursesApi.getCourse(courseId);
    } catch (error) {
      console.error('Failed to fetch course:', error);
      uiStore.showNotification({
        type: 'error',
        title: $t('common.error'),
        message: 'Failed to load course'
      });
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
      course.is_enrolled = true;
      uiStore.showNotification({
        type: 'success',
        title: 'Enrolled Successfully',
        message: `You are now enrolled in ${course.title}`
      });
      goto(`/courses/${courseId}/learn`);
    } catch (error) {
      uiStore.showNotification({
        type: 'error',
        title: $t('common.error'),
        message: error.message || 'Failed to enroll'
      });
    } finally {
      enrolling = false;
    }
  };

  const levelColors = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'danger'
  };
</script>

{#if loading}
  <div class="animate-pulse space-y-6">
    <div class="h-64 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
    <div class="space-y-4">
      <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
      <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
    </div>
  </div>
{:else if course}
  <div class="space-y-6">
    <!-- Hero Section -->
    <div class="relative bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 rounded-2xl overflow-hidden">
      <div class="absolute inset-0 bg-black/20"></div>
      <div class="relative p-8 md:p-12">
        <div class="max-w-4xl">
          <div class="flex flex-wrap items-center gap-3 mb-4">
            <Badge variant={levelColors[course.level]}>
              {$t(`course.${course.level}`)}
            </Badge>
            <Badge variant="default">
              {course.category_name}
            </Badge>
            {#if course.is_featured}
              <Badge variant="accent">Featured</Badge>
            {/if}
          </div>
          
          <h1 class="text-3xl md:text-4xl font-bold text-white mb-4">
            {course.title}
          </h1>
          
          <p class="text-lg text-white/90 mb-6">
            {course.short_description}
          </p>
          
          <div class="flex flex-wrap items-center gap-6 text-white/80">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>{course.instructor.full_name}</span>
            </div>
            
            {#if course.average_rating > 0}
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span>{course.average_rating.toFixed(1)} ({course.reviews_count} reviews)</span>
              </div>
            {/if}
            
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <span>{formatters.number(course.enrolled_count)} students</span>
            </div>
            
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{course.duration_hours} hours</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Card -->
    <Card variant="bordered" class="sticky top-20 float-right ml-6 mb-6 w-full md:w-80">
      <div class="space-y-4">
        {#if course.preview_video}
          <div class="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
            <iframe
              src={course.preview_video}
              title={`${course.title} preview video`}
              class="w-full h-full"
              frameborder="0"
              allowfullscreen
            ></iframe>
          </div>
        {/if}
        
        <div class="text-center">
          {#if course.is_enrolled}
            <Button
              href={`/courses/${courseId}/learn`}
              variant="primary"
              size="large"
              fullWidth
            >
              {$t('course.continueLearning')}
            </Button>
          {:else}
            <Button
              onclick={handleEnroll}
              variant="primary"
              size="large"
              fullWidth
              loading={enrolling}
            >
              {$t('course.enrollNow')}
            </Button>
          {/if}
        </div>
        
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400">Level</span>
            <span class="font-medium text-gray-900 dark:text-white">
              {$t(`course.${course.level}`)}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400">Duration</span>
            <span class="font-medium text-gray-900 dark:text-white">
              {course.duration_hours} hours
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400">Language</span>
            <span class="font-medium text-gray-900 dark:text-white">
              {course.language === 'ar' ? 'العربية' : 'English'}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400">Certificate</span>
            <span class="font-medium text-gray-900 dark:text-white">
              Yes
            </span>
          </div>
        </div>
      </div>
    </Card>

    <!-- Content Tabs -->
    <div class="max-w-4xl">
      <Tabs {tabs} />
    </div>
  </div>
{/if}

{#snippet Overview()}
  <div class="prose prose-gray dark:prose-invert max-w-none">
    <h3>About this course</h3>
    <p>{course.description}</p>
    
    {#if course.learning_outcomes}
      <h3>What you'll learn</h3>
      <ul>
        {#each course.learning_outcomes.split('\n') as outcome}
          <li>{outcome}</li>
        {/each}
      </ul>
    {/if}
    
    {#if course.prerequisites}
      <h3>Prerequisites</h3>
      <p>{course.prerequisites}</p>
    {/if}
  </div>
{/snippet}

{#snippet Curriculum()}
  <div>
    <div class="mb-4 text-sm text-gray-600 dark:text-gray-400">
      {course.modules?.length || 0} modules • {course.total_lessons || 0} lessons
    </div>
    <LessonList 
      modules={course.modules} 
      isEnrolled={course.is_enrolled}
    />
  </div>
{/snippet}

{#snippet Instructor()}
  <Card variant="bordered">
    <div class="flex items-start gap-4">
      {#if course.instructor.avatar}
        <img
          src={course.instructor.avatar}
          alt={course.instructor.full_name}
          class="w-20 h-20 rounded-full object-cover"
        />
      {:else}
        <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-2xl font-medium">
          {course.instructor.full_name?.[0]}
        </div>
      {/if}
      
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          {course.instructor.full_name}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {$t(`auth.${course.instructor.role}`)}
        </p>
        
        {#if course.instructor.bio}
          <p class="mt-3 text-gray-700 dark:text-gray-300">
            {course.instructor.bio}
          </p>
        {/if}
      </div>
    </div>
  </Card>
{/snippet}

{#snippet Reviews()}
  <div class="space-y-4">
    {#if course.reviews?.length > 0}
      {#each course.reviews as review}
        <Card variant="bordered">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              {#if review.student_avatar}
                <img
                  src={review.student_avatar}
                  alt={review.student_name}
                  class="w-10 h-10 rounded-full object-cover"
                />
              {:else}
                <div class="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                  <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              {/if}
            </div>
            
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <h4 class="font-medium text-gray-900 dark:text-white">
                  {review.student_name}
                </h4>
                <div class="flex items-center gap-1">
                  {#each Array(5) as _, i}
                    <svg 
                      class="w-4 h-4 {i < review.rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}" 
                      fill="currentColor" 
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  {/each}
                </div>
              </div>
              
              <p class="mt-2 text-gray-700 dark:text-gray-300">
                {review.comment}
              </p>
              
              <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {formatters.date(review.created_at)}
              </p>
            </div>
          </div>
        </Card>
      {/each}
    {:else}
      <div class="text-center py-8">
        <p class="text-gray-500 dark:text-gray-400">No reviews yet</p>
      </div>
    {/if}
  </div>
{/snippet}
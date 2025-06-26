<!-- front/src/routes/(app)/courses/[uuid]/learn/+page.svelte -->
<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { coursesApi } from '$lib/apis/courses.js';
  import { currentUser } from '$lib/stores/auth.store.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import LessonList from '$lib/components/course/LessonList.svelte';
  import VideoPlayer from '$lib/components/course/VideoPlayer.svelte';
  import LessonContent from '$lib/components/course/LessonContent.svelte';
  import CourseProgress from '$lib/components/course/CourseProgress.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Tabs from '$lib/components/common/Tabs.svelte';

  const courseId = $page.params.uuid;
  
  let course = $state(null);
  let enrollment = $state(null);
  let currentLesson = $state(null);
  let loading = $state(true);
  let completingLesson = $state(false);

  // Derive navigation lessons
  let previousLesson = $derived(() => {
    if (!course?.modules || !currentLesson) return null;
    let prev = null;
    for (const module of course.modules) {
      for (const lesson of module.lessons) {
        if (lesson.uuid === currentLesson.uuid) {
          return prev;
        }
        prev = lesson;
      }
    }
    return null;
  });

  let nextLesson = $derived(() => {
    if (!course?.modules || !currentLesson) return null;
    let foundCurrent = false;
    for (const module of course.modules) {
      for (const lesson of module.lessons) {
        if (foundCurrent && !lesson.is_completed) {
          return lesson;
        }
        if (lesson.uuid === currentLesson.uuid) {
          foundCurrent = true;
        }
      }
    }
    return null;
  });

  const lessonTabs = [
    {
      label: 'Overview',
      content: () => LessonOverview
    },
    {
      label: 'Resources',
      content: () => LessonResources
    },
    {
      label: 'Discussion',
      content: () => LessonDiscussion
    }
  ];

  onMount(async () => {
    await fetchCourse();
    await fetchEnrollment();
  });

  const fetchCourse = async () => {
    try {
      course = await coursesApi.getCourse(courseId);
      
      // Find first incomplete lesson
      if (course.modules?.length > 0) {
        for (const module of course.modules) {
          for (const lesson of module.lessons) {
            if (!lesson.is_completed) {
              await loadLesson(lesson);
              return;
            }
          }
        }
        // All lessons completed, load first lesson
        if (course.modules[0]?.lessons[0]) {
          await loadLesson(course.modules[0].lessons[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch course:', error);
      goto('/my-courses');
    } finally {
      loading = false;
    }
  };

  const fetchEnrollment = async () => {
    try {
      const enrollments = await coursesApi.getMyEnrollments();
      enrollment = enrollments.find(e => e.course.uuid === courseId);
    } catch (error) {
      console.error('Failed to fetch enrollment:', error);
    }
  };

  const loadLesson = async (lesson) => {
    try {
      currentLesson = await coursesApi.getLesson(lesson.uuid);
    } catch (error) {
      console.error('Failed to load lesson:', error);
    }
  };

  const completeLesson = async () => {
    if (!currentLesson || currentLesson.is_completed) return;

    completingLesson = true;
    try {
      await coursesApi.completeLesson(currentLesson.uuid);
      currentLesson.is_completed = true;
      
      // Update enrollment progress
      if (enrollment) {
        enrollment.progress_percentage = Math.min(100, enrollment.progress_percentage + (100 / course.total_lessons));
      }

      uiStore.showNotification({
        type: 'success',
        title: 'Lesson Completed!',
        message: 'Great job! Keep up the good work.'
      });

      // Auto-load next lesson if available
      if (nextLesson()) {
        await loadLesson(nextLesson());
      } else {
        // Course completed
        uiStore.showNotification({
          type: 'success',
          title: 'Course Completed!',
          message: 'Congratulations! You have completed all lessons.'
        });
      }
    } catch (error) {
      uiStore.showNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to complete lesson'
      });
    } finally {
      completingLesson = false;
    }
  };
</script>

{#if loading}
  <div class="flex items-center justify-center h-screen">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
      <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">Loading course...</p>
    </div>
  </div>
{:else if course && currentLesson}
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <a href={`/courses/${courseId}`} class="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to course
        </a>
        <h2 class="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
          {course.title}
        </h2>
        <div class="mt-3">
          <CourseProgress progress={enrollment?.progress_percentage || 0} />
        </div>
      </div>
      
      <div class="p-4">
        <LessonList
          modules={course.modules}
          currentLessonId={currentLesson.uuid}
          onLessonClick={loadLesson}
          isEnrolled={true}
        />
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <!-- Lesson Header -->
      <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-semibold text-gray-900 dark:text-white">
              {currentLesson.title}
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {currentLesson.module.title}
            </p>
          </div>
          
          <div class="flex items-center gap-3">
            {#if currentLesson.is_completed}
              <span class="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-sm font-medium rounded-full">
                Completed
              </span>
            {:else}
              <Button
                variant="primary"
                onclick={completeLesson}
                loading={completingLesson}
              >
                {$t('course.markComplete')}
              </Button>
            {/if}
          </div>
        </div>
      </header>

      <!-- Lesson Content -->
      <div class="flex-1 overflow-y-auto">
        <div class="max-w-5xl mx-auto px-6 py-8">
          {#if currentLesson.content_type === 'video'}
            <VideoPlayer 
              url={currentLesson.video_url}
              duration={currentLesson.video_duration}
              onComplete={completeLesson}
            />
          {:else}
            <LessonContent lesson={currentLesson} />
          {/if}

          <!-- Tabs -->
          <div class="mt-8">
            <Tabs tabs={lessonTabs} />
          </div>

          <!-- Navigation -->
          <div class="mt-8 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 pt-6">
            <Button
              variant="outline"
              onclick={() => previousLesson() && loadLesson(previousLesson())}
              disabled={!previousLesson()}
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Previous Lesson
            </Button>
            
            <Button
              variant="primary"
              onclick={() => nextLesson() && loadLesson(nextLesson())}
              disabled={!nextLesson()}
            >
              Next Lesson
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </Button>
          </div>
        </div>
      </div>
    </main>
  </div>
{/if}

{#snippet LessonOverview()}
  <div class="prose prose-gray dark:prose-invert max-w-none">
    {#if currentLesson.description}
      <h3>Lesson Overview</h3>
      <p>{currentLesson.description}</p>
    {/if}
    
    {#if currentLesson.text_content}
      {@html currentLesson.text_content}
    {/if}
  </div>
{/snippet}

{#snippet LessonResources()}
  <div class="space-y-4">
    {#if currentLesson.resources?.length > 0}
      {#each currentLesson.resources as resource}
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
              {#if resource.resource_type === 'document'}
                <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              {:else if resource.resource_type === 'link'}
                <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              {:else}
                <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              {/if}
            </div>
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white">
                {resource.title}
              </h4>
              {#if resource.description}
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {resource.description}
                </p>
              {/if}
            </div>
          </div>
          
          <Button
            href={resource.url || resource.file}
            variant="outline"
            size="small"
            target="_blank"
          >
            {resource.resource_type === 'link' ? 'Open' : 'Download'}
          </Button>
        </div>
      {/each}
    {:else}
      <p class="text-center text-gray-500 dark:text-gray-400 py-8">
        No resources available for this lesson
      </p>
    {/if}
  </div>
{/snippet}

{#snippet LessonDiscussion()}
  <div class="space-y-4">
    <Button variant="primary" href={`/forum/lesson/${currentLesson.uuid}`}>
      View Lesson Discussion
    </Button>
  </div>
{/snippet}
<!-- front/src/lib/components/course/LessonContent.svelte -->
<script>
    import { onMount } from 'svelte';
    import { courseStore } from '$lib/stores/course.store.js';
    import { classNames } from '$lib/utils/helpers.js';
    import VideoPlayer from './VideoPlayer.svelte';
    import Button from '$lib/components/common/Button.svelte';
    import Card from '$lib/components/common/Card.svelte';
    import Badge from '$lib/components/common/Badge.svelte';
    import { formatters } from '$lib/utils/formatters.js';
  
    let {
      lesson = null,
      enrollment = null,
      onComplete = () => {},
      onNext = () => {},
      onPrevious = () => {},
      hasNext = false,
      hasPrevious = false
    } = $props();
  
    let isCompleted = $state(false);
    let notes = $state('');
    let showNotes = $state(false);
  
    onMount(() => {
      // Start learning session
      courseStore.startLearningSession(lesson.module.course.uuid, lesson.uuid);
      
      // Check if already completed
      isCompleted = lesson.is_completed || false;
    });
  
    async function handleComplete() {
      const result = await courseStore.completeLesson(lesson.uuid);
      if (result.success) {
        isCompleted = true;
        if (hasNext) {
          setTimeout(() => onNext(), 1000);
        }
      }
    }
  
    function handleVideoProgress(data) {
      courseStore.updateLessonProgress(lesson.uuid, {
        lastPosition: data.currentTime,
        percentComplete: data.progress
      });
    }
  
    function saveNotes() {
      courseStore.addNote({
        lessonId: lesson.uuid,
        content: notes,
        timestamp: videoElement?.currentTime || 0
      });
      notes = '';
    }
  </script>
  
  <div class="lesson-content space-y-6">
    <!-- Lesson Header -->
    <div class="flex items-center justify-between">
      <div>
        <div class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
          <span>{lesson.module.title}</span>
          <span>/</span>
          <span>Lesson {lesson.order}</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {lesson.title}
        </h1>
      </div>
      
      <div class="flex items-center space-x-4">
        {#if isCompleted}
          <Badge variant="success">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Completed
          </Badge>
        {/if}
        
        <Badge variant="info">
          {formatters.duration(lesson.estimated_time_minutes * 60)}
        </Badge>
      </div>
    </div>
  
    <!-- Content Area -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        {#if lesson.content_type === 'video' && lesson.video_url}
          <Card padding="none" variant="bordered">
            <VideoPlayer
              url={lesson.video_url}
              duration={lesson.video_duration}
              onComplete={handleComplete}
              onProgress={handleVideoProgress}
            />
          </Card>
        {:else if lesson.content_type === 'text'}
          <Card>
            <div class="prose prose-lg dark:prose-invert max-w-none">
              {@html lesson.text_content}
            </div>
          </Card>
        {:else if lesson.content_type === 'pdf' && lesson.file_attachment}
          <Card padding="none" variant="bordered">
            <iframe
              src={lesson.file_attachment}
              title={lesson.title}
              class="w-full h-[600px]"
              frameborder="0"
            />
          </Card>
        {:else if lesson.content_type === 'slides'}
          <Card>
            <p class="text-gray-500 dark:text-gray-400">
              Slides viewer not implemented yet
            </p>
          </Card>
        {/if}
  
        <!-- Description -->
        {#if lesson.description}
          <Card>
            <h3 class="text-lg font-semibold mb-3">About this lesson</h3>
            <p class="text-gray-600 dark:text-gray-400">
              {lesson.description}
            </p>
          </Card>
        {/if}
  
        <!-- Resources -->
        {#if lesson.resources?.length > 0}
          <Card>
            <h3 class="text-lg font-semibold mb-4">Resources</h3>
            <div class="space-y-3">
              {#each lesson.resources as resource}
                <a
                  href={resource.file || resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <div class="flex items-center space-x-3">
                    <div class="p-2 bg-primary-100 dark:bg-primary-900/30 rounded">
                      <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p class="font-medium text-gray-900 dark:text-white">
                        {resource.title}
                      </p>
                      {#if resource.description}
                        <p class="text-sm text-gray-500 dark:text-gray-400">
                          {resource.description}
                        </p>
                      {/if}
                    </div>
                  </div>
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              {/each}
            </div>
          </Card>
        {/if}
      </div>
  
      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Progress Card -->
        <Card>
          <h3 class="text-lg font-semibold mb-4">Your Progress</h3>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-sm mb-2">
                <span class="text-gray-600 dark:text-gray-400">Course Progress</span>
                <span class="font-medium">{enrollment?.progress_percentage || 0}%</span>
              </div>
              <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-primary-500 rounded-full transition-all duration-300"
                  style="width: {enrollment?.progress_percentage || 0}%"
                />
              </div>
            </div>
            
            {#if !isCompleted}
              <Button 
                onclick={handleComplete}
                variant="primary"
                fullWidth
              >
                Mark as Complete
              </Button>
            {/if}
          </div>
        </Card>
  
        <!-- Notes -->
        <Card>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold">Notes</h3>
            <button
              onclick={() => showNotes = !showNotes}
              class="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
            >
              {showNotes ? 'Hide' : 'Show'}
            </button>
          </div>
          
          {#if showNotes}
            <div class="space-y-3">
              <textarea
                bind:value={notes}
                placeholder="Take notes here..."
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                rows="4"
              />
              <Button 
                onclick={saveNotes}
                variant="outline"
                size="small"
                fullWidth
                disabled={!notes.trim()}
              >
                Save Note
              </Button>
            </div>
          {/if}
        </Card>
  
        <!-- Navigation -->
        <Card>
          <h3 class="text-lg font-semibold mb-4">Navigation</h3>
          <div class="space-y-2">
            <Button
              onclick={onPrevious}
              variant="outline"
              fullWidth
              disabled={!hasPrevious}
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Previous Lesson
            </Button>
            
            <Button
              onclick={onNext}
              variant="primary"
              fullWidth
              disabled={!hasNext}
            >
              Next Lesson
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </Button>
          </div>
        </Card>
      </div>
    </div>
</div>
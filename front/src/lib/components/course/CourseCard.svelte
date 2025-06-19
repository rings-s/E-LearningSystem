<!-- front/src/lib/components/course/CourseCard.svelte -->
<script>
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n/index.js';
    import { formatters } from '$lib/utils/formatters.js';
    import Card from '../common/Card.svelte';
    import Badge from '../common/Badge.svelte';
  
    let { course } = $props();
  
    const handleClick = () => {
      goto(`/courses/${course.uuid}`);
    };
  
    const levelColors = {
      beginner: 'success',
      intermediate: 'warning',
      advanced: 'danger'
    };
  </script>
  
  <Card variant="bordered" hoverable onclick={handleClick} class="h-full flex flex-col">
    <!-- Thumbnail -->
    <div class="relative -m-6 mb-4">
      {#if course.thumbnail}
        <img
          src={course.thumbnail}
          alt={course.title}
          class="w-full h-48 object-cover rounded-t-xl"
        />
      {:else}
        <div class="w-full h-48 bg-gradient-to-br from-primary-400 to-primary-600 rounded-t-xl flex items-center justify-center">
          <svg class="w-16 h-16 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
      {/if}
      
      {#if course.is_featured}
        <div class="absolute top-2 right-2">
          <Badge variant="accent">Featured</Badge>
        </div>
      {/if}
    </div>
  
    <!-- Content -->
    <div class="flex-1 flex flex-col">
      <div class="flex items-start justify-between gap-2 mb-2">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white line-clamp-2">
          {course.title}
        </h3>
        <Badge variant={levelColors[course.level]} size="small">
          {$t(`course.${course.level}`)}
        </Badge>
      </div>
  
      <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-4">
        {course.short_description}
      </p>
  
      <!-- Instructor -->
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
          <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <span class="text-sm text-gray-700 dark:text-gray-300">
          {course.instructor_name}
        </span>
      </div>
  
      <!-- Stats -->
      <div class="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-4">
            <span class="flex items-center gap-1 text-gray-500 dark:text-gray-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {course.duration_hours}h
            </span>
            <span class="flex items-center gap-1 text-gray-500 dark:text-gray-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              {formatters.number(course.enrolled_count)}
            </span>
          </div>
          
          {#if course.average_rating > 0}
            <div class="flex items-center gap-1">
              <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span class="text-gray-700 dark:text-gray-300 font-medium">
                {course.average_rating.toFixed(1)}
              </span>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </Card>
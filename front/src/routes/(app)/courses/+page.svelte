<!-- front/src/routes/(app)/courses/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { coursesApi } from '$lib/apis/courses.js';
    import { t } from '$lib/i18n/index.js';
    import { debounce } from '$lib/utils/helpers.js';
    import CourseCard from '$lib/components/course/CourseCard.svelte';
    import Input from '$lib/components/common/Input.svelte';
    import Select from '$lib/components/common/Select.svelte';
    import Button from '$lib/components/common/Button.svelte';
    import Tabs from '$lib/components/common/Tabs.svelte';
  
    let courses = $state([]);
    let loading = $state(true);
    let filters = $state({
      search: '',
      category: '',
      level: '',
      language: ''
    });
  
    let categories = $state([]);
    let totalPages = $state(1);
    let currentPage = $state(1);
  
    const levelOptions = [
      { value: '', label: $t('common.all') },
      { value: 'beginner', label: $t('course.beginner') },
      { value: 'intermediate', label: $t('course.intermediate') },
      { value: 'advanced', label: $t('course.advanced') }
    ];
  
    const tabs = [
      {
        label: $t('course.allCourses'),
        content: () => AllCourses
      },
      {
        label: $t('course.featuredCourses'),
        content: () => FeaturedCourses
      },
      {
        label: $t('course.newCourses'),
        content: () => NewCourses
      }
    ];
  
    onMount(async () => {
      await fetchCourses();
      await fetchCategories();
    });
  
    const fetchCourses = async (page = 1) => {
      loading = true;
      try {
        const params = {
          page,
          ...Object.fromEntries(
            Object.entries(filters).filter(([_, value]) => value)
          )
        };
        
        const response = await coursesApi.getCourses(params);
        courses = response.results || response;
        totalPages = Math.ceil((response.count || courses.length) / 20);
        currentPage = page;
      } catch (error) {
        console.error('Failed to fetch courses:', error);
      } finally {
        loading = false;
      }
    };
  
    const fetchCategories = async () => {
      try {
        const response = await coursesApi.getCategories();
        categories = response.results || response;
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };
  
    const debouncedSearch = debounce(() => fetchCourses(), 500);
  
    $effect(() => {
      if (filters.search !== undefined) {
        debouncedSearch();
      }
    });
  </script>
  
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {$t('navigation.courses')}
        </h1>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Explore our wide range of courses
        </p>
      </div>
    </div>
  
    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Input
          type="search"
          placeholder={$t('common.search')}
          bind:value={filters.search}
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />'
        />
        
        <Select
          bind:value={filters.category}
          options={[
            { value: '', label: 'All Categories' },
            ...categories.map(cat => ({ value: cat.slug, label: cat.name }))
          ]}
        />
        
        <Select
          bind:value={filters.level}
          options={levelOptions}
        />
        
        <Button
          variant="outline"
          onclick={() => {
            filters = { search: '', category: '', level: '', language: '' };
            fetchCourses();
          }}
        >
          Clear Filters
        </Button>
      </div>
    </div>
  
    <!-- Tabs -->
    <Tabs {tabs} />
  </div>
  
  {#snippet AllCourses()}
    {#if loading}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {#each Array(8) as _}
          <div class="animate-pulse">
            <div class="bg-gray-200 dark:bg-gray-700 rounded-xl h-48"></div>
            <div class="mt-4 space-y-2">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else if courses.length === 0}
      <div class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No courses found</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Try adjusting your filters or search terms
        </p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {#each courses as course}
          <CourseCard {course} />
        {/each}
      </div>
  
      <!-- Pagination -->
      {#if totalPages > 1}
        <div class="mt-8 flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="small"
            disabled={currentPage === 1}
            onclick={() => fetchCourses(currentPage - 1)}
          >
            Previous
          </Button>
          
          <span class="text-sm text-gray-700 dark:text-gray-300">
            Page {currentPage} of {totalPages}
          </span>
          
          <Button
            variant="outline"
            size="small"
            disabled={currentPage === totalPages}
            onclick={() => fetchCourses(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      {/if}
    {/if}
  {/snippet}
  
  {#snippet FeaturedCourses()}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {#each courses.filter(c => c.is_featured) as course}
        <CourseCard {course} />
      {/each}
    </div>
  {/snippet}
  
  {#snippet NewCourses()}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {#each courses.slice(0, 8) as course}
        <CourseCard {course} />
      {/each}
    </div>
  {/snippet}
<!-- front/src/routes/(app)/courses/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { coursesApi } from '$lib/apis/courses.js';
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
  let error = $state('');
  let debugInfo = $state(''); // Add debug info

  const levelOptions = [
    { value: '', label: 'All Levels' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' }
  ];

  const tabs = [
    {
      label: 'All Courses',
      content: () => AllCourses
    },
    {
      label: 'Featured Courses',
      content: () => FeaturedCourses
    },
    {
      label: 'New Courses',
      content: () => NewCourses
    }
  ];

  onMount(async () => {
    await Promise.all([
      fetchCourses(),
      fetchCategories()
    ]);
  });

  const fetchCourses = async (page = 1) => {
    loading = true;
    error = '';
    debugInfo = '';
    
    try {
      const params = {
        page,
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, value]) => value)
        )
      };
      
      console.log('Fetching courses with params:', params);
      const response = await coursesApi.getCourses(params);
      console.log('Raw API response:', response);
      
      // Handle both paginated and non-paginated responses
      if (response.results) {
        courses = response.results;
        totalPages = Math.ceil(response.count / 20);
        debugInfo = `Paginated: ${response.results.length} courses, ${response.count} total`;
      } else if (Array.isArray(response)) {
        courses = response;
        totalPages = 1;
        debugInfo = `Array: ${response.length} courses`;
      } else {
        courses = [];
        totalPages = 1;
        debugInfo = `Unknown response format: ${typeof response}`;
      }
      
      console.log('Processed courses:', courses);
      currentPage = page;
    } catch (err) {
      console.error('Failed to fetch courses:', err);
      error = `Failed to load courses: ${err.message}`;
      courses = [];
      debugInfo = `Error: ${err.message}`;
    } finally {
      loading = false;
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await coursesApi.getCategories();
      console.log('Categories response:', response);
      categories = response.results || response || [];
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };

  const debouncedSearch = debounce(() => fetchCourses(), 500);

  // Watch for filter changes
  $effect(() => {
    if (filters.search !== undefined) {
      debouncedSearch();
    }
  });

  const clearFilters = () => {
    filters = { search: '', category: '', level: '', language: '' };
    fetchCourses(1);
  };

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      fetchCourses(page);
    }
  };
</script>

<div class="container mx-auto px-4 py-8 space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        Courses
      </h1>
      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
        Explore our wide range of courses
      </p>
    </div>
  </div>

  <!-- Debug Info (remove this after debugging) -->
  {#if debugInfo}
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <p class="text-sm text-blue-700 dark:text-blue-200">Debug: {debugInfo}</p>
      <p class="text-xs text-blue-600 dark:text-blue-300 mt-1">
        Courses array length: {courses.length} | Loading: {loading}
      </p>
    </div>
  {/if}

  <!-- Filters -->
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Input
        type="search"
        placeholder="Search courses..."
        bind:value={filters.search}
        icon='<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />'
      />
      
      <Select
        bind:value={filters.category}
        options={[
          { value: '', label: 'All Categories' },
          ...categories.map(cat => ({ value: cat.uuid, label: cat.name }))
        ]}
        placeholder="Select category"
      />
      
      <Select
        bind:value={filters.level}
        options={levelOptions}
        placeholder="Select level"
      />
      
      <Button
        variant="outline"
        onclick={clearFilters}
      >
        Clear Filters
      </Button>
    </div>
  </div>

  <!-- Error Message -->
  {#if error}
    <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex">
        <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="ml-3 text-sm text-red-700 dark:text-red-200">{error}</p>
      </div>
    </div>
  {/if}

  <!-- Content -->
  <div class="space-y-6">
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
            onclick={() => goToPage(currentPage - 1)}
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
            onclick={() => goToPage(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      {/if}
    {/if}
  </div>
</div>
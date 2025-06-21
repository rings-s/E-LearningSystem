<!-- front/src/routes/courses/create/+page.svelte -->
<script>
    import { goto } from '$app/navigation';
    import { coursesApi } from '$lib/apis/courses.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import Card from '$lib/components/common/Card.svelte';
    import Button from '$lib/components/common/Button.svelte';
    import Input from '$lib/components/common/Input.svelte';
    import Badge from '$lib/components/common/Badge.svelte';
  
    let currentStep = $state(1);
    let saving = $state(false);
    
    let courseData = $state({
      // Basic Info
      title: '',
      slug: '',
      short_description: '',
      description: '',
      
      // Category & Tags
      category: '',
      tags: [],
      
      // Settings
      level: 'beginner',
      language: 'en',
      duration_hours: 1,
      
      // Requirements
      prerequisites: '',
      learning_outcomes: '',
      
      // Pricing & Access
      enrollment_limit: null,
      
      // Status
      status: 'draft',
      is_featured: false
    });
  
    let categories = $state([]);
    let tagInput = $state('');
    
    $effect(() => {
      fetchCategories();
    });
  
    async function fetchCategories() {
      try {
        const response = await coursesApi.getCategories();
        categories = response.results || response;
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    }
  
    $effect(() => {
      if (courseData.title) {
        courseData.slug = courseData.title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/(^-|-$)/g, '');
      }
    });
  
    function addTag() {
      if (tagInput && !courseData.tags.includes(tagInput)) {
        courseData.tags = [...courseData.tags, tagInput];
        tagInput = '';
      }
    }
  
    function removeTag(tag) {
      courseData.tags = courseData.tags.filter(t => t !== tag);
    }
  
    async function saveCourse() {
      if (!validateStep(currentStep)) return;
  
      saving = true;
      try {
        const response = await coursesApi.createCourse({
          ...courseData,
          tags: courseData.tags.map(tag => ({ name: tag, slug: tag.toLowerCase() }))
        });
        
        uiStore.showNotification({
          type: 'success',
          title: 'Course Created',
          message: 'Your course has been created successfully!'
        });
        
        goto(`/courses/${response.uuid}/manage`);
      } catch (error) {
        uiStore.showNotification({
          type: 'error',
          title: 'Error',
          message: error.message || 'Failed to create course'
        });
      } finally {
        saving = false;
      }
    }
  
    function validateStep(step) {
      switch(step) {
        case 1:
          if (!courseData.title || !courseData.short_description || !courseData.description) {
            uiStore.showNotification({
              type: 'error',
              title: 'Validation Error',
              message: 'Please fill in all required fields'
            });
            return false;
          }
          break;
        case 2:
          if (!courseData.category) {
            uiStore.showNotification({
              type: 'error',
              title: 'Validation Error',
              message: 'Please select a category'
            });
            return false;
          }
          break;
        case 3:
          if (!courseData.learning_outcomes) {
            uiStore.showNotification({
              type: 'error',
              title: 'Validation Error',
              message: 'Please add learning outcomes'
            });
            return false;
          }
          break;
      }
      return true;
    }
  
    function nextStep() {
      if (validateStep(currentStep)) {
        currentStep = Math.min(currentStep + 1, 4);
      }
    }
  
    function previousStep() {
      currentStep = Math.max(currentStep - 1, 1);
    }
  
    const steps = [
      { number: 1, title: 'Basic Information', icon: '📝' },
      { number: 2, title: 'Category & Settings', icon: '⚙️' },
      { number: 3, title: 'Learning Outcomes', icon: '🎯' },
      { number: 4, title: 'Review & Publish', icon: '✅' }
    ];
  </script>
  
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Create New Course
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Share your knowledge and create an engaging learning experience
      </p>
    </div>
  
    <!-- Progress Steps -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        {#each steps as step, index}
          <div class="flex-1 relative">
            <div class="flex items-center">
              <div class="relative z-10 w-12 h-12 rounded-full flex items-center justify-center {
                currentStep >= step.number 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
              }">
                <span class="text-lg">{step.icon}</span>
              </div>
              {#if index < steps.length - 1}
                <div class="flex-1 h-1 mx-2 {
                  currentStep > step.number 
                    ? 'bg-primary-600' 
                    : 'bg-gray-200 dark:bg-gray-700'
                }"></div>
              {/if}
            </div>
            <p class="mt-2 text-xs text-center {
              currentStep >= step.number 
                ? 'text-gray-900 dark:text-white font-medium' 
                : 'text-gray-500 dark:text-gray-400'
            }">
              {step.title}
            </p>
          </div>
        {/each}
      </div>
    </div>
  
    <!-- Form Content -->
    <Card variant="bordered" class="mb-8">
      {#if currentStep === 1}
        <!-- Step 1: Basic Information -->
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Basic Information
          </h2>
          
          <Input
            label="Course Title"
            bind:value={courseData.title}
            required
            placeholder="e.g., Complete Web Development Bootcamp"
            helperText="Choose a clear, descriptive title for your course"
          />
  
          <Input
            label="URL Slug"
            bind:value={courseData.slug}
            required
            placeholder="complete-web-development-bootcamp"
            helperText="This will be used in the course URL"
          />
  
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Short Description
            </label>
            <textarea
              bind:value={courseData.short_description}
              required
              rows="2"
              maxlength="255"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="A brief description that appears in course listings"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {courseData.short_description.length}/255 characters
            </p>
          </div>
  
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Full Description
            </label>
            <textarea
              bind:value={courseData.description}
              required
              rows="8"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Provide a detailed description of what students will learn"
            ></textarea>
          </div>
        </div>
      {:else if currentStep === 2}
        <!-- Step 2: Category & Settings -->
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Category & Settings
          </h2>
  
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Category
            </label>
            <select
              bind:value={courseData.category}
              required
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select a category</option>
              {#each categories as category}
                <option value={category.uuid}>{category.name}</option>
              {/each}
            </select>
          </div>
  
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tags
            </label>
            <div class="flex gap-2 mb-2">
              <input
                bind:value={tagInput}
                onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                placeholder="Add tags (press Enter)"
                class="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <Button type="button" onclick={addTag} variant="outline" size="small">
                Add
              </Button>
            </div>
            <div class="flex flex-wrap gap-2">
              {#each courseData.tags as tag}
                <Badge variant="info">
                  {tag}
                  <button
                    type="button"
                    onclick={() => removeTag(tag)}
                    class="ml-1 text-current hover:text-red-500"
                  >
                    ×
                  </button>
                </Badge>
              {/each}
            </div>
          </div>
  
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Level
              </label>
              <select
                bind:value={courseData.level}
                class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
  
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Language
              </label>
              <select
                bind:value={courseData.language}
                class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="en">English</option>
                <option value="ar">Arabic</option>
              </select>
            </div>
  
            <Input
              type="number"
              label="Duration (hours)"
              bind:value={courseData.duration_hours}
              min="1"
              required
            />
          </div>
  
          <Input
            type="number"
            label="Enrollment Limit (optional)"
            bind:value={courseData.enrollment_limit}
            placeholder="Leave empty for unlimited"
            helperText="Maximum number of students who can enroll"
          />
        </div>
      {:else if currentStep === 3}
        <!-- Step 3: Learning Outcomes -->
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Learning Outcomes
          </h2>
  
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Prerequisites
            </label>
            <textarea
              bind:value={courseData.prerequisites}
              rows="4"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="What should students know before taking this course? (optional)"
            ></textarea>
          </div>
  
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Learning Outcomes
            </label>
            <textarea
              bind:value={courseData.learning_outcomes}
              required
              rows="6"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="What will students be able to do after completing this course? (one per line)"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              List specific skills and knowledge students will gain
            </p>
          </div>
        </div>
      {:else if currentStep === 4}
        <!-- Step 4: Review & Publish -->
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Review & Publish
          </h2>
  
          <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-6 space-y-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Course Summary</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500 dark:text-gray-400">Title:</span>
                <p class="font-medium text-gray-900 dark:text-white">{courseData.title}</p>
              </div>
              
              <div>
                <span class="text-gray-500 dark:text-gray-400">Level:</span>
                <p class="font-medium text-gray-900 dark:text-white capitalize">{courseData.level}</p>
              </div>
              
              <div>
                <span class="text-gray-500 dark:text-gray-400">Duration:</span>
                <p class="font-medium text-gray-900 dark:text-white">{courseData.duration_hours} hours</p>
              </div>
              
              <div>
                <span class="text-gray-500 dark:text-gray-400">Language:</span>
                <p class="font-medium text-gray-900 dark:text-white">{courseData.language === 'en' ? 'English' : 'Arabic'}</p>
              </div>
            </div>
  
            <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
              <span class="text-gray-500 dark:text-gray-400 text-sm">Description:</span>
              <p class="mt-1 text-gray-900 dark:text-white">{courseData.short_description}</p>
            </div>
          </div>
  
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <p class="text-sm text-blue-800 dark:text-blue-200">
              <strong>Note:</strong> Your course will be created as a draft. You can add modules and lessons after creation, then publish when ready.
            </p>
          </div>
        </div>
      {/if}
    </Card>
  
    <!-- Navigation Buttons -->
    <div class="flex justify-between">
      <Button
        variant="outline"
        onclick={previousStep}
        disabled={currentStep === 1}
      >
        Previous
      </Button>
      
      {#if currentStep < 4}
        <Button variant="primary" onclick={nextStep}>
          Next
        </Button>
      {:else}
        <Button
          variant="primary"
          onclick={saveCourse}
          loading={saving}
        >
          Create Course
        </Button>
      {/if}
    </div>
  </div>
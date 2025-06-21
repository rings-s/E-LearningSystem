<!-- front/src/lib/components/auth/AuthCard.svelte -->
<script>
    import { fade } from 'svelte/transition';
    
    let {
      title = '',
      subtitle = '',
      children,
      footer = null
    } = $props();
  </script>
  
  <div class="space-y-8">
    <!-- Header -->
    {#if title || subtitle}
      <div class="text-center space-y-2" in:fade={{ delay: 100, duration: 400 }}>
        {#if title}
          <h1 class="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            {title}
          </h1>
        {/if}
        {#if subtitle}
          <p class="text-gray-600 dark:text-gray-400">
            {subtitle}
          </p>
        {/if}
      </div>
    {/if}
  
    <!-- Main Card -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl shadow-gray-200/50 dark:shadow-gray-900/50 p-8 space-y-6 border border-gray-100 dark:border-gray-700"
         in:fade={{ delay: 200, duration: 400 }}>
      {@render children()}
    </div>
  
    <!-- Footer -->
    {#if footer}
      <div class="text-center text-sm text-gray-600 dark:text-gray-400"
           in:fade={{ delay: 300, duration: 400 }}>
        {@render footer()}
      </div>
    {/if}
  </div>
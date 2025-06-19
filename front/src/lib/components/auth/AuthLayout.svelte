<!-- front/src/lib/components/auth/AuthLayout.svelte -->
<script>
    import { t } from '$lib/i18n/index.js';
    import Card from '../common/Card.svelte';
  
    let { 
      title = '',
      subtitle = '',
      showLogo = true,
      class: className = ''
    } = $props();
  </script>
  
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-md w-full space-y-8 {className}">
      {#if showLogo}
        <div class="text-center">
          <a href="/" class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl text-white text-2xl font-bold mb-4 hover:shadow-lg transition-shadow">
            E
          </a>
          <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
            {title}
          </h2>
          {#if subtitle}
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {@html subtitle}
            </p>
          {/if}
        </div>
      {/if}
  
      <Card variant="bordered" padding="large">
        {@render $$slots.default()}
      </Card>
  
      {#if $$slots.footer}
        <div class="text-center text-sm text-gray-600 dark:text-gray-400">
          {@render $$slots.footer()}
        </div>
      {/if}
    </div>
  </div>
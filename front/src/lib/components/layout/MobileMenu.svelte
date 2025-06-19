<!-- front/src/lib/components/common/NotificationToast.svelte -->
<script>
    import { fade, fly } from 'svelte/transition';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { portal } from '$lib/utils/helpers.js';
  
    const notifications = $derived($uiStore.notifications);
  
    const variants = {
      success: {
        bg: 'bg-green-50 dark:bg-green-900/20',
        border: 'border-green-200 dark:border-green-800',
        icon: 'text-green-600 dark:text-green-400',
        title: 'text-green-800 dark:text-green-200'
      },
      error: {
        bg: 'bg-red-50 dark:bg-red-900/20',
        border: 'border-red-200 dark:border-red-800',
        icon: 'text-red-600 dark:text-red-400',
        title: 'text-red-800 dark:text-red-200'
      },
      warning: {
        bg: 'bg-yellow-50 dark:bg-yellow-900/20',
        border: 'border-yellow-200 dark:border-yellow-800',
        icon: 'text-yellow-600 dark:text-yellow-400',
        title: 'text-yellow-800 dark:text-yellow-200'
      },
      info: {
        bg: 'bg-blue-50 dark:bg-blue-900/20',
        border: 'border-blue-200 dark:border-blue-800',
        icon: 'text-blue-600 dark:text-blue-400',
        title: 'text-blue-800 dark:text-blue-200'
      }
    };
  
    const icons = {
      success: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />',
      error: '<path stroke-linecap="round" stroke-linejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />',
      warning: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />',
      info: '<path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />'
    };
  </script>
  
  <div class="fixed top-20 right-4 z-50 space-y-2" use:portal>
    {#each notifications as notification (notification.id)}
      {@const variant = variants[notification.type || 'info']}
      <div
        class="max-w-sm w-full {variant.bg} {variant.border} border rounded-lg shadow-lg pointer-events-auto"
        in:fly={{ x: 100, duration: 300 }}
        out:fade={{ duration: 200 }}
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg class="w-5 h-5 {variant.icon}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {@html icons[notification.type || 'info']}
              </svg>
            </div>
            <div class="ml-3 w-0 flex-1">
              {#if notification.title}
                <p class="text-sm font-medium {variant.title}">
                  {notification.title}
                </p>
              {/if}
              {#if notification.message}
                <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  {notification.message}
                </p>
              {/if}
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button
                onclick={() => uiStore.removeNotification(notification.id)}
                class="inline-flex text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    {/each}
  </div>
<!-- front/src/lib/components/common/NotificationToast.svelte -->
<script>
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { notificationStore } from '$lib/stores/notification.store.js';
  
  const typeStyles = {
    success: {
      bg: 'from-stellar-500/20 to-stellar-600/20',
      border: 'border-stellar-500/30',
      icon: 'text-stellar-600 dark:text-stellar-400',
      iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    error: {
      bg: 'from-red-500/20 to-red-600/20',
      border: 'border-red-500/30',
      icon: 'text-red-600 dark:text-red-400',
      iconPath: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    warning: {
      bg: 'from-cosmic-500/20 to-cosmic-600/20',
      border: 'border-cosmic-500/30',
      icon: 'text-cosmic-600 dark:text-cosmic-400',
      iconPath: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
    },
    info: {
      bg: 'from-nebula-500/20 to-nebula-600/20',
      border: 'border-nebula-500/30',
      icon: 'text-nebula-600 dark:text-nebula-400',
      iconPath: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    }
  };
</script>

<div class="toast-container" aria-live="polite" aria-atomic="true">
  {#each $notificationStore as notification (notification.id)}
    <div
      class="glass mb-3 p-4 rounded-xl border {typeStyles[notification.type].border} bg-gradient-to-r {typeStyles[notification.type].bg} shadow-lg"
      transition:fly={{ x: 300, duration: 300, easing: quintOut }}
    >
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-6 h-6 {typeStyles[notification.type].icon}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={typeStyles[notification.type].iconPath} />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 dark:text-white">
            {notification.title}
          </p>
          {#if notification.message}
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {notification.message}
            </p>
          {/if}
        </div>
        <button
          onclick={() => notificationStore.remove(notification.id)}
          class="flex-shrink-0 ml-4 p-1 rounded-lg hover:bg-gray-100/50 dark:hover:bg-gray-800/50 transition-colors"
        >
          <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  {/each}
</div>
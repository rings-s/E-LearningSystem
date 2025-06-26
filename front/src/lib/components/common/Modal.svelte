<!-- front/src/lib/components/common/Modal.svelte -->
<script>
  import { fade, fly } from 'svelte/transition';
  import { classNames } from '$lib/utils/helpers.js';
  import { portal, focusTrap, scrollLock } from '$lib/utils/helpers.js';

  let {
    open = false,
    onClose = () => {},
    title = '',
    size = 'medium',
    closeOnBackdrop = true,
    closeOnEscape = true,
    class: className = '',
    children
  } = $props();

  let modalElement;

  const sizes = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  };

  const handleBackdropClick = () => {
    if (closeOnBackdrop) {
      onClose();
    }
  };

  $effect(() => {
    if (open) {
      scrollLock(true);
      
      const handleKeydown = (e) => {
        if (e.key === 'Escape' && closeOnEscape) {
          onClose();
        }
      };
      
      document.addEventListener('keydown', handleKeydown);
      
      return () => {
        scrollLock(false);
        document.removeEventListener('keydown', handleKeydown);
      };
    }
  });
</script>

{#if open}
  <div class="fixed inset-0 z-50 overflow-y-auto" use:portal>
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm"
      transition:fade={{ duration: 200 }}
      onclick={handleBackdropClick}
      aria-hidden="true"
    />

    <!-- Modal -->
    <div class="flex min-h-screen items-center justify-center p-4">
      <div
        bind:this={modalElement}
        class={classNames(
          'relative w-full bg-white dark:bg-gray-800 rounded-xl shadow-xl',
          sizes[size],
          className
        )}
        transition:fly={{ y: 20, duration: 300 }}
        use:focusTrap
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 id="modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          <button
            onclick={onClose}
            class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="p-6">
          {@render children()}
        </div>
      </div>
    </div>
  </div>
{/if}
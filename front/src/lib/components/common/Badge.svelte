<!-- front/src/lib/components/common/Badge.svelte -->
<script>
    import { classNames } from '$lib/utils/helpers.js';
  
    let {
      variant = 'default', // 'default', 'primary', 'success', 'warning', 'danger', 'info'
      size = 'medium', // 'small', 'medium', 'large'
      removable = false,
      onRemove = () => {},
      class: className = ''
    } = $props();
  
    const variants = {
      default: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
      success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      danger: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
      info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      accent: 'bg-accent-100 text-accent-700 dark:bg-accent-900/30 dark:text-accent-400'
    };
  
    const sizes = {
      small: 'px-2 py-0.5 text-xs',
      medium: 'px-2.5 py-1 text-sm',
      large: 'px-3 py-1.5 text-base'
    };
  </script>
  
  <span class={classNames(
    'inline-flex items-center font-medium rounded-full',
    variants[variant],
    sizes[size],
    className
  )}>
    {@render $$slots.default()}
    
    {#if removable}
      <button
        onclick={onRemove}
        class="ml-1 -mr-0.5 inline-flex items-center justify-center w-4 h-4 text-current hover:bg-black/10 dark:hover:bg-white/10 rounded-full transition-colors"
        aria-label="Remove"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    {/if}
  </span>
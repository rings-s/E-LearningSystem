<!-- front/src/lib/components/common/Button.svelte -->
<script>
    import { classNames } from '$lib/utils/helpers.js';
  
    let {
      variant = 'primary', // 'primary', 'secondary', 'outline', 'ghost', 'danger'
      size = 'medium', // 'small', 'medium', 'large'
      fullWidth = false,
      loading = false,
      disabled = false,
      type = 'button',
      href = null,
      onclick = () => {},
      class: className = '',
      ...rest
    } = $props();
  
    const variants = {
      primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 dark:bg-primary-500 dark:hover:bg-primary-600',
      secondary: 'bg-secondary-600 text-white hover:bg-secondary-700 focus:ring-secondary-500 dark:bg-secondary-500 dark:hover:bg-secondary-600',
      outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-primary-500 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700',
      ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-primary-500 dark:text-gray-300 dark:hover:bg-gray-700',
      danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 dark:bg-red-500 dark:hover:bg-red-600'
    };
  
    const sizes = {
      small: 'px-3 py-1.5 text-xs',
      medium: 'px-4 py-2 text-sm',
      large: 'px-6 py-3 text-base'
    };
  
    const classes = classNames(
      'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
      variants[variant],
      sizes[size],
      fullWidth && 'w-full',
      (disabled || loading) && 'opacity-50 cursor-not-allowed',
      className
    );
  
    const handleClick = (e) => {
      if (!disabled && !loading) {
        onclick(e);
      }
    };
  </script>
  
  {#if href && !disabled}
    <a {href} class={classes} {...rest}>
      {#if loading}
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      {@render $$slots.default()}
    </a>
  {:else}
    <button
      {type}
      {disabled}
      class={classes}
      onclick={handleClick}
      {...rest}
    >
      {#if loading}
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      {@render $$slots.default()}
    </button>
  {/if}
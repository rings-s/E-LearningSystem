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
    children,
    iconLeft = null,
    iconRight = null,
    ...rest
  } = $props();

  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:cursor-not-allowed disabled:opacity-50 transform active:scale-[0.98]';

  const variants = {
    primary: 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 focus:ring-primary-500 text-white shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 border border-transparent',
    secondary: 'bg-gradient-to-r from-secondary-600 to-secondary-700 hover:from-secondary-700 hover:to-secondary-800 focus:ring-secondary-500 text-white shadow-lg shadow-secondary-500/25 hover:shadow-xl hover:shadow-secondary-500/30 border border-transparent',
    outline: 'bg-transparent border-2 border-gray-300 text-gray-700 hover:border-gray-400 hover:bg-gray-50 focus:ring-gray-500 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:border-gray-500',
    ghost: 'bg-transparent border-2 border-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800',
    danger: 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 focus:ring-red-500 text-white shadow-lg shadow-red-500/25 hover:shadow-xl hover:shadow-red-500/30 border border-transparent'
  };

  const sizes = {
    small: 'px-4 py-2 text-sm rounded-lg gap-2',
    medium: 'px-6 py-3 text-base rounded-xl gap-2.5',
    large: 'px-8 py-4 text-lg rounded-2xl gap-3'
  };

  const iconSizes = {
    small: 'w-4 h-4',
    medium: 'w-5 h-5',
    large: 'w-6 h-6'
  };

  const classes = classNames(
    baseStyles,
    variants[variant],
    sizes[size],
    fullWidth && 'w-full',
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
      <svg class="animate-spin {iconSizes[size]}" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {:else if iconLeft}
      <svg class={iconSizes[size]} fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        {@html iconLeft}
      </svg>
    {/if}
    {@render children()}
    {#if iconRight && !loading}
      <svg class={iconSizes[size]} fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        {@html iconRight}
      </svg>
    {/if}
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
      <svg class="animate-spin {iconSizes[size]}" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {:else if iconLeft}
      <svg class={iconSizes[size]} fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        {@html iconLeft}
      </svg>
    {/if}
    {@render children()}
    {#if iconRight && !loading}
      <svg class={iconSizes[size]} fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        {@html iconRight}
      </svg>
    {/if}
  </button>
{/if}
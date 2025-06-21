<!-- front/src/lib/components/common/Button.svelte -->
<script>
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

  const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 rounded-lg';

  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm focus:ring-blue-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white shadow-sm focus:ring-gray-500',
    outline: 'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:ring-blue-500',
    ghost: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white shadow-sm focus:ring-red-500'
  };

  const sizes = {
    small: 'px-3 py-1.5 text-sm gap-1.5',
    medium: 'px-4 py-2 text-sm gap-2',
    large: 'px-6 py-3 text-base gap-2'
  };

  const iconSizes = {
    small: 'w-4 h-4',
    medium: 'w-4 h-4',
    large: 'w-5 h-5'
  };

  const classes = [
    baseStyles,
    variants[variant],
    sizes[size],
    fullWidth && 'w-full',
    className
  ].filter(Boolean).join(' ');

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
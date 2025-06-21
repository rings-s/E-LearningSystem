<!-- front/src/lib/components/common/Card.svelte -->
<script>
  let {
    variant = 'default',
    padding = 'normal',
    class: className = '',
    hoverable = false,
    onclick = null,
    header = undefined,
    footer = undefined,
    children
  } = $props();

  const variants = {
    default: 'bg-white dark:bg-gray-800',
    bordered: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    elevated: 'bg-white dark:bg-gray-800 shadow-lg'
  };

  const paddings = {
    none: '',
    small: 'p-4',
    normal: 'p-6',
    large: 'p-8'
  };

  const classes = [
    'rounded-lg transition-colors',
    variants[variant],
    paddings[padding],
    hoverable && 'hover:shadow-md cursor-pointer',
    onclick && 'cursor-pointer',
    className
  ].filter(Boolean).join(' ');

  const handleKeyDown = (event) => {
    if (onclick && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      onclick(event);
    }
  };
</script>

<div
  class={classes}
  onclick={onclick}
  onkeydown={handleKeyDown}
  role={onclick ? 'button' : undefined}
  tabindex={onclick ? 0 : undefined}
>
  {#if header}
    <div class="card-header -m-6 mb-6 p-6 border-b border-gray-200 dark:border-gray-700">
      {@render header()}
    </div>
  {/if}

  <div class="card-body">
    {@render children()}
  </div>

  {#if footer}
    <div class="card-footer -m-6 mt-6 p-6 border-t border-gray-200 dark:border-gray-700">
      {@render footer()}
    </div>
  {/if}
</div>
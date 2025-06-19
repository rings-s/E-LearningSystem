<!-- front/src/lib/components/common/Card.svelte -->
<script>
    import { classNames } from '$lib/utils/helpers.js';
  
    let {
      variant = 'default', // 'default', 'bordered', 'elevated', 'gradient'
      padding = 'normal', // 'none', 'small', 'normal', 'large'
      class: className = '',
      hoverable = false,
      onclick = null
    } = $props();
  
    const variants = {
      default: 'bg-white dark:bg-gray-800',
      bordered: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
      elevated: 'bg-white dark:bg-gray-800 shadow-lg',
      gradient: 'bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900'
    };
  
    const paddings = {
      none: '',
      small: 'p-4',
      normal: 'p-6',
      large: 'p-8'
    };
  </script>
  
  <div
    class={classNames(
      'rounded-xl transition-all duration-200',
      variants[variant],
      paddings[padding],
      hoverable && 'hover:shadow-xl hover:-translate-y-0.5 cursor-pointer',
      onclick && 'cursor-pointer',
      className
    )}
    onclick={onclick}
    role={onclick ? 'button' : undefined}
    tabindex={onclick ? 0 : undefined}
  >
    {#if $$slots.header}
      <div class="card-header -m-6 mb-6 p-6 border-b border-gray-200 dark:border-gray-700">
        {@render $$slots.header()}
      </div>
    {/if}
  
    <div class="card-body">
      {@render $$slots.default()}
    </div>
  
    {#if $$slots.footer}
      <div class="card-footer -m-6 mt-6 p-6 border-t border-gray-200 dark:border-gray-700">
        {@render $$slots.footer()}
      </div>
    {/if}
  </div>
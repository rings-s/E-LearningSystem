<!-- front/src/lib/components/common/Tabs.svelte -->
<script>
    import { writable } from 'svelte/store';
    import { fade } from 'svelte/transition';
    import { classNames } from '$lib/utils/helpers.js';
  
    let { 
      tabs = [],
      defaultTab = 0,
      variant = 'default', // 'default', 'pills', 'underline'
      fullWidth = false,
      class: className = ''
    } = $props();
  
    const activeTab = writable(defaultTab);
    
    const setActiveTab = (index) => activeTab.set(index);
  
    const tabStyles = {
      default: {
        container: 'border-b border-gray-200 dark:border-gray-700',
        list: 'flex space-x-8',
        tab: (active) => classNames(
          'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
          active
            ? 'border-primary-500 text-primary-600 dark:text-primary-400'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
        )
      },
      pills: {
        container: '',
        list: 'flex space-x-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg',
        tab: (active) => classNames(
          'px-4 py-2 rounded-md text-sm font-medium transition-all',
          active
            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
        )
      },
      underline: {
        container: '',
        list: 'flex space-x-6',
        tab: (active) => classNames(
          'pb-2 border-b-2 text-sm font-medium transition-colors',
          active
            ? 'border-primary-500 text-primary-600 dark:text-primary-400'
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
        )
      }
    };
  
    const styles = tabStyles[variant];
  </script>
  
  <div class={classNames('tabs', className)}>
    <div class={styles.container}>
      <nav class={classNames(styles.list, fullWidth && 'w-full')} aria-label="Tabs">
        {#each tabs as tab, index}
          <button
            onclick={() => setActiveTab(index)}
            class={classNames(
              styles.tab($activeTab === index),
              fullWidth && 'flex-1 text-center',
              tab.disabled && 'opacity-50 cursor-not-allowed'
            )}
            disabled={tab.disabled}
            aria-current={$activeTab === index ? 'page' : undefined}
          >
            {#if tab.icon}
              <span class="inline-flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {@html tab.icon}
                </svg>
                <span>{tab.label}</span>
              </span>
            {:else}
              {tab.label}
            {/if}
            {#if tab.badge}
              <span class="ml-2 px-2 py-0.5 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
                {tab.badge}
              </span>
            {/if}
          </button>
        {/each}
      </nav>
    </div>
  
    <div class="mt-6">
      {#each tabs as tab, index}
        {#if $activeTab === index}
          <div in:fade={{ duration: 200 }}>
            {@render tab.content()}
          </div>
        {/if}
      {/each}
    </div>
  </div>
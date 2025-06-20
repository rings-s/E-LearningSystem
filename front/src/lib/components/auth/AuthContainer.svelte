<script>
    import { fade, fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    
    let { 
        title = '',
        subtitle = '',
        showLogo = true,
        maxWidth = 'md',
        children,
        footer
    } = $props();

    const maxWidthClasses = {
        sm: 'max-w-sm',
        md: 'max-w-md', 
        lg: 'max-w-lg',
        xl: 'max-w-xl'
    };
</script>

<div class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <!-- Background Pattern -->
    <div class="absolute inset-0 bg-grid-pattern opacity-5 dark:opacity-10"></div>
    
    <div class="relative w-full {maxWidthClasses[maxWidth]} space-y-8" 
         in:fly={{ y: 20, duration: 600, easing: quintOut }}>
        
        {#if showLogo}
            <div class="text-center" in:fade={{ delay: 200, duration: 400 }}>
                <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-3xl text-white text-3xl font-bold mb-6 shadow-xl shadow-primary-500/25 transform hover:scale-105 transition-transform duration-200">
                    E
                </div>
                
                <h1 class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent mb-2">
                    {title}
                </h1>
                
                {#if subtitle}
                    <p class="text-lg text-gray-600 dark:text-gray-400">
                        {@html subtitle}
                    </p>
                {/if}
            </div>
        {/if}

        <!-- Main Content Card -->
        <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-gray-500/10 border border-gray-200/20 dark:border-gray-700/20 p-8 sm:p-10"
             in:fly={{ y: 20, delay: 300, duration: 600, easing: quintOut }}>
            {@render children()}
        </div>

        {#if footer}
            <div class="text-center text-sm text-gray-600 dark:text-gray-400"
                 in:fade={{ delay: 400, duration: 400 }}>
                {@render footer()}
            </div>
        {/if}
    </div>
</div>

<style>
    .bg-grid-pattern {
        background-image: radial-gradient(circle, #e5e7eb 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    :global(.dark) .bg-grid-pattern {
        background-image: radial-gradient(circle, #374151 1px, transparent 1px);
    }
</style>
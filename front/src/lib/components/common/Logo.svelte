<!-- front/src/lib/components/common/Logo.svelte -->
<script>
    import { classNames } from '$lib/utils/helpers.js';
    
    let {
        size = 'medium',
        showText = true,
        href = '/',
        class: className = ''
    } = $props();
    
    const sizes = {
        small: { logo: 'w-8 h-8', text: 'text-lg' },
        medium: { logo: 'w-10 h-10', text: 'text-xl' },
        large: { logo: 'w-16 h-16', text: 'text-2xl' }
    };
</script>

<a {href} class={classNames('inline-flex items-center gap-3 group', className)}>
    <div class={classNames(
        'relative overflow-hidden rounded-xl transition-all duration-300 group-hover:scale-105',
        sizes[size].logo
    )}>
        <div class="w-full h-full bg-gradient-to-br from-primary-500 to-secondary-600 flex items-center justify-center">
            <span class="text-white font-bold {sizes[size].text}">244</span>
        </div>
    </div>
    
    {#if showText}
        <span class={classNames(
            'font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent transition-all duration-300',
            sizes[size].text
        )}>
            244SCHOOL
        </span>
    {/if}
</a>
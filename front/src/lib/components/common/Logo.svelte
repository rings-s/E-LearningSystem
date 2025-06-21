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
        <img 
            src="/logo.png" 
            alt="E-Learning Platform"
            class="w-full h-full object-cover"
            onerror={(event) => {
    const img = event.target;
    if (img instanceof HTMLImageElement) {
        img.onerror = null;
        img.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Cdefs%3E%3ClinearGradient id=%22grad%22 x1=%220%25%22 y1=%220%25%22 x2=%22100%25%22 y2=%22100%25%22%3E%3Cstop offset=%220%25%22 style=%22stop-color:%234f46e5%22/%3E%3Cstop offset=%22100%25%22 style=%22stop-color:%236366f1%22/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width=%22100%22 height=%22100%22 fill=%22url(%23grad)%22/%3E%3Ctext x=%2250%22 y=%2265%22 font-family=%22Arial, sans-serif%22 font-size=%2250%22 font-weight=%22bold%22 text-anchor=%22middle%22 fill=%22white%22%3EE%3C/text%3E%3C/svg%3E';
    }
}}
        />
    </div>
    
    {#if showText}
        <span class={classNames(
            'font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent transition-all duration-300',
            sizes[size].text
        )}>
            249SCHOOL
        </span>
    {/if}
</a>
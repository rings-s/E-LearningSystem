<!-- front/src/routes/+page.svelte -->
<script>
    import { goto } from '$app/navigation';
    import { isAuthenticated } from '$lib/services/auth.service.js';
    import { t } from '$lib/i18n/index.js';
    import Button from '$lib/components/common/Button.svelte';
    
    $effect(() => {
        if ($isAuthenticated) {
            goto('/dashboard');
        }
    });
</script>

<div class="min-h-screen flex items-center justify-center">
    <div class="text-center max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
            <span class="bg-gradient-to-r from-primary-600 via-secondary-600 to-accent-600 bg-clip-text text-transparent">
                Welcome to 249SCHOOL
            </span>
        </h1>
        
        <p class="text-xl sm:text-2xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Your gateway to quality online education. Learn from experts, grow your skills, and achieve your goals.
        </p>
        
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button href="/register" variant="primary" size="large">
                {$t('actions.getStarted')}
            </Button>
            <Button href="/courses" variant="outline" size="large">
                {$t('actions.learnMore')}
            </Button>
        </div>
        
        <div class="mt-20 grid grid-cols-1 sm:grid-cols-3 gap-8">
            <div class="text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Quality Content</h3>
                <p class="text-gray-600 dark:text-gray-400">Learn from industry experts with carefully curated courses</p>
            </div>
            
            <div class="text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-secondary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Interactive Learning</h3>
                <p class="text-gray-600 dark:text-gray-400">Engage with quizzes, assignments, and hands-on projects</p>
            </div>
            
            <div class="text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-accent-500 to-secondary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Get Certified</h3>
                <p class="text-gray-600 dark:text-gray-400">Earn certificates to showcase your achievements</p>
            </div>
        </div>
    </div>
</div>
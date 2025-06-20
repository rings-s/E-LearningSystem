<script>
    let { steps = [], currentStep = 0 } = $props();
</script>

<div class="flex items-center justify-center mb-8">
    {#each steps as step, index}
        <div class="flex items-center">
            <div class="flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300 {
                index < currentStep 
                    ? 'bg-primary-600 border-primary-600 text-white' 
                    : index === currentStep 
                    ? 'border-primary-600 text-primary-600 bg-primary-50 dark:bg-primary-900/20' 
                    : 'border-gray-300 dark:border-gray-600 text-gray-400'
            }">
                {#if index < currentStep}
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                {:else}
                    <span class="text-sm font-semibold">{index + 1}</span>
                {/if}
            </div>
            
            {#if index < steps.length - 1}
                <div class="w-16 h-0.5 mx-4 {
                    index < currentStep ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
                } transition-colors duration-300"></div>
            {/if}
        </div>
    {/each}
</div>

<div class="text-center mb-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        {steps[currentStep]?.title}
    </h3>
    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
        {steps[currentStep]?.description}
    </p>
</div>
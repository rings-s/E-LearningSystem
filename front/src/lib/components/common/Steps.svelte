<!-- front/src/lib/components/common/Steps.svelte -->
<script>
    import { writable } from 'svelte/store';
    import { fly } from 'svelte/transition';
    import { classNames } from '$lib/utils/helpers.js';
  
    let {
      steps = [],
      currentStep = 0,
      orientation = 'horizontal', // 'horizontal' or 'vertical'
      allowStepClick = false,
      onStepChange = () => {},
      class: className = ''
    } = $props();
  
    const activeStep = writable(currentStep);
    
    $effect(() => {
      activeStep.set(currentStep);
    });
  
    const goToStep = (index) => {
      if (allowStepClick && index <= Math.max(...steps.filter(s => s.completed).map((_, i) => i))) {
        activeStep.set(index);
        onStepChange(index);
      }
    };
  
    const nextStep = () => {
      if ($activeStep < steps.length - 1) {
        activeStep.update(n => n + 1);
        onStepChange($activeStep);
      }
    };
  
    const prevStep = () => {
      if ($activeStep > 0) {
        activeStep.update(n => n - 1);
        onStepChange($activeStep);
      }
    };
  
    const isStepActive = (index) => index === $activeStep;
    const isStepCompleted = (index) => index < $activeStep || steps[index]?.completed;
    const isStepClickable = (index) => allowStepClick && (isStepCompleted(index) || isStepActive(index));
  </script>
  
  <div class={classNames('steps', className)}>
    <nav aria-label="Progress" class={classNames(
      orientation === 'vertical' && 'flex'
    )}>
      <ol class={classNames(
        'flex',
        orientation === 'vertical' ? 'flex-col space-y-4' : 'items-center space-x-4 sm:space-x-8'
      )}>
        {#each steps as step, index}
          <li class={classNames(
            'relative',
            orientation === 'horizontal' && index !== steps.length - 1 && 'flex-1'
          )}>
            <button
              onclick={() => goToStep(index)}
              disabled={!isStepClickable(index)}
              class={classNames(
                'group flex items-center w-full',
                isStepClickable(index) && 'cursor-pointer'
              )}
            >
              <!-- Step indicator -->
              <span class={classNames(
                'flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200',
                isStepCompleted(index)
                  ? 'bg-primary-600 dark:bg-primary-500'
                  : isStepActive(index)
                  ? 'border-2 border-primary-600 dark:border-primary-500 bg-white dark:bg-gray-800'
                  : 'border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800'
              )}>
                {#if isStepCompleted(index) && !isStepActive(index)}
                  <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                {:else}
                  <span class={classNames(
                    'text-sm font-medium',
                    isStepActive(index)
                      ? 'text-primary-600 dark:text-primary-400'
                      : isStepCompleted(index)
                      ? 'text-white'
                      : 'text-gray-500 dark:text-gray-400'
                  )}>
                    {index + 1}
                  </span>
                {/if}
              </span>
  
              <!-- Step content -->
              <span class="ml-4 flex flex-col">
                <span class={classNames(
                  'text-sm font-medium',
                  isStepActive(index)
                    ? 'text-primary-600 dark:text-primary-400'
                    : isStepCompleted(index)
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-500 dark:text-gray-400'
                )}>
                  {step.title}
                </span>
                {#if step.description}
                  <span class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {step.description}
                  </span>
                {/if}
              </span>
            </button>
  
            <!-- Connector line -->
            {#if index !== steps.length - 1}
              <div class={classNames(
                'absolute transition-all duration-200',
                orientation === 'horizontal'
                  ? 'top-5 left-10 -ml-px w-full h-0.5'
                  : 'left-5 top-10 w-0.5 h-full'
              )}>
                <div class={classNames(
                  'h-full w-full',
                  isStepCompleted(index + 1)
                    ? 'bg-primary-600 dark:bg-primary-500'
                    : 'bg-gray-300 dark:bg-gray-600'
                )} />
              </div>
            {/if}
          </li>
        {/each}
      </ol>
    </nav>
  
    <!-- Step content -->
    <div class={classNames(
      'mt-8',
      orientation === 'vertical' && 'flex-1 ml-12'
    )}>
      {#key $activeStep}
        <div in:fly={{ x: 20, duration: 300 }}>
          {@render steps[$activeStep].content()}
        </div>
      {/key}
    </div>
  
    <!-- Navigation buttons -->
    <div class="mt-8 flex justify-between">
      <button
        onclick={prevStep}
        disabled={$activeStep === 0}
        class={classNames(
          'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
          $activeStep === 0
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-800 dark:text-gray-600'
            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700'
        )}
      >
        Previous
      </button>
      
      <button
        onclick={nextStep}
        disabled={$activeStep === steps.length - 1}
        class={classNames(
          'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
          $activeStep === steps.length - 1
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-800 dark:text-gray-600'
            : 'bg-primary-600 text-white hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600'
        )}
      >
        {$activeStep === steps.length - 1 ? 'Complete' : 'Next'}
      </button>
    </div>
  </div>
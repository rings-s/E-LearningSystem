<!-- front/src/lib/components/common/Input.svelte -->
<script>
  import { classNames } from '$lib/utils/helpers.js';
  import { fade, slide } from 'svelte/transition';

  let {
    type = 'text',
    name = '',
    label = '',
    placeholder = '',
    value = $bindable(''),
    error = '',
    disabled = false,
    required = false,
    readonly = false,
    icon = null,
    hint = '',
    showPasswordToggle = false,
    class: className = '',
    onblur = () => {},
    oninput = () => {},
    onfocus = () => {},
    ...rest
  } = $props();

  let inputElement;
  let touched = $state(false);
  let focused = $state(false);
  let showPassword = $state(false);
  
  const id = `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const actualType = $derived(
    type === 'password' && showPassword ? 'text' : type
  );

  const handleBlur = (e) => {
    touched = true;
    focused = false;
    onblur(e);
  };

  const handleFocus = (e) => {
    focused = true;
    onfocus(e);
  };

  const shouldShowError = $derived(error && touched);
  
  const containerClasses = $derived(classNames(
    'relative rounded-2xl transition-all duration-200',
    focused && 'ring-2 ring-primary-500 ring-offset-2 dark:ring-offset-gray-900',
    shouldShowError && 'ring-2 ring-red-500 ring-offset-2 dark:ring-offset-gray-900'
  ));

  const inputClasses = $derived(classNames(
    'block w-full rounded-2xl border-0 bg-gray-50 dark:bg-gray-800 transition-all duration-200',
    'text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500',
    'focus:ring-0 focus:outline-none',
    icon && 'pl-12',
    showPasswordToggle && type === 'password' && 'pr-12',
    disabled && 'opacity-50 cursor-not-allowed',
    'px-4 py-3.5 text-base'
  ));
</script>

<div class={classNames('form-group space-y-2', className)}>
  {#if label}
    <label 
      for={id}
      class="flex items-center gap-1 text-sm font-semibold text-gray-700 dark:text-gray-300"
    >
      {label}
      {#if required}
        <span class="text-red-500">*</span>
      {/if}
    </label>
  {/if}

  <div class={containerClasses}>
    {#if icon}
      <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
        <div class="w-5 h-5 {focused ? 'text-primary-600 dark:text-primary-400' : 'text-gray-400'} transition-colors duration-200">
          {@html icon}
        </div>
      </div>
    {/if}

    <input
      bind:this={inputElement}
      {id}
      type={actualType}
      {name}
      bind:value
      {placeholder}
      {disabled}
      {required}
      {readonly}
      class={inputClasses}
      oninput={oninput}
      onblur={handleBlur}
      onfocus={handleFocus}
      {...rest}
    />

    {#if showPasswordToggle && type === 'password'}
      <button
        type="button"
        onclick={() => showPassword = !showPassword}
        class="absolute inset-y-0 right-0 pr-4 flex items-center z-10 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200"
        tabindex="-1"
      >
        {#if showPassword}
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
          </svg>
        {:else}
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        {/if}
      </button>
    {/if}
  </div>

  {#if hint && !shouldShowError}
    <p class="text-xs text-gray-500 dark:text-gray-400 pl-1" transition:slide={{ duration: 200 }}>
      {hint}
    </p>
  {/if}

  {#if shouldShowError}
    <p class="text-xs text-red-600 dark:text-red-400 flex items-center gap-1.5 pl-1" transition:slide={{ duration: 200 }}>
      <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      {error}
    </p>
  {/if}
</div>
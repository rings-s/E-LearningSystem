<!-- front/src/lib/components/common/Input.svelte -->
<script>
  import { classNames } from '$lib/utils/helpers.js';

  let {
    type = 'text',
    name = '',
    label = '',
    placeholder = '',
    value = '',
    error = '',
    disabled = false,
    required = false,
    readonly = false,
    icon = null,
    hint = '',
    class: className = '',
    onblur = () => {},
    oninput = () => {},
    ...rest
  } = $props();

  let inputElement;
  let touched = $state(false);
  const id = `input-${Math.random().toString(36).substr(2, 9)}`;

  const handleBlur = (e) => {
    touched = true;
    onblur(e);
  };

  const handleInput = (e) => {
    value = e.target.value;
    oninput(e);
  };

  // Only show error if field has been touched or has a value
  const shouldShowError = $derived(error && (touched || value));
</script>

<div class={classNames('form-group', className)}>
  {#if label}
    <label 
      for={id}
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
    >
      {label}
      {#if required}
        <span class="text-red-500">*</span>
      {/if}
    </label>
  {/if}

  <div class="relative">
    {#if icon}
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {@html icon}
        </svg>
      </div>
    {/if}

    <input
      bind:this={inputElement}
      {id}
      {type}
      {name}
      {value}
      {placeholder}
      {disabled}
      {required}
      {readonly}
      class={classNames(
        'block w-full rounded-lg border transition-colors duration-200',
        'text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500',
        'bg-white dark:bg-gray-800',
        'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        icon && 'pl-10',
        shouldShowError
          ? 'border-red-300 dark:border-red-600'
          : 'border-gray-300 dark:border-gray-600',
        disabled && 'opacity-50 cursor-not-allowed',
        'px-3 py-2'
      )}
      oninput={handleInput}
      onblur={handleBlur}
      {...rest}
    />
  </div>

  {#if hint && !shouldShowError}
    <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
      {hint}
    </p>
  {/if}

  {#if shouldShowError}
    <p class="mt-1 text-xs text-red-600 dark:text-red-400">
      {error}
    </p>
  {/if}
</div>
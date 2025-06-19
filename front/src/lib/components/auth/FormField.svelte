<!-- front/src/lib/components/auth/FormField.svelte -->
<script>
    import Input from '../common/Input.svelte';
    import Select from '../common/Select.svelte';
  
    let {
      type = 'text',
      name = '',
      label = '',
      value = '',
      error = '',
      required = false,
      options = [],
      icon = null,
      ...rest
    } = $props();
  </script>
  
  {#if type === 'select'}
    <Select
      {name}
      {label}
      bind:value
      {error}
      {required}
      {options}
      {...rest}
    />
  {:else}
    <Input
      {type}
      {name}
      {label}
      bind:value
      {error}
      {required}
      {icon}
      {...rest}
    />
  {/if}
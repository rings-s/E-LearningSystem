<!-- front/src/lib/components/auth/FormField.svelte -->
<script>
  import Input from '$lib/components/common/Input.svelte';
  import Select from '$lib/components/common/Select.svelte';

  let {
    type = 'text',
    name = '',
    label = '',
    value = $bindable(''),
    error = '',
    required = false,
    options = [],
    icon = null,
    onblur = () => {},
    oninput = () => {},
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
    {onblur}
    {oninput}
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
    {onblur}
    {oninput}
    {...rest}
  />
{/if}
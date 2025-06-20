<!-- front/src/routes/(auth)/login/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.store.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { validators, validateForm } from '$lib/utils/validators.js';
  import Input from '$lib/components/common/Input.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Card from '$lib/components/common/Card.svelte';

  let formData = $state({
    email: '',
    password: ''
  });

  let errors = $state({});
  let loading = $state(false);
  let touched = $state({});

  const validationRules = {
    email: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.email, message: $t('errors.invalidEmail') }
    ],
    password: [
      { validator: validators.required, message: $t('errors.requiredField') }
    ]
  };

  // Only show errors for touched fields
  const getFieldError = (fieldName) => {
    return touched[fieldName] ? errors[fieldName] || '' : '';
  };

  const handleFieldBlur = (fieldName) => {
    touched[fieldName] = true;
    validateField(fieldName);
  };

  const handleFieldInput = (fieldName) => {
    if (touched[fieldName]) {
      validateField(fieldName);
    }
  };

  const validateField = (fieldName) => {
    const fieldValue = formData[fieldName];
    const rules = validationRules[fieldName] || [];
    
    for (const rule of rules) {
      if (!rule.validator(fieldValue)) {
        errors[fieldName] = rule.message;
        return false;
      }
    }
    
    // Clear error if validation passes
    if (errors[fieldName]) {
      delete errors[fieldName];
      errors = { ...errors };
    }
    return true;
  };

  async function handleSubmit(e) {
    e.preventDefault();
    
    // Mark all fields as touched
    touched = { email: true, password: true };
    
    const validation = validateForm(formData, validationRules);
    if (!validation.isValid) {
      errors = validation.errors;
      return;
    }

    loading = true;
    const result = await authStore.login(formData);
    loading = false;

    if (result.success) {
      uiStore.showNotification({
        type: 'success',
        title: $t('auth.loginSuccess'),
        message: $t('common.welcome') + ', ' + result.user.full_name
      });
      goto('/dashboard');
    } else {
      uiStore.showNotification({
        type: 'error',
        title: $t('common.error'),
        message: result.error || $t('auth.invalidCredentials')
      });
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full">
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl text-white text-2xl font-bold mb-4">
        E
      </div>
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
        {$t('auth.login')}
      </h2>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {$t('auth.dontHaveAccount')}
        <a href="/register" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">
          {$t('auth.register')}
        </a>
      </p>
    </div>

    <Card variant="bordered" padding="large">
      <form onsubmit={handleSubmit} class="space-y-6">
        <Input
          type="email"
          name="email"
          label={$t('auth.email')}
          bind:value={formData.email}
          error={getFieldError('email')}
          onblur={() => handleFieldBlur('email')}
          oninput={() => handleFieldInput('email')}
          required
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
        />

        <Input
          type="password"
          name="password"
          label={$t('auth.password')}
          bind:value={formData.password}
          error={getFieldError('password')}
          onblur={() => handleFieldBlur('password')}
          oninput={() => handleFieldInput('password')}
          required
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
        />

        <div class="flex items-center justify-between">
          <label class="flex items-center">
            <input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700">
            <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
              Remember me
            </span>
          </label>

          <a href="/forgot-password" class="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400">
            {$t('auth.forgotPassword')}
          </a>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="large"
          fullWidth
          loading={loading}
        >
          {$t('auth.login')}
        </Button>
      </form>
    </Card>
  </div>
</div>
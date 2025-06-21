<!-- front/src/routes/(auth)/login/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.store.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { validators, validateForm } from '$lib/utils/validators.js';
  import { classNames } from '$lib/utils/helpers.js';
  import Input from '$lib/components/common/Input.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Card from '$lib/components/common/Card.svelte';
  import Logo from '$lib/components/common/Logo.svelte';

  let formData = $state({
    email: '',
    password: '',
    rememberMe: false
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
    
    delete errors[fieldName];
    errors = { ...errors };
    return true;
  };

  async function handleSubmit(e) {
    e.preventDefault();
    
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

<svelte:head>
  <title>{$t('auth.login')} - EduVerse</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-primary-50/20 dark:from-gray-900 dark:via-gray-800 dark:to-primary-900/20 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full">
    <!-- Logo and Header -->
    <div class="text-center mb-8">
      <Logo size="large" showText={false} class="mx-auto mb-6" />
      <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
        {$t('auth.welcomeBack')}
      </h2>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {$t('auth.dontHaveAccount')}
        <a href="/register" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 transition-colors">
          {$t('auth.register')}
        </a>
      </p>
    </div>

    <Card variant="bordered" padding="large" class="backdrop-blur-sm bg-white/90 dark:bg-gray-800/90">
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
          placeholder={$t('auth.enterEmail')}
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10c2 2 0 002 2z" />'
        />

        <div>
          <Input
            type="password"
            name="password"
            label={$t('auth.password')}
            bind:value={formData.password}
            error={getFieldError('password')}
            onblur={() => handleFieldBlur('password')}
            oninput={() => handleFieldInput('password')}
            required
            placeholder={$t('auth.enterPassword')}
            icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
          />
        </div>

        <div class="flex items-center justify-between">
          <label class="flex items-center cursor-pointer group">
            <input 
              type="checkbox" 
              bind:checked={formData.rememberMe}
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 transition-all duration-200"
            >
            <span class="ml-2 text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors">
              {$t('auth.rememberMe')}
            </span>
          </label>

          <a href="/forgot-password" class="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400 transition-colors">
            {$t('auth.forgotPassword')}
          </a>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="large"
          fullWidth
          loading={loading}
          class="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 transform hover:scale-[1.02] transition-all duration-300"
        >
          {loading ? $t('auth.loggingIn') : $t('auth.login')}
        </Button>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white dark:bg-gray-800 text-gray-500">
              {$t('auth.orContinueWith')}
            </span>
          </div>
        </div>

        <!-- Social Login Buttons
        <div class="grid grid-cols-2 gap-3">
          <button
            type="button"
            class="flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 hover:scale-[1.02]"
          >
            <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google
          </button>
          
          <button
            type="button"
            class="flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 hover:scale-[1.02]"
          >
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </button>
        </div> -->
      </form>
    </Card>

    <!-- Footer Links -->
    <div class="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
      <p>
        {$t('auth.needHelp')} 
        <a href="/help" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 transition-colors">
          {$t('auth.contactSupport')}
        </a>
      </p>
    </div>
  </div>
</div>
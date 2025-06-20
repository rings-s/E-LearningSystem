<!-- front/src/routes/(auth)/forgot-password/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { authApi } from '$lib/apis/auth.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { validators, validateForm } from '$lib/utils/validators.js';
  import AuthLayout from '$lib/components/auth/AuthLayout.svelte';
  import FormField from '$lib/components/auth/FormField.svelte';
  import Button from '$lib/components/common/Button.svelte';

  let email = $state('');
  let loading = $state(false);
  let submitted = $state(false);
  let error = $state('');

  const validationRules = {
    email: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.email, message: $t('errors.invalidEmail') }
    ]
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validation = validateForm({ email }, validationRules);
    if (!validation.isValid) {
      error = validation.errors.email;
      return;
    }

    loading = true;
    error = '';

    try {
      await authApi.requestPasswordReset(email);
      submitted = true;
    } catch (err) {
      error = err.message || 'Failed to send reset email';
    } finally {
      loading = false;
    }
  };
</script>

<AuthLayout 
  title={$t('auth.forgotPassword')}
  subtitle={submitted ? '' : "Enter your email and we'll send you a reset code"}
>
  {#if submitted}
    <div class="text-center space-y-4">
      <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto">
        <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      
      <div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">
          Check your email
        </h3>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          We've sent a password reset code to <strong>{email}</strong>
        </p>
      </div>

      <Button
        href={`/reset-password?email=${encodeURIComponent(email)}`}
        variant="primary"
        fullWidth
      >
        Enter Reset Code
      </Button>
      
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Didn't receive the email? Check your spam folder or
        <button 
          onclick={() => submitted = false}
          class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400"
        >
          try again
        </button>
      </p>
    </div>
  {:else}
    <form onsubmit={handleSubmit} class="space-y-6">
      <FormField
        type="email"
        name="email"
        label={$t('auth.email')}
        bind:value={email}
        error={error}
        required
        icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
      />

      <Button
        type="submit"
        variant="primary"
        size="large"
        fullWidth
        loading={loading}
      >
        Send Reset Code
      </Button>
    </form>
  {/if}

  {#snippet footer()}
    <p>
      Remember your password? <a href="/login" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">{$t('auth.login')}</a>
    </p>
  {/snippet}
</AuthLayout>
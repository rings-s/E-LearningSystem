<!-- front/src/routes/(auth)/reset-password/+page.svelte -->
<script>
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { authApi } from '$lib/apis/auth.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import { validators, validateForm } from '$lib/utils/validators.js';
    import AuthLayout from '$lib/components/auth/AuthLayout.svelte';
    import FormField from '$lib/components/auth/FormField.svelte';
    import Button from '$lib/components/common/Button.svelte';
  
    const email = $page.url.searchParams.get('email') || '';
    
    let formData = $state({
      email,
      reset_code: '',
      new_password: '',
      confirm_password: ''
    });
    
    let errors = $state({});
    let loading = $state(false);
  
    const validationRules = {
      reset_code: [
        { validator: validators.required, message: 'Reset code is required' },
        { validator: validators.minLength(6), message: 'Invalid reset code' }
      ],
      new_password: [
        { validator: validators.required, message: $t('errors.requiredField') },
        { validator: validators.minLength(8), message: $t('errors.passwordTooShort') }
      ],
      confirm_password: [
        { validator: validators.required, message: $t('errors.requiredField') },
        { validator: validators.matchField('new_password'), message: $t('errors.passwordsDoNotMatch') }
      ]
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      
      const validation = validateForm(formData, validationRules);
      if (!validation.isValid) {
        errors = validation.errors;
        return;
      }
  
      loading = true;
      errors = {};
  
      try {
        await authApi.confirmPasswordReset(formData);
        
        uiStore.showNotification({
          type: 'success',
          title: $t('auth.passwordChanged'),
          message: 'You can now login with your new password'
        });
        
        goto('/login');
      } catch (err) {
        errors.general = err.message || 'Failed to reset password';
      } finally {
        loading = false;
      }
    };
  </script>
  
  <AuthLayout 
    title={$t('auth.resetPassword')}
    subtitle="Enter the code we sent to your email"
  >
    <form onsubmit={handleSubmit} class="space-y-6">
      {#if !email}
        <FormField
          type="email"
          name="email"
          label={$t('auth.email')}
          bind:value={formData.email}
          error={errors.email}
          required
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
        />
      {/if}
  
      <FormField
        name="reset_code"
        label="Reset Code"
        bind:value={formData.reset_code}
        error={errors.reset_code}
        placeholder="Enter 6-digit code"
        required
        icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
      />
  
      <FormField
        type="password"
        name="new_password"
        label={$t('auth.newPassword')}
        bind:value={formData.new_password}
        error={errors.new_password}
        required
        icon='<path stroke-linecap="round" stroke-linejoin="round" d="M15 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />'
      />
  
      <FormField
        type="password"
        name="confirm_password"
        label={$t('auth.confirmPassword')}
        bind:value={formData.confirm_password}
        error={errors.confirm_password}
        required
        icon='<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />'
      />
  
      {#if errors.general}
        <div class="rounded-lg bg-red-50 dark:bg-red-900/20 p-4">
          <p class="text-sm text-red-800 dark:text-red-200">
            {errors.general}
          </p>
        </div>
      {/if}
  
      <Button
        type="submit"
        variant="primary"
        size="large"
        fullWidth
        loading={loading}
      >
        Reset Password
      </Button>
    </form>
  
    {@snippet footer()}
      <p>
        Need help? <a href="/help" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">Contact Support</a>
      </p>
    {/snippet}
  </AuthLayout>
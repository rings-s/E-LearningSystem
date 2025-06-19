<!-- front/src/routes/(auth)/verify-email/+page.svelte -->
<script>
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { authApi } from '$lib/apis/auth.js';
    import { authStore } from '$lib/stores/auth.store.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import AuthLayout from '$lib/components/auth/AuthLayout.svelte';
    import Button from '$lib/components/common/Button.svelte';
  
    const email = $page.url.searchParams.get('email') || '';
    let verificationCode = $state('');
    let loading = $state(false);
    let resending = $state(false);
    let error = $state('');
    let resendTimer = $state(0);
  
    // Auto-fill code inputs
    let codeInputs = $state(['', '', '', '', '', '']);
    let inputRefs = [];
  
    onMount(() => {
      if (!email) {
        goto('/register');
      }
      startResendTimer();
    });
  
    const startResendTimer = () => {
      resendTimer = 60;
      const interval = setInterval(() => {
        resendTimer--;
        if (resendTimer <= 0) {
          clearInterval(interval);
        }
      }, 1000);
    };
  
    const handleCodeInput = (index, value) => {
      if (value.length > 1) {
        // Handle paste
        const pastedCode = value.slice(0, 6);
        for (let i = 0; i < pastedCode.length; i++) {
          if (i < 6) {
            codeInputs[i] = pastedCode[i];
          }
        }
        verificationCode = codeInputs.join('');
        inputRefs[5]?.focus();
      } else {
        codeInputs[index] = value;
        verificationCode = codeInputs.join('');
        
        // Auto-focus next input
        if (value && index < 5) {
          inputRefs[index + 1]?.focus();
        }
      }
    };
  
    const handleKeyDown = (index, e) => {
      if (e.key === 'Backspace' && !codeInputs[index] && index > 0) {
        inputRefs[index - 1]?.focus();
      }
    };
  
    const handleVerify = async () => {
      if (verificationCode.length !== 6) {
        error = 'Please enter the complete verification code';
        return;
      }
  
      loading = true;
      error = '';
  
      try {
        const response = await authApi.verifyEmail({
          email,
          verification_code: verificationCode
        });
  
        // Set auth tokens
        if (response.tokens) {
          authStore.setTokens(response.tokens);
          authStore.setUser(response.user);
        }
  
        uiStore.showNotification({
          type: 'success',
          title: $t('auth.emailVerified'),
          message: 'Welcome to ' + $t('common.appName')
        });
  
        goto('/dashboard');
      } catch (err) {
        error = err.message || 'Invalid verification code';
      } finally {
        loading = false;
      }
    };
  
    const handleResend = async () => {
      resending = true;
      error = '';
  
      try {
        await authApi.resendVerification(email);
        
        uiStore.showNotification({
          type: 'success',
          title: 'Code Resent',
          message: 'A new verification code has been sent to your email'
        });
        
        // Reset inputs
        codeInputs = ['', '', '', '', '', ''];
        verificationCode = '';
        inputRefs[0]?.focus();
        
        startResendTimer();
      } catch (err) {
        error = err.message || 'Failed to resend code';
      } finally {
        resending = false;
      }
    };
  </script>
  
  <AuthLayout 
    title={$t('auth.verifyEmail')}
    subtitle="We've sent a verification code to <strong>{email}</strong>"
  >
    <form onsubmit|preventDefault={handleVerify} class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
          {$t('auth.verificationCode')}
        </label>
        
        <div class="flex gap-2 justify-center">
          {#each codeInputs as code, index}
            <input
              bind:this={inputRefs[index]}
              type="text"
              inputmode="numeric"
              maxlength="1"
              value={code}
              oninput={(e) => handleCodeInput(index, e.target.value)}
              onkeydown={(e) => handleKeyDown(index, e)}
              class="w-12 h-12 text-center text-lg font-semibold rounded-lg border-2 transition-all
                {code ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600'}
                focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
                dark:bg-gray-800 dark:text-white"
              placeholder="·"
            />
          {/each}
        </div>
      </div>
  
      {#if error}
        <div class="rounded-lg bg-red-50 dark:bg-red-900/20 p-4">
          <p class="text-sm text-red-800 dark:text-red-200">
            {error}
          </p>
        </div>
      {/if}
  
      <Button
        type="submit"
        variant="primary"
        size="large"
        fullWidth
        loading={loading}
        disabled={verificationCode.length !== 6}
      >
        Verify Email
      </Button>
  
      <div class="text-center">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Didn't receive the code?
          {#if resendTimer > 0}
            <span class="text-gray-500">
              Resend in {resendTimer}s
            </span>
          {:else}
            <button
              type="button"
              onclick={handleResend}
              disabled={resending}
              class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 disabled:opacity-50"
            >
              {$t('auth.resendCode')}
            </button>
          {/if}
        </p>
      </div>
    </form>
  
    {@snippet footer()}
      <p>
        Wrong email? <a href="/register" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">Start over</a>
      </p>
    {/snippet}
  </AuthLayout>
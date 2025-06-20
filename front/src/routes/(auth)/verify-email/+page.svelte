<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { authStore } from '$lib/services/auth.service.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  
  import AuthContainer from '$lib/components/auth/AuthContainer.svelte';
  import CodeInput from '$lib/components/auth/CodeInput.svelte';
  import AuthButton from '$lib/components/auth/AuthButton.svelte';

  // Get translation function
  const translate = $derived($t);

  const email = $page.url.searchParams.get('email') || '';
  let verificationCode = $state('');
  let loading = $state(false);
  let resending = $state(false);
  let error = $state('');
  let resendTimer = $state(0);
  let codeInputRef;

  onMount(() => {
      if (!email) {
          goto('/register');
          return;
      }
      startResendTimer();
      // Auto-focus code input
      setTimeout(() => codeInputRef?.focus(), 100);
  });

  function startResendTimer() {
      resendTimer = 60;
      const interval = setInterval(() => {
          resendTimer--;
          if (resendTimer <= 0) {
              clearInterval(interval);
          }
      }, 1000);
  }

  function handleCodeComplete(code) {
      verificationCode = code;
      handleVerify();
  }

  async function handleVerify() {
      if (verificationCode.length !== 6) {
          error = 'Please enter the complete verification code';
          return;
      }

      loading = true;
      error = '';

      const result = await authStore.verifyEmail(email, verificationCode);
      loading = false;

      if (result.success) {
          uiStore.showNotification({
              type: 'success',
              title: 'Email Verified!',
              message: `Welcome to ${translate('common.appName')}, ${result.user.first_name}!`
          });
          goto('/dashboard');
      } else {
          error = result.error;
          codeInputRef?.clear();
      }
  }

  async function handleResend() {
      resending = true;
      error = '';

      const result = await authStore.resendVerification(email);
      resending = false;

      if (result.success) {
          uiStore.showNotification({
              type: 'success',
              title: 'Code Resent',
              message: 'A new verification code has been sent to your email'
          });
          
          codeInputRef?.clear();
          startResendTimer();
      } else {
          error = result.error;
      }
  }

  function maskEmail(email) {
      const [username, domain] = email.split('@');
      const maskedUsername = username.length > 2 
          ? username[0] + '*'.repeat(username.length - 2) + username.slice(-1)
          : username;
      return `${maskedUsername}@${domain}`;
  }
</script>

<AuthContainer 
  title="Check Your Email"
  subtitle="We've sent a 6-digit verification code to"
  footer={footerSnippet}>
  
  <div class="space-y-8">
      <!-- Email Display -->
      <div class="text-center">
          <div class="inline-flex items-center justify-center w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-full mb-4">
              <svg class="w-10 h-10 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
          </div>
          <p class="text-lg font-semibold text-gray-900 dark:text-white">
              {maskEmail(email)}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Enter the code below to verify your email address
          </p>
      </div>

      <!-- Code Input -->
      <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 text-center mb-4">
              Verification Code
          </label>
          
          <CodeInput
              bind:this={codeInputRef}
              bind:value={verificationCode}
              {error}
              disabled={loading}
              onComplete={handleCodeComplete}
          />
      </div>

      <!-- Submit Button -->
      <AuthButton
          onclick={handleVerify}
          loading={loading}
          disabled={loading || verificationCode.length !== 6}
      >
          {loading ? 'Verifying...' : 'Verify Email'}
      </AuthButton>

      <!-- Resend Section -->
      <div class="text-center space-y-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">
              Didn't receive the code?
          </p>
          
          {#if resendTimer > 0}
              <p class="text-sm text-gray-500 dark:text-gray-500" in:fade>
                  Resend available in {resendTimer} seconds
              </p>
          {:else}
              <button
                  type="button"
                  onclick={handleResend}
                  disabled={resending}
                  class="text-sm font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                  {resending ? 'Sending...' : 'Resend Code'}
              </button>
          {/if}

          <!-- Tips -->
          <div class="bg-gray-50 dark:bg-gray-800/50 rounded-2xl p-4 text-left">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  Can't find the email?
              </h4>
              <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• Check your spam or junk folder</li>
                  <li>• Make sure you entered the correct email address</li>
                  <li>• The code expires in 24 hours</li>
                  <li>• Contact support if you continue having issues</li>
              </ul>
          </div>
      </div>
  </div>
</AuthContainer>

{#snippet footerSnippet()}
  <p class="text-center">
      Wrong email? 
      <a href="/register" class="font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors">
          Start over
      </a>
  </p>
{/snippet}
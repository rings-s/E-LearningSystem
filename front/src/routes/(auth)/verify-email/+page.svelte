<!-- front/src/routes/(auth)/verify-email/+page.svelte -->
<script>
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { fade } from 'svelte/transition';
    import { authStore } from '$lib/services/auth.service.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import { classNames } from '$lib/utils/helpers.js';
    import CodeInput from '$lib/components/auth/CodeInput.svelte';
    import Button from '$lib/components/common/Button.svelte';
    import Card from '$lib/components/common/Card.svelte';
    import Logo from '$lib/components/common/Logo.svelte';
  
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
            error = $t('auth.enterCompleteCode');
            return;
        }
  
        loading = true;
        error = '';
  
        const result = await authStore.verifyEmail(email, verificationCode);
        loading = false;
  
        if (result.success) {
            uiStore.showNotification({
                type: 'success',
                title: $t('auth.emailVerified'),
                message: `${$t('common.welcome')} ${$t('common.to')} EduVerse, ${result.user.first_name}!`
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
                title: $t('auth.codeResent'),
                message: $t('auth.newCodeSent')
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
  
  <svelte:head>
    <title>{$t('auth.verifyEmail')} - EduVerse</title>
  </svelte:head>
  
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-primary-50/20 dark:from-gray-900 dark:via-gray-800 dark:to-primary-900/20 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <Logo size="large" showText={false} class="mx-auto mb-6" />
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
          {$t('auth.checkYourEmail')}
        </h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {$t('auth.verificationCodeSent')}
        </p>
      </div>
  
      <Card variant="bordered" padding="large" class="backdrop-blur-sm bg-white/90 dark:bg-gray-800/90">
        <div class="space-y-8">
            <!-- Email Display -->
            <div class="text-center">
                <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full mb-4 shadow-xl">
                    <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                </div>
                <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    {maskEmail(email)}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {$t('auth.enterCodeBelow')}
                </p>
            </div>
  
            <!-- Code Input -->
            <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 text-center mb-4">
                    {$t('auth.verificationCode')}
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
            <Button
                onclick={handleVerify}
                loading={loading}
                disabled={loading || verificationCode.length !== 6}
                variant="primary"
                fullWidth
                size="large"
                class="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 transform hover:scale-[1.02] transition-all duration-300"
            >
                {loading ? $t('auth.verifying') : $t('auth.verifyEmail')}
            </Button>
  
            <!-- Resend Section -->
            <div class="text-center space-y-4">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                    {$t('auth.didntReceiveCode')}
                </p>
                
                {#if resendTimer > 0}
                    <p class="text-sm text-gray-500 dark:text-gray-500" in:fade>
                        {$t('auth.resendIn')} {resendTimer} {$t('auth.seconds')}
                    </p>
                {:else}
                    <button
                        type="button"
                        onclick={handleResend}
                        disabled={resending}
                        class="text-sm font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {resending ? $t('auth.sending') : $t('auth.resendCode')}
                    </button>
                {/if}
  
                <!-- Tips -->
                <div class="bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-4 text-left">
                    <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                        {$t('auth.cantFindEmail')}
                    </h4>
                    <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                        <li>• {$t('auth.checkSpam')}</li>
                        <li>• {$t('auth.correctEmail')}</li>
                        <li>• {$t('auth.codeExpires')}</li>
                        <li>• {$t('auth.contactSupportIfIssues')}</li>
                    </ul>
                </div>
            </div>
        </div>
      </Card>
  
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600 dark:text-gray-400">
            {$t('auth.wrongEmail')} 
            <a href="/register" class="font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors">
                {$t('auth.startOver')}
            </a>
        </p>
      </div>
    </div>
  </div>
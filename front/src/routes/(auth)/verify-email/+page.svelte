<!-- front/src/routes/(auth)/verify-email/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.store.js';
	import { t } from '$lib/i18n/index.js';

	const email = $page.url.searchParams.get('email') || '';
	let verificationCode = $state('');
	let loading = $state(false);
	let resending = $state(false);
	let error = $state('');
	let resendTimer = $state(0);
	let inputs = $state(Array(6).fill(''));
	let inputRefs = [];

	onMount(() => {
		if (!email) {
			goto('/register');
			return;
		}
		startResendTimer();
		setTimeout(() => inputRefs[0]?.focus(), 100);
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

	function handleInput(index, value) {
		if (value.length > 1) {
			// Handle paste
			const pastedCode = value.slice(0, 6);
			for (let i = 0; i < 6; i++) {
				inputs[i] = pastedCode[i] || '';
			}
			const lastFilledIndex = Math.min(pastedCode.length - 1, 5);
			inputRefs[lastFilledIndex]?.focus();
		} else {
			inputs[index] = value;
			if (value && index < 5) {
				inputRefs[index + 1]?.focus();
			}
		}
		
		verificationCode = inputs.join('');
		if (verificationCode.length === 6) {
			handleVerify();
		}
	}

	function handleKeyDown(index, e) {
		if (e.key === 'Backspace') {
			if (!inputs[index] && index > 0) {
				inputRefs[index - 1]?.focus();
			} else {
				inputs[index] = '';
			}
		} else if (e.key === 'ArrowLeft' && index > 0) {
			inputRefs[index - 1]?.focus();
		} else if (e.key === 'ArrowRight' && index < 5) {
			inputRefs[index + 1]?.focus();
		}
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
			goto('/dashboard');
		} else {
			error = result.error;
			clearInputs();
		}
	}

	async function handleResend() {
		resending = true;
		error = '';

		const result = await authStore.resendVerification(email);
		resending = false;

		if (result.success) {
			clearInputs();
			startResendTimer();
		} else {
			error = result.error;
		}
	}

	function clearInputs() {
		inputs = Array(6).fill('');
		verificationCode = '';
		inputRefs[0]?.focus();
	}

	function maskEmail(email) {
		const [username, domain] = email.split('@');
		const maskedUsername =
			username.length > 2
				? username[0] + '*'.repeat(username.length - 2) + username.slice(-1)
				: username;
		return `${maskedUsername}@${domain}`;
	}
</script>

<svelte:head>
	<title>{$t('auth.verifyEmail')} - 244SCHOOL</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8 dark:bg-gray-900">
	<!-- Header -->
	<div class="sm:mx-auto sm:w-full sm:max-w-md">
		<div class="flex justify-center">
			<div class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-3 shadow-lg">
				<span class="text-white text-xl font-bold">244</span>
			</div>
		</div>
		<h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
			{$t('auth.checkYourEmail')}
		</h2>
		<p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
			{$t('auth.verificationCodeSent')}
		</p>
	</div>

	<!-- Main Card -->
	<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
		<div class="bg-white py-8 px-4 shadow-sm rounded-xl border border-gray-200 sm:px-10 dark:bg-gray-800 dark:border-gray-700">
			<div class="space-y-6">
				<!-- Email Display -->
				<div class="text-center">
					<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900/50">
						<svg class="h-8 w-8 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
						</svg>
					</div>
					<p class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
						{maskEmail(email)}
					</p>
					<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
						{$t('auth.enterCodeBelow')}
					</p>
				</div>

				<!-- Code Input -->
				<div>
					<label class="block text-center text-sm font-medium text-gray-900 dark:text-white mb-4">
						{$t('auth.verificationCode')}
					</label>

					<div class="flex justify-center space-x-3">
						{#each inputs as input, index}
							<input
								bind:this={inputRefs[index]}
								type="text"
								inputmode="numeric"
								maxlength="1"
								value={input}
								disabled={loading}
								oninput={(e) => handleInput(index, e.target.value)}
								onkeydown={(e) => handleKeyDown(index, e)}
								class="h-12 w-12 text-center text-lg font-bold rounded-lg border-2 transition-all duration-200 {
									error
										? 'border-red-300 bg-red-50 dark:border-red-600 dark:bg-red-900/20'
										: input
											? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400'
											: 'border-gray-300 hover:border-gray-400 dark:border-gray-600 dark:hover:border-gray-500'
								} focus:border-indigo-500 focus:ring-indigo-500/20 focus:ring-2 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-gray-700 dark:text-white"
								placeholder="•"
							/>
						{/each}
					</div>

					{#if error}
						<div class="mt-3 flex items-center justify-center text-sm text-red-600 dark:text-red-400">
							<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							{error}
						</div>
					{/if}
				</div>

				<!-- Submit Button -->
				<button
					onclick={handleVerify}
					disabled={loading || verificationCode.length !== 6}
					class="flex w-full justify-center rounded-lg bg-indigo-600 px-3 py-3 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if loading}
						<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						{$t('auth.verifying')}
					{:else}
						{$t('auth.verifyEmail')}
					{/if}
				</button>

				<!-- Resend Section -->
				<div class="text-center space-y-3">
					<p class="text-sm text-gray-600 dark:text-gray-400">
						{$t('auth.didntReceiveCode')}
					</p>

					{#if resendTimer > 0}
						<p class="text-sm text-gray-500">
							{$t('auth.resendIn')} {resendTimer} {$t('auth.seconds')}
						</p>
					{:else}
						<button
							type="button"
							onclick={handleResend}
							disabled={resending}
							class="text-sm font-semibold text-indigo-600 hover:text-indigo-500 disabled:cursor-not-allowed disabled:opacity-50 dark:text-indigo-400"
						>
							{resending ? $t('auth.sending') : $t('auth.resendCode')}
						</button>
					{/if}

					<!-- Help Text -->
					<div class="rounded-lg bg-gray-50 p-4 text-left dark:bg-gray-900/50">
						<h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">
							{$t('auth.cantFindEmail')}
						</h4>
						<ul class="space-y-1 text-xs text-gray-600 dark:text-gray-400">
							<li>• {$t('auth.checkSpam')}</li>
							<li>• {$t('auth.correctEmail')}</li>
							<li>• {$t('auth.codeExpires')}</li>
						</ul>
					</div>
				</div>
			</div>
		</div>

		<!-- Footer -->
		<div class="mt-6 text-center">
			<p class="text-sm text-gray-600 dark:text-gray-400">
				{$t('auth.wrongEmail')}
				<a href="/register" class="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
					{$t('auth.startOver')}
				</a>
			</p>
		</div>
	</div>
</div>
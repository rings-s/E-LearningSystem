<script>
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '#lib/stores/auth.store.js';
	import { t } from '#lib/i18n/index.js';
	import Button from '#lib/components/common/Button.svelte';

	const email = page.url.searchParams.get('email') || '';
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

<svelte:head><title>{$t('auth.verifyEmail')} · Ilmora</title></svelte:head>

<span
	class="bg-primary-50 text-primary-600 dark:bg-primary-400/10 dark:text-primary-400 flex size-12 items-center justify-center rounded-2xl"
>
	<svg class="size-6" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
		/>
	</svg>
</span>
<h1 class="mt-6 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
	{$t('auth.checkYourEmail')}
</h1>
<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
	{$t('auth.verificationCodeSent')}
	<strong class="font-medium text-gray-900 dark:text-white">{maskEmail(email)}</strong>
</p>

<div class="mt-8 space-y-6">
	<fieldset>
		<legend class="mb-3 text-sm font-medium text-gray-800 dark:text-gray-200">
			{$t('auth.verificationCode')}
		</legend>
		<div class="grid grid-cols-6 gap-2 sm:gap-3" dir="ltr">
			{#each inputs as input, index}
				<input
					bind:this={inputRefs[index]}
					type="text"
					inputmode="numeric"
					autocomplete={index === 0 ? 'one-time-code' : 'off'}
					maxlength="1"
					value={input}
					disabled={loading}
					aria-label="Digit {index + 1}"
					oninput={(e) => handleInput(index, e.target.value)}
					onkeydown={(e) => handleKeyDown(index, e)}
					class="aspect-square w-full rounded-xl border-0 bg-white text-center text-xl font-semibold text-gray-900 shadow-xs ring-1 ring-inset focus:ring-2 focus:outline-none disabled:opacity-50 dark:bg-white/5 dark:text-white {error
						? 'ring-danger-400 focus:ring-danger-500'
						: input
							? 'ring-primary-400 focus:ring-primary-500'
							: 'focus:ring-primary-500 ring-gray-200 dark:ring-white/10'}"
				/>
			{/each}
		</div>
		{#if error}
			<p class="text-danger-600 dark:text-danger-400 mt-2 text-sm" role="alert">{error}</p>
		{/if}
	</fieldset>

	<Button
		onclick={handleVerify}
		size="large"
		fullWidth
		{loading}
		disabled={verificationCode.length !== 6}
	>
		{loading ? $t('auth.verifying') : $t('auth.verifyEmail')}
	</Button>

	<p class="text-sm text-gray-600 dark:text-gray-400">
		{$t('auth.didntReceiveCode')}
		{#if resendTimer > 0}
			<span class="text-gray-500">{$t('auth.resendIn')} {resendTimer}{$t('auth.seconds')}</span>
		{:else}
			<button
				type="button"
				onclick={handleResend}
				disabled={resending}
				class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium disabled:opacity-50"
			>
				{resending ? $t('auth.sending') : $t('auth.resendCode')}
			</button>
		{/if}
	</p>

	<div class="rounded-xl bg-gray-50 p-4 ring-1 ring-gray-200/80 dark:bg-white/5 dark:ring-white/10">
		<p class="text-sm font-medium text-gray-900 dark:text-white">{$t('auth.cantFindEmail')}</p>
		<ul class="mt-2 list-disc space-y-1 ps-4 text-xs text-gray-600 dark:text-gray-400">
			<li>{$t('auth.checkSpam')}</li>
			<li>{$t('auth.correctEmail')}</li>
			<li>{$t('auth.codeExpires')}</li>
		</ul>
	</div>

	<p class="text-sm text-gray-600 dark:text-gray-400">
		{$t('auth.wrongEmail')}
		<a
			href="/register"
			class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium"
		>
			{$t('auth.startOver')}
		</a>
	</p>
</div>

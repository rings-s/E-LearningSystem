<!-- front/src/routes/(auth)/forgot-password/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { authApi } from '#lib/apis/auth.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t } from '#lib/i18n/index.js';
	import { validators, validateForm } from '#lib/utils/validators.js';
	import { classNames } from '#lib/utils/helpers.js';
	import Input from '#lib/components/common/Input.svelte';
	import Button from '#lib/components/common/Button.svelte';

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
			error = err.message || $t('errors.resetPasswordFailed');
		} finally {
			loading = false;
		}
	};
</script>

<svelte:head>
	<title>{$t('auth.forgotPassword')} · Ilmora</title>
</svelte:head>

{#if submitted}
	<div class="text-center sm:text-start">
		<span
			class="bg-success-50 text-success-600 dark:bg-success-400/10 dark:text-success-400 mx-auto flex size-12 items-center justify-center rounded-2xl sm:mx-0"
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
			{$t('auth.checkEmail')}
		</h1>
		<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
			{$t('auth.resetLinkSent')}
			<strong class="font-medium text-gray-900 dark:text-white">{email}</strong>
		</p>

		<Button
			href={`/reset-password?email=${encodeURIComponent(email)}`}
			size="large"
			fullWidth
			class="mt-8"
		>
			{$t('auth.enterResetCode')}
		</Button>

		<p class="mt-6 text-sm text-gray-600 dark:text-gray-400">
			{$t('auth.didntReceiveEmail')}
			<button
				type="button"
				onclick={() => (submitted = false)}
				class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium"
			>
				{$t('auth.tryAgain')}
			</button>
		</p>
	</div>
{:else}
	<h1 class="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
		{$t('auth.forgotPassword')}
	</h1>
	<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">{$t('auth.enterEmailForReset')}</p>

	<form onsubmit={handleSubmit} class="mt-8 space-y-5" novalidate>
		<Input
			type="email"
			name="email"
			label={$t('auth.email')}
			autocomplete="email"
			bind:value={email}
			{error}
			required
			placeholder={$t('auth.enterEmail')}
		/>
		<Button type="submit" size="large" fullWidth {loading}>
			{loading ? $t('auth.sending') : $t('auth.sendResetLink')}
		</Button>
	</form>

	<p class="mt-8 text-sm text-gray-600 dark:text-gray-400">
		{$t('auth.rememberPassword')}
		<a
			href="/login"
			class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium"
		>
			{$t('auth.login')}
		</a>
	</p>
{/if}

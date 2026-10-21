<!-- front/src/routes/(auth)/login/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { authStore, isLoading } from '#lib/stores/auth.store.js';
	import { t } from '#lib/i18n/index.js';
	import { validators } from '#lib/utils/validators.js';
	import Input from '#lib/components/common/Input.svelte';
	import Button from '#lib/components/common/Button.svelte';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let rememberMe = $state(false);

	// Field validation states
	let emailTouched = $state(false);
	let passwordTouched = $state(false);

	// Computed validation
	const emailValid = $derived(validators.email(email));
	const passwordValid = $derived(validators.password(password));
	const formValid = $derived(emailValid && passwordValid && email && password);

	// Field errors
	const emailError = $derived(
		emailTouched && email && !emailValid ? $t('errors.invalidEmail') : ''
	);
	const passwordError = $derived(
		passwordTouched && password && !passwordValid ? $t('errors.passwordTooShort') : ''
	);

	async function handleSubmit(e) {
		e.preventDefault();

		// Mark all fields as touched
		emailTouched = true;
		passwordTouched = true;

		if (!formValid) return;

		error = '';
		const result = await authStore.login({ email, password });

		if (result.success) {
			goto('/dashboard');
		} else {
			error = result.error;
		}
	}
</script>

<svelte:head>
	<title>{$t('auth.login')} · Ilmora</title>
</svelte:head>

<h1 class="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
	{$t('auth.welcomeBack')}
</h1>
<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
	{$t('auth.dontHaveAccount')}
	<a
		href="/register"
		class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium"
	>
		{$t('auth.register')}
	</a>
</p>

<form onsubmit={handleSubmit} class="mt-8 space-y-5" novalidate>
	<Input
		id="email"
		name="email"
		type="email"
		label={$t('auth.email')}
		autocomplete="email"
		required
		bind:value={email}
		onblur={() => (emailTouched = true)}
		error={emailError}
		placeholder={$t('auth.enterEmail')}
	/>

	<div class="space-y-2">
		<Input
			id="password"
			name="password"
			type="password"
			label={$t('auth.password')}
			autocomplete="current-password"
			required
			showPasswordToggle
			bind:value={password}
			onblur={() => (passwordTouched = true)}
			error={passwordError}
			placeholder={$t('auth.enterPassword')}
		/>
		<div class="flex items-center justify-between">
			<label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
				<input
					type="checkbox"
					bind:checked={rememberMe}
					class="text-primary-600 focus:ring-primary-500 size-4 rounded border-gray-300 dark:border-white/20 dark:bg-white/5"
				/>
				{$t('auth.rememberMe')}
			</label>
			<a
				href="/forgot-password"
				class="text-primary-600 hover:text-primary-700 dark:text-primary-400 text-sm font-medium"
			>
				{$t('auth.forgotPassword')}
			</a>
		</div>
	</div>

	{#if error}
		<div
			class="bg-danger-50 text-danger-800 ring-danger-600/15 dark:bg-danger-400/10 dark:text-danger-200 rounded-xl p-3 text-sm ring-1"
			role="alert"
		>
			{error}
		</div>
	{/if}

	<Button type="submit" size="large" fullWidth loading={$isLoading} disabled={!formValid}>
		{$isLoading ? $t('auth.loggingIn') : $t('auth.login')}
	</Button>
</form>

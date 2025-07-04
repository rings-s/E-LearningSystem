<!-- front/src/routes/(auth)/forgot-password/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { authApi } from '$lib/apis/auth.js';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { t } from '$lib/i18n/index.js';
	import { validators, validateForm } from '$lib/utils/validators.js';
	import { classNames } from '$lib/utils/helpers.js';
	import FormField from '$lib/components/auth/FormField.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Logo from '$lib/components/common/Logo.svelte';

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
	<title>{$t('auth.forgotPassword')} - EduVerse</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
	<div class="w-full max-w-md">
		<div class="mb-8 text-center">
			<Logo size="large" showText={false} class="mx-auto mb-6" />
			<h2 class="text-3xl font-bold text-gray-900 sm:text-4xl dark:text-white">
				{$t('auth.forgotPassword')}
			</h2>
			<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
				{submitted ? $t('auth.checkEmailForReset') : $t('auth.enterEmailForReset')}
			</p>
		</div>

		<Card
			variant="bordered"
			padding="large"
			class="bg-white/90 backdrop-blur-sm dark:bg-gray-800/90"
		>
			{#if submitted}
				<div class="space-y-6 text-center">
					<div
						class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-green-400 to-emerald-600 shadow-xl"
					>
						<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
							/>
						</svg>
					</div>

					<div>
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
							{$t('auth.checkEmail')}
						</h3>
						<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
							{$t('auth.resetLinkSent')}
							<strong class="text-gray-900 dark:text-white">{email}</strong>
						</p>
					</div>

					<Button
						href={`/reset-password?email=${encodeURIComponent(email)}`}
						variant="primary"
						fullWidth
						class="from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 bg-gradient-to-r"
					>
						{$t('auth.enterResetCode')}
					</Button>

					<div class="space-y-3">
						<p class="text-sm text-gray-600 dark:text-gray-400">
							{$t('auth.didntReceiveEmail')}
						</p>
						<div class="flex flex-col justify-center gap-2 sm:flex-row">
							<button
								onclick={() => (submitted = false)}
								class="text-primary-600 hover:text-primary-500 dark:text-primary-400 text-sm font-medium transition-colors"
							>
								{$t('auth.tryAgain')}
							</button>
							<span class="hidden text-gray-400 sm:inline">•</span>
							<a
								href="/help"
								class="text-primary-600 hover:text-primary-500 dark:text-primary-400 text-sm font-medium transition-colors"
							>
								{$t('auth.contactSupport')}
							</a>
						</div>
					</div>
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
						placeholder={$t('auth.enterEmail')}
						icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
					/>

					<Button
						type="submit"
						variant="primary"
						size="large"
						fullWidth
						{loading}
						class="from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 transform bg-gradient-to-r transition-all duration-300 hover:scale-[1.02]"
					>
						{loading ? $t('auth.sending') : $t('auth.sendResetLink')}
					</Button>
				</form>
			{/if}
		</Card>

		<div class="mt-6 text-center">
			<p class="text-sm text-gray-600 dark:text-gray-400">
				{$t('auth.rememberPassword')}
				<a
					href="/login"
					class="text-primary-600 hover:text-primary-500 dark:text-primary-400 font-medium transition-colors"
				>
					{$t('auth.login')}
				</a>
			</p>
		</div>
	</div>
</div>

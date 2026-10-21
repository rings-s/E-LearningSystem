<script>
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { authApi } from '#lib/apis/auth.js';
	import { uiStore } from '#lib/stores/ui.store.js';
	import { t } from '#lib/i18n/index.js';
	import { validators, validateForm } from '#lib/utils/validators.js';
	import { classNames } from '#lib/utils/helpers.js';
	import FormField from '#lib/components/auth/FormField.svelte';
	import Button from '#lib/components/common/Button.svelte';

	const email = page.url.searchParams.get('email') || '';
	const code = page.url.searchParams.get('code') || '';

	let formData = $state({
		email,
		reset_code: code,
		new_password: '',
		confirm_password: ''
	});

	let errors = $state({});
	let loading = $state(false);
	let touched = $state({});

	const validationRules = {
		email: [
			{ validator: validators.required, message: $t('errors.requiredField') },
			{ validator: validators.email, message: $t('errors.invalidEmail') }
		],
		reset_code: [
			{ validator: validators.required, message: $t('auth.resetCodeRequired') },
			{ validator: validators.minLength(6), message: $t('auth.invalidResetCode') }
		],
		new_password: [
			{ validator: validators.required, message: $t('errors.requiredField') },
			{ validator: validators.minLength(8), message: $t('errors.passwordTooShort') }
		],
		confirm_password: [
			{
				validator: validators.required,
				message: $t('errors.requiredField')
			},

			{
				validator: validators.matchField('new_password'),
				message: $t('errors.passwordsDoNotMatch')
			}
		]
	};

	const passwordStrength = $derived.by(() => {
		const password = formData.new_password;
		if (!password) return { score: 0, text: '', color: '#6b7280' };
		let score = 0;
		if (password.length >= 8) score++;
		if (/[a-z]/.test(password)) score++;
		if (/[A-Z]/.test(password)) score++;
		if (/\d/.test(password)) score++;
		if (/[^A-Za-z0-9]/.test(password)) score++;

		const levels = [
			{ score: 0, text: '', color: '#6b7280' },
			{ score: 1, text: $t('auth.veryWeak'), color: '#ef4444' },
			{ score: 2, text: $t('auth.weak'), color: '#f97316' },
			{ score: 3, text: $t('auth.fair'), color: '#eab308' },
			{ score: 4, text: $t('auth.good'), color: '#3b82f6' },
			{ score: 5, text: $t('auth.strong'), color: '#22c55e' }
		];
		return levels[score];
	});

	const handleFieldBlur = (fieldName) => {
		touched[fieldName] = true;
		validateField(fieldName);
	};

	const validateField = (fieldName) => {
		const value = formData[fieldName];
		const rules = validationRules[fieldName] || [];
		for (const rule of rules) {
			if (!rule.validator(value, formData)) {
				errors[fieldName] = rule.message;
				return false;
			}
		}
		delete errors[fieldName];
		errors = { ...errors };
		return true;
	};

	const getFieldError = (fieldName) => {
		return touched[fieldName] ? errors[fieldName] : '';
	};

	const handleSubmit = async (e) => {
		e.preventDefault();

		Object.keys(formData).forEach((field) => {
			touched[field] = true;
			validateField(field);
		});

		const validation = validateForm(formData, validationRules);
		if (!validation.isValid) {
			errors = validation.errors;
			return;
		}

		loading = true;

		try {
			await authApi.confirmPasswordReset(formData);

			uiStore.showNotification({
				type: 'success',
				title: $t('auth.passwordChanged'),
				message: $t('auth.passwordResetSuccess')
			});

			goto('/login');
		} catch (err) {
			uiStore.showNotification({
				type: 'error',
				title: $t('common.error'),
				message: err.message || $t('auth.resetPasswordFailed')
			});
		} finally {
			loading = false;
		}
	};
</script>

<svelte:head><title>{$t('auth.resetPassword')} · Ilmora</title></svelte:head>

<h1 class="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
	{$t('auth.resetPassword')}
</h1>
<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">{$t('auth.enterCodeAndNewPassword')}</p>

<form onsubmit={handleSubmit} class="mt-8 space-y-5" novalidate>
	{#if !email}
		<FormField
			type="email"
			name="email"
			label={$t('auth.email')}
			bind:value={formData.email}
			error={getFieldError('email')}
			onblur={() => handleFieldBlur('email')}
			required
			placeholder={$t('auth.enterEmail')}
		/>
	{:else}
		<div
			class="rounded-xl bg-gray-50 p-3 ring-1 ring-gray-200/80 dark:bg-white/5 dark:ring-white/10"
		>
			<p class="text-sm text-gray-600 dark:text-gray-400">
				{$t('auth.resettingPasswordFor')}:
				<strong class="text-gray-900 dark:text-white">{email}</strong>
			</p>
		</div>
	{/if}

	<FormField
		name="reset_code"
		label={$t('auth.resetCode')}
		bind:value={formData.reset_code}
		error={getFieldError('reset_code')}
		onblur={() => handleFieldBlur('reset_code')}
		placeholder={$t('auth.enter6DigitCode')}
		required
	/>

	<div class="space-y-4">
		<FormField
			type="password"
			name="new_password"
			label={$t('auth.newPassword')}
			bind:value={formData.new_password}
			error={getFieldError('new_password')}
			onblur={() => handleFieldBlur('new_password')}
			required
			placeholder={$t('auth.enterNewPassword')}
		/>

		{#if formData.new_password}
			<div class="space-y-2">
				<div class="flex items-center justify-between">
					<span class="text-sm text-gray-600 dark:text-gray-400"
						>{$t('auth.passwordStrength')}:</span
					>
					<span class="text-sm font-medium" style="color: {passwordStrength.color}">
						{passwordStrength.text}
					</span>
				</div>
				<div class="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
					<div
						class="h-2 rounded-full transition-all duration-500 ease-out"
						style="width: {(passwordStrength.score / 5) *
							100}%; background-color: {passwordStrength.color}"
					></div>
				</div>
			</div>
		{/if}

		<FormField
			type="password"
			name="confirm_password"
			label={$t('auth.confirmPassword')}
			bind:value={formData.confirm_password}
			error={getFieldError('confirm_password')}
			onblur={() => handleFieldBlur('confirm_password')}
			required
			placeholder={$t('auth.reenterPassword')}
		/>
	</div>

	<Button type="submit" variant="primary" size="large" fullWidth {loading}>
		{loading ? $t('auth.resetting') : $t('auth.resetPassword')}
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

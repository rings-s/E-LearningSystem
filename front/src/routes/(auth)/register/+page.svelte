<!-- front/src/routes/(auth)/register/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { authStore } from '#lib/stores/auth.store.js';
	import { t } from '#lib/i18n/index.js';
	import { validators } from '#lib/utils/validators.js';
	import { ROLES } from '#lib/utils/constants.js';
	import Input from '#lib/components/common/Input.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Steps from '#lib/components/common/Steps.svelte';

	// State
	let currentStep = $state(0);
	let loading = $state(false);
	let submitError = $state('');

	let formData = $state({
		role: '',
		first_name: '',
		last_name: '',
		email: '',
		phone_number: '',
		date_of_birth: '',
		password: '',
		confirm_password: ''
	});

	let touched = $state({});

	// Validation
	const validateField = (field, value) => {
		switch (field) {
			case 'role':
				return !!value;
			case 'first_name':
			case 'last_name':
				return value && value.length >= 2;
			case 'email':
				return validators.email(value);
			case 'password':
				return validators.password(value);
			case 'confirm_password':
				return value === formData.password;
			default:
				return true;
		}
	};

	const getFieldError = (field) => {
		if (!touched[field]) return '';

		const value = formData[field];
		if (!validateField(field, value)) {
			switch (field) {
				case 'role':
					return $t('auth.selectAccountType');
				case 'first_name':
				case 'last_name':
					return $t('auth.nameTooShort');
				case 'email':
					return $t('errors.invalidEmail');
				case 'password':
					return $t('errors.passwordTooShort');
				case 'confirm_password':
					return $t('errors.passwordsDoNotMatch');
				default:
					return '';
			}
		}
		return '';
	};

	// Step validation
	const stepValid = $derived.by(() => {
		const stepFields = [
			['role'],
			['first_name', 'last_name', 'email'],
			['password', 'confirm_password']
		][currentStep];

		return stepFields.every((field) => validateField(field, formData[field]));
	});

	// Password strength
	const passwordStrength = $derived.by(() => {
		const password = formData.password;
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

	// Handlers
	function handleFieldBlur(field) {
		touched[field] = true;
	}

	function nextStep() {
		if (stepValid) {
			currentStep = Math.min(currentStep + 1, 2);
		}
	}

	function prevStep() {
		currentStep = Math.max(currentStep - 1, 0);
	}

	async function handleSubmit() {
		// Mark all fields as touched
		Object.keys(formData).forEach((field) => (touched[field] = true));

		if (!stepValid) return;

		// The API rejects "" for optional fields like date_of_birth, so leave empty ones out
		const payload = Object.fromEntries(
			Object.entries(formData).filter(
				([key, value]) => !['phone_number', 'date_of_birth'].includes(key) || value
			)
		);

		loading = true;
		submitError = '';
		const result = await authStore.register(payload);
		loading = false;

		if (result.success) {
			goto(`/verify-email?email=${encodeURIComponent(formData.email)}`);
		} else {
			submitError = result.error || $t('auth.registrationFailed');
		}
	}

	// Role options
	const roleOptions = [
		{
			value: ROLES.STUDENT,
			label: $t('auth.student'),
			description: $t('auth.studentDescription'),
			icon: 'M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z'
		},
		{
			value: ROLES.TEACHER,
			label: $t('auth.teacher'),
			description: $t('auth.teacherDescription'),
			icon: 'M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25'
		}
	];

	const steps = [
		{ title: $t('auth.accountType'), description: $t('auth.chooseRole') },
		{ title: $t('auth.personalInfo'), description: $t('auth.tellUsAboutYou') },
		{ title: $t('auth.security'), description: $t('auth.secureAccount') }
	];
</script>

<svelte:head>
	<title>{$t('auth.register')} · Ilmora</title>
</svelte:head>

<h1 class="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
	{$t('auth.createAccount')}
</h1>
<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
	{$t('auth.alreadyHaveAccount')}
	<a
		href="/login"
		class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium"
	>
		{$t('auth.login')}
	</a>
</p>

<Steps {steps} currentStep={currentStep + 1} compact class="mt-8" />

<div class="mt-8">
	{#if currentStep === 0}
		<fieldset class="space-y-3">
			<legend class="sr-only">{$t('auth.chooseAccountType')}</legend>
			{#each roleOptions as option}
				{@const selected = formData.role === option.value}
				<button
					type="button"
					onclick={() => {
						formData.role = option.value;
						touched.role = true;
					}}
					aria-pressed={selected}
					class="flex w-full items-center gap-4 rounded-2xl p-4 text-start ring-1 transition-colors {selected
						? 'bg-primary-50 ring-primary-600 dark:bg-primary-400/10 dark:ring-primary-400 ring-2'
						: 'ring-gray-200 hover:bg-gray-50 dark:ring-white/10 dark:hover:bg-white/5'}"
				>
					<span
						class="flex size-10 shrink-0 items-center justify-center rounded-xl {selected
							? 'bg-primary-600 text-white'
							: 'bg-gray-100 text-gray-600 dark:bg-white/10 dark:text-gray-300'}"
					>
						<svg
							class="size-5"
							fill="none"
							stroke="currentColor"
							stroke-width="1.75"
							viewBox="0 0 24 24"
						>
							<path stroke-linecap="round" stroke-linejoin="round" d={option.icon} />
						</svg>
					</span>
					<span class="min-w-0 flex-1">
						<span class="block text-sm font-semibold text-gray-900 dark:text-white"
							>{option.label}</span
						>
						<span class="block text-sm text-gray-600 dark:text-gray-400">{option.description}</span>
					</span>
					<span
						class="flex size-5 shrink-0 items-center justify-center rounded-full ring-1 {selected
							? 'bg-primary-600 ring-primary-600'
							: 'ring-gray-300 dark:ring-white/20'}"
						aria-hidden="true"
					>
						{#if selected}<span class="size-2 rounded-full bg-white"></span>{/if}
					</span>
				</button>
			{/each}
			{#if getFieldError('role')}
				<p class="text-danger-600 dark:text-danger-400 text-sm">{getFieldError('role')}</p>
			{/if}
		</fieldset>
	{:else if currentStep === 1}
		<div class="space-y-4">
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
				<Input
					label={$t('auth.firstName')}
					autocomplete="given-name"
					bind:value={formData.first_name}
					onblur={() => handleFieldBlur('first_name')}
					error={getFieldError('first_name')}
					placeholder={$t('auth.enterFirstName')}
				/>
				<Input
					label={$t('auth.lastName')}
					autocomplete="family-name"
					bind:value={formData.last_name}
					onblur={() => handleFieldBlur('last_name')}
					error={getFieldError('last_name')}
					placeholder={$t('auth.enterLastName')}
				/>
			</div>
			<Input
				type="email"
				label={$t('auth.email')}
				autocomplete="email"
				bind:value={formData.email}
				onblur={() => handleFieldBlur('email')}
				error={getFieldError('email')}
				placeholder={$t('auth.enterEmail')}
			/>
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
				<Input
					type="tel"
					label="{$t('auth.phoneNumber')} ({$t('common.optional')})"
					autocomplete="tel"
					bind:value={formData.phone_number}
					placeholder="+1234567890"
				/>
				<Input
					type="date"
					label="{$t('auth.dateOfBirth')} ({$t('common.optional')})"
					bind:value={formData.date_of_birth}
				/>
			</div>
		</div>
	{:else if currentStep === 2}
		<div class="space-y-4">
			<div class="space-y-2">
				<Input
					type="password"
					label={$t('auth.password')}
					autocomplete="new-password"
					showPasswordToggle
					bind:value={formData.password}
					onblur={() => handleFieldBlur('password')}
					error={getFieldError('password')}
					placeholder={$t('auth.enterPassword')}
				/>
				{#if formData.password}
					<div class="flex items-center gap-3">
						<div class="h-1.5 flex-1 overflow-hidden rounded-full bg-gray-100 dark:bg-white/10">
							<div
								class="h-full rounded-full transition-[width] duration-300"
								style="width: {(passwordStrength.score / 5) *
									100}%; background-color: {passwordStrength.color}"
							></div>
						</div>
						<span class="text-xs font-medium" style="color: {passwordStrength.color}">
							{passwordStrength.text}
						</span>
					</div>
				{/if}
			</div>
			<Input
				type="password"
				label={$t('auth.confirmPassword')}
				autocomplete="new-password"
				showPasswordToggle
				bind:value={formData.confirm_password}
				onblur={() => handleFieldBlur('confirm_password')}
				error={getFieldError('confirm_password')}
				placeholder={$t('auth.reenterPassword')}
			/>
			<p class="text-xs text-gray-500 dark:text-gray-400">
				{$t('auth.termsAgreement')}
				{$t('auth.termsOfService')}
				{$t('common.and')}
				{$t('auth.privacyPolicy')}.
			</p>
		</div>
	{/if}

	{#if submitError}
		<div
			class="bg-danger-50 text-danger-800 ring-danger-600/15 dark:bg-danger-400/10 dark:text-danger-200 mt-6 rounded-xl p-3 text-sm ring-1"
			role="alert"
		>
			{submitError}
		</div>
	{/if}

	<div class="mt-8 flex gap-3">
		{#if currentStep > 0}
			<Button variant="outline" size="large" onclick={prevStep}>{$t('common.previous')}</Button>
		{/if}
		{#if currentStep < 2}
			<Button size="large" class="flex-1" onclick={nextStep} disabled={!stepValid}>
				{$t('common.next')}
			</Button>
		{:else}
			<Button size="large" class="flex-1" onclick={handleSubmit} disabled={!stepValid} {loading}>
				{loading ? $t('auth.creating') : $t('auth.createAccount')}
			</Button>
		{/if}
	</div>
</div>

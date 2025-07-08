<!-- front/src/routes/(auth)/register/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.store.js';
	import { t } from '$lib/i18n/index.js';
	import { validators } from '$lib/utils/validators.js';
	import { ROLES } from '$lib/utils/constants.js';

	// State
	let currentStep = $state(0);
	let loading = $state(false);

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
	const stepValid = $derived(() => {
		const stepFields = [
			['role'],
			['first_name', 'last_name', 'email'],
			['password', 'confirm_password']
		][currentStep];

		return stepFields.every(field => validateField(field, formData[field]));
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
		Object.keys(formData).forEach(field => touched[field] = true);

		if (!stepValid) return;

		loading = true;
		const result = await authStore.register(formData);
		loading = false;

		if (result.success) {
			goto(`/verify-email?email=${encodeURIComponent(formData.email)}`);
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
	<title>{$t('auth.register')} - 244SCHOOL</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8 dark:bg-gray-900">
	<!-- Header -->
	<div class="sm:mx-auto sm:w-full sm:max-w-2xl">
		<div class="flex justify-center">
			<div class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-3 shadow-lg">
				<span class="text-white text-xl font-bold">244</span>
			</div>
		</div>
		<h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
			{$t('auth.createAccount')}
		</h2>
		<p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
			{$t('auth.alreadyHaveAccount')}
			<a href="/login" class="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
				{$t('auth.login')}
			</a>
		</p>
	</div>

	<!-- Progress Steps -->
	<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
		<nav aria-label="Progress">
			<ol class="flex items-center">
				{#each steps as step, index}
					<li class="relative {index !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''} flex-1">
						<!-- Step Content -->
						<div class="flex items-center">
							<div class="relative flex h-8 w-8 items-center justify-center rounded-full {
								index < currentStep ? 'bg-indigo-600' :
								index === currentStep ? 'border-2 border-indigo-600 bg-white dark:bg-gray-800' :
								'border-2 border-gray-300 bg-white dark:bg-gray-800 dark:border-gray-600'
							}">
								{#if index < currentStep}
									<svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
									</svg>
								{:else}
									<span class="text-sm font-medium {index === currentStep ? 'text-indigo-600' : 'text-gray-500 dark:text-gray-400'}">{index + 1}</span>
								{/if}
							</div>
							<span class="ml-4 text-sm font-medium {index === currentStep ? 'text-indigo-600' : index < currentStep ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">{step.title}</span>
						</div>

						<!-- Connector -->
						{#if index !== steps.length - 1}
							<div class="absolute top-4 left-4 -ml-px mt-0.5 h-0.5 w-full bg-gray-300 dark:bg-gray-600" aria-hidden="true"></div>
						{/if}
					</li>
				{/each}
			</ol>
		</nav>
	</div>

	<!-- Main Card -->
	<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
		<div class="bg-white py-8 px-4 shadow-sm rounded-xl border border-gray-200 sm:px-10 dark:bg-gray-800 dark:border-gray-700">
			
			{#if currentStep === 0}
				<!-- Step 1: Account Type -->
				<div class="space-y-6">
					<div class="text-center">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">{$t('auth.chooseAccountType')}</h3>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">{$t('auth.chooseRole')}</p>
					</div>

					<div class="space-y-4">
						{#each roleOptions as option}
							<button
								type="button"
								onclick={() => formData.role = option.value}
								class="relative flex w-full cursor-pointer rounded-lg border p-4 focus:outline-none {
									formData.role === option.value 
										? 'border-indigo-600 ring-2 ring-indigo-600 bg-indigo-50 dark:bg-indigo-900/20' 
										: 'border-gray-300 hover:border-gray-400 dark:border-gray-600 dark:hover:border-gray-500'
								}"
							>
								<div class="flex items-center w-full">
									<div class="flex-shrink-0">
										<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600">
											<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={option.icon} />
											</svg>
										</div>
									</div>
									<div class="ml-4 flex-1">
										<span class="block text-sm font-medium text-gray-900 dark:text-white">{option.label}</span>
										<span class="block text-sm text-gray-500 dark:text-gray-400">{option.description}</span>
									</div>
									{#if formData.role === option.value}
										<div class="flex-shrink-0">
											<svg class="h-5 w-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
										</div>
									{/if}
								</div>
							</button>
						{/each}
					</div>

					{#if getFieldError('role')}
						<div class="rounded-lg bg-red-50 p-4 border border-red-200 dark:bg-red-900/20 dark:border-red-800">
							<p class="text-sm text-red-800 dark:text-red-200">{getFieldError('role')}</p>
						</div>
					{/if}
				</div>

			{:else if currentStep === 1}
				<!-- Step 2: Personal Information -->
				<div class="space-y-6">
					<div class="text-center">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">{$t('auth.tellUsAboutYou')}</h3>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">{$t('auth.personalInfo')}</p>
					</div>

					<div class="space-y-4">
						<!-- Name Fields -->
						<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
							<div>
								<label class="block text-sm font-medium text-gray-900 dark:text-white">{$t('auth.firstName')}</label>
								<input
									type="text"
									bind:value={formData.first_name}
									onblur={() => handleFieldBlur('first_name')}
									class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 dark:bg-gray-700 dark:border-gray-600 dark:text-white {getFieldError('first_name') ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}"
									placeholder={$t('auth.enterFirstName')}
								/>
								{#if getFieldError('first_name')}
									<p class="mt-1 text-sm text-red-600 dark:text-red-400">{getFieldError('first_name')}</p>
								{/if}
							</div>

							<div>
								<label class="block text-sm font-medium text-gray-900 dark:text-white">{$t('auth.lastName')}</label>
								<input
									type="text"
									bind:value={formData.last_name}
									onblur={() => handleFieldBlur('last_name')}
									class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 dark:bg-gray-700 dark:border-gray-600 dark:text-white {getFieldError('last_name') ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}"
									placeholder={$t('auth.enterLastName')}
								/>
								{#if getFieldError('last_name')}
									<p class="mt-1 text-sm text-red-600 dark:text-red-400">{getFieldError('last_name')}</p>
								{/if}
							</div>
						</div>

						<!-- Email -->
						<div>
							<label class="block text-sm font-medium text-gray-900 dark:text-white">{$t('auth.email')}</label>
							<input
								type="email"
								bind:value={formData.email}
								onblur={() => handleFieldBlur('email')}
								class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 dark:bg-gray-700 dark:border-gray-600 dark:text-white {getFieldError('email') ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}"
								placeholder={$t('auth.enterEmail')}
							/>
							{#if getFieldError('email')}
								<p class="mt-1 text-sm text-red-600 dark:text-red-400">{getFieldError('email')}</p>
							{/if}
						</div>

						<!-- Optional Fields -->
						<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
							<div>
								<label class="block text-sm font-medium text-gray-900 dark:text-white">
									{$t('auth.phoneNumber')} 
									<span class="text-gray-500">({$t('common.optional')})</span>
								</label>
								<input
									type="tel"
									bind:value={formData.phone_number}
									class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
									placeholder="+1234567890"
								/>
							</div>

							<div>
								<label class="block text-sm font-medium text-gray-900 dark:text-white">
									{$t('auth.dateOfBirth')} 
									<span class="text-gray-500">({$t('common.optional')})</span>
								</label>
								<input
									type="date"
									bind:value={formData.date_of_birth}
									class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
								/>
							</div>
						</div>
					</div>
				</div>

			{:else if currentStep === 2}
				<!-- Step 3: Security -->
				<div class="space-y-6">
					<div class="text-center">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">{$t('auth.secureAccount')}</h3>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">{$t('auth.security')}</p>
					</div>

					<div class="space-y-4">
						<!-- Password -->
						<div>
							<label class="block text-sm font-medium text-gray-900 dark:text-white">{$t('auth.password')}</label>
							<input
								type="password"
								bind:value={formData.password}
								onblur={() => handleFieldBlur('password')}
								class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 dark:bg-gray-700 dark:border-gray-600 dark:text-white {getFieldError('password') ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}"
								placeholder={$t('auth.enterPassword')}
							/>
							{#if getFieldError('password')}
								<p class="mt-1 text-sm text-red-600 dark:text-red-400">{getFieldError('password')}</p>
							{/if}

							<!-- Password Strength -->
							{#if formData.password}
								<div class="mt-2">
									<div class="flex items-center justify-between text-sm">
										<span class="text-gray-600 dark:text-gray-400">{$t('auth.passwordStrength')}:</span>
										<span style="color: {passwordStrength.color}">{passwordStrength.text}</span>
									</div>
									<div class="mt-1 h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
										<div
											class="h-2 rounded-full transition-all duration-300"
											style="width: {(passwordStrength.score / 5) * 100}%; background-color: {passwordStrength.color}"
										></div>
									</div>
								</div>
							{/if}
						</div>

						<!-- Confirm Password -->
						<div>
							<label class="block text-sm font-medium text-gray-900 dark:text-white">{$t('auth.confirmPassword')}</label>
							<input
								type="password"
								bind:value={formData.confirm_password}
								onblur={() => handleFieldBlur('confirm_password')}
								class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 dark:bg-gray-700 dark:border-gray-600 dark:text-white {getFieldError('confirm_password') ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}"
								placeholder={$t('auth.reenterPassword')}
							/>
							{#if getFieldError('confirm_password')}
								<p class="mt-1 text-sm text-red-600 dark:text-red-400">{getFieldError('confirm_password')}</p>
							{/if}
						</div>

						<!-- Terms Agreement -->
						<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-900/50">
							<p class="text-xs text-gray-600 dark:text-gray-400">
								{$t('auth.termsAgreement')}
								<a href="/terms" class="text-indigo-600 underline hover:text-indigo-500 dark:text-indigo-400">{$t('auth.termsOfService')}</a>
								{$t('common.and')}
								<a href="/privacy" class="text-indigo-600 underline hover:text-indigo-500 dark:text-indigo-400">{$t('auth.privacyPolicy')}</a>
							</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Navigation Buttons -->
			<div class="mt-8 flex justify-between">
				<button
					type="button"
					onclick={prevStep}
					disabled={currentStep === 0}
					class="inline-flex justify-center rounded-lg border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-600"
				>
					{$t('common.previous')}
				</button>

				{#if currentStep < 2}
					<button
						type="button"
						onclick={nextStep}
						disabled={!stepValid}
						class="inline-flex justify-center rounded-lg border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
					>
						{$t('common.next')}
					</button>
				{:else}
					<button
						type="button"
						onclick={handleSubmit}
						disabled={!stepValid || loading}
						class="inline-flex justify-center rounded-lg border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
					>
						{#if loading}
							<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							{$t('auth.creating')}
						{:else}
							{$t('auth.createAccount')}
						{/if}
					</button>
				{/if}
			</div>
		</div>
	</div>
</div>
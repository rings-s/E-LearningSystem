<!-- front/src/routes/(auth)/login/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { authStore, isLoading } from '$lib/stores/auth.store.js';
	import { t } from '$lib/i18n/index.js';
	import { validators } from '$lib/utils/validators.js';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let showPassword = $state(false);
	let rememberMe = $state(false);

	// Field validation states
	let emailTouched = $state(false);
	let passwordTouched = $state(false);

	// Computed validation
	const emailValid = $derived(validators.email(email));
	const passwordValid = $derived(validators.password(password));
	const formValid = $derived(emailValid && passwordValid && email && password);

	// Field errors
	const emailError = $derived(emailTouched && email && !emailValid ? $t('errors.invalidEmail') : '');
	const passwordError = $derived(passwordTouched && password && !passwordValid ? $t('errors.passwordTooShort') : '');

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

	function togglePasswordVisibility() {
		showPassword = !showPassword;
	}
</script>

<svelte:head>
	<title>{$t('auth.login')} - 244SCHOOL</title>
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
			{$t('auth.welcomeBack')}
		</h2>
		<p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
			{$t('auth.dontHaveAccount')}
			<a href="/register" class="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
				{$t('auth.register')}
			</a>
		</p>
	</div>

	<!-- Main Card -->
	<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
		<div class="bg-white py-8 px-4 shadow-sm rounded-xl border border-gray-200 sm:px-10 dark:bg-gray-800 dark:border-gray-700">
			<form onsubmit={handleSubmit} class="space-y-6">
				<!-- Email Field -->
				<div>
					<label for="email" class="block text-sm font-medium leading-6 text-gray-900 dark:text-gray-100">
						{$t('auth.email')}
					</label>
					<div class="mt-2 relative">
						<input
							id="email"
							name="email"
							type="email"
							autocomplete="email"
							required
							bind:value={email}
							onblur={() => emailTouched = true}
							class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 dark:bg-gray-700 dark:text-white dark:ring-gray-600 dark:placeholder:text-gray-400 dark:focus:ring-indigo-500 {emailError ? 'ring-red-500 focus:ring-red-500' : ''}"
							placeholder={$t('auth.enterEmail')}
						/>
						{#if emailError}
							<div class="mt-1 flex items-center text-sm text-red-600 dark:text-red-400">
								<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								{emailError}
							</div>
						{/if}
					</div>
				</div>

				<!-- Password Field -->
				<div>
					<label for="password" class="block text-sm font-medium leading-6 text-gray-900 dark:text-gray-100">
						{$t('auth.password')}
					</label>
					<div class="mt-2 relative">
						<input
							id="password"
							name="password"
							type={showPassword ? 'text' : 'password'}
							autocomplete="current-password"
							required
							bind:value={password}
							onblur={() => passwordTouched = true}
							class="block w-full rounded-lg border-0 py-3 px-4 pr-12 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 dark:bg-gray-700 dark:text-white dark:ring-gray-600 dark:placeholder:text-gray-400 dark:focus:ring-indigo-500 {passwordError ? 'ring-red-500 focus:ring-red-500' : ''}"
							placeholder={$t('auth.enterPassword')}
						/>
						<button
							type="button"
							onclick={togglePasswordVisibility}
							class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
						>
							{#if showPassword}
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
								</svg>
							{:else}
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								</svg>
							{/if}
						</button>
						{#if passwordError}
							<div class="mt-1 flex items-center text-sm text-red-600 dark:text-red-400">
								<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								{passwordError}
							</div>
						{/if}
					</div>
				</div>

				<!-- Remember Me & Forgot Password -->
				<div class="flex items-center justify-between">
					<div class="flex items-center">
						<input
							id="remember-me"
							name="remember-me"
							type="checkbox"
							bind:checked={rememberMe}
							class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600 dark:border-gray-600 dark:bg-gray-700"
						/>
						<label for="remember-me" class="ml-3 block text-sm leading-6 text-gray-900 dark:text-gray-100">
							{$t('auth.rememberMe')}
						</label>
					</div>

					<div class="text-sm leading-6">
						<a href="/forgot-password" class="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
							{$t('auth.forgotPassword')}
						</a>
					</div>
				</div>

				<!-- Error Message -->
				{#if error}
					<div class="rounded-lg bg-red-50 p-4 border border-red-200 dark:bg-red-900/20 dark:border-red-800">
						<div class="flex">
							<div class="flex-shrink-0">
								<svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							</div>
							<div class="ml-3">
								<p class="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
							</div>
						</div>
					</div>
				{/if}

				<!-- Submit Button -->
				<div>
					<button
						type="submit"
						disabled={$isLoading || !formValid}
						class="flex w-full justify-center rounded-lg bg-indigo-600 px-3 py-3 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-indigo-500 dark:hover:bg-indigo-400"
					>
						{#if $isLoading}
							<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							{$t('auth.loggingIn')}
						{:else}
							{$t('auth.login')}
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
</div>
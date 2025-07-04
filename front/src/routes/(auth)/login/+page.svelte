<!-- front/src/routes/(auth)/login/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { authStore, isLoading } from '$lib/stores/auth.store.js';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let showPassword = $state(false);
	let emailFocused = $state(false);
	let passwordFocused = $state(false);

	async function handleSubmit(e) {
		e.preventDefault();
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
	<title>Login - Your App</title>
</svelte:head>

<div
	class="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4"
>
	<!-- Background Elements -->
	<div class="absolute inset-0 overflow-hidden">
		<div
			class="animate-blob absolute -top-40 -right-40 h-80 w-80 rounded-full bg-purple-300 opacity-70 mix-blend-multiply blur-xl filter"
		></div>
		<div
			class="animate-blob animation-delay-2000 absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-blue-300 opacity-70 mix-blend-multiply blur-xl filter"
		></div>
		<div
			class="animate-blob animation-delay-4000 absolute top-40 left-40 h-80 w-80 rounded-full bg-pink-300 opacity-70 mix-blend-multiply blur-xl filter"
		></div>
	</div>

	<!-- Login Card -->
	<div class="relative w-full max-w-md">
		<div
			class="relative overflow-hidden rounded-2xl border border-white/20 bg-white/80 p-8 shadow-2xl backdrop-blur-lg"
		>
			<!-- Card Header -->
			<div class="mb-8 text-center">
				<div
					class="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-purple-600"
				>
					<svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
						></path>
					</svg>
				</div>
				<h2
					class="mb-2 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-3xl font-bold text-transparent"
				>
					Welcome Back
				</h2>
				<p class="text-gray-600">Sign in to your account</p>
			</div>

			<!-- Login Form -->
			<form onsubmit={handleSubmit} class="space-y-6">
				<!-- Email Field -->
				<div class="relative">
					<label for="email-input" class="mb-2 block text-sm font-semibold text-gray-700">Email Address</label>
					<div class="relative">
						<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
							<svg
								class="h-5 w-5 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
								></path>
							</svg>
						</div>
						<input
							id="email-input"
							type="email"
							bind:value={email}
							onfocus={() => (emailFocused = true)}
							onblur={() => (emailFocused = false)}
							required
							class="w-full rounded-xl border-2 py-3 pr-4 pl-10 transition-all duration-200
                       {emailFocused
								? 'border-blue-500 ring-4 ring-blue-500/10'
								: 'border-gray-200 hover:border-gray-300'}
                       bg-white/50 backdrop-blur-sm focus:border-blue-500 focus:ring-4
                       focus:ring-blue-500/10 focus:outline-none"
							placeholder="Enter your email"
						/>
					</div>
				</div>

				<!-- Password Field -->
				<div class="relative">
					<label for="password-input" class="mb-2 block text-sm font-semibold text-gray-700">Password</label>
					<div class="relative">
						<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
							<svg
								class="h-5 w-5 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
								></path>
							</svg>
						</div>
						<input
							id="password-input"
							type={showPassword ? 'text' : 'password'}
							bind:value={password}
							onfocus={() => (passwordFocused = true)}
							onblur={() => (passwordFocused = false)}
							required
							class="w-full rounded-xl border-2 py-3 pr-12 pl-10 transition-all duration-200
                       {passwordFocused
								? 'border-blue-500 ring-4 ring-blue-500/10'
								: 'border-gray-200 hover:border-gray-300'}
                       bg-white/50 backdrop-blur-sm focus:border-blue-500 focus:ring-4
                       focus:ring-blue-500/10 focus:outline-none"
							placeholder="Enter your password"
						/>
						<button
							type="button"
							onclick={togglePasswordVisibility}
							class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 transition-colors hover:text-gray-600"
						>
							{#if showPassword}
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
									></path>
								</svg>
							{:else}
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
									></path>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
									></path>
								</svg>
							{/if}
						</button>
					</div>
				</div>

				<!-- Error Message -->
				{#if error}
					<div class="flex items-center space-x-2 rounded-xl border border-red-200 bg-red-50 p-3">
						<svg
							class="h-5 w-5 flex-shrink-0 text-red-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"
							></path>
						</svg>
						<p class="text-sm font-medium text-red-700">{error}</p>
					</div>
				{/if}

				<!-- Remember Me & Forgot Password -->
				<div class="flex items-center justify-between">
					<label class="flex items-center">
						<input
							type="checkbox"
							class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						/>
						<span class="ml-2 text-sm text-gray-600">Remember me</span>
					</label>
					<a href="/forgot-password" class="text-sm font-medium text-blue-600 hover:text-blue-800">
						Forgot password?
					</a>
				</div>

				<!-- Submit Button -->
				<button
					type="submit"
					disabled={$isLoading}
					class="w-full transform rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-3 font-semibold
                   text-white shadow-lg transition-all duration-200 hover:scale-[1.02] hover:from-blue-700
                   hover:to-purple-700 hover:shadow-xl focus:ring-4 focus:ring-blue-500/50 focus:outline-none
                   disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
				>
					{#if $isLoading}
						<div class="flex items-center justify-center">
							<svg
								class="mr-3 -ml-1 h-5 w-5 animate-spin text-white"
								fill="none"
								viewBox="0 0 24 24"
							>
								<circle
									class="opacity-25"
									cx="12"
									cy="12"
									r="10"
									stroke="currentColor"
									stroke-width="4"
								></circle>
								<path
									class="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
								></path>
							</svg>
							Signing in...
						</div>
					{:else}
						Sign In
					{/if}
				</button>
			</form>

			<!-- Register Link -->
			<p class="mt-8 text-center text-gray-600">
				Don't have an account?
				<a
					href="/register"
					class="font-semibold text-blue-600 transition-colors hover:text-blue-800 hover:underline"
				>
					Create one
				</a>
			</p>
		</div>
	</div>
</div>

<style>
	@keyframes blob {
		0% {
			transform: translate(0px, 0px) scale(1);
		}
		33% {
			transform: translate(30px, -50px) scale(1.1);
		}
		66% {
			transform: translate(-20px, 20px) scale(0.9);
		}
		100% {
			transform: translate(0px, 0px) scale(1);
		}
	}

	.animate-blob {
		animation: blob 7s infinite;
	}

	.animation-delay-2000 {
		animation-delay: 2s;
	}

	.animation-delay-4000 {
		animation-delay: 4s;
	}
</style>

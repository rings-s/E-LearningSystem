<script>
	import { fade } from 'svelte/transition';

	let {
		length = 6,
		value = '',
		error = '',
		disabled = false,
		onComplete = () => {},
		class: className = ''
	} = $props();

	let inputs = $state(Array(length).fill(''));
	let inputRefs = [];

	$effect(() => {
		value = inputs.join('');
		if (value.length === length) {
			onComplete(value);
		}
	});

	function handleInput(index, inputValue) {
		if (inputValue.length > 1) {
			// Handle paste
			const pastedCode = inputValue.slice(0, length);
			for (let i = 0; i < length; i++) {
				inputs[i] = pastedCode[i] || '';
			}
			const lastFilledIndex = Math.min(pastedCode.length - 1, length - 1);
			inputRefs[lastFilledIndex]?.focus();
		} else {
			inputs[index] = inputValue;
			if (inputValue && index < length - 1) {
				inputRefs[index + 1]?.focus();
			}
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
		} else if (e.key === 'ArrowRight' && index < length - 1) {
			inputRefs[index + 1]?.focus();
		}
	}

	export function clear() {
		inputs = Array(length).fill('');
		inputRefs[0]?.focus();
	}

	export function focus() {
		inputRefs[0]?.focus();
	}
</script>

<div class="space-y-4 {className}">
	<div class="flex justify-center gap-3">
		{#each inputs as input, index}
			<input
				bind:this={inputRefs[index]}
				type="text"
				inputmode="numeric"
				maxlength="1"
				value={input}
				{disabled}
				oninput={(e) => handleInput(index, e.target.value)}
				onkeydown={(e) => handleKeyDown(index, e)}
				class="h-14 w-14 rounded-2xl border-2 text-center text-xl font-bold transition-all duration-200 {error
					? 'border-red-300 bg-red-50 dark:border-red-600 dark:bg-red-900/20'
					: input
						? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
						: 'border-gray-300 hover:border-gray-400 dark:border-gray-600 dark:hover:border-gray-500'} focus:border-primary-500 focus:ring-primary-500/20 focus:ring-2 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-gray-800 dark:text-white"
				placeholder="•"
			/>
		{/each}
	</div>

	{#if error}
		<p
			class="flex items-center justify-center gap-1 text-center text-sm text-red-600 dark:text-red-400"
			in:fade
		>
			<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			{error}
		</p>
	{/if}
</div>

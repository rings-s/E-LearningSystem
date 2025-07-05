<!-- front/src/lib/components/course/VideoPlayer.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { courseStore, currentLearningProgress } from '$lib/stores/course.store.js';
	import { classNames } from '$lib/utils/helpers.js';

	let {
		url = '',
		duration = 0,
		onComplete = () => {},
		onProgress = () => {},
		autoplay = false,
		controls = true,
		class: className = ''
	} = $props();

	let videoElement;
	let containerElement;
	let isPlaying = $state(false);
	let currentTime = $state(0);
	let progress = $state(0);
	let volume = $state(1);
	let playbackRate = $state(1);
	let isFullscreen = $state(false);
	let showControls = $state(true);
	let controlsTimeout;
	let buffered = $state(0);
	let isMuted = $state(false);
	let isLoading = $state(true);

	onMount(() => {
		if (videoElement) {
			videoElement.addEventListener('timeupdate', handleTimeUpdate);
			videoElement.addEventListener('ended', handleEnded);
			videoElement.addEventListener('play', () => (isPlaying = true));
			videoElement.addEventListener('pause', () => (isPlaying = false));
			videoElement.addEventListener('progress', handleProgress);
			videoElement.addEventListener('loadeddata', () => (isLoading = false));
			videoElement.addEventListener('waiting', () => (isLoading = true));
			videoElement.addEventListener('canplay', () => (isLoading = false));

			// Load saved progress from derived store
			const savedProgress = $currentLearningProgress;
			if (savedProgress?.lastPosition) {
				videoElement.currentTime = savedProgress.lastPosition;
			}

			// Handle fullscreen changes
			document.addEventListener('fullscreenchange', handleFullscreenChange);
		}
	});

	onDestroy(() => {
		if (videoElement) {
			videoElement.removeEventListener('timeupdate', handleTimeUpdate);
			videoElement.removeEventListener('ended', handleEnded);
			videoElement.removeEventListener('progress', handleProgress);
		}
		document.removeEventListener('fullscreenchange', handleFullscreenChange);
		clearTimeout(controlsTimeout);
	});

	function handleTimeUpdate() {
		currentTime = videoElement.currentTime;
		progress = (currentTime / duration) * 100;

		// Save progress every 5 seconds
		if (Math.floor(currentTime) % 5 === 0) {
			onProgress({
				currentTime,
				progress,
				duration
			});
		}
	}

	function handleProgress() {
		if (videoElement.buffered.length > 0) {
			buffered = (videoElement.buffered.end(0) / duration) * 100;
		}
	}

	function handleEnded() {
		isPlaying = false;
		onComplete();
	}

	function handleFullscreenChange() {
		isFullscreen = !!document.fullscreenElement;
	}

	function togglePlay() {
		if (videoElement.paused) {
			videoElement.play();
		} else {
			videoElement.pause();
		}
	}

	function seek(e) {
		const rect = e.currentTarget.getBoundingClientRect();
		const pos = (e.clientX - rect.left) / rect.width;
		videoElement.currentTime = pos * duration;
	}

	function changeVolume(e) {
		volume = parseFloat(e.target.value);
		videoElement.volume = volume;
		isMuted = volume === 0;
	}

	function toggleMute() {
		if (isMuted) {
			videoElement.volume = volume || 0.5;
			isMuted = false;
		} else {
			videoElement.volume = 0;
			isMuted = true;
		}
	}

	function changeSpeed() {
		const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2];
		const currentIndex = speeds.indexOf(playbackRate);
		const nextIndex = (currentIndex + 1) % speeds.length;
		playbackRate = speeds[nextIndex];
		videoElement.playbackRate = playbackRate;
	}

	function toggleFullscreen() {
		if (!document.fullscreenElement) {
			containerElement.requestFullscreen();
		} else {
			document.exitFullscreen();
		}
	}

	function skip(seconds) {
		videoElement.currentTime = Math.max(0, Math.min(duration, currentTime + seconds));
	}

	function formatTime(seconds) {
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = Math.floor(seconds % 60);

		if (h > 0) {
			return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
		}
		return `${m}:${s.toString().padStart(2, '0')}`;
	}

	function showControlsTemporarily() {
		showControls = true;
		clearTimeout(controlsTimeout);

		if (controls && isPlaying) {
			controlsTimeout = setTimeout(() => {
				showControls = false;
			}, 3000);
		}
	}

	function handleKeydown(e) {
		switch (e.key) {
			case ' ':
			case 'k':
				e.preventDefault();
				togglePlay();
				break;
			case 'ArrowLeft':
				e.preventDefault();
				skip(-10);
				break;
			case 'ArrowRight':
				e.preventDefault();
				skip(10);
				break;
			case 'ArrowUp':
				e.preventDefault();
				volume = Math.min(1, volume + 0.1);
				videoElement.volume = volume;
				break;
			case 'ArrowDown':
				e.preventDefault();
				volume = Math.max(0, volume - 0.1);
				videoElement.volume = volume;
				break;
			case 'f':
				e.preventDefault();
				toggleFullscreen();
				break;
			case 'm':
				e.preventDefault();
				toggleMute();
				break;
		}
	}
</script>

<div
	bind:this={containerElement}
	class={classNames(
		'video-player relative overflow-hidden rounded-lg bg-black',
		isFullscreen && 'fixed inset-0 z-50',
		className
	)}
	onmousemove={showControlsTemporarily}
	onmouseleave={() => isPlaying && (showControls = false)}
	onkeydown={handleKeydown}
	tabindex="0"
>
	<video bind:this={videoElement} src={url} class="h-full w-full" {autoplay} playsinline />

	<!-- Loading Spinner -->
	{#if isLoading}
		<div class="absolute inset-0 flex items-center justify-center bg-black/50">
			<div
				class="h-12 w-12 animate-spin rounded-full border-4 border-white/30 border-t-white"
			></div>
		</div>
	{/if}

	<!-- Controls -->
	{#if controls}
		<div
			class={classNames(
				'absolute inset-0 flex flex-col justify-end transition-opacity duration-300',
				showControls ? 'opacity-100' : 'pointer-events-none opacity-0'
			)}
		>
			<!-- Gradient Overlay -->
			<div
				class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent"
			></div>

			<!-- Control Bar -->
			<div class="relative space-y-2 p-4">
				<!-- Progress Bar -->
				<div class="group h-1 cursor-pointer transition-all duration-200 hover:h-2" onclick={seek}>
					<div class="relative h-full overflow-hidden rounded-full bg-white/30">
						<!-- Buffered -->
						<div class="absolute inset-y-0 left-0 bg-white/40" style="width: {buffered}%"></div>

						<!-- Progress -->
						<div class="bg-primary-500 absolute inset-y-0 left-0" style="width: {progress}%">
							<div
								class="absolute top-1/2 right-0 h-3 w-3 -translate-y-1/2 rounded-full bg-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100"
							></div>
						</div>
					</div>
				</div>

				<!-- Controls Row -->
				<div class="flex items-center justify-between">
					<!-- Left Controls -->
					<div class="flex items-center space-x-4">
						<!-- Play/Pause -->
						<button
							onclick={togglePlay}
							class="text-white transition-colors hover:text-gray-200"
							aria-label={isPlaying ? 'Pause' : 'Play'}
						>
							{#if isPlaying}
								<svg class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
									<path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
								</svg>
							{:else}
								<svg class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
									<path d="M8 5v14l11-7z" />
								</svg>
							{/if}
						</button>

						<!-- Skip Buttons -->
						<button
							onclick={() => skip(-10)}
							class="text-white transition-colors hover:text-gray-200"
							aria-label="Skip backward 10 seconds"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 8V4m0 0L8 8m4-4l4 4m-4 4v8"
								/>
							</svg>
							<span class="text-xs">-10</span>
						</button>

						<button
							onclick={() => skip(10)}
							class="text-white transition-colors hover:text-gray-200"
							aria-label="Skip forward 10 seconds"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 16v4m0 0l4-4m-4 4l-4-4m4-4V4"
								/>
							</svg>
							<span class="text-xs">+10</span>
						</button>

						<!-- Volume -->
						<div class="flex items-center space-x-2">
							<button
								onclick={toggleMute}
								class="text-white transition-colors hover:text-gray-200"
								aria-label={isMuted ? 'Unmute' : 'Mute'}
							>
								{#if isMuted || volume === 0}
									<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
											clip-rule="evenodd"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
										/>
									</svg>
								{:else}
									<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
										/>
									</svg>
								{/if}
							</button>

							<input
								type="range"
								min="0"
								max="1"
								step="0.1"
								value={isMuted ? 0 : volume}
								onchange={changeVolume}
								class="slider h-1 w-20 cursor-pointer appearance-none rounded-lg bg-white/30"
								aria-label="Volume"
							/>
						</div>

						<!-- Time Display -->
						<div class="text-sm text-white">
							<span>{formatTime(currentTime)}</span>
							<span class="mx-1">/</span>
							<span>{formatTime(duration)}</span>
						</div>
					</div>

					<!-- Right Controls -->
					<div class="flex items-center space-x-4">
						<!-- Playback Speed -->
						<button
							onclick={changeSpeed}
							class="text-sm font-medium text-white transition-colors hover:text-gray-200"
							aria-label="Change playback speed"
						>
							{playbackRate}x
						</button>

						<!-- Fullscreen -->
						<button
							onclick={toggleFullscreen}
							class="text-white transition-colors hover:text-gray-200"
							aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
						>
							{#if isFullscreen}
								<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 9V5H5m0 4h4m6 0h4m0 0v4m0-4v-4m-4 10v4m0 0h4m-4 0H5m4 0H5v-4"
									/>
								</svg>
							{:else}
								<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 8V4m0 0h4M4 4l5 5m11-5h-4m4 0v4m0-4l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
									/>
								</svg>
							{/if}
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.slider::-webkit-slider-thumb {
		appearance: none;
		width: 12px;
		height: 12px;
		background: white;
		border-radius: 50%;
		cursor: pointer;
	}

	.slider::-moz-range-thumb {
		width: 12px;
		height: 12px;
		background: white;
		border-radius: 50%;
		cursor: pointer;
		border: none;
	}
</style>

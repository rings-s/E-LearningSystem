<!-- front/src/lib/components/course/YouTubePlayer.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';

	let {
		videoId = '',
		autoplay = false,
		muted = false,
		controls = true,
		modestBranding = true,
		rel = 0,
		showInfo = false,
		onReady = () => {},
		onStateChange = () => {},
		onProgress = () => {},
		class: className = ''
	} = $props();

	let player;
	let playerReady = $state(false);
	let isPlaying = $state(false);
	let currentTime = $state(0);
	let duration = $state(0);
	let playerElement = $state();

	// Extract video ID from YouTube URL if needed
	const extractVideoId = (url) => {
		if (!url) return '';
		if (url.length === 11) return url; // Already an ID

		const regex =
			/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
		const match = url.match(regex);
		return match ? match[1] : '';
	};

	const actualVideoId = $derived(extractVideoId(videoId));

	onMount(() => {
		if (browser && actualVideoId) {
			loadYouTubeAPI();
		}
	});

	onDestroy(() => {
		if (player && typeof player.destroy === 'function') {
			player.destroy();
		}
	});

	function loadYouTubeAPI() {
		if (window.YT && window.YT.Player) {
			initializePlayer();
		} else {
			if (!window.onYouTubeIframeAPIReady) {
				window.onYouTubeIframeAPIReady = () => {
					initializePlayer();
				};

				const script = document.createElement('script');
				script.src = 'https://www.youtube.com/iframe_api';
				document.head.appendChild(script);
			}
		}
	}

	function initializePlayer() {
		if (!playerElement || !actualVideoId) return;

		player = new window.YT.Player(playerElement, {
			videoId: actualVideoId,
			playerVars: {
				autoplay: autoplay ? 1 : 0,
				mute: muted ? 1 : 0,
				controls: controls ? 1 : 0,
				modestbranding: modestBranding ? 1 : 0,
				rel: rel,
				showinfo: showInfo ? 1 : 0,
				iv_load_policy: 3, // Hide annotations
				cc_load_policy: 0, // Hide captions by default
				playsinline: 1,
				origin: window.location.origin
			},
			events: {
				onReady: handlePlayerReady,
				onStateChange: handleStateChange
			}
		});
	}

	function handlePlayerReady(event) {
		playerReady = true;
		duration = player.getDuration();
		onReady(event);

		// Start progress tracking
		if (isPlaying) {
			startProgressTracking();
		}
	}

	function handleStateChange(event) {
		const state = event.data;
		isPlaying = state === window.YT.PlayerState.PLAYING;

		if (isPlaying) {
			startProgressTracking();
		} else {
			stopProgressTracking();
		}

		onStateChange(event);
	}

	let progressInterval;

	function startProgressTracking() {
		if (progressInterval) return;

		progressInterval = setInterval(() => {
			if (player && playerReady) {
				currentTime = player.getCurrentTime();
				const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

				onProgress({
					currentTime,
					duration,
					progress
				});
			}
		}, 1000);
	}

	function stopProgressTracking() {
		if (progressInterval) {
			clearInterval(progressInterval);
			progressInterval = null;
		}
	}

	// Public methods
	export function play() {
		if (player && playerReady) {
			player.playVideo();
		}
	}

	export function pause() {
		if (player && playerReady) {
			player.pauseVideo();
		}
	}

	export function seekTo(seconds) {
		if (player && playerReady) {
			player.seekTo(seconds);
		}
	}

	export function getCurrentTime() {
		return player && playerReady ? player.getCurrentTime() : 0;
	}

	export function getDuration() {
		return player && playerReady ? player.getDuration() : 0;
	}

	export function getPlayerState() {
		return player && playerReady ? player.getPlayerState() : -1;
	}
</script>

<div class="youtube-player {className}">
	{#if actualVideoId}
		<div class="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
			<div bind:this={playerElement} class="h-full w-full"></div>

			{#if !playerReady}
				<div class="absolute inset-0 flex items-center justify-center bg-gray-900">
					<div class="text-center text-white">
						<div
							class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-2 border-white border-t-transparent"
						></div>
						<p class="text-sm">Loading video...</p>
					</div>
				</div>
			{/if}
		</div>
	{:else}
		<div
			class="flex aspect-video w-full items-center justify-center rounded-lg bg-gray-200 dark:bg-gray-800"
		>
			<div class="text-center text-gray-500">
				<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<p>No video available</p>
			</div>
		</div>
	{/if}
</div>

<style>
	:global(.youtube-player iframe) {
		width: 100% !important;
		height: 100% !important;
	}
</style>

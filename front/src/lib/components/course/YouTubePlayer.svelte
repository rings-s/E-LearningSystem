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
	let initializationError = $state(null);

	// Debug logging
	function debugLog(message, data = null) {
		if (typeof console !== 'undefined') {
			console.log(`[YouTube Player] ${message}`, data || '');
		}
	}

	// Extract video ID from YouTube URL if needed
	const extractVideoId = (url) => {
		debugLog('Extracting video ID from:', url);
		if (!url) return '';
		if (url.length === 11) return url; // Already an ID

		const regex =
			/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
		const match = url.match(regex);
		const extractedId = match ? match[1] : '';
		debugLog('Extracted video ID:', extractedId);
		return extractedId;
	};

	const actualVideoId = $derived(extractVideoId(videoId));

	onMount(() => {
		debugLog('YouTube Player component mounted');
		if (browser && actualVideoId) {
			debugLog('Browser environment detected, loading YouTube API');
			loadYouTubeAPI();
		} else {
			debugLog('No video ID or not in browser environment');
		}
	});

	onDestroy(() => {
		debugLog('YouTube Player component destroyed');
		if (player && typeof player.destroy === 'function') {
			try {
				player.destroy();
				debugLog('Player destroyed successfully');
			} catch (error) {
				debugLog('Error destroying player:', error);
			}
		}
		stopProgressTracking();
	});

	function loadYouTubeAPI() {
		debugLog('Loading YouTube API');
		
		// Check if API is already loaded
		if (window.YT && window.YT.Player) {
			debugLog('YouTube API already loaded, initializing player');
			initializePlayer();
			return;
		}

		// Set up API ready callback
		if (!window.onYouTubeIframeAPIReady) {
			window.onYouTubeIframeAPIReady = () => {
				debugLog('YouTube API ready callback triggered');
				initializePlayer();
			};

			// Load the API script
			const script = document.createElement('script');
			script.src = 'https://www.youtube.com/iframe_api';
			script.async = true;
			script.onerror = () => {
				debugLog('Failed to load YouTube API script');
				initializationError = 'Failed to load YouTube API';
			};
			
			debugLog('Appending YouTube API script to document');
			document.head.appendChild(script);
		}
	}

	function initializePlayer() {
		if (!playerElement || !actualVideoId) {
			debugLog('Cannot initialize player: missing element or video ID');
			return;
		}
		
		debugLog('Initializing YouTube player with video ID:', actualVideoId);
		
		try {
			// Get current origin for security
			const currentOrigin = window.location.origin;
			const currentHost = window.location.host;
			debugLog('Current origin:', currentOrigin);
			debugLog('Current host:', currentHost);
			
			player = new window.YT.Player(playerElement, {
				videoId: actualVideoId,
				host: 'https://www.youtube-nocookie.com', // Use privacy-enhanced mode
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
					origin: currentOrigin, // Fix origin mismatch
					enablejsapi: 1,
					fs: 1, // Allow fullscreen
					hl: 'en', // Set language to avoid locale issues
					disablekb: 0, // Enable keyboard controls
					widget_referrer: currentOrigin // Set referrer to avoid warnings
				},
				events: {
					onReady: handlePlayerReady,
					onStateChange: handleStateChange,
					onError: handlePlayerError
				}
			});
			
			debugLog('Player initialization request sent');
		} catch (error) {
			debugLog('Error initializing player:', error);
			initializationError = 'Failed to initialize video player';
		}
	}

	function handlePlayerReady(event) {
		try {
			debugLog('YouTube player ready event received');
			playerReady = true;
			
			// Get video duration safely
			try {
				duration = player.getDuration() || 0;
				debugLog('Video duration:', duration);
			} catch (durationError) {
				debugLog('Error getting duration:', durationError);
				duration = 0;
			}
			
			onReady(event);

			// Start progress tracking if playing
			if (isPlaying) {
				startProgressTracking();
			}
			
			debugLog('Player ready handling completed');
		} catch (error) {
			debugLog('Error in player ready handler:', error);
			initializationError = 'Player initialization failed';
		}
	}

	function handleStateChange(event) {
		try {
			const state = event.data;
			const wasPlaying = isPlaying;
			isPlaying = state === window.YT.PlayerState.PLAYING;
			
			debugLog('Player state changed:', {
				state: state,
				isPlaying: isPlaying,
				stateName: getStateName(state)
			});

			if (isPlaying && !wasPlaying) {
				startProgressTracking();
			} else if (!isPlaying && wasPlaying) {
				stopProgressTracking();
			}

			onStateChange(event);
		} catch (error) {
			debugLog('Error in state change handler:', error);
		}
	}

	function handlePlayerError(event) {
		const errorCode = event.data;
		const errorMessages = {
			2: 'Invalid video ID',
			5: 'HTML5 player error',
			100: 'Video not found or private',
			101: 'Video not allowed to be played in embedded players',
			150: 'Video not allowed to be played in embedded players'
		};
		
		const errorMessage = errorMessages[errorCode] || `YouTube player error: ${errorCode}`;
		debugLog('Player error:', errorMessage);
		initializationError = errorMessage;
	}

	function getStateName(state) {
		const stateNames = {
			[-1]: 'UNSTARTED',
			[0]: 'ENDED',
			[1]: 'PLAYING',
			[2]: 'PAUSED',
			[3]: 'BUFFERING',
			[5]: 'CUED'
		};
		return stateNames[state] || 'UNKNOWN';
	}

	let progressInterval;

	function startProgressTracking() {
		if (progressInterval) {
			debugLog('Progress tracking already running');
			return;
		}

		debugLog('Starting progress tracking');
		progressInterval = setInterval(() => {
			try {
				if (player && playerReady && typeof player.getCurrentTime === 'function') {
					const newCurrentTime = player.getCurrentTime() || 0;
   				const newDuration = player.getDuration() || duration;
   				
   				// Only update if values have changed significantly
   				if (Math.abs(newCurrentTime - currentTime) > 0.5) {
   					currentTime = newCurrentTime;
   					duration = newDuration;
   					
   					const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

   					onProgress({
   						currentTime,
   						duration,
   						progress
   					});
   				}
   			}
   		} catch (error) {
   			debugLog('Progress tracking error:', error);
   			stopProgressTracking();
   		}
   	}, 1000);
   }

   function stopProgressTracking() {
   	if (progressInterval) {
   		debugLog('Stopping progress tracking');
   		clearInterval(progressInterval);
   		progressInterval = null;
   	}
   }

   // Public methods for external control
   export function play() {
   	debugLog('Public play() called');
   	if (player && playerReady) {
   		try {
   			player.playVideo();
   		} catch (error) {
   			debugLog('Error playing video:', error);
   		}
   	}
   }

   export function pause() {
   	debugLog('Public pause() called');
   	if (player && playerReady) {
   		try {
   			player.pauseVideo();
   		} catch (error) {
   			debugLog('Error pausing video:', error);
   		}
   	}
   }

   export function seekTo(seconds) {
   	debugLog('Public seekTo() called:', seconds);
   	if (player && playerReady) {
   		try {
   			player.seekTo(seconds);
   		} catch (error) {
   			debugLog('Error seeking video:', error);
   		}
   	}
   }

   export function getCurrentTime() {
   	if (player && playerReady) {
   		try {
   			return player.getCurrentTime();
   		} catch (error) {
   			debugLog('Error getting current time:', error);
   		}
   	}
   	return 0;
   }

   export function getDuration() {
   	if (player && playerReady) {
   		try {
   			return player.getDuration();
   		} catch (error) {
   			debugLog('Error getting duration:', error);
   		}
   	}
   	return 0;
   }

   export function getPlayerState() {
   	if (player && playerReady) {
   		try {
   			return player.getPlayerState();
   		} catch (error) {
   			debugLog('Error getting player state:', error);
   		}
   	}
   	return -1;
   }
</script>

<div class="youtube-player {className}">
   {#if actualVideoId}
   	<div class="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
   		<div bind:this={playerElement} class="h-full w-full"></div>

   		{#if !playerReady && !initializationError}
   			<div class="absolute inset-0 flex items-center justify-center bg-gray-900">
   				<div class="text-center text-white">
   					<div
   						class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-2 border-white border-t-transparent"
   					></div>
   					<p class="text-sm">Loading video...</p>
   				</div>
   			</div>
   		{/if}

   		{#if initializationError}
   			<div class="absolute inset-0 flex items-center justify-center bg-red-900">
   				<div class="text-center text-white p-4">
   					<svg class="mx-auto mb-4 h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
   						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
   					</svg>
   					<p class="text-sm font-medium mb-2">Video Error</p>
   					<p class="text-xs text-red-200">{initializationError}</p>
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
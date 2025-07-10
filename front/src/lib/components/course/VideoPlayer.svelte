<!-- front/src/lib/components/course/VideoPlayer.svelte -->
<script>
	import { onMount } from 'svelte';
	import YouTubePlayer from './YouTubePlayer.svelte';

	let {
		url = '',
		duration = 0,
		onComplete = () => {},
		onProgress = () => {},
		autoplay = false,
		controls = true,
		class: className = ''
	} = $props();

	let videoType = $state('unknown');
	let videoId = $state('');
	let youtubePlayer = $state();

	// Detect video type and extract ID
	function detectVideoType(videoUrl) {
		if (!videoUrl) return { type: 'unknown', id: '' };

		// YouTube detection
		const youtubeRegex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/)([^"&?\/\s]{11})|youtu\.be\/([^"&?\/\s]{11}))/;
		const youtubeMatch = videoUrl.match(youtubeRegex);
		if (youtubeMatch) {
			return {
				type: 'youtube',
				id: youtubeMatch[1] || youtubeMatch[2]
			};
		}

		// Vimeo detection
		const vimeoRegex = /vimeo\.com\/(?:video\/)?(\d+)/;
		const vimeoMatch = videoUrl.match(vimeoRegex);
		if (vimeoMatch) {
			return {
				type: 'vimeo',
				id: vimeoMatch[1]
			};
		}

		// Check if it's a direct video file
		const videoExtensions = /\.(mp4|webm|ogg|mov|avi|mkv)$/i;
		if (videoExtensions.test(videoUrl)) {
			return {
				type: 'direct',
				id: videoUrl
			};
		}

		return { type: 'unknown', id: '' };
	}

	onMount(() => {
		const detection = detectVideoType(url);
		videoType = detection.type;
		videoId = detection.id;
	});

	// Handle progress updates from YouTube player
	function handleYouTubeProgress(data) {
		onProgress(data);
		
		// Auto-complete when video reaches 90%
		if (data.progress >= 90) {
			onComplete();
		}
	}

	// Handle direct video progress
	function handleDirectVideoProgress(event) {
		const video = event.target;
		const currentTime = video.currentTime;
		const duration = video.duration;
		const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

		onProgress({
			currentTime,
			duration,
			progress
		});

		// Auto-complete when video reaches 90%
		if (progress >= 90) {
			onComplete();
		}
	}

	// Public methods for external control
	export function play() {
		if (videoType === 'youtube' && youtubePlayer) {
			youtubePlayer.play();
		} else if (videoType === 'direct') {
			const video = document.querySelector('.direct-video');
			if (video) video.play();
		}
	}

	export function pause() {
		if (videoType === 'youtube' && youtubePlayer) {
			youtubePlayer.pause();
		} else if (videoType === 'direct') {
			const video = document.querySelector('.direct-video');
			if (video) video.pause();
		}
	}

	export function seekTo(seconds) {
		if (videoType === 'youtube' && youtubePlayer) {
			youtubePlayer.seekTo(seconds);
		} else if (videoType === 'direct') {
			const video = document.querySelector('.direct-video');
			if (video) video.currentTime = seconds;
		}
	}

	export function getCurrentTime() {
		if (videoType === 'youtube' && youtubePlayer) {
			return youtubePlayer.getCurrentTime();
		} else if (videoType === 'direct') {
			const video = document.querySelector('.direct-video');
			return video ? video.currentTime : 0;
		}
		return 0;
	}

	export function getDuration() {
		if (videoType === 'youtube' && youtubePlayer) {
			return youtubePlayer.getDuration();
		} else if (videoType === 'direct') {
			const video = document.querySelector('.direct-video');
			return video ? video.duration : 0;
		}
		return duration || 0;
	}
</script>

<div class="video-player {className}">
	{#if videoType === 'youtube' && videoId}
		<YouTubePlayer
			bind:this={youtubePlayer}
			videoId={videoId}
			{autoplay}
			{controls}
			onProgress={handleYouTubeProgress}
			onReady={onComplete}
		/>
	{:else if videoType === 'direct' && videoId}
		<div class="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
			<video
				class="direct-video w-full h-full"
				src={videoId}
				{controls}
				preload="metadata"
				ontimeupdate={handleDirectVideoProgress}
				onended={onComplete}
				onloadedmetadata={(e) => {
					const video = e.target;
					onProgress({
						currentTime: 0,
						duration: video.duration,
						progress: 0
					});
				}}
			>
				<track kind="captions" />
				Your browser does not support the video tag.
			</video>
		</div>
	{:else if videoType === 'vimeo' && videoId}
		<div class="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
			<iframe
				src="https://player.vimeo.com/video/{videoId}"
				width="100%"
				height="100%"
				frameborder="0"
				allow="autoplay; fullscreen; picture-in-picture"
				allowfullscreen
				title="Vimeo video player"
			></iframe>
		</div>
	{:else}
		<div class="flex aspect-video w-full items-center justify-center rounded-lg bg-gray-200 dark:bg-gray-800">
			<div class="text-center text-gray-500">
				<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<p class="text-sm">Video format not supported</p>
				<p class="text-xs text-gray-400 mt-1">
					{videoType === 'unknown' ? 'Unknown video type' : `${videoType} videos are not yet supported`}
				</p>
			</div>
		</div>
	{/if}
</div>

<style>
	:global(.video-player video) {
		width: 100% !important;
		height: 100% !important;
	}
</style>
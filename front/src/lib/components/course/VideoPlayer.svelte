// front/src/lib/components/course/VideoPlayer.svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import { courseStore } from '$lib/stores/course.store.js';

  let {
    url = '',
    duration = 0,
    onComplete = () => {},
    onProgress = () => {},
    autoplay = false,
    controls = true
  } = $props();

  let videoElement;
  let isPlaying = $state(false);
  let currentTime = $state(0);
  let progress = $state(0);
  let volume = $state(1);
  let playbackRate = $state(1);
  let isFullscreen = $state(false);
  let showControls = $state(true);
  let controlsTimeout;

  onMount(() => {
    if (videoElement) {
      videoElement.addEventListener('timeupdate', handleTimeUpdate);
      videoElement.addEventListener('ended', handleEnded);
      videoElement.addEventListener('play', () => isPlaying = true);
      videoElement.addEventListener('pause', () => isPlaying = false);
      
      // Load saved progress
      const savedProgress = courseStore.currentLearningProgress;
      if (savedProgress?.lastPosition) {
        videoElement.currentTime = savedProgress.lastPosition;
      }
    }
  });

  onDestroy(() => {
    if (videoElement) {
      videoElement.removeEventListener('timeupdate', handleTimeUpdate);
      videoElement.removeEventListener('ended', handleEnded);
    }
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

  function handleEnded() {
    isPlaying = false;
    onComplete();
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
    volume = e.target.value;
    videoElement.volume = volume;
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
      videoElement.parentElement.requestFullscreen();
      isFullscreen = true;
    } else {
      document.exitFullscreen();
      isFullscreen = false;
    }
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
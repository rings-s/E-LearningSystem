<!-- front/src/lib/components/dashboard/DashboardHeader.svelte -->
<script>
	import { fade, fly } from 'svelte/transition';
	import { formatters } from '$lib/utils/formatters.js';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';

	let { 
		userName, 
		userRole, 
		refreshing = false, 
		onRefresh = () => {} 
	} = $props();

	// Dynamic greeting based on time
	const greeting = $derived(() => {
		const hour = new Date().getHours();
		if (hour < 12) return 'Good morning';
		if (hour < 17) return 'Good afternoon';
		return 'Good evening';
	});

	// Role-specific welcome messages
	const welcomeMessage = $derived(() => {
		switch (userRole) {
			case 'student':
				return 'Ready to continue your learning journey?';
			case 'teacher':
				return 'Manage your courses and track student progress.';
			case 'manager':
			case 'admin':
				return 'Monitor platform performance and user engagement.';
			default:
				return 'Welcome to your personalized dashboard.';
		}
	});

	// Current date and time
	const currentDateTime = $derived(() => {
		const now = new Date();
		return {
			date: now.toLocaleDateString('en-US', { 
				weekday: 'long', 
				year: 'numeric', 
				month: 'long', 
				day: 'numeric' 
			}),
			time: now.toLocaleTimeString('en-US', { 
				hour: '2-digit', 
				minute: '2-digit' 
			})
		};
	});

	// Role badge configuration
	const roleBadge = $derived(() => {
		switch (userRole) {
			case 'student':
				return { variant: 'primary', icon: '🎓' };
			case 'teacher':
				return { variant: 'success', icon: '👨‍🏫' };
			case 'manager':
				return { variant: 'warning', icon: '👨‍💼' };
			case 'admin':
				return { variant: 'danger', icon: '⚡' };
			default:
				return { variant: 'secondary', icon: '👤' };
		}
	});
</script>

<header class="relative overflow-hidden mb-8" in:fly={{ y: -20, duration: 600 }}>
	<!-- Background gradient -->
	<div class="absolute inset-0 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 rounded-2xl"></div>
	
	<!-- Floating background elements -->
	<div class="absolute top-0 right-0 -mr-20 -mt-20 opacity-10">
		<div class="w-40 h-40 bg-gradient-to-br from-blue-400 to-purple-400 rounded-full blur-3xl"></div>
	</div>
	<div class="absolute bottom-0 left-0 -ml-20 -mb-20 opacity-10">
		<div class="w-32 h-32 bg-gradient-to-tr from-indigo-400 to-cyan-400 rounded-full blur-2xl"></div>
	</div>

	<!-- Content -->
	<div class="relative z-10 p-6 lg:p-8">
		<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
			<!-- Welcome Section -->
			<div class="space-y-2">
				<div class="flex items-center gap-3">
					<h1 class="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent dark:from-white dark:to-gray-300">
						{greeting()}, {userName}! 
						<span class="inline-block animate-bounce">👋</span>
					</h1>
					<Badge variant={roleBadge().variant} class="hidden sm:inline-flex">
						<span class="mr-1">{roleBadge().icon}</span>
						{userRole.charAt(0).toUpperCase() + userRole.slice(1)}
					</Badge>
				</div>
				
				<p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl">
					{welcomeMessage()}
				</p>
				
				<div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
					<div class="flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 0V6a2 2 0 012-2h4a2 2 0 012 2v1m-6 0h6m-6 0v10a1 1 0 001 1h4a1 1 0 001-1V7m-6 0V6a2 2 0 012-2h4a2 2 0 012 2v1" />
						</svg>
						<span>{currentDateTime().date}</span>
					</div>
					<div class="flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span>{currentDateTime().time}</span>
					</div>
				</div>
			</div>

			<!-- Action Section -->
			<div class="flex flex-col sm:flex-row gap-3">
				<!-- Refresh Button -->
				<Button
					onclick={onRefresh}
					variant="outline"
					size="medium"
					disabled={refreshing}
					loading={refreshing}
					class="backdrop-blur-sm bg-white/70 border-white/30 hover:bg-white/80 dark:bg-gray-800/70 dark:border-gray-700/30 dark:hover:bg-gray-800/80"
				>
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
					</svg>
					{refreshing ? 'Refreshing...' : 'Refresh Data'}
				</Button>

				<!-- Role-specific action button -->
				{#if userRole === 'student'}
					<Button
						href="/courses"
						variant="primary"
						size="medium"
						class="shadow-lg hover:shadow-xl transition-all duration-300"
					>
						<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
						Explore Courses
					</Button>
				{:else if userRole === 'teacher'}
					<Button
						href="/courses/create"
						variant="primary"
						size="medium"
						class="shadow-lg hover:shadow-xl transition-all duration-300"
					>
						<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
						</svg>
						Create Course
					</Button>
				{:else if userRole === 'manager' || userRole === 'admin'}
					<Button
						href="/admin"
						variant="primary"
						size="medium"
						class="shadow-lg hover:shadow-xl transition-all duration-300"
					>
						<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
						</svg>
						Admin Panel
					</Button>
				{/if}
			</div>
		</div>
	</div>
</header>
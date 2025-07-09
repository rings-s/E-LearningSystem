<!-- front/src/lib/components/dashboard/QuickActions.svelte -->
<script>
	import { fade, fly } from 'svelte/transition';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';

	let { userRole, onAction = () => {} } = $props();

	// Role-specific quick actions
	const actions = $derived(() => {
		switch (userRole) {
			case 'student':
				return [
					{
						id: 'browse_courses',
						title: 'Browse Courses',
						description: 'Discover new learning opportunities',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />',
						color: 'blue',
						href: '/courses'
					},
					{
						id: 'view_courses',
						title: 'My Courses',
						description: 'Continue your enrolled courses',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />',
						color: 'green',
						href: '/my-courses'
					},
					{
						id: 'view_certificates',
						title: 'Certificates',
						description: 'View your earned certificates',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />',
						color: 'yellow',
						href: '/certificates'
					}
				];

			case 'teacher':
				return [
					{
						id: 'create_course',
						title: 'Create Course',
						description: 'Build a new learning experience',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />',
						color: 'blue',
						href: '/courses/create'
					},
					{
						id: 'view_courses',
						title: 'My Courses',
						description: 'Manage your published courses',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />',
						color: 'green',
						href: '/my-courses'
					},
					{
						id: 'manage_students',
						title: 'Manage Students',
						description: 'View and support your students',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />',
						color: 'purple',
						href: '/teacher/students'
					},
					{
						id: 'view_analytics',
						title: 'View Analytics',
						description: 'Analyze course performance',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />',
						color: 'orange',
						href: '/teacher/analytics'
					}
				];

			case 'manager':
			case 'admin':
				return [
					{
						id: 'manage_users',
						title: 'Manage Users',
						description: 'Oversee platform users',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />',
						color: 'blue',
						href: '/admin/users'
					},
					{
						id: 'manage_courses',
						title: 'Manage Courses',
						description: 'Review and moderate courses',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />',
						color: 'green',
						href: '/admin/courses'
					},
					{
						id: 'view_analytics',
						title: 'Platform Analytics',
						description: 'Monitor platform performance',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />',
						color: 'purple',
						href: '/admin/analytics'
					},
					{
						id: 'platform_settings',
						title: 'Platform Settings',
						description: 'Configure system settings',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />',
						color: 'orange',
						href: '/admin/settings'
					}
				];

			default:
				return [
					{
						id: 'explore',
						title: 'Explore Platform',
						description: 'Discover what you can do',
						icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />',
						color: 'blue',
						href: '/'
					}
				];
		}
	});

	const colorClasses = {
		blue: 'hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-200 dark:hover:border-blue-800',
		green: 'hover:bg-green-50 dark:hover:bg-green-900/20 hover:border-green-200 dark:hover:border-green-800',
		purple: 'hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:border-purple-200 dark:hover:border-purple-800',
		orange: 'hover:bg-orange-50 dark:hover:bg-orange-900/20 hover:border-orange-200 dark:hover:border-orange-800',
		yellow: 'hover:bg-yellow-50 dark:hover:bg-yellow-900/20 hover:border-yellow-200 dark:hover:border-yellow-800'
	};

	const iconColorClasses = {
		blue: 'text-blue-600 dark:text-blue-400',
		green: 'text-green-600 dark:text-green-400', 
		purple: 'text-purple-600 dark:text-purple-400',
		orange: 'text-orange-600 dark:text-orange-400',
		yellow: 'text-yellow-600 dark:text-yellow-400'
	};

	function handleActionClick(action) {
		if (action.href) {
			window.location.href = action.href;
		} else {
			onAction(action.id);
		}
	}
</script>

<div class="space-y-6" in:fly={{ y: 20, duration: 600, delay: 200 }}>
	<Card class="p-6">
		<div class="flex items-center justify-between mb-6">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
				Quick Actions
			</h3>
			<div class="text-sm text-gray-500 dark:text-gray-400">
				{userRole.charAt(0).toUpperCase() + userRole.slice(1)} tools
			</div>
		</div>
		
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
			{#each actions as action, index}
				<button
					onclick={() => handleActionClick(action)}
					class="group relative overflow-hidden rounded-xl border border-gray-200 bg-white p-6 text-left transition-all duration-300 hover:shadow-lg hover:-translate-y-1 dark:border-gray-700 dark:bg-gray-800 {colorClasses[action.color]}"
					in:fly={{ y: 20, duration: 400, delay: 100 + (index * 50) }}
				>
					<!-- Icon -->
					<div class="mb-4">
						<div class="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gray-100 dark:bg-gray-700 group-hover:scale-110 transition-transform duration-300">
							<svg class="w-6 h-6 {iconColorClasses[action.color]}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								{@html action.icon}
							</svg>
						</div>
					</div>

					<!-- Content -->
					<div class="space-y-2">
						<h4 class="font-semibold text-gray-900 dark:text-white group-hover:text-{action.color}-600 dark:group-hover:text-{action.color}-400 transition-colors">
							{action.title}
						</h4>
						<p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
							{action.description}
						</p>
					</div>

					<!-- Arrow icon -->
					<div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
						<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
						</svg>
					</div>

					<!-- Hover gradient effect -->
					<div class="absolute inset-0 bg-gradient-to-r from-{action.color}-500/0 to-{action.color}-500/0 group-hover:from-{action.color}-500/5 group-hover:to-{action.color}-500/10 transition-all duration-300 pointer-events-none rounded-xl"></div>
				</button>
			{/each}
		</div>
	</Card>
</div>
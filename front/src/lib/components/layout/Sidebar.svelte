<!-- front/src/lib/components/layout/Sidebar.svelte -->
<script>
	import { page } from '$app/stores';
	import { fade, fly } from 'svelte/transition';
	import { uiStore } from '$lib/stores/ui.store.js';
	import { currentUser, userRole } from '$lib/services/auth.service.js';
	import { t } from '$lib/i18n/index.js';
	import { classNames } from '$lib/utils/helpers.js';

	const navigation = $derived([
		{ name: $t('navigation.dashboard'), href: '/dashboard', icon: 'grid' },
		{ name: $t('navigation.courses'), href: '/courses', icon: 'book' },
		{ name: $t('navigation.myCourses'), href: '/my-courses', icon: 'bookmark' },
		...($userRole === 'teacher'
			? [
				{ name: $t('navigation.teacherCourses'), href: '/teacher/courses', icon: 'teaching' },
				{ name: $t('navigation.teacherStudents'), href: '/teacher/students', icon: 'users' }
			]
			: []),
		{ name: $t('navigation.forum'), href: '/forum', icon: 'chat' },
		{ name: $t('navigation.certificates'), href: '/certificates', icon: 'award' }
	]);

	const isActive = (href) => {
		return $page.url.pathname.startsWith(href);
	};

	const icons = {
		grid: `<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />`,
		book: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />`,
		bookmark: `<path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />`,
		academic: `<path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />`,
		teaching: `<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />`,
		users: `<path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />`,
		chat: `<path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />`,
		award: `<path stroke-linecap="round" stroke-linejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.492a46.32 46.32 0 012.916.52 6.003 6.003 0 01-5.395 4.972m0 0a6.726 6.726 0 01-2.749 1.35m0 0a6.772 6.772 0 01-3.044 0" />`
	};
</script>

<aside
	class={classNames(
		'fixed inset-y-0 left-0 z-40 w-64 transform transition-transform duration-300 ease-in-out',
		'border-r border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800',
		$uiStore.sidebarOpen ? 'translate-x-0' : '-translate-x-full',
		'lg:static lg:inset-0 lg:translate-x-0'
	)}
>
	<div class="flex h-full flex-col">
		<!-- Logo -->
		<div class="flex h-16 items-center justify-between border-b px-6">
			<div class="flex items-center space-x-3">
				<div
					class="from-primary-500 to-primary-600 flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br font-bold text-white"
				>
					E
				</div>
				<span class="text-lg font-semibold text-gray-900 dark:text-white">
					{$t('common.appName')}
				</span>
			</div>
		</div>

		<!-- Navigation -->
		<nav class="flex-1 space-y-1 px-4 py-6">
			{#each navigation as item}
				<a
					href={item.href}
					class={classNames(
						'group flex items-center rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-200',
						isActive(item.href)
							? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400'
							: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
					)}
				>
					<svg
						class={classNames(
							'mr-3 h-5 w-5 transition-colors',
							isActive(item.href)
								? 'text-primary-600 dark:text-primary-400'
								: 'text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'
						)}
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
					>
						{@html icons[item.icon]}
					</svg>
					{item.name}
				</a>
			{/each}
		</nav>

		<!-- User Profile -->
		<div class="border-t p-4">
			<div class="flex items-center space-x-3 px-2">
				<div class="flex-shrink-0">
					{#if $currentUser?.avatar}
						<img
							src={$currentUser.avatar}
							alt={$currentUser.full_name}
							class="h-10 w-10 rounded-full object-cover"
						/>
					{:else}
						<div
							class="from-primary-400 to-primary-600 flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br font-medium text-white"
						>
							{$currentUser?.first_name?.[0]}{$currentUser?.last_name?.[0]}
						</div>
					{/if}
				</div>
				<div class="min-w-0 flex-1">
					<p class="truncate text-sm font-medium text-gray-900 dark:text-white">
						{$currentUser?.full_name || $currentUser?.email}
					</p>
					<p class="truncate text-xs text-gray-500 dark:text-gray-400">
						{$t(`auth.${$currentUser?.role}`)}
					</p>
				</div>
			</div>
		</div>
	</div>
</aside>

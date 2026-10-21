<!-- front/src/lib/components/layout/Sidebar.svelte -->
<!-- Role-aware navigation, used as the desktop sidebar and inside the mobile drawer. -->
<script>
	import { page } from '$app/state';
	import { currentUser } from '#lib/services/auth.service.js';
	import { t } from '#lib/i18n/index.js';
	import { classNames, isTeacher } from '#lib/utils/helpers.js';
	import Logo from '#lib/components/common/Logo.svelte';

	let { onNavigate = () => {}, footer } = $props();

	const icons = {
		home: 'M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25',
		search: 'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z',
		book: 'M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25',
		award:
			'M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.492a46.32 46.32 0 012.916.52 6.003 6.003 0 01-5.395 4.972m0 0a6.726 6.726 0 01-2.749 1.35m0 0a6.772 6.772 0 01-3.044 0',
		chat: 'M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155',
		teach:
			'M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5',
		users:
			'M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z',
		plus: 'M12 4.5v15m7.5-7.5h-15'
	};

	const groups = $derived([
		{
			label: $t('navigation.learn'),
			items: [
				{ label: $t('navigation.dashboard'), href: '/dashboard', icon: 'home' },
				{ label: $t('navigation.courses'), href: '/courses', icon: 'search', exact: true },
				{ label: $t('navigation.myCourses'), href: '/my-courses', icon: 'book' },
				{ label: $t('navigation.certificates'), href: '/certificates', icon: 'award' }
			]
		},
		...(isTeacher($currentUser)
			? [
					{
						label: $t('navigation.teach'),
						items: [
							{ label: $t('navigation.teaching'), href: '/teacher/courses', icon: 'teach' },
							{ label: $t('navigation.students'), href: '/teacher/students', icon: 'users' },
							{ label: $t('navigation.newCourse'), href: '/teacher/courses/create', icon: 'plus' }
						]
					}
				]
			: []),
		{
			label: $t('navigation.community'),
			items: [{ label: $t('navigation.forum'), href: '/forum', icon: 'chat' }]
		}
	]);

	const allHrefs = $derived(groups.flatMap((g) => g.items.map((i) => i.href)));

	// Most specific match wins, so "/teacher/courses/create" doesn't also light up "/teacher/courses"
	const isActive = (item) => {
		const path = page.url.pathname;
		if (item.exact) return path === item.href;
		if (path !== item.href && !path.startsWith(item.href + '/')) return false;
		return !allHrefs.some(
			(h) => h.length > item.href.length && (path === h || path.startsWith(h + '/'))
		);
	};
</script>

<div class="flex h-full flex-col">
	<div class="flex h-16 shrink-0 items-center px-5">
		<Logo href="/dashboard" size="small" />
	</div>

	<nav class="flex-1 scrollbar-thin space-y-6 overflow-y-auto px-3 py-4">
		{#each groups as group}
			<div>
				<p
					class="mb-1.5 px-3 text-[11px] font-semibold tracking-wider text-gray-400 uppercase dark:text-gray-500"
				>
					{group.label}
				</p>
				<ul class="space-y-0.5">
					{#each group.items as item}
						{@const active = isActive(item)}
						<li>
							<a
								href={item.href}
								onclick={onNavigate}
								aria-current={active ? 'page' : undefined}
								class={classNames(
									'group flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors',
									active
										? 'bg-primary-50 text-primary-700 dark:bg-primary-400/10 dark:text-primary-300'
										: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-white'
								)}
							>
								<svg
									class={classNames(
										'size-5 shrink-0',
										active
											? 'text-primary-600 dark:text-primary-400'
											: 'text-gray-400 group-hover:text-gray-600 dark:text-gray-500 dark:group-hover:text-gray-300'
									)}
									fill="none"
									stroke="currentColor"
									stroke-width="1.75"
									viewBox="0 0 24 24"
									aria-hidden="true"
								>
									<path stroke-linecap="round" stroke-linejoin="round" d={icons[item.icon]} />
								</svg>
								{item.label}
							</a>
						</li>
					{/each}
				</ul>
			</div>
		{/each}
	</nav>

	{#if footer}
		<div class="flex items-center gap-1 border-t border-gray-200/80 p-3 dark:border-white/10">
			{@render footer()}
		</div>
	{/if}
</div>

<script>
	import { t } from '#lib/i18n/index.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import { coursesApi } from '#lib/apis/courses.js';
	import { debounce, classNames } from '#lib/utils/helpers.js';
	import { formatters } from '#lib/utils/formatters.js';

	// Components
	import PageHeader from '#lib/components/common/PageHeader.svelte';
	import EmptyState from '#lib/components/common/EmptyState.svelte';
	import Skeleton from '#lib/components/common/Skeleton.svelte';
	import CourseCard from '#lib/components/course/CourseCard.svelte';
	import Input from '#lib/components/common/Input.svelte';
	import Select from '#lib/components/common/Select.svelte';
	import Button from '#lib/components/common/Button.svelte';
	import Badge from '#lib/components/common/Badge.svelte';

	/** @type {any[]} */
	let courses = $state([]);
	/** @type {any[]} */
	let categories = $state([]);
	let loading = $state(true);
	let searchLoading = $state(false);

	let filters = $state({
		search: page.url.searchParams.get('search') || '',
		category: page.url.searchParams.get('category') || '',
		level: page.url.searchParams.get('level') || '',
		sortBy: page.url.searchParams.get('sort') || 'relevance'
	});

	let pagination = $state({
		currentPage: parseInt(page.url.searchParams.get('page')) || 1,
		totalPages: 1,
		totalCourses: 0,
		hasNext: false,
		hasPrev: false
	});

	const levelOptions = $derived([
		{ value: '', label: $t('catalog.allLevels') },
		{ value: 'beginner', label: $t('catalog.beginner') },
		{ value: 'intermediate', label: $t('catalog.intermediate') },
		{ value: 'advanced', label: $t('catalog.advanced') }
	]);

	const sortOptions = $derived([
		{ value: 'relevance', label: $t('catalog.mostRelevant') },
		{ value: 'newest', label: $t('catalog.newestFirst') },
		{ value: 'popular', label: $t('catalog.mostPopular') },
		{ value: 'rating', label: $t('catalog.highestRated') },
		{ value: 'duration', label: $t('catalog.shortestFirst') }
	]);

	onMount(async () => {
		await Promise.all([fetchCategories(), fetchCourses()]);
	});

	const fetchCourses = async (page = 1) => {
		if (page === 1) {
			loading = true;
		} else {
			searchLoading = true;
		}

		try {
			const params = {
				page,
				page_size: 12,
				...Object.fromEntries(Object.entries(filters).filter(([_, value]) => value))
			};

			const response = await coursesApi.getCourses(params);

			if (response.results) {
				courses = response.results;
				pagination = {
					currentPage: page,
					totalPages: Math.ceil(response.count / 12),
					totalCourses: response.count,
					hasNext: response.next !== null,
					hasPrev: response.previous !== null
				};
			} else if (Array.isArray(response)) {
				courses = response;
				pagination = {
					currentPage: 1,
					totalPages: 1,
					totalCourses: response.length,
					hasNext: false,
					hasPrev: false
				};
			}

			// Update URL
			updateURL();
		} catch (error) {
			console.error('Failed to fetch courses:', error);
			courses = [];
		} finally {
			loading = false;
			searchLoading = false;
		}
	};

	const fetchCategories = async () => {
		try {
			const response = await coursesApi.getCategories();
			categories = response.results || response || [];
		} catch (error) {
			console.error('Failed to fetch categories:', error);
		}
	};

	const updateURL = () => {
		const url = new URL(window.location);

		Object.entries(filters).forEach(([key, value]) => {
			if (value) {
				url.searchParams.set(key, value);
			} else {
				url.searchParams.delete(key);
			}
		});

		if (pagination.currentPage > 1) {
			url.searchParams.set('page', pagination.currentPage.toString());
		} else {
			url.searchParams.delete('page');
		}

		goto(url.toString(), { shallow: true, replace: true });
	};

	const debouncedSearch = debounce(() => {
		fetchCourses(1);
	}, 500);

	// Watch for filter changes
	$effect(() => {
		if (filters.search !== undefined) {
			debouncedSearch();
		}
	});

	const handleFilterChange = () => {
		pagination.currentPage = 1;
		fetchCourses(1);
	};

	const clearFilters = () => {
		filters = { search: '', category: '', level: '', sortBy: 'relevance' };
		pagination.currentPage = 1;
		fetchCourses(1);
	};

	const goToPage = (page) => {
		if (page >= 1 && page <= pagination.totalPages) {
			fetchCourses(page);
			window.scrollTo({ top: 0, behavior: 'smooth' });
		}
	};

	const hasActiveFilters = $derived(
		filters.search || filters.category || filters.level || filters.sortBy !== 'relevance'
	);
</script>

<!-- front/src/routes/(app)/courses/+page.svelte -->

<svelte:head>
	<title>{$t('catalog.pageTitle')}</title>
	<meta name="description" content={$t('catalog.metaDescription')} />
</svelte:head>

<div class="space-y-6">
	<PageHeader title={$t('catalog.title')} description={$t('catalog.description')} />

	<!-- Search + filters -->
	<div
		class="space-y-4 rounded-2xl bg-white p-4 shadow-xs ring-1 ring-gray-200/80 sm:p-5 dark:bg-gray-900 dark:ring-white/10"
	>
		<Input
			type="search"
			placeholder={$t('catalog.searchPlaceholder')}
			bind:value={filters.search}
			icon="<path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z' />"
		/>
		<div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
			<Select
				bind:value={filters.category}
				onchange={handleFilterChange}
				options={[
					{ value: '', label: $t('catalog.allCategories') },
					...categories.map((cat) => ({ value: cat.slug, label: cat.name }))
				]}
				placeholder=""
			/>
			<Select
				bind:value={filters.level}
				onchange={handleFilterChange}
				options={levelOptions}
				placeholder=""
			/>
			<Select
				bind:value={filters.sortBy}
				onchange={handleFilterChange}
				options={sortOptions}
				placeholder=""
			/>
		</div>

		{#if hasActiveFilters}
			<div
				class="flex flex-wrap items-center gap-2 border-t border-gray-100 pt-4 dark:border-white/5"
			>
				{#if filters.search}
					<Badge
						variant="primary"
						removable
						onRemove={() => {
							filters.search = '';
							handleFilterChange();
						}}
					>
						“{filters.search}”
					</Badge>
				{/if}
				{#if filters.category}
					{@const category = categories.find((c) => c.slug === filters.category)}
					<Badge
						variant="primary"
						removable
						onRemove={() => {
							filters.category = '';
							handleFilterChange();
						}}
					>
						{category?.name || filters.category}
					</Badge>
				{/if}
				{#if filters.level}
					<Badge
						variant="primary"
						removable
						class="capitalize"
						onRemove={() => {
							filters.level = '';
							handleFilterChange();
						}}
					>
						{filters.level}
					</Badge>
				{/if}
				<button
					type="button"
					onclick={clearFilters}
					class="ms-auto text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
				>
					{$t('catalog.clearAll')}
				</button>
			</div>
		{/if}
	</div>

	<!-- Results -->
	<p class="text-sm text-gray-600 dark:text-gray-400" aria-live="polite">
		{#if loading}
			{$t('catalog.loading')}
		{:else if pagination.totalCourses > 0}
			<span class="font-medium text-gray-900 dark:text-white">
				{$t('catalog.coursesCount', { count: formatters.number(pagination.totalCourses) })}
			</span>
			{#if pagination.totalPages > 1}
				· {$t('catalog.pageOf', { current: pagination.currentPage, total: pagination.totalPages })}
			{/if}
		{/if}
	</p>

	{#if loading}
		<div class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
			<Skeleton variant="card" count={6} />
		</div>
	{:else if courses.length === 0}
		<EmptyState
			title={$t('catalog.noCourses')}
			description={$t('catalog.noCoursesDesc')}
			icon={'<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />'}
		>
			{#snippet actions()}
				{#if hasActiveFilters}
					<Button onclick={clearFilters}>{$t('catalog.clearFilters')}</Button>
				{/if}
			{/snippet}
		</EmptyState>
	{:else}
		<div class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
			{#each courses as course (course.uuid)}
				<div in:fade={{ duration: 200 }}>
					<CourseCard {course} />
				</div>
			{/each}
		</div>

		{#if pagination.totalPages > 1}
			<nav
				class="flex items-center justify-center gap-2 pt-4"
				aria-label={$t('catalog.pagination')}
			>
				<Button
					variant="outline"
					size="small"
					onclick={() => goToPage(pagination.currentPage - 1)}
					disabled={!pagination.hasPrev || searchLoading}
				>
					{$t('catalog.previous')}
				</Button>
				<div class="hidden items-center gap-1 sm:flex">
					{#each Array(Math.min(5, pagination.totalPages)) as _, i}
						{@const pageNum = Math.max(1, pagination.currentPage - 2) + i}
						{#if pageNum <= pagination.totalPages}
							<button
								type="button"
								onclick={() => goToPage(pageNum)}
								disabled={searchLoading}
								aria-current={pageNum === pagination.currentPage ? 'page' : undefined}
								class={classNames(
									'size-8 rounded-lg text-sm font-medium transition-colors',
									pageNum === pagination.currentPage
										? 'bg-primary-600 text-white'
										: 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-white/10'
								)}
							>
								{pageNum}
							</button>
						{/if}
					{/each}
				</div>
				<span class="text-sm text-gray-600 sm:hidden dark:text-gray-400">
					{pagination.currentPage} / {pagination.totalPages}
				</span>
				<Button
					variant="outline"
					size="small"
					onclick={() => goToPage(pagination.currentPage + 1)}
					disabled={!pagination.hasNext || searchLoading}
				>
					{$t('catalog.next')}
				</Button>
			</nav>
		{/if}
	{/if}
</div>

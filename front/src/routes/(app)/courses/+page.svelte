<!-- front/src/routes/(app)/courses/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { fade, fly, scale } from 'svelte/transition';
	import { coursesApi } from '$lib/apis/courses.js';
	import { debounce, classNames } from '$lib/utils/helpers.js';
	import { formatters } from '$lib/utils/formatters.js';

	// Components
	import CourseCard from '$lib/components/course/CourseCard.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Select from '$lib/components/common/Select.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';

	/** @type {any[]} */
	let courses = $state([]);
	/** @type {any[]} */
	let categories = $state([]);
	let loading = $state(true);
	let searchLoading = $state(false);

	let filters = $state({
		search: $page.url.searchParams.get('search') || '',
		category: $page.url.searchParams.get('category') || '',
		level: $page.url.searchParams.get('level') || '',
		sortBy: $page.url.searchParams.get('sort') || 'relevance'
	});

	let pagination = $state({
		currentPage: parseInt($page.url.searchParams.get('page')) || 1,
		totalPages: 1,
		totalCourses: 0,
		hasNext: false,
		hasPrev: false
	});

	const levelOptions = [
		{ value: '', label: 'All Levels' },
		{ value: 'beginner', label: 'Beginner' },
		{ value: 'intermediate', label: 'Intermediate' },
		{ value: 'advanced', label: 'Advanced' }
	];

	const sortOptions = [
		{ value: 'relevance', label: 'Most Relevant' },
		{ value: 'newest', label: 'Newest First' },
		{ value: 'popular', label: 'Most Popular' },
		{ value: 'rating', label: 'Highest Rated' },
		{ value: 'duration', label: 'Shortest First' }
	];

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

		window.history.replaceState({}, '', url);
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

<svelte:head>
	<title>Courses - 244SCHOOL</title>
	<meta
		name="description"
		content="Explore our wide range of online courses and start your learning journey with 244SCHOOL"
	/>
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800"
>
	<!-- Hero Section -->
	<div class="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600 text-white" in:fade={{ duration: 800 }}>
		<!-- Background Pattern -->
		<div class="absolute inset-0 opacity-10">
			<div class="h-full w-full bg-white bg-opacity-5" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0); background-size: 40px 40px;"></div>
		</div>
		
		<div class="container relative mx-auto px-4 py-20">
			<div class="mx-auto max-w-4xl text-center">
				<div in:fly={{ y: 30, delay: 200, duration: 800 }}>
					<h1 class="mb-6 text-4xl font-bold leading-tight lg:text-6xl">
						Discover Your Next
						<span class="bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
							Learning Adventure
						</span>
					</h1>
					<p class="mb-8 text-xl leading-relaxed text-white/90 lg:text-2xl">
						Explore thousands of courses from world-class instructors and accelerate your career
					</p>
				</div>

				<!-- Quick Search -->
				<div class="mx-auto max-w-2xl" in:fly={{ y: 30, delay: 400, duration: 800 }}>
					<div class="relative">
						<Input
							type="search"
							placeholder="What do you want to learn today?"
							bind:value={filters.search}
							class="h-14 border-white/20 bg-white/10 text-lg text-white placeholder-white/70 backdrop-blur-sm focus:bg-white/20 focus:ring-white/30"
							icon="<path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' />"
						/>
					</div>
				</div>
			</div>
		</div>
	</div>

	<div class="container mx-auto px-4 py-12">
		<!-- Filters Section -->
		<div in:fly={{ y: 20, delay: 600, duration: 600 }}>
			<Card variant="bordered" class="mb-8 bg-white/95 backdrop-blur-sm shadow-lg dark:bg-gray-800/95">
				<div class="flex flex-col gap-6 lg:flex-row">
					<div class="grid flex-1 grid-cols-1 gap-4 md:grid-cols-3">
						<Select
							bind:value={filters.category}
							onchange={handleFilterChange}
							options={[
								{ value: '', label: 'All Categories' },
								...categories.map((cat) => ({ value: cat.uuid, label: cat.name }))
							]}
							placeholder="Category"
						/>

						<Select
							bind:value={filters.level}
							onchange={handleFilterChange}
							options={levelOptions}
							placeholder="Level"
						/>

						<Select
							bind:value={filters.sortBy}
							onchange={handleFilterChange}
							options={sortOptions}
							placeholder="Sort by"
						/>
					</div>

					<div class="flex gap-2">
						{#if hasActiveFilters}
							<Button variant="outline" onclick={clearFilters} size="medium" class="transition-all hover:scale-105">
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
								</svg>
								Clear Filters
							</Button>
						{/if}
					</div>
				</div>

				<!-- Active Filters -->
			{#if hasActiveFilters}
				<div class="mt-4 border-t border-gray-200 pt-4 dark:border-gray-700">
					<div class="flex flex-wrap items-center gap-2">
						<span class="text-sm text-gray-600 dark:text-gray-400">Active filters:</span>

						{#if filters.search}
							<Badge
								variant="primary"
								removable
								onRemove={() => {
									filters.search = '';
									handleFilterChange();
								}}
							>
								Search: "{filters.search}"
							</Badge>
						{/if}

						{#if filters.category}
							{@const category = categories.find((c) => c.uuid === filters.category)}
							<Badge
								variant="primary"
								removable
								onRemove={() => {
									filters.category = '';
									handleFilterChange();
								}}
							>
								Category: {category?.name || filters.category}
							</Badge>
						{/if}

						{#if filters.level}
							<Badge
								variant="primary"
								removable
								onRemove={() => {
									filters.level = '';
									handleFilterChange();
								}}
							>
								Level: {filters.level}
							</Badge>
						{/if}
					</div>
				</div>
			{/if}
			</Card>
		</div>

		<!-- Results Header -->
		<div class="mb-8 flex items-center justify-between" in:fly={{ y: 20, delay: 800, duration: 600 }}>
			<div>
				<h2 class="text-3xl font-bold text-gray-900 dark:text-white">
					{#if loading}
						<span class="flex items-center gap-3">
							<div class="h-6 w-6 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
							Loading courses...
						</span>
					{:else}
						{pagination.totalCourses > 0
							? `${formatters.number(pagination.totalCourses)} courses found`
							: 'No courses found'}
					{/if}
				</h2>
				{#if !loading && pagination.totalCourses > 0}
					<p class="mt-2 text-lg text-gray-600 dark:text-gray-400">
						Showing page {pagination.currentPage} of {pagination.totalPages}
					</p>
				{/if}
			</div>
			
			{#if !loading && pagination.totalCourses > 0}
				<div class="text-right">
					<p class="text-sm text-gray-500 dark:text-gray-400">
						Find the perfect course for you
					</p>
				</div>
			{/if}
		</div>

		<!-- Course Grid -->
		{#if loading}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
				{#each Array(12) as _, index}
					<div class="animate-pulse" in:fly={{ y: 20, delay: index * 50, duration: 400 }}>
						<div class="mb-4 h-48 rounded-2xl bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600"></div>
						<div class="space-y-3">
							<div class="h-6 w-3/4 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-4 w-1/2 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-4 w-2/3 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
						</div>
					</div>
				{/each}
			</div>
		{:else if courses.length === 0}
			<div in:fade={{ duration: 500 }}>
				<Card variant="bordered" class="py-20 text-center shadow-lg">
					<div in:scale={{ duration: 600, start: 0.8 }}>
						<svg class="mx-auto mb-6 h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
						</svg>
						<h3 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">No courses found</h3>
						<p class="mx-auto mb-8 max-w-md text-lg text-gray-600 dark:text-gray-400">
							Try adjusting your search terms or filters to find what you're looking for.
						</p>
						<Button onclick={clearFilters} variant="primary" size="large" class="transition-all hover:scale-105">
							<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
							</svg>
							Clear All Filters
						</Button>
					</div>
				</Card>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
				{#each courses as course, index}
					<div in:fly={{ y: 30, delay: index * 100, duration: 600 }}>
						<CourseCard {course} />
					</div>
				{/each}
			</div>

			<!-- Pagination -->
			{#if pagination.totalPages > 1}
				<div class="mt-16 flex items-center justify-center" in:fade={{ delay: 1000, duration: 500 }}>
					<Card variant="bordered" class="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm dark:bg-gray-800/80">
						<Button
							variant="ghost"
							onclick={() => goToPage(pagination.currentPage - 1)}
							disabled={!pagination.hasPrev || searchLoading}
							class="transition-all hover:scale-105"
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
							</svg>
							Previous
						</Button>
						
						<div class="mx-4 flex items-center gap-1">
							{#each Array(Math.min(5, pagination.totalPages)) as _, i}
								{@const pageNum = Math.max(1, pagination.currentPage - 2) + i}
								{#if pageNum <= pagination.totalPages}
									<Button
										variant={pageNum === pagination.currentPage ? 'primary' : 'ghost'}
										onclick={() => goToPage(pageNum)}
										disabled={searchLoading}
										size="small"
										class={classNames(
											"h-10 w-10 transition-all hover:scale-110",
											pageNum === pagination.currentPage ? "shadow-lg" : ""
										)}
									>
										{pageNum}
									</Button>
								{/if}
							{/each}
						</div>
						
						<Button
							variant="ghost"
							onclick={() => goToPage(pagination.currentPage + 1)}
							disabled={!pagination.hasNext || searchLoading}
							class="transition-all hover:scale-105"
						>
							Next
							<svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
							</svg>
						</Button>
					</Card>
				</div>
			{/if}
		{/if}
	</div>
</div>

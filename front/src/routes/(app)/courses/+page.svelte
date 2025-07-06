<!-- front/src/routes/(app)/courses/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { replaceState } from '$app/navigation';
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

		replaceState(url.toString(), {});
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

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
	<!-- Reduced Hero Section -->
	<div class="relative overflow-hidden" in:fade={{ duration: 800 }}>
		<!-- Animated Background -->
		<div class="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600">
			<!-- Animated geometric pattern -->
			<div class="absolute inset-0 opacity-10">
				<svg class="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
					<defs>
						<pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
							<path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/>
						</pattern>
					</defs>
					<rect width="100%" height="100%" fill="url(#grid)" />
				</svg>
			</div>
			
			<!-- Floating geometric shapes -->
			<div class="absolute inset-0 overflow-hidden">
				{#each Array(6) as _, i}
					<div 
						class="absolute rounded-full bg-white/5 animate-float-gentle"
						style="
							width: {20 + Math.random() * 30}px; 
							height: {20 + Math.random() * 30}px;
							left: {Math.random() * 100}%;
							top: {Math.random() * 100}%;
							animation-delay: {i * 0.6}s;
							animation-duration: {6 + Math.random() * 4}s;
						"
					></div>
				{/each}
			</div>

			<!-- Gradient overlay -->
			<div class="absolute inset-0 bg-gradient-to-r from-black/20 via-transparent to-black/20"></div>
		</div>
		
		<!-- Reduced padding: py-20 -> py-16 -->
		<div class="container relative mx-auto px-4 py-16">
			<div class="mx-auto max-w-4xl text-center text-white">
				<div in:fly={{ y: 30, delay: 200, duration: 800 }}>
					<div class="mb-4 inline-flex items-center rounded-full bg-white/10 px-6 py-2 backdrop-blur-sm">
						<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
						</svg>
						<span class="text-sm font-medium">Course Catalog</span>
					</div>
					
					<!-- Reduced text size: text-5xl lg:text-6xl -> text-4xl lg:text-5xl -->
					<h1 class="mb-6 text-4xl font-bold leading-tight lg:text-5xl">
						Discover Your Next
						<span class="bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
							Learning Adventure
						</span>
					</h1>
					<!-- Reduced text size: text-xl -> text-lg -->
					<p class="mb-6 text-lg leading-relaxed text-white/90">
						Explore thousands of courses from world-class instructors and accelerate your career with cutting-edge skills
					</p>
				</div>

				<!-- Enhanced Quick Search -->
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

				<!-- Quick Stats - reduced margin: mt-12 -> mt-8 -->
				{#if !loading}
					<div class="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3" in:fly={{ y: 30, delay: 600, duration: 800 }}>
						<div class="group rounded-xl bg-white/10 p-4 backdrop-blur-sm transition-all hover:bg-white/15 hover:scale-105">
							<div class="text-2xl font-bold">{formatters.number(pagination.totalCourses)}</div>
							<div class="text-sm text-white/80">Total Courses</div>
						</div>
						<div class="group rounded-xl bg-white/10 p-4 backdrop-blur-sm transition-all hover:bg-white/15 hover:scale-105">
							<div class="text-2xl font-bold">{categories.length}</div>
							<div class="text-sm text-white/80">Categories</div>
						</div>
						<div class="group rounded-xl bg-white/10 p-4 backdrop-blur-sm transition-all hover:bg-white/15 hover:scale-105">
							<div class="text-2xl font-bold">24/7</div>
							<div class="text-sm text-white/80">Access</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="container mx-auto px-4 py-12">
		<!-- Enhanced Filters Section -->
		<div class="mb-8" in:fly={{ y: 20, delay: 600, duration: 600 }}>
			<Card variant="bordered" class="bg-white/95 backdrop-blur-sm shadow-xl dark:bg-gray-800/95">
				<div class="space-y-6">
					<!-- Filter Controls -->
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
								class="h-12"
							/>

							<Select
								bind:value={filters.level}
								onchange={handleFilterChange}
								options={levelOptions}
								placeholder="Level"
								class="h-12"
							/>

							<Select
								bind:value={filters.sortBy}
								onchange={handleFilterChange}
								options={sortOptions}
								placeholder="Sort by"
								class="h-12"
							/>
						</div>

						<div class="flex gap-3">
							{#if hasActiveFilters}
								<Button 
									variant="outline" 
									onclick={clearFilters} 
									size="medium" 
									class="whitespace-nowrap transition-all hover:scale-105"
								>
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
						<div class="border-t border-gray-200 pt-6 dark:border-gray-700">
							<div class="flex flex-wrap items-center gap-3">
								<span class="text-sm font-medium text-gray-600 dark:text-gray-400">Active filters:</span>

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
				</div>
			</Card>
		</div>

		<!-- Enhanced Results Header -->
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

		<!-- Enhanced Course Grid with increased card width -->
		{#if loading}
			<!-- Changed from xl:grid-cols-4 to xl:grid-cols-3 for wider cards -->
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each Array(12) as _, index}
					<div class="animate-pulse" in:fly={{ y: 20, delay: index * 50, duration: 400 }}>
						<Card variant="bordered" class="overflow-hidden">
							<div class="space-y-4">
								<div class="h-48 rounded-xl bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600"></div>
								<div class="space-y-3">
									<div class="h-6 w-3/4 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
									<div class="h-4 w-1/2 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
									<div class="h-4 w-2/3 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
								</div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{:else if courses.length === 0}
			<!-- Enhanced Empty State -->
			<div in:fade={{ duration: 500 }}>
				<Card variant="bordered" class="py-20 text-center shadow-xl">
					<div in:scale={{ duration: 600, start: 0.8 }}>
						<div class="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900 dark:to-primary-800">
							<svg class="h-12 w-12 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
							</svg>
						</div>
						<h3 class="mb-4 text-2xl font-bold text-gray-900 dark:text-white">No courses found</h3>
						<p class="mx-auto mb-8 max-w-md text-lg text-gray-600 dark:text-gray-400">
							Try adjusting your search terms or filters to discover amazing courses that match your interests.
						</p>
						<div class="flex flex-col gap-4 sm:flex-row sm:justify-center">
							<Button 
								onclick={clearFilters} 
								variant="primary" 
								size="large" 
								class="transition-all hover:scale-105"
							>
								<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
								</svg>
								Clear All Filters
							</Button>
							<Button 
								variant="outline" 
								size="large"
								onclick={() => filters.search = ''}
							>
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
								Browse All
							</Button>
						</div>
					</div>
				</Card>
			</div>
		{:else}
			<!-- Changed from xl:grid-cols-4 to xl:grid-cols-3 for wider cards -->
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each courses as course, index}
					<div 
						in:fly={{ y: 30, delay: index * 100, duration: 600 }}
						class="group transition-all duration-300 hover:-translate-y-2"
					>
						<CourseCard {course} />
					</div>
				{/each}
			</div>

			<!-- Enhanced Pagination -->
			{#if pagination.totalPages > 1}
				<div class="mt-16 flex items-center justify-center" in:fade={{ delay: 1000, duration: 500 }}>
					<Card variant="bordered" class="inline-flex items-center gap-2 bg-white/95 backdrop-blur-sm shadow-xl dark:bg-gray-800/95">
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

<style>
	@keyframes float-gentle {
		0%, 100% {
			transform: translateY(0px) rotate(0deg);
		}
		33% {
			transform: translateY(-20px) rotate(1deg);
		}
		66% {
			transform: translateY(-10px) rotate(-1deg);
		}
	}

	.animate-float-gentle {
		animation: float-gentle 6s ease-in-out infinite;
	}
</style>
<!-- front/src/routes/(app)/forum/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { coreApi } from '$lib/apis/core.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { t } from '$lib/i18n/index.js';
	import { formatters } from '$lib/utils/formatters.js';
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	let forums = $state([]);
	let discussions = $state([]);
	let loading = $state(true);
	let selectedForum = $state(null);
	let showCreateModal = $state(false);
	let searchQuery = $state('');
	let filterType = $state('all');

	let newDiscussion = $state({
		title: '',
		content: '',
		discussion_type: 'discussion'
	});

	onMount(async () => {
		await fetchForums();
		await fetchDiscussions();
	});

	const fetchForums = async () => {
		try {
			const response = await coreApi.getForums();
			forums = response.results || response;
		} catch (error) {
			// Forums fetch failed - continue with empty array
		}
	};

	const fetchDiscussions = async (forumId = null) => {
		loading = true;
		try {
			const params = {};
			if (forumId) params.forum = forumId;
			if (searchQuery) params.search = searchQuery;
			if (filterType !== 'all') params.discussion_type = filterType;

			const response = await coreApi.getDiscussions(params);
			discussions = response.results || response;
		} catch (error) {
			// Discussions fetch failed - continue with empty array
		} finally {
			loading = false;
		}
	};

	const createDiscussion = async () => {
		if (!selectedForum) {
			alert('Please select a course forum first');
			return;
		}

		try {
			await coreApi.createDiscussion({
				...newDiscussion,
				forum: selectedForum.uuid
			});

			showCreateModal = false;
			newDiscussion = { title: '', content: '', discussion_type: 'discussion' };
			await fetchDiscussions(selectedForum?.uuid);
		} catch (error) {
			alert('Failed to create discussion. Please try again.');
		}
	};

	const typeConfig = {
		question: {
			icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />',
			color: 'warning',
			label: 'Question'
		},
		discussion: {
			icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />',
			color: 'info',
			label: 'Discussion'
		},
		announcement: {
			icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />',
			color: 'primary',
			label: 'Announcement'
		}
	};

	// Fix for avatar error handling
	function handleAvatarError(event) {
		event.target.style.display = 'none';
	}
</script>

<div class="container mx-auto max-w-7xl px-4 py-8">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">Forum</h1>
		<p class="text-gray-600 dark:text-gray-400">
			Join discussions, ask questions, and share knowledge with the community
		</p>
	</div>

	<div class="grid grid-cols-1 gap-6 lg:grid-cols-4">
		<!-- Sidebar -->
		<div class="lg:col-span-1">
			<!-- Course Forums -->
			<Card variant="bordered" class="mb-6">
				<h3 class="mb-4 font-semibold text-gray-900 dark:text-white">Course Forums</h3>
				<div class="space-y-1">
					<button
						onclick={() => {
							selectedForum = null;
							fetchDiscussions();
						}}
						class="w-full rounded-lg px-3 py-2.5 text-left transition-all {!selectedForum
							? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 font-medium'
							: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}"
					>
						<div class="flex items-center justify-between">
							<span>All Forums</span>
							<span class="text-xs text-gray-500 dark:text-gray-400">
								{discussions.length}
							</span>
						</div>
					</button>

					{#each forums as forum}
						<button
							onclick={() => {
								selectedForum = forum;
								fetchDiscussions(forum.uuid);
							}}
							class="w-full rounded-lg px-3 py-2.5 text-left transition-all {selectedForum?.uuid ===
							forum.uuid
								? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 font-medium'
								: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}"
						>
							<div class="flex items-center justify-between">
								<span class="truncate">{forum.course_title}</span>
								<span class="text-xs text-gray-500 dark:text-gray-400">
									{forum.discussions_count}
								</span>
							</div>
						</button>
					{/each}
				</div>
			</Card>

			<!-- Filters -->
			<Card variant="bordered">
				<h3 class="mb-4 font-semibold text-gray-900 dark:text-white">Filter by Type</h3>
				<div class="space-y-2">
					<label class="flex cursor-pointer items-center space-x-2">
						<input
							type="radio"
							bind:group={filterType}
							value="all"
							onchange={() => fetchDiscussions(selectedForum?.uuid)}
							class="text-primary-600 focus:ring-primary-500"
						/>
						<span class="text-sm text-gray-700 dark:text-gray-300">All Types</span>
					</label>
					{#each Object.entries(typeConfig) as [type, config]}
						<label class="flex cursor-pointer items-center space-x-2">
							<input
								type="radio"
								bind:group={filterType}
								value={type}
								onchange={() => fetchDiscussions(selectedForum?.uuid)}
								class="text-primary-600 focus:ring-primary-500"
							/>
							<span class="text-sm text-gray-700 dark:text-gray-300">{config.label}</span>
						</label>
					{/each}
				</div>
			</Card>
		</div>

		<!-- Main Content -->
		<div class="space-y-6 lg:col-span-3">
			<!-- Actions Bar -->
			<div class="flex flex-col gap-4 sm:flex-row">
				<Input
					type="search"
					placeholder="Search discussions..."
					bind:value={searchQuery}
					onchange={() => fetchDiscussions(selectedForum?.uuid)}
					class="flex-1"
					icon="<path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' />"
				/>

				{#if selectedForum}
					<Button variant="primary" onclick={() => (showCreateModal = true)}>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4v16m8-8H4"
							/>
						</svg>
						New Discussion
					</Button>
				{/if}
			</div>

			<!-- Discussions List -->
			{#if loading}
				<div class="space-y-4">
					{#each Array(3) as _}
						<div class="animate-pulse">
							<div class="h-32 rounded-xl bg-gray-200 dark:bg-gray-700"></div>
						</div>
					{/each}
				</div>
			{:else if discussions.length === 0}
				<Card variant="bordered" class="py-16 text-center">
					<svg
						class="mx-auto mb-4 h-12 w-12 text-gray-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
						/>
					</svg>
					<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">No discussions yet</h3>
					<p class="text-gray-500 dark:text-gray-400">
						{selectedForum
							? 'Be the first to start a discussion in this forum'
							: 'Select a forum to view discussions'}
					</p>
				</Card>
			{:else}
				<div class="space-y-4">
					{#each discussions as discussion}
						<Card
							variant="bordered"
							hoverable
							onclick={() => (window.location.href = `/forum/discussion/${discussion.uuid}`)}
							class="transition-all duration-200 hover:shadow-md"
						>
							<div class="flex gap-4">
								<!-- Type Icon -->
								<div class="flex-shrink-0">
									<div
										class="h-12 w-12 rounded-xl bg-{typeConfig[discussion.discussion_type]
											.color}-100 dark:bg-{typeConfig[discussion.discussion_type]
											.color}-900/20 flex items-center justify-center"
									>
										<svg
											class="h-6 w-6 text-{typeConfig[discussion.discussion_type]
												.color}-600 dark:text-{typeConfig[discussion.discussion_type].color}-400"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											{@html typeConfig[discussion.discussion_type].icon}
										</svg>
									</div>
								</div>

								<!-- Content -->
								<div class="min-w-0 flex-1">
									<div class="mb-2 flex items-start justify-between gap-2">
										<h3 class="line-clamp-1 text-lg font-medium text-gray-900 dark:text-white">
											{discussion.title}
										</h3>
										<div class="flex flex-shrink-0 items-center gap-2">
											{#if discussion.is_pinned}
												<Badge variant="accent" size="small">
													<svg
														class="mr-1 h-3 w-3"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
														/>
													</svg>
													Pinned
												</Badge>
											{/if}
											{#if discussion.is_resolved}
												<Badge variant="success" size="small">
													<svg
														class="mr-1 h-3 w-3"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
														/>
													</svg>
													Resolved
												</Badge>
											{/if}
										</div>
									</div>

									<p class="mb-3 line-clamp-2 text-gray-600 dark:text-gray-400">
										{discussion.content}
									</p>

									<div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
										<div class="flex items-center gap-1.5">
											{#if discussion.author_avatar}
												<img
													src={discussion.author_avatar}
													alt={discussion.author_name}
													class="h-5 w-5 rounded-full bg-gray-200 dark:bg-gray-700"
													onerror={handleAvatarError}
												/>
											{:else}
												<div
													class="flex h-5 w-5 items-center justify-center rounded-full bg-gray-200 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-400"
												>
													{discussion.author_name?.[0]?.toUpperCase() || '?'}
												</div>
											{/if}
											<span>{discussion.author_name}</span>
										</div>
										<span>•</span>
										<span>{formatters.relativeTime(discussion.created_at)}</span>
										<span>•</span>
										<span class="flex items-center gap-1">
											<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
												/>
											</svg>
											{discussion.replies_count}
										</span>
										<span>•</span>
										<span class="flex items-center gap-1">
											<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
												/>
											</svg>
											{discussion.views_count}
										</span>
									</div>
								</div>
							</div>
						</Card>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>

<!-- Create Discussion Modal -->
<Modal
	open={showCreateModal}
	onClose={() => (showCreateModal = false)}
	title="Create New Discussion"
	size="large"
>
	<form
		onsubmit={(e) => {
			e.preventDefault();
			createDiscussion();
		}}
		class="space-y-6"
	>
		<div>
			<label class="mb-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
				Discussion Type
			</label>
			<div class="grid grid-cols-3 gap-3">
				{#each Object.entries(typeConfig) as [type, config]}
					<button
						type="button"
						onclick={() => (newDiscussion.discussion_type = type)}
						class="rounded-xl border-2 p-4 transition-all {newDiscussion.discussion_type === type
							? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
							: 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'}"
					>
						<svg
							class="mx-auto mb-2 h-6 w-6 {newDiscussion.discussion_type === type
								? `text-${config.color}-600 dark:text-${config.color}-400`
								: 'text-gray-400'}"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							{@html config.icon}
						</svg>
						<span
							class="text-sm font-medium {newDiscussion.discussion_type === type
								? 'text-gray-900 dark:text-white'
								: 'text-gray-600 dark:text-gray-400'}"
						>
							{config.label}
						</span>
					</button>
				{/each}
			</div>
		</div>

		<Input
			label="Title"
			bind:value={newDiscussion.title}
			required
			placeholder={newDiscussion.discussion_type === 'question'
				? "What's your question?"
				: 'Enter a descriptive title'}
		/>

		<div>
			<label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
				Content
			</label>
			<textarea
				bind:value={newDiscussion.content}
				required
				rows="6"
				class="focus:ring-primary-500 focus:border-primary-500 w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm transition-all focus:ring-2 dark:border-gray-600 dark:bg-gray-800"
				placeholder={newDiscussion.discussion_type === 'question'
					? 'Provide details about your question...'
					: 'Share your thoughts...'}
			></textarea>
		</div>
	</form>

	{#snippet footer()}
		<div class="flex justify-end gap-3">
			<Button variant="ghost" onclick={() => (showCreateModal = false)}>Cancel</Button>
			<Button variant="primary" onclick={createDiscussion}>Create Discussion</Button>
		</div>
	{/snippet}
</Modal>

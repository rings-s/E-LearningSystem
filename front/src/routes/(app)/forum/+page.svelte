<!-- front/src/routes/(app)/forum/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { coreApi } from '$lib/apis/core.js';
    import { currentUser } from '$lib/stores/auth.store.js';
    import { t } from '$lib/i18n/index.js';
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
        console.error('Failed to fetch forums:', error);
      }
    };
  
    const fetchDiscussions = async (forumId = null) => {
      loading = true;
      try {
        const params = forumId ? { forum: forumId } : {};
        if (searchQuery) params.search = searchQuery;
        
        const response = await coreApi.getDiscussions(params);
        discussions = response.results || response;
      } catch (error) {
        console.error('Failed to fetch discussions:', error);
      } finally {
        loading = false;
      }
    };
  
    const createDiscussion = async () => {
      try {
        await coreApi.createDiscussion({
          ...newDiscussion,
          forum: selectedForum.uuid
        });
        
        showCreateModal = false;
        newDiscussion = { title: '', content: '', discussion_type: 'discussion' };
        await fetchDiscussions(selectedForum?.uuid);
      } catch (error) {
        console.error('Failed to create discussion:', error);
      }
    };
  
    const getTypeIcon = (type) => {
      const icons = {
        question: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />',
        discussion: '<path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />',
        announcement: '<path stroke-linecap="round" stroke-linejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />'
      };
      return icons[type] || icons.discussion;
    };
  
    const getTypeColor = (type) => {
      const colors = {
        question: 'warning',
        discussion: 'info',
        announcement: 'primary'
      };
      return colors[type] || 'default';
    };
  </script>
  
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {$t('navigation.forum')}
        </h1>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Join discussions and ask questions
        </p>
      </div>
      
      {#if selectedForum}
        <Button variant="primary" onclick={() => showCreateModal = true}>
          New Discussion
        </Button>
      {/if}
    </div>
  
    <!-- Forums List -->
    {#if forums.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="md:col-span-1">
          <Card variant="bordered">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-4">
              Course Forums
            </h3>
            <div class="space-y-2">
              <button
                onclick={() => {
                  selectedForum = null;
                  fetchDiscussions();
                }}
                class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors {
                  !selectedForum ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
                }"
              >
                All Discussions
              </button>
              
              {#each forums as forum}
                <button
                  onclick={() => {
                    selectedForum = forum;
                    fetchDiscussions(forum.uuid);
                  }}
                  class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors {
                    selectedForum?.uuid === forum.uuid ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
                  }"
                >
                  <div class="font-medium">{forum.course_title}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {forum.discussions_count} discussions
                  </div>
                </button>
              {/each}
            </div>
          </Card>
        </div>
  
        <div class="md:col-span-2 space-y-4">
          <!-- Search -->
          <Input
            type="search"
            placeholder="Search discussions..."
            bind:value={searchQuery}
            onchange={() => fetchDiscussions(selectedForum?.uuid)}
            icon='<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />'
          />
  
          <!-- Discussions List -->
          {#if loading}
            <div class="space-y-4">
              {#each Array(5) as _}
                <div class="animate-pulse">
                  <div class="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                </div>
              {/each}
            </div>
          {:else if discussions.length === 0}
            <Card variant="bordered" class="text-center py-12">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                No discussions yet
              </h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Be the first to start a discussion
              </p>
            </Card>
          {:else}
            <div class="space-y-4">
              {#each discussions as discussion}
                <Card
                  variant="bordered"
                  hoverable
                  onclick={() => window.location.href = `/forum/discussion/${discussion.uuid}`}
                >
                  <div class="flex gap-4">
                    <!-- Type Icon -->
                    <div class="flex-shrink-0">
                      <div class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                        <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          {@html getTypeIcon(discussion.discussion_type)}
                        </svg>
                      </div>
                    </div>
  
                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-start justify-between gap-2">
                        <div>
                          <h3 class="text-base font-medium text-gray-900 dark:text-white">
                            {discussion.title}
                          </h3>
                          <div class="flex items-center gap-2 mt-1">
                            <Badge variant={getTypeColor(discussion.discussion_type)} size="small">
                              {discussion.discussion_type}
                            </Badge>
                            {#if discussion.is_pinned}
                              <Badge variant="accent" size="small">Pinned</Badge>
                            {/if}
                            {#if discussion.is_resolved}
                              <Badge variant="success" size="small">Resolved</Badge>
                            {/if}
                          </div>
                        </div>
                      </div>
  
                      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                        {discussion.content}
                      </p>
  
                      <div class="mt-3 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>{discussion.author_name}</span>
                        <span>·</span>
                        <span>{new Date(discussion.created_at).toLocaleDateString()}</span>
                        <span>·</span>
                        <span>{discussion.replies_count} replies</span>
                        <span>·</span>
                        <span>{discussion.views_count} views</span>
                      </div>
                    </div>
                  </div>
                </Card>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Create Discussion Modal -->
  <Modal
    open={showCreateModal}
    onClose={() => showCreateModal = false}
    title="New Discussion"
    size="large"
  >
    <form onsubmit|preventDefault={createDiscussion} class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Type
        </label>
        <div class="grid grid-cols-3 gap-2">
          {#each ['discussion', 'question', 'announcement'] as type}
            <button
              type="button"
              onclick={() => newDiscussion.discussion_type = type}
              class="p-3 rounded-lg border-2 transition-all {
                newDiscussion.discussion_type === type
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }"
            >
              <svg class="w-5 h-5 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {@html getTypeIcon(type)}
              </svg>
              <span class="text-xs">{type}</span>
            </button>
          {/each}
        </div>
      </div>
  
      <Input
        label="Title"
        bind:value={newDiscussion.title}
        required
        placeholder="Enter a descriptive title"
      />
  
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Content
        </label>
        <textarea
          bind:value={newDiscussion.content}
          required
          rows="6"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder="Share your thoughts..."
        ></textarea>
      </div>
    </form>
  
    {@snippet footer()}
      <Button variant="ghost" onclick={() => showCreateModal = false}>
        Cancel
      </Button>
      <Button variant="primary" onclick={createDiscussion}>
        Create Discussion
      </Button>
    {/snippet}
  </Modal>
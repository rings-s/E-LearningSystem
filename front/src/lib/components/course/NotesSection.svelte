<script>
  export let notes;
  export let notesSaving = false;
  export let notesLastSaved = null;
  export let saveNotes;
</script>

<div class="mb-4 flex items-center justify-between">
  <div class="flex items-center gap-3">
    <div class="rounded-lg bg-yellow-100 p-2 dark:bg-yellow-900/30">
      <svg class="h-5 w-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    </div>
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">My Notes</h3>
  </div>
  <div class="text-xs text-gray-500 dark:text-gray-400">
    {#if notesSaving}
      <span class="flex items-center gap-1">
        <div class="h-3 w-3 animate-spin rounded-full border border-primary-500 border-t-transparent"></div>
        Saving...
      </span>
    {:else if notesLastSaved}
      <span>Saved just now</span>
    {:else}
      <span>Auto-saves</span>
    {/if}
  </div>
</div>

<div class="space-y-3">
  <textarea
    bind:value={notes}
    placeholder="Take notes about this lesson... Notes are automatically saved to your account."
    class="h-32 w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 transition-all focus:border-primary-500 focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
  ></textarea>

  <div class="flex items-center justify-between">
    <div class="text-xs text-gray-500 dark:text-gray-400">
      Notes are synced across devices
    </div>
    <button
      on:click={() => saveNotes(true)}
      class="rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm text-gray-900 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700 transition-all hover:scale-105"
      disabled={!notes.trim() || notesSaving}
    >
      {notesSaving ? 'Saving...' : 'Save Now'}
    </button>
  </div>
</div>

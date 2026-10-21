<script>
	import { t } from '#lib/i18n/index.js';
	let {
		notes = $bindable([]),
		currentNote = $bindable(''),
		noteSearchQuery = $bindable(''),
		savingNote = false,
		loadingNotes = false,
		currentLesson = null,
		videoProgress = { currentTime: 0 },
		onAddNote = () => {},
		onDeleteNote = () => {}
	} = $props();

	let filteredNotes = $derived.by(() => {
		const query = noteSearchQuery.trim().toLowerCase();
		if (!query) return notes;
		return notes.filter(
			(note) =>
				note.content?.toLowerCase().includes(query) ||
				note.lessonTitle?.toLowerCase().includes(query)
		);
	});

	function formatTimestamp(seconds = 0) {
		const m = Math.floor(seconds / 60);
		const s = Math.floor(seconds % 60);
		return `${m}:${s.toString().padStart(2, '0')}`;
	}
</script>

<div class="space-y-4">
	<div class="flex items-center justify-between">
		<h3 class="font-medium text-gray-900 dark:text-white">{$t('learn.myNotes')}</h3>
		{#if currentLesson}
			<span class="text-xs text-gray-500 dark:text-gray-400">
				{$t('learn.atTime', { time: formatTimestamp(videoProgress?.currentTime) })}
			</span>
		{/if}
	</div>

	<div class="space-y-2">
		<textarea
			bind:value={currentNote}
			placeholder={$t('learn.writeNote')}
			class="focus:border-primary-500 focus:ring-primary-500 h-24 w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
		></textarea>
		<button
			onclick={onAddNote}
			disabled={!currentNote.trim() || savingNote}
			class="bg-primary-600 hover:bg-primary-700 w-full rounded-lg px-3 py-2 text-sm font-medium text-white transition-colors disabled:cursor-not-allowed disabled:opacity-50"
		>
			{savingNote ? $t('learn.saving') : $t('learn.addNote')}
		</button>
	</div>

	{#if notes.length > 0}
		<input
			type="search"
			bind:value={noteSearchQuery}
			placeholder={$t('learn.searchNotes')}
			class="focus:border-primary-500 focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
		/>
	{/if}

	{#if loadingNotes}
		<p class="text-sm text-gray-500 dark:text-gray-400">{$t('learn.loadingNotes')}</p>
	{:else if filteredNotes.length === 0}
		<p class="text-sm text-gray-500 dark:text-gray-400">
			{notes.length === 0 ? $t('learn.noNotes') : $t('learn.noNotesMatch')}
		</p>
	{:else}
		<ul class="space-y-2">
			{#each filteredNotes as note (note.id)}
				<li class="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
					<div class="mb-1 flex items-center justify-between gap-2">
						<span class="truncate text-xs text-gray-500 dark:text-gray-400">
							{note.lessonTitle ?? $t('learn.lesson')} · {formatTimestamp(note.timestamp)}
						</span>
						<button
							onclick={() => onDeleteNote(note.id)}
							class="text-xs text-red-600 hover:underline dark:text-red-400"
							aria-label={$t('learn.deleteNote')}
						>
							{$t('learn.delete')}
						</button>
					</div>
					<p class="text-sm whitespace-pre-wrap text-gray-900 dark:text-white">{note.content}</p>
				</li>
			{/each}
		</ul>
	{/if}
</div>

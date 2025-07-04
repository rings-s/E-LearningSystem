<!-- front/src/routes/(app)/my-courses/[uuid]/notes/+page.svelte -->
<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { coursesApi } from '$lib/apis/courses.js';
	import { currentUser } from '$lib/stores/auth.store.js';
	import { formatters } from '$lib/utils/formatters.js';
	import { debounce } from '$lib/utils/helpers.js';

	// Components
	import Card from '$lib/components/common/Card.svelte';
	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';

	const courseId = $page.params.uuid;

	let course = $state(null);
	let lessonsWithNotes = $state([]);
	let loading = $state(true);
	let searchQuery = $state('');
	let editingNote = $state(null);
	let tempNoteContent = $state('');

	// Filter lessons based on search
	let filteredLessons = $derived(() => {
		if (!searchQuery.trim()) return lessonsWithNotes;
		return lessonsWithNotes.filter(lesson => 
			lesson.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
			lesson.moduleTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
			lesson.notes.toLowerCase().includes(searchQuery.toLowerCase())
		);
	});

	onMount(async () => {
		await Promise.all([fetchCourse(), fetchNotesData()]);
	});

	const fetchCourse = async () => {
		try {
			course = await coursesApi.getCourse(courseId);
		} catch (error) {
			// Fail silently, as the main data is the notes themselves
		}
	};

	const fetchNotesData = async () => {
		loading = true;
		try {
			const courseData = await coursesApi.getCourse(courseId, { cache: 'no-store' });
			if (!courseData.modules) return;

			const allLessons = courseData.modules.flatMap(module =>
				module.lessons.map(lesson => ({
					...lesson,
					moduleTitle: module.title
				}))
			);

			// Fetch notes for each lesson
			const lessonsWithNotesData = await Promise.all(
				allLessons.map(async (lesson) => {
					try {
						const notesResponse = await coursesApi.getLessonNotes(lesson.uuid, { cache: 'no-store' });
						return {
							...lesson,
							notes: notesResponse.notes || '',
							hasNotes: !!(notesResponse.notes && notesResponse.notes.trim())
						};
					} catch (error) {
						return {
							...lesson,
							notes: '',
							hasNotes: false
						};
					}
				})
			);

			// Only show lessons that have notes
			lessonsWithNotes = lessonsWithNotesData.filter(lesson => lesson.hasNotes);
		} catch (error) {
			// Handle error appropriately
		} finally {
			loading = false;
		}
	};

	const editNote = (lesson) => {
		editingNote = lesson.uuid;
		tempNoteContent = lesson.notes;
	};

	const saveNote = async (lesson) => {
		try {
			await coursesApi.saveLessonNotes(lesson.uuid, tempNoteContent);
			
			// Update the lesson in our state
			const lessonIndex = lessonsWithNotes.findIndex(l => l.uuid === lesson.uuid);
			if (lessonIndex !== -1) {
				lessonsWithNotes[lessonIndex].notes = tempNoteContent;
				lessonsWithNotes[lessonIndex].hasNotes = !!(tempNoteContent && tempNoteContent.trim());
				
				// Remove from list if notes are empty
				if (!lessonsWithNotes[lessonIndex].hasNotes) {
					lessonsWithNotes = lessonsWithNotes.filter((_, i) => i !== lessonIndex);
				}
			}
			
			editingNote = null;
		} catch (error) {
			alert('Failed to save note. Please try again.');
		}
	};

	const cancelEdit = () => {
		editingNote = null;
		tempNoteContent = '';
	};

	const deleteNote = async (lesson) => {
		if (!confirm('Are you sure you want to delete this note?')) return;
		
		try {
			await coursesApi.saveLessonNotes(lesson.uuid, '');
			lessonsWithNotes = lessonsWithNotes.filter(l => l.uuid !== lesson.uuid);
		} catch (error) {
			alert('Failed to delete note. Please try again.');
		}
	};
</script>

<svelte:head>
	<title>My Notes - {course?.title || 'Course'} - 244SCHOOL</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
	<div class="container mx-auto px-4 py-8">
		<!-- Header -->
		<div class="mb-8" in:fade={{ duration: 600 }}>
			<div class="mb-4 flex items-center gap-4">
				<Button
					href={`/courses/${courseId}`}
					variant="ghost"
					size="medium"
					class="text-gray-600 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400"
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
					Back to Course
				</Button>
			</div>

			<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">My Notes</h1>
			<p class="text-lg text-gray-600 dark:text-gray-400">
				{#if course}
					All your notes for <span class="font-medium text-primary-600 dark:text-primary-400">{course.title}</span>
				{:else}
					Your course notes
				{/if}
			</p>
		</div>

		<!-- Search and Actions -->
		<div class="mb-6" in:fly={{ y: 20, delay: 200, duration: 600 }}>
			<Card variant="bordered" class="bg-white/80 backdrop-blur-sm dark:bg-gray-800/80">
				<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
					<Input
						type="search"
						placeholder="Search your notes..."
						bind:value={searchQuery}
						class="flex-1"
						icon="<path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' />"
					/>
					
					<div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						{filteredLessons.length} {filteredLessons.length === 1 ? 'note' : 'notes'}
					</div>
				</div>
			</Card>
		</div>

		<!-- Notes List -->
		{#if loading}
			<div class="space-y-4">
				{#each Array(3) as _, index}
					<div class="animate-pulse" in:fly={{ y: 20, delay: index * 100, duration: 400 }}>
						<Card variant="bordered">
							<div class="space-y-3">
								<div class="h-6 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-4 w-1/2 rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-20 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{:else if filteredLessons.length === 0}
			<div in:fade={{ delay: 400, duration: 500 }}>
				<Card variant="bordered" class="py-16 text-center">
					<svg class="mx-auto mb-6 h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">
						{searchQuery ? 'No notes found' : 'No notes yet'}
					</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">
						{searchQuery 
							? 'Try adjusting your search terms'
							: 'Start taking notes while learning to see them here'
						}
					</p>
					{#if !searchQuery}
						<Button
							href={`/courses/${courseId}/learn`}
							variant="primary"
							size="medium"
						>
							Start Learning
						</Button>
					{/if}
				</Card>
			</div>
		{:else}
			<div class="space-y-4">
				{#each filteredLessons as lesson, index}
					<div in:fly={{ y: 20, delay: index * 100, duration: 600 }}>
						<Card 
							variant="bordered" 
							class="transition-all duration-200 hover:shadow-md"
						>
							<div class="space-y-4">
								<!-- Lesson Header -->
								<div class="flex items-start justify-between">
									<div class="flex-1">
										<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
											{lesson.title}
										</h3>
										<p class="text-sm text-gray-600 dark:text-gray-400">
											{lesson.moduleTitle}
										</p>
									</div>
									
									<div class="flex items-center gap-2">
										<Button
											href={`/courses/${courseId}/learn`}
											variant="ghost"
											size="small"
											class="text-primary-600 hover:text-primary-700 dark:text-primary-400"
										>
											<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											Go to Lesson
										</Button>
										
										{#if editingNote === lesson.uuid}
											<Button onclick={() => saveNote(lesson)} variant="primary" size="small">
												Save
											</Button>
											<Button onclick={cancelEdit} variant="ghost" size="small">
												Cancel
											</Button>
										{:else}
											<Button onclick={() => editNote(lesson)} variant="ghost" size="small">
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
												</svg>
											</Button>
											<Button onclick={() => deleteNote(lesson)} variant="ghost" size="small" class="text-red-600 hover:text-red-700">
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
												</svg>
											</Button>
										{/if}
									</div>
								</div>

								<!-- Note Content -->
								<div class="border-t border-gray-200 pt-4 dark:border-gray-700">
									{#if editingNote === lesson.uuid}
										<textarea
											bind:value={tempNoteContent}
											class="focus:ring-primary-500 focus:border-primary-500 w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
											rows="6"
											placeholder="Edit your notes..."
										></textarea>
									{:else}
										<div class="prose prose-sm dark:prose-invert max-w-none">
											<p class="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
												{lesson.notes}
											</p>
										</div>
									{/if}
								</div>
							</div>
						</Card>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
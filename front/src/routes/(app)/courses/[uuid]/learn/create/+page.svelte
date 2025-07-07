<!-- Addition to front/src/routes/(app)/courses/[uuid]/learn/+page.svelte -->
<!-- Add this after the existing script imports -->

<script>
	// ... existing imports and code ...
	
	// Add this state for lesson creation
	let showCreateLessonModal = $state(false);
	
	// Add this derived state to check if user can create lessons
	let canCreateLessons = $derived(() => 
		$currentUser?.role === 'teacher' || 
		$currentUser?.is_staff ||
		course?.instructor?.uuid === $currentUser?.uuid
	);
</script>

<!-- Add this button in the sidebar when activeTab is 'lessons' -->
<!-- Insert this in the lessons tab section -->

{:else if sidebar.activeTab === 'lessons'}
	<!-- Lesson List with Create Button -->
	<div class="space-y-4">
		{#if canCreateLessons}
			<div class="mb-4">
				<Button
					href={`/courses/${courseId}/learn/create`}
					variant="primary"
					size="small"
					fullWidth
					class="shadow-md hover:scale-105 transition-all"
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					Add New Lesson
				</Button>
			</div>
		{/if}

		{#if course?.modules}
			<LessonList
				modules={course.modules}
				currentLessonId={currentLesson?.uuid}
				onLessonClick={navigateToLesson}
				isEnrolled={!!enrollment}
			/>
		{/if}
	</div>
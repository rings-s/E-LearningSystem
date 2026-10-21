<!-- front/src/lib/components/layout/PreferenceToggles.svelte -->
<!-- Theme and language switches shared by the public header and the app top bar. -->
<script>
	import { uiStore, theme } from '#lib/stores/ui.store.js';
	import { locale, t } from '#lib/i18n/index.js';

	const iconButton =
		'flex size-10 items-center justify-center rounded-xl text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-white/10 dark:hover:text-white';
</script>

<button
	type="button"
	onclick={() => uiStore.setLanguage($locale === 'en' ? 'ar' : 'en')}
	class="{iconButton} w-auto px-3 text-sm font-medium"
	aria-label={$t('ui.switchLanguage')}
>
	{$locale === 'en' ? 'عربي' : 'EN'}
</button>

<button
	type="button"
	onclick={() => uiStore.toggleTheme()}
	class={iconButton}
	aria-label={$theme === 'dark' ? $t('ui.lightMode') : $t('ui.darkMode')}
>
	<svg class="size-5" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
		{#if $theme === 'dark'}
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"
			/>
		{:else}
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"
			/>
		{/if}
	</svg>
</button>

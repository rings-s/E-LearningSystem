<!-- front/src/lib/components/course/PDFViewer.svelte -->
<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	let {
		src = '',
		title = 'PDF Document',
		width = '100%',
		height = '600px',
		showToolbar = true,
		class: className = ''
	} = $props();

	let loading = $state(true);
	let error = $state(null);
	let pdfSupported = $state(false);

	onMount(() => {
		if (browser) {
			checkPDFSupport();
		}
	});

	function checkPDFSupport() {
		const isSupported = 'application/pdf' in navigator.mimeTypes || 
							navigator.userAgent.includes('Chrome') || 
							navigator.userAgent.includes('Firefox') ||
							navigator.userAgent.includes('Safari');
		pdfSupported = isSupported;
		loading = false;
	}

	function handleLoad() {
		loading = false;
		error = null;
	}

	function handleError() {
		loading = false;
		error = 'Failed to load PDF document';
	}

	function downloadPDF() {
		const link = document.createElement('a');
		link.href = src;
		link.download = title.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.pdf';
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	const pdfUrl = $derived(() => {
		if (!src) return '';
		if (!showToolbar && src.includes('.pdf')) {
			const separator = src.includes('?') ? '&' : '#';
			return `${src}${separator}toolbar=0&navpanes=0&scrollbar=0`;
		}
		return src;
	});
</script>

<div class="pdf-viewer {className}" style="width: {width}; height: {height};">
	{#if loading}
		<div class="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-800 rounded-lg">
			<div class="text-center">
				<div class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary-500 border-t-transparent"></div>
				<p class="text-gray-600 dark:text-gray-400">Loading PDF...</p>
			</div>
		</div>
	{:else if error}
		<div class="flex items-center justify-center h-full bg-red-50 dark:bg-red-900/20 rounded-lg border-2 border-red-200 dark:border-red-800">
			<div class="text-center text-red-600 dark:text-red-400">
				<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<p class="mb-4 font-medium">{error}</p>
				<button 
					onclick={downloadPDF}
					class="rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
				>
					Download PDF
				</button>
			</div>
		</div>
	{:else if !pdfSupported}
		<div class="flex items-center justify-center h-full bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border-2 border-yellow-200 dark:border-yellow-800">
			<div class="text-center text-yellow-600 dark:text-yellow-400">
				<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
				</svg>
				<p class="mb-4 font-medium">PDF viewing not supported in this browser</p>
				<button 
					onclick={downloadPDF}
					class="rounded-lg bg-yellow-600 px-4 py-2 text-white hover:bg-yellow-700 transition-colors focus:outline-none focus:ring-2 focus:ring-yellow-500"
				>
					Download PDF
				</button>
			</div>
		</div>
	{:else}
		<div class="relative h-full w-full overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
			<!-- PDF Header -->
			<div class="flex items-center justify-between bg-gray-100 px-4 py-2 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
				<h3 class="font-medium text-gray-900 dark:text-white truncate">{title}</h3>
				<div class="flex items-center gap-2">
					<button
						onclick={() => window.open(pdfUrl, '_blank')}
						class="rounded-lg bg-gray-600 px-3 py-1 text-sm text-white hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
						title="Open in new tab"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
						</svg>
					</button>
					<button
						onclick={downloadPDF}
						class="rounded-lg bg-primary-600 px-3 py-1 text-sm text-white hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
						title="Download PDF"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
					</button>
				</div>
			</div>

			<!-- PDF Content -->
			<div class="h-full bg-white dark:bg-gray-900">
				{#if pdfUrl}
					<iframe
						src={pdfUrl}
						title={title}
						class="h-full w-full border-0"
						onload={handleLoad}
						onerror={handleError}
						style="height: calc(100% - 3rem);"
						sandbox="allow-scripts allow-same-origin allow-downloads"
					></iframe>
				{:else}
					<div class="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-800">
						<div class="text-center text-gray-500 dark:text-gray-400">
							<svg class="mx-auto mb-4 h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							<p>No PDF source provided</p>
						</div>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.pdf-viewer {
		position: relative;
		background: white;
		border-radius: 0.5rem;
		overflow: hidden;
	}

	:global(.dark) .pdf-viewer {
		background: rgb(31 41 55);
	}

	.pdf-viewer iframe {
		display: block;
		width: 100%;
	}
</style>
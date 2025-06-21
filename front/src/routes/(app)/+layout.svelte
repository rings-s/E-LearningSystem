<!-- front/src/routes/(app)/+layout.svelte -->
<script>
    import { page } from '$app/stores';
    import { fade } from 'svelte/transition';
    import Header from '$lib/components/layout/Header.svelte';
    import Sidebar from '$lib/components/layout/Sidebar.svelte';
    import { uiStore } from '$lib/stores/ui.store.js';
    
    let { children } = $props();
  </script>
  
  <div class="min-h-screen">
    <Header />
    
    <div class="flex pt-24">
      <!-- Optional: Keep sidebar for desktop -->
      <Sidebar />
      
      <!-- Main Content -->
      <main class="flex-1 px-4 sm:px-6 lg:px-8 pb-8">
        <div class="max-w-7xl mx-auto">
          <div transition:fade={{ duration: 300 }}>
            {@render children()}
          </div>
        </div>
      </main>
    </div>
  </div>
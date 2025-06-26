<!-- front/src/routes/(auth)/login/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { authStore, isLoading } from '$lib/stores/auth.store.js';
  
  let email = $state('');
  let password = $state('');
  let error = $state('');

  async function handleSubmit(e) {
      e.preventDefault();
      error = '';
      
      const result = await authStore.login({ email, password });
      
      if (result.success) {
          goto('/dashboard');
      } else {
          error = result.error;
      }
  }
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="max-w-md w-full p-8">
      <h2 class="text-2xl font-bold mb-6">Login</h2>
      
      <form onsubmit={handleSubmit} class="space-y-4">
          <div>
              <label class="block text-sm font-medium mb-2">Email</label>
              <input 
                  type="email" 
                  bind:value={email}
                  required
                  class="w-full p-3 border rounded-lg"
                  placeholder="Enter your email"
              />
          </div>
          
          <div>
              <label class="block text-sm font-medium mb-2">Password</label>
              <input 
                  type="password" 
                  bind:value={password}
                  required
                  class="w-full p-3 border rounded-lg"
                  placeholder="Enter your password"
              />
          </div>
          
          {#if error}
              <p class="text-red-600 text-sm">{error}</p>
          {/if}
          
          <button 
              type="submit" 
              disabled={$isLoading}
              class="w-full bg-blue-600 text-white p-3 rounded-lg disabled:opacity-50"
          >
              {$isLoading ? 'Logging in...' : 'Login'}
          </button>
      </form>
      
      <p class="mt-4 text-center">
          Don't have an account? 
          <a href="/register" class="text-blue-600 hover:underline">Register</a>
      </p>
  </div>
</div>
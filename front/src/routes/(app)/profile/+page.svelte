<!-- front/src/routes/(app)/profile/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { authStore, currentUser } from '$lib/stores/auth.store.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import { validators, validateForm } from '$lib/utils/validators.js';
    import Card from '$lib/components/common/Card.svelte';
    import Button from '$lib/components/common/Button.svelte';
    import Tabs from '$lib/components/common/Tabs.svelte';
    import Input from '$lib/components/common/Input.svelte';
    import Badge from '$lib/components/common/Badge.svelte';
  
    let loading = $state(false);
    let uploadingAvatar = $state(false);
    let profileData = $state({
      first_name: '',
      last_name: '',
      phone_number: '',
      date_of_birth: '',
      bio: '',
      education_level: '',
      institution: '',
      field_of_study: '',
      learning_goals: '',
      linkedin_url: '',
      github_url: '',
      website_url: ''
    });
  
    let errors = $state({});
  
    const tabs = [
      {
        label: $t('profile.personalInfo'),
        content: () => PersonalInfo
      },
      {
        label: $t('profile.education'),
        content: () => Education
      },
      {
        label: $t('profile.socialLinks'),
        content: () => SocialLinks
      },
      {
        label: $t('profile.preferences'),
        content: () => Preferences
      }
    ];
  
    onMount(() => {
      if ($currentUser) {
        profileData = {
          first_name: $currentUser.first_name || '',
          last_name: $currentUser.last_name || '',
          phone_number: $currentUser.phone_number || '',
          date_of_birth: $currentUser.date_of_birth || '',
          bio: $currentUser.profile?.bio || '',
          education_level: $currentUser.profile?.education_level || '',
          institution: $currentUser.profile?.institution || '',
          field_of_study: $currentUser.profile?.field_of_study || '',
          learning_goals: $currentUser.profile?.learning_goals || '',
          linkedin_url: $currentUser.profile?.linkedin_url || '',
          github_url: $currentUser.profile?.github_url || '',
          website_url: $currentUser.profile?.website_url || ''
        };
      }
    });
  
    const handleAvatarUpload = async (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
  
      uploadingAvatar = true;
      const result = await authStore.uploadAvatar(file);
      uploadingAvatar = false;
  
      if (result.success) {
        uiStore.showNotification({
          type: 'success',
          title: 'Avatar Updated',
          message: 'Your profile picture has been updated'
        });
      } else {
        uiStore.showNotification({
          type: 'error',
          title: 'Upload Failed',
          message: result.error || 'Failed to upload avatar'
        });
      }
    };
  
    const updateProfile = async () => {
      loading = true;
      const result = await authStore.updateProfile(profileData);
      loading = false;
  
      if (result.success) {
        uiStore.showNotification({
          type: 'success',
          title: 'Profile Updated',
          message: 'Your profile has been updated successfully'
        });
      } else {
        uiStore.showNotification({
          type: 'error',
          title: 'Update Failed',
          message: result.error || 'Failed to update profile'
        });
      }
    };
</script>
  
<div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        {$t('profile.profile')}
      </h1>
      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
        Manage your personal information and preferences
      </p>
    </div>
  
    <!-- Profile Card -->
    <Card variant="bordered">
      <div class="flex items-center gap-6">
        <div class="relative">
          {#if $currentUser?.avatar}
            <img
              src={$currentUser.avatar}
              alt={$currentUser.full_name}
              class="w-24 h-24 rounded-full object-cover"
            />
          {:else}
            <div class="w-24 h-24 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-2xl font-medium">
              {$currentUser?.first_name?.[0]}{$currentUser?.last_name?.[0]}
            </div>
          {/if}
          
          <label class="absolute bottom-0 right-0 w-8 h-8 bg-primary-600 hover:bg-primary-700 rounded-full flex items-center justify-center cursor-pointer transition-colors">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <input
              type="file"
              accept="image/*"
              class="hidden"
              onchange={handleAvatarUpload}
              disabled={uploadingAvatar}
            />
          </label>
        </div>
  
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {$currentUser?.full_name || $currentUser?.email}
          </h2>
          <p class="text-gray-600 dark:text-gray-400">
            {$currentUser?.email}
          </p>
          <div class="mt-2">
            <Badge variant="primary">
              {$t(`auth.${$currentUser?.role}`)}
            </Badge>
          </div>
        </div>
      </div>
    </Card>
  
    <!-- Profile Tabs -->
    <Tabs {tabs} />
  </div>
  
  {#snippet PersonalInfo()}
    <form onsubmit|preventDefault={updateProfile} class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label={$t('auth.firstName')}
          bind:value={profileData.first_name}
          error={errors.first_name}
          required
        />
        
        <Input
          label={$t('auth.lastName')}
          bind:value={profileData.last_name}
          error={errors.last_name}
          required
        />
      </div>
  
      <Input
        type="tel"
        label={$t('auth.phoneNumber')}
        bind:value={profileData.phone_number}
        error={errors.phone_number}
        placeholder="+1234567890"
      />
  
      <Input
        type="date"
        label={$t('auth.dateOfBirth')}
        bind:value={profileData.date_of_birth}
        error={errors.date_of_birth}
      />
  
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {$t('profile.bio')}
        </label>
        <textarea
          bind:value={profileData.bio}
          rows="4"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder="Tell us about yourself..."
        ></textarea>
      </div>
  
      <div class="pt-4">
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          Save Changes
        </Button>
      </div>
    </form>
  {/snippet}
  
  {#snippet Education()}
    <form onsubmit|preventDefault={updateProfile} class="space-y-4">
      <Input
        label={$t('profile.education')} Level"
        bind:value={profileData.education_level}
        placeholder="e.g., Bachelor's Degree"
      />
  
      <Input
        label="Institution"
        bind:value={profileData.institution}
        placeholder="e.g., University Name"
      />
  
      <Input
        label="Field of Study"
        bind:value={profileData.field_of_study}
        placeholder="e.g., Computer Science"
      />
  
      {#if $currentUser?.role === 'student'}
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Learning Goals
          </label>
          <textarea
            bind:value={profileData.learning_goals}
            rows="4"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="What do you want to achieve?"
          ></textarea>
        </div>
      {/if}
  
      <div class="pt-4">
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          Save Changes
        </Button>
      </div>
    </form>
  {/snippet}
  
  {#snippet SocialLinks()}
    <form onsubmit|preventDefault={updateProfile} class="space-y-4">
      <Input
        type="url"
        label="LinkedIn Profile"
        bind:value={profileData.linkedin_url}
        placeholder="https://linkedin.com/in/username"
        icon='<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'
      />
  
      <Input
        type="url"
        label="GitHub Profile"
        bind:value={profileData.github_url}
        placeholder="https://github.com/username"
        icon='<path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>'
      />
  
      <Input
        type="url"
        label="Personal Website"
        bind:value={profileData.website_url}
        placeholder="https://example.com"
        icon='<path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />'
      />
  
      <div class="pt-4">
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          Save Changes
        </Button>
      </div>
    </form>
  {/snippet}
  
  {#snippet Preferences()}
    <Card variant="bordered">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Account Settings
      </h3>
      
      <div class="space-y-4">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-white mb-2">
            Email Notifications
          </h4>
          <div class="space-y-2">
            <label class="flex items-center">
              <input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700">
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Course updates and announcements
              </span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700">
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Forum replies and mentions
              </span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700">
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Learning reminders
              </span>
            </label>
          </div>
        </div>
  
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
          <h4 class="font-medium text-gray-900 dark:text-white mb-2">
            Privacy
          </h4>
          <div class="space-y-2">
            <label class="flex items-center">
              <input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700">
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Show my profile to other students
              </span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700">
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Show my learning activity
              </span>
            </label>
          </div>
        </div>
  
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
          <Button variant="primary">
            Save Preferences
          </Button>
        </div>
      </div>
    </Card>
  {/snippet}
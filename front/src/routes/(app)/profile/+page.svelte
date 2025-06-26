<!-- front/src/routes/(app)/profile/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { authStore, currentUser } from '$lib/services/auth.service.js';
  import { authApi } from '$lib/apis/auth.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { validators, validateForm } from '$lib/utils/validators.js';
  import { classNames } from '$lib/utils/helpers.js';
  import FormField from '$lib/components/auth/FormField.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Card from '$lib/components/common/Card.svelte';
  import Tabs from '$lib/components/common/Tabs.svelte';

  let loading = $state(false);
  let uploadingAvatar = $state(false);
  let savingProfile = $state(false);
  let fileInput;
  
  let formData = $state({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    date_of_birth: '',
    bio: '',
    education_level: '',
    institution: '',
    field_of_study: '',
    learning_goals: '',
    preferred_language: 'en',
    time_zone: 'UTC',
    linkedin_url: '',
    github_url: '',
    website_url: ''
  });

  let errors = $state({});
  let touched = $state({});

  const validationRules = {
    first_name: [
      { validator: validators.required, message: 'First name is required' },
      { validator: validators.minLength(2), message: 'Name too short' }
    ],
    last_name: [
      { validator: validators.required, message: 'Last name is required' },
      { validator: validators.minLength(2), message: 'Name too short' }
    ],
    email: [
      { validator: validators.required, message: 'Email is required' },
      { validator: validators.email, message: 'Invalid email' }
    ],
    phone_number: [{ validator: validators.phoneNumber, message: 'Invalid phone number' }]
  };

  onMount(() => {
    const user = currentUser();
    if (user) {
      formData = {
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone_number: user.phone_number || '',
        date_of_birth: user.date_of_birth || '',
        bio: user.profile?.bio || '',
        education_level: user.profile?.education_level || '',
        institution: user.profile?.institution || '',
        field_of_study: user.profile?.field_of_study || '',
        learning_goals: user.profile?.learning_goals || '',
        preferred_language: user.profile?.preferred_language || 'en',
        time_zone: user.profile?.time_zone || 'UTC',
        linkedin_url: user.profile?.linkedin_url || '',
        github_url: user.profile?.github_url || '',
        website_url: user.profile?.website_url || ''
      };
    }
  });

  async function handleAvatarChange(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      uiStore.showNotification({
        type: 'error',
        title: 'Invalid file type',
        message: 'Please upload an image file'
      });
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      uiStore.showNotification({
        type: 'error',
        title: 'File too large',
        message: 'Maximum file size is 5MB'
      });
      return;
    }

    uploadingAvatar = true;

    try {
      const response = await authApi.uploadAvatar(file);
      
      // Update local user data
      await authStore.updateProfile({ avatar: response.avatar });
      
      uiStore.showNotification({
        type: 'success',
        title: 'Avatar updated',
        message: 'Your avatar has been updated successfully'
      });
    } catch (error) {
      console.error('Avatar upload error:', error);
      uiStore.showNotification({
        type: 'error',
        title: 'Error',
        message: error.message || 'Failed to upload avatar'
      });
    } finally {
      uploadingAvatar = false;
    }
  }

  async function handleProfileSubmit(e) {
    e.preventDefault();
    
    const validation = validateForm(formData, validationRules);
    if (!validation.isValid) {
      errors = validation.errors;
      Object.keys(validation.errors).forEach(key => {
        touched[key] = true;
      });
      return;
    }

    savingProfile = true;

    try {
      const result = await authStore.updateProfile(formData);
      
      if (result.success) {
        uiStore.showNotification({
          type: 'success',
          title: 'Profile updated',
          message: 'Your profile has been updated successfully'
        });
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('Profile update error:', error);
      uiStore.showNotification({
        type: 'error',
        title: 'Error',
        message: error.message || 'Failed to update profile'
      });
    } finally {
      savingProfile = false;
    }
  }

  const tabs = [
    {
      label: 'Personal Info',
      content: () => PersonalInfoTab
    },
    {
      label: 'Education',
      content: () => EducationTab
    },
    {
      label: 'Preferences',
      content: () => PreferencesTab
    },
    {
      label: 'Social Links',
      content: () => SocialLinksTab
    }
  ];

  function validateField(fieldName) {
    const value = formData[fieldName];
    const rules = validationRules[fieldName] || [];
    for (const rule of rules) {
      if (!rule.validator(value, formData)) {
        errors[fieldName] = rule.message;
        return false;
      }
    }
    delete errors[fieldName];
    errors = { ...errors };
    return true;
  }

  function handleFieldBlur(fieldName) {
    touched[fieldName] = true;
    validateField(fieldName);
  }

  function getFieldError(fieldName) {
    return touched[fieldName] ? errors[fieldName] : '';
  }

  function getFullName() {
    const user = currentUser();
    if (!user) return '';
    return `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email;
  }

  function getUserInitials() {
    const user = currentUser();
    if (!user) return '?';
    
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    } else if (user.first_name) {
      return user.first_name[0].toUpperCase();
    } else if (user.email) {
      return user.email[0].toUpperCase();
    }
    return '?';
  }
</script>

<svelte:head>
  <title>Profile - 244SCHOOL</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        Profile
      </h1>
      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
        Manage your profile information
      </p>
    </div>

    <!-- Avatar Section -->
    <Card variant="bordered">
      <div class="flex items-center gap-6">
        <div class="relative group">
          <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
            {#if currentUser()?.avatar}
              <img 
                src={currentUser().avatar} 
                alt={getFullName()}
                class="w-full h-full object-cover"
              />
            {:else}
              <div class="w-full h-full flex items-center justify-center text-2xl font-bold text-gray-400 dark:text-gray-600">
                {getUserInitials()}
              </div>
            {/if}
          </div>
          
          <button
            onclick={() => fileInput?.click()}
            disabled={uploadingAvatar}
            class={classNames(
              'absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity',
              uploadingAvatar && 'opacity-100'
            )}
          >
            {#if uploadingAvatar}
              <div class="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            {:else}
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            {/if}
          </button>
          
          <input
            bind:this={fileInput}
            type="file"
            accept="image/*"
            onchange={handleAvatarChange}
            class="hidden"
          />
        </div>
        
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {getFullName()}
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 capitalize">
            {currentUser()?.role || 'Student'}
          </p>
          <Button
            onclick={() => fileInput?.click()}
            variant="outline"
            size="small"
            class="mt-2"
            disabled={uploadingAvatar}
          >
            Change Avatar
          </Button>
        </div>
      </div>
    </Card>

    <!-- Profile Form -->
    <Card variant="bordered">
      <form onsubmit={handleProfileSubmit}>
        <Tabs {tabs} variant="underline" />

        <div class="mt-6 flex justify-end">
          <Button
            type="submit"
            variant="primary"
            loading={savingProfile}
            disabled={savingProfile}
          >
            {savingProfile ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Card>
  </div>
</div>

{#snippet PersonalInfoTab()}
  <div class="space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
      <FormField
        name="first_name"
        label="First Name"
        bind:value={formData.first_name}
        error={getFieldError('first_name')}
        onblur={() => handleFieldBlur('first_name')}
        required
      />
      
      <FormField
        name="last_name"
        label="Last Name"
        bind:value={formData.last_name}
        error={getFieldError('last_name')}
        onblur={() => handleFieldBlur('last_name')}
        required
      />
    </div>

    <FormField
      type="email"
      name="email"
      label="Email"
      bind:value={formData.email}
      error={getFieldError('email')}
      onblur={() => handleFieldBlur('email')}
      required
      disabled
    />

    <FormField
      type="tel"
      name="phone_number"
      label="Phone Number"
      bind:value={formData.phone_number}
      error={getFieldError('phone_number')}
      onblur={() => handleFieldBlur('phone_number')}
    />

    <FormField
      type="date"
      name="date_of_birth"
      label="Date of Birth"
      bind:value={formData.date_of_birth}
    />

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Bio
      </label>
      <textarea
        bind:value={formData.bio}
        rows="4"
        class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
        placeholder="Tell us about yourself..."
      ></textarea>
    </div>
  </div>
{/snippet}

{#snippet EducationTab()}
  <div class="space-y-6">
    <FormField
      name="education_level"
      label="Education Level"
      bind:value={formData.education_level}
      placeholder="e.g., Bachelor's Degree"
    />

    <FormField
      name="institution"
      label="Institution"
      bind:value={formData.institution}
      placeholder="Your school or university"
    />

    <FormField
      name="field_of_study"
      label="Field of Study"
      bind:value={formData.field_of_study}
      placeholder="Your major or field"
    />

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Learning Goals
      </label>
      <textarea
        bind:value={formData.learning_goals}
        rows="4"
        class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
        placeholder="What do you want to achieve?"
      ></textarea>
    </div>
  </div>
{/snippet}

{#snippet PreferencesTab()}
  <div class="space-y-6">
    <FormField
      type="select"
      name="preferred_language"
      label="Preferred Language"
      bind:value={formData.preferred_language}
      options={[
        { value: 'en', label: 'English' },
        { value: 'ar', label: 'العربية' }
      ]}
    />

    <FormField
      type="select"
      name="time_zone"
      label="Time Zone"
      bind:value={formData.time_zone}
      options={[
        { value: 'UTC', label: 'UTC' },
        { value: 'America/New_York', label: 'Eastern Time' },
        { value: 'America/Chicago', label: 'Central Time' },
        { value: 'America/Denver', label: 'Mountain Time' },
        { value: 'America/Los_Angeles', label: 'Pacific Time' },
        { value: 'Europe/London', label: 'London' },
        { value: 'Europe/Paris', label: 'Paris' },
        { value: 'Asia/Dubai', label: 'Dubai' },
        { value: 'Asia/Kolkata', label: 'India' },
        { value: 'Asia/Singapore', label: 'Singapore' },
        { value: 'Asia/Tokyo', label: 'Tokyo' },
        { value: 'Australia/Sydney', label: 'Sydney' }
      ]}
    />
  </div>
{/snippet}

{#snippet SocialLinksTab()}
  <div class="space-y-6">
    <FormField
      type="url"
      name="linkedin_url"
      label="LinkedIn"
      bind:value={formData.linkedin_url}
      placeholder="https://linkedin.com/in/yourprofile"
    />

    <FormField
      type="url"
      name="github_url"
      label="GitHub"
      bind:value={formData.github_url}
      placeholder="https://github.com/yourusername"
    />

    <FormField
      type="url"
      name="website_url"
      label="Personal Website"
      bind:value={formData.website_url}
      placeholder="https://yourwebsite.com"
    />
  </div>
{/snippet}
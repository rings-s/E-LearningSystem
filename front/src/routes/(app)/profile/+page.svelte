<!-- front/src/routes/(app)/profile/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { authStore, currentUser } from '$lib/stores/auth.store.js';
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
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.minLength(2), message: $t('auth.nameTooShort') }
    ],
    last_name: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.minLength(2), message: $t('auth.nameTooShort') }
    ],
    email: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.email, message: $t('errors.invalidEmail') }
    ],
    phone_number: [{ validator: validators.phoneNumber, message: $t('errors.invalidPhone') }]
  };

  onMount(() => {
    if ($currentUser) {
      formData = {
        first_name: $currentUser.first_name || '',
        last_name: $currentUser.last_name || '',
        email: $currentUser.email || '',
        phone_number: $currentUser.phone_number || '',
        date_of_birth: $currentUser.date_of_birth || '',
        bio: $currentUser.profile?.bio || '',
        education_level: $currentUser.profile?.education_level || '',
        institution: $currentUser.profile?.institution || '',
        field_of_study: $currentUser.profile?.field_of_study || '',
        learning_goals: $currentUser.profile?.learning_goals || '',
        preferred_language: $currentUser.profile?.preferred_language || 'en',
        time_zone: $currentUser.profile?.time_zone || 'UTC',
        linkedin_url: $currentUser.profile?.linkedin_url || '',
        github_url: $currentUser.profile?.github_url || '',
        website_url: $currentUser.profile?.website_url || ''
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
        title: $t('errors.invalidFileType'),
        message: $t('errors.uploadImageOnly')
      });
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      uiStore.showNotification({
        type: 'error',
        title: $t('errors.fileTooLarge'),
        message: $t('errors.maxFileSize5MB')
      });
      return;
    }

    uploadingAvatar = true;

    try {
      const response = await authApi.uploadAvatar(file);
      
      // Update local user data
      authStore.updateProfile({ avatar: response.avatar });
      
      uiStore.showNotification({
        type: 'success',
        title: $t('profile.avatarUpdated'),
        message: $t('profile.avatarUpdateSuccess')
      });
    } catch (error) {
      uiStore.showNotification({
        type: 'error',
        title: $t('common.error'),
        message: error.message || $t('errors.uploadFailed')
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
          title: $t('profile.updated'),
          message: $t('profile.updateSuccess')
        });
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      uiStore.showNotification({
        type: 'error',
        title: $t('common.error'),
        message: error.message || $t('errors.updateFailed')
      });
    } finally {
      savingProfile = false;
    }
  }

  const tabs = [
    {
      label: $t('profile.personalInfo'),
      content: () => PersonalInfoTab
    },
    {
      label: $t('profile.education'),
      content: () => EducationTab
    },
    {
      label: $t('profile.preferences'),
      content: () => PreferencesTab
    },
    {
      label: $t('profile.socialLinks'),
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
</script>

<svelte:head>
  <title>{$t('profile.profile')} - EduVerse</title>
</svelte:head>

<div class="max-w-4xl mx-auto space-y-6">
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
      {$t('profile.profile')}
    </h1>
    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
      {$t('profile.manageYourProfile')}
    </p>
  </div>

  <!-- Avatar Section -->
  <Card variant="bordered">
    <div class="flex items-center gap-6">
      <div class="relative group">
        <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
          {#if $currentUser?.avatar}
            <img 
              src={$currentUser.avatar} 
              alt={$currentUser.full_name}
              class="w-full h-full object-cover"
            />
          {:else}
            <div class="w-full h-full flex items-center justify-center text-2xl font-bold text-gray-400 dark:text-gray-600">
              {$currentUser?.first_name?.[0]}{$currentUser?.last_name?.[0]}
            </div>
          {/if}
        </div>
        
        <button
          onclick={() => fileInput.click()}
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
          {$currentUser?.full_name || $currentUser?.email}
        </h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {$t(`auth.${$currentUser?.role}`)}
        </p>
        <Button
          onclick={() => fileInput.click()}
          variant="outline"
          size="small"
          class="mt-2"
          disabled={uploadingAvatar}
        >
          {$t('profile.changeAvatar')}
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
          {savingProfile ? $t('common.saving') : $t('common.save')}
        </Button>
      </div>
    </form>
  </Card>
</div>

{#snippet PersonalInfoTab()}
  <div class="space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
      <FormField
        name="first_name"
        label={$t('auth.firstName')}
        bind:value={formData.first_name}
        error={getFieldError('first_name')}
        onblur={() => handleFieldBlur('first_name')}
        required
      />
      
      <FormField
        name="last_name"
        label={$t('auth.lastName')}
        bind:value={formData.last_name}
        error={getFieldError('last_name')}
        onblur={() => handleFieldBlur('last_name')}
        required
      />
    </div>

    <FormField
      type="email"
      name="email"
      label={$t('auth.email')}
      bind:value={formData.email}
      error={getFieldError('email')}
      onblur={() => handleFieldBlur('email')}
      required
      disabled
    />

    <FormField
      type="tel"
      name="phone_number"
      label={$t('auth.phoneNumber')}
      bind:value={formData.phone_number}
      error={getFieldError('phone_number')}
      onblur={() => handleFieldBlur('phone_number')}
    />

    <FormField
      type="date"
      name="date_of_birth"
      label={$t('auth.dateOfBirth')}
      bind:value={formData.date_of_birth}
    />

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {$t('profile.bio')}
      </label>
      <textarea
        bind:value={formData.bio}
        rows="4"
        class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
        placeholder={$t('profile.tellUsAboutYourself')}
      ></textarea>
    </div>
  </div>
{/snippet}

{#snippet EducationTab()}
  <div class="space-y-6">
    <FormField
      name="education_level"
      label={$t('profile.educationLevel')}
      bind:value={formData.education_level}
      placeholder={$t('profile.selectEducationLevel')}
    />

    <FormField
      name="institution"
      label={$t('profile.institution')}
      bind:value={formData.institution}
      placeholder={$t('profile.enterInstitution')}
    />

    <FormField
      name="field_of_study"
      label={$t('profile.fieldOfStudy')}
      bind:value={formData.field_of_study}
      placeholder={$t('profile.enterFieldOfStudy')}
    />

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {$t('profile.learningGoals')}
      </label>
      <textarea
        bind:value={formData.learning_goals}
        rows="4"
        class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
        placeholder={$t('profile.describeLearningGoals')}
      ></textarea>
    </div>
  </div>
{/snippet}

{#snippet PreferencesTab()}
  <div class="space-y-6">
    <FormField
      type="select"
      name="preferred_language"
      label={$t('profile.preferredLanguage')}
      bind:value={formData.preferred_language}
      options={[
        { value: 'en', label: 'English' },
        { value: 'ar', label: 'العربية' }
      ]}
    />

    <FormField
      type="select"
      name="time_zone"
      label={$t('profile.timeZone')}
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
      icon='<path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />'
    />

    <FormField
      type="url"
      name="github_url"
      label="GitHub"
      bind:value={formData.github_url}
      placeholder="https://github.com/yourusername"
      icon='<path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />'
    />

    <FormField
      type="url"
      name="website_url"
      label={$t('profile.personalWebsite')}
      bind:value={formData.website_url}
      placeholder="https://yourwebsite.com"
      icon='<path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />'
    />
  </div>
{/snippet}
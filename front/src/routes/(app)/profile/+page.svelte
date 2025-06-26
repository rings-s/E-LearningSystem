<!-- front/src/routes/(app)/profile/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { authStore, currentUser } from '$lib/stores/auth.store.js';
  import { authApi } from '$lib/apis/auth.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { validators, validateForm } from '$lib/utils/validators.js';
  import { classNames } from '$lib/utils/helpers.js';
  import Button from '$lib/components/common/Button.svelte';
  import Card from '$lib/components/common/Card.svelte';

  let loading = $state(false);
  let uploadingAvatar = $state(false);
  let savingProfile = $state(false);
  let activeTab = $state('personal');
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
    time_zone: 'Africa/Khartoum', // Sudan timezone
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

  // Reactive computations
  let user = $state(null);
  
  // Watch for current user changes
  $effect(() => {
    user = $currentUser;
    if (user) {
      // Update form data when user changes
      formData.first_name = user.first_name || '';
      formData.last_name = user.last_name || '';
      formData.email = user.email || '';
      formData.phone_number = user.phone_number || '';
      formData.date_of_birth = user.date_of_birth || '';
      formData.bio = user.profile?.bio || '';
      formData.education_level = user.profile?.education_level || '';
      formData.institution = user.profile?.institution || '';
      formData.field_of_study = user.profile?.field_of_study || '';
      formData.learning_goals = user.profile?.learning_goals || '';
      formData.preferred_language = user.profile?.preferred_language || 'en';
      formData.time_zone = user.profile?.time_zone || 'Africa/Khartoum';
      formData.linkedin_url = user.profile?.linkedin_url || '';
      formData.github_url = user.profile?.github_url || '';
      formData.website_url = user.profile?.website_url || '';
    }
  });

  function getFullName() {
    if (!user) return 'Unknown User';
    
    const firstName = user.first_name?.trim() || '';
    const lastName = user.last_name?.trim() || '';
    
    if (firstName && lastName) {
      return `${firstName} ${lastName}`;
    } else if (firstName) {
      return firstName;
    } else if (lastName) {
      return lastName;
    } else {
      return user.email || 'Unknown User';
    }
  }

  function getUserInitials() {
    if (!user) return '?';
    
    const firstName = user.first_name?.trim() || '';
    const lastName = user.last_name?.trim() || '';
    
    if (firstName && lastName) {
      return `${firstName[0]}${lastName[0]}`.toUpperCase();
    } else if (firstName) {
      return firstName[0].toUpperCase();
    } else if (user.email) {
      return user.email[0].toUpperCase();
    }
    return '?';
  }

  async function handleAvatarChange(event) {
    const file = event.target.files[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      uiStore.showNotification({
        type: 'error',
        title: 'Invalid file type',
        message: 'Please upload an image file (JPG, PNG, WebP)'
      });
      return;
    }

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
      
      // Refresh user data
      await authStore.init();
      
      uiStore.showNotification({
        type: 'success',
        title: 'Avatar updated',
        message: 'Your avatar has been updated successfully'
      });
    } catch (error) {
      console.error('Avatar upload error:', error);
      uiStore.showNotification({
        type: 'error',
        title: 'Upload failed',
        message: error.message || 'Failed to upload avatar'
      });
    } finally {
      uploadingAvatar = false;
      // Clear the file input
      if (fileInput) {
        fileInput.value = '';
      }
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
      
      uiStore.showNotification({
        type: 'error',
        title: 'Validation Error',
        message: 'Please fix the errors below'
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
        
        // Reset touched fields after successful save
        touched = {};
        errors = {};
      } else {
        throw new Error(result.error || 'Failed to update profile');
      }
    } catch (error) {
      console.error('Profile update error:', error);
      uiStore.showNotification({
        type: 'error',
        title: 'Update failed',
        message: error.message || 'Failed to update profile'
      });
    } finally {
      savingProfile = false;
    }
  }

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
            {#if user?.avatar}
              <img 
                src={user.avatar} 
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
            type="button"
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
            {user?.role || 'Student'}
          </p>
          <Button
            type="button"
            onclick={() => fileInput?.click()}
            variant="outline"
            size="small"
            class="mt-2"
            disabled={uploadingAvatar}
          >
            {uploadingAvatar ? 'Uploading...' : 'Change Avatar'}
          </Button>
        </div>
      </div>
    </Card>

    <!-- Profile Form -->
    <Card variant="bordered">
      <form onsubmit={handleProfileSubmit}>
        <!-- Tab Navigation -->
        <div class="border-b border-gray-200 dark:border-gray-700 mb-6">
          <nav class="-mb-px flex space-x-8">
            <button
              type="button"
              onclick={() => activeTab = 'personal'}
              class="py-2 px-1 border-b-2 font-medium text-sm {
                activeTab === 'personal'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }"
            >
              Personal Info
            </button>
            <button
              type="button"
              onclick={() => activeTab = 'education'}
              class="py-2 px-1 border-b-2 font-medium text-sm {
                activeTab === 'education'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }"
            >
              Education
            </button>
            <button
              type="button"
              onclick={() => activeTab = 'preferences'}
              class="py-2 px-1 border-b-2 font-medium text-sm {
                activeTab === 'preferences'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }"
            >
              Preferences
            </button>
            <button
              type="button"
              onclick={() => activeTab = 'social'}
              class="py-2 px-1 border-b-2 font-medium text-sm {
                activeTab === 'social'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }"
            >
              Social Links
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        {#if activeTab === 'personal'}
          <div class="space-y-6">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  First Name *
                </label>
                <input
                  type="text"
                  bind:value={formData.first_name}
                  onblur={() => handleFieldBlur('first_name')}
                  required
                  class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200 {
                    getFieldError('first_name') ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
                  }"
                  placeholder="Enter your first name"
                />
                {#if getFieldError('first_name')}
                  <p class="mt-1 text-xs text-red-600">{getFieldError('first_name')}</p>
                {/if}
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Last Name *
                </label>
                <input
                  type="text"
                  bind:value={formData.last_name}
                  onblur={() => handleFieldBlur('last_name')}
                  required
                  class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200 {
                    getFieldError('last_name') ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
                  }"
                  placeholder="Enter your last name"
                />
                {#if getFieldError('last_name')}
                  <p class="mt-1 text-xs text-red-600">{getFieldError('last_name')}</p>
                {/if}
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email *
              </label>
              <input
                type="email"
                bind:value={formData.email}
                disabled
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 px-3 py-2 text-sm text-gray-500 dark:text-gray-400 cursor-not-allowed"
              />
              <p class="mt-1 text-xs text-gray-500">Email cannot be changed</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                bind:value={formData.phone_number}
                onblur={() => handleFieldBlur('phone_number')}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                placeholder="+249123456789"
              />
              {#if getFieldError('phone_number')}
                <p class="mt-1 text-xs text-red-600">{getFieldError('phone_number')}</p>
              {/if}
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Date of Birth
              </label>
              <input
                type="date"
                bind:value={formData.date_of_birth}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
              />
            </div>

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
        {:else if activeTab === 'education'}
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Education Level
              </label>
              <input
                type="text"
                bind:value={formData.education_level}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                placeholder="e.g., Bachelor's Degree"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Institution
              </label>
              <input
                type="text"
                bind:value={formData.institution}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                placeholder="Your school or university"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Field of Study
              </label>
              <input
                type="text"
                bind:value={formData.field_of_study}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                placeholder="Your major or field"
              />
            </div>

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
        {:else if activeTab === 'preferences'}
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Preferred Language
              </label>
              <select
                bind:value={formData.preferred_language}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
              >
                <option value="en">English</option>
                <option value="ar">العربية (Arabic)</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Time Zone
              </label>
              <select
                bind:value={formData.time_zone}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
              >
                <option value="Africa/Khartoum">Sudan (CAT)</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="Europe/London">London</option>
                <option value="Asia/Dubai">Dubai</option>
                <option value="Asia/Riyadh">Riyadh</option>
              </select>
            </div>
          </div>
        {:else if activeTab === 'social'}
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                LinkedIn
              </label>
              <input
                type="url"
                bind:value={formData.linkedin_url}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                placeholder="https://linkedin.com/in/yourprofile"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                GitHub
              </label>
              <input
                type="url"
                bind:value={formData.github_url}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                placeholder="https://github.com/yourusername"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Personal Website
              </label>
              <input
                type="url"
                bind:value={formData.website_url}
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                placeholder="https://yourwebsite.com"
              />
            </div>
          </div>
        {/if}

        <!-- Save Button -->
        <div class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              loading={savingProfile}
              disabled={savingProfile}
              class="min-w-[120px]"
            >
              {savingProfile ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
      </form>
    </Card>
  </div>
</div>
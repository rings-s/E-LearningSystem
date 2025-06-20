<!-- front/src/routes/(auth)/register/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.store.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { validators } from '$lib/utils/validators.js';
  import { ROLES } from '$lib/utils/constants.js';
  import FormField from '$lib/components/auth/FormField.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Card from '$lib/components/common/Card.svelte';

  // --- State Definition ---
  let currentStep = $state(0);
  let loading = $state(false);
  
  let formData = $state({
    role: '',
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    date_of_birth: '',
    password: '',
    confirm_password: ''
  });

  // --- Types for strong type-safety ---
  type FormData = typeof formData;
  type FormFieldNames = keyof FormData;
  type Errors = { [K in FormFieldNames]?: string };
  type Touched = { [K in FormFieldNames]?: boolean };

  let errors = $state<Errors>({});
  let touched = $state<Touched>({});

  // --- Validation Logic ---
  const validationRules: { [key: string]: any[] } = {
    role: [{ validator: validators.required, message: 'Please select an account type' }],
    first_name: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.minLength(2), message: 'Name must be at least 2 characters' }
    ],
    last_name: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.minLength(2), message: 'Name must be at least 2 characters' }
    ],
    email: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.email, message: $t('errors.invalidEmail') }
    ],
    phone_number: [{ validator: validators.phoneNumber, message: 'Invalid phone number format' }],
    password: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.minLength(8), message: $t('errors.passwordTooShort') }
    ],
    confirm_password: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.matchField('password'), message: $t('errors.passwordsDoNotMatch') }
    ]
  };

  const validateField = (fieldName: FormFieldNames): boolean => {
    const value = formData[fieldName];
    const rules = validationRules[fieldName] || [];
    for (const rule of rules) {
      if (!rule.validator(value, formData)) {
        errors[fieldName] = rule.message;
        return false;
      }
    }
    delete errors[fieldName];
    return true;
  };

  const handleFieldBlur = (fieldName: FormFieldNames) => {
    touched[fieldName] = true;
    validateField(fieldName);
  };

  const getFieldError = (fieldName: FormFieldNames): string | undefined => {
    return touched[fieldName] ? errors[fieldName] : undefined;
  };

  // --- Step Management ---
  const stepFields: FormFieldNames[][] = [
    ['role'],
    ['first_name', 'last_name', 'email'],
    ['password', 'confirm_password']
  ];

  const isStepValid = (stepIndex: number): boolean => {
    const fields = stepFields[stepIndex];
    if (!fields) return false;
    
    const allFieldsHaveValues = fields.every(field => !!formData[field]);
    if (!allFieldsHaveValues) return false;

    const noErrorsForStep = fields.every(field => !errors[field]);
    return noErrorsForStep;
  };

  const nextStep = () => {
    const fieldsToValidate = stepFields[currentStep];
    fieldsToValidate.forEach(field => {
        touched[field] = true;
        validateField(field);
    });

    const currentStepIsValid = fieldsToValidate.every(field => validateField(field));

    if (currentStepIsValid) {
      if (currentStep < steps.length - 1) {
        currentStep++;
      }
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      currentStep--;
    }
  };

  // --- Derived State ---
  const passwordStrength = $derived.by(() => {
    const password = formData.password;
    if (!password) return { score: 0, text: '', color: 'gray' };
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    const levels = [
      { score: 0, text: '', color: 'gray' },
      { score: 1, text: 'Very Weak', color: 'red' },
      { score: 2, text: 'Weak', color: 'orange' },
      { score: 3, text: 'Fair', color: 'yellow' },
      { score: 4, text: 'Good', color: 'blue' },
      { score: 5, text: 'Strong', color: 'green' }
    ];
    return levels[score];
  });

  const steps = $derived([
    {
      title: 'Account Type',
      description: 'Choose your role',
      completed: isStepValid(0) && currentStep > 0
    },
    {
      title: 'Personal Information',
      description: 'Tell us about yourself',
      completed: isStepValid(1) && currentStep > 1
    },
    {
      title: 'Security',
      description: 'Secure your account',
      completed: false
    }
  ]);
  
  const canProceed = $derived(isStepValid(currentStep));

  // --- Form Submission ---
  const handleSubmit = async () => {
    stepFields.flat().forEach(field => {
        touched[field] = true;
        validateField(field as FormFieldNames);
    });

    const isFormValid = stepFields.every((_, index) => isStepValid(index));

    if (!isFormValid) {
      uiStore.showNotification({
        type: 'error',
        title: 'Validation Error',
        message: 'Please fix the errors before submitting.'
      });
      return;
    }

    loading = true;
    const result = await authStore.register(formData);
    loading = false;

    if (result.success) {
      uiStore.showNotification({
        type: 'success',
        title: $t('auth.registerSuccess'),
        message: 'Please check your email for verification code'
      });
      goto(`/verify-email?email=${encodeURIComponent(formData.email)}`);
    } else {
      uiStore.showNotification({
        type: 'error',
        title: $t('common.error'),
        message: result.error || 'Registration failed'
      });
    }
  };
  
  // --- UI Data ---
  const roleOptions = [
    { value: ROLES.STUDENT, label: $t('auth.student'), description: 'Learn new skills and earn certificates', icon: '🎓' },
    { value: ROLES.TEACHER, label: $t('auth.teacher'), description: 'Create and teach courses to students', icon: '👨‍🏫' }
  ];

</script>

<svelte:head>
<title>Register - {$t('common.appName')}</title>
</svelte:head>

<!-- Include Header -->
<header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <!-- Logo -->
      <a href="/" class="flex items-center space-x-3">
        <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center text-white font-bold">
          E
        </div>
        <span class="text-lg font-semibold text-gray-900 dark:text-white">
          {$t('common.appName')}
        </span>
      </a>
      
      <!-- Right side controls -->
      <div class="flex items-center space-x-4">
        <!-- Theme Toggle -->
        <button
          onclick={() => uiStore.toggleTheme()}
          class="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors"
          aria-label="Toggle theme"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>

        <!-- Auth Links -->
        <div class="flex items-center space-x-4">
          <a href="/login" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400">
            {$t('auth.login')}
          </a>
          <a href="/courses" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400">
            Courses
          </a>
        </div>
      </div>
    </div>
  </div>
</header>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
  <!-- Header -->
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      {$t('auth.register')}
    </h1>
    <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
      {$t('auth.alreadyHaveAccount')}
      <a href="/login" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">
        {$t('auth.login')}
      </a>
    </p>
  </div>

  <Card variant="bordered" padding="large">
    <!-- Progress Steps -->
    <div class="mb-8">
      <nav aria-label="Progress">
        <ol class="flex items-center">
          {#each steps as step, index}
            <li class="relative {index !== steps.length - 1 ? 'flex-1 pr-8 sm:pr-20' : ''}">
              <!-- Step indicator -->
              <div class="flex items-center">
                <div class="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 {
                  index < currentStep
                    ? 'bg-primary-600 text-white'
                    : index === currentStep
                    ? 'border-2 border-primary-600 bg-white text-primary-600 dark:bg-gray-800'
                    : 'border-2 border-gray-300 bg-white text-gray-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400'
                }">
                  {#if index < currentStep}
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  {:else}
                    <span class="text-sm font-medium">{index + 1}</span>
                  {/if}
                </div>
                
                <div class="ml-4 min-w-0 hidden sm:block">
                  <span class="text-sm font-medium {
                    index === currentStep
                      ? 'text-primary-600 dark:text-primary-400'
                      : index < currentStep
                      ? 'text-gray-900 dark:text-white'
                      : 'text-gray-500 dark:text-gray-400'
                  }">{step.title}</span>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{step.description}</p>
                </div>
              </div>

              <!-- Connector line -->
              {#if index !== steps.length - 1}
                <div class="absolute top-5 left-10 w-full h-0.5 {
                  index < currentStep ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
                }"></div>
              {/if}
            </li>
          {/each}
        </ol>
      </nav>
    </div>

    <!-- Step Content -->
    <div class="space-y-6">
      {#if currentStep === 0}
        <!-- Step 1: Account Type -->
        <div class="space-y-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            How do you want to use {$t('common.appName')}?
          </h3>
          
          <div class="grid gap-4">
            {#each roleOptions as option}
              <button
                type="button"
                onclick={() => formData.role = option.value}
                class="relative p-6 border-2 rounded-xl text-left transition-all hover:shadow-md {
                  formData.role === option.value 
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }"
              >
                <div class="flex items-start gap-4">
                  <div class="text-3xl">{option.icon}</div>
                  <div class="flex-1">
                    <h4 class="font-semibold text-gray-900 dark:text-white">
                      {option.label}
                    </h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {option.description}
                    </p>
                  </div>
                  {#if formData.role === option.value}
                    <div class="flex-shrink-0">
                      <div class="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                  {/if}
                </div>
              </button>
            {/each}
          </div>
          
          {#if getFieldError('role')}
            <p class="text-sm text-red-600 dark:text-red-400">{getFieldError('role')}</p>
          {/if}
        </div>
      {:else if currentStep === 1}
        <!-- Step 2: Personal Information -->
        <div class="space-y-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            Tell us about yourself
          </h3>
          
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <FormField
                name="first_name"
                label={$t('auth.firstName')}
                bind:value={formData.first_name}
                error={getFieldError('first_name')}
                onblur={() => handleFieldBlur('first_name')}
                required
                icon='<path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />'
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
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
            />

            <FormField
              type="tel"
              name="phone_number"
              label="{$t('auth.phoneNumber')} (Optional)"
              bind:value={formData.phone_number}
              error={getFieldError('phone_number')}
              onblur={() => handleFieldBlur('phone_number')}
              placeholder="+1234567890"
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />'
            />

            <FormField
              type="date"
              name="date_of_birth"
              label="{$t('auth.dateOfBirth')} (Optional)"
              bind:value={formData.date_of_birth}
              error={getFieldError('date_of_birth')}
              onblur={() => handleFieldBlur('date_of_birth')}
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />'
            />
          </div>
        </div>
      {:else if currentStep === 2}
        <!-- Step 3: Security -->
        <div class="space-y-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            Secure your account
          </h3>
          
          <div class="space-y-4">
            <FormField
              type="password"
              name="password"
              label={$t('auth.password')}
              bind:value={formData.password}
              error={getFieldError('password')}
              onblur={() => handleFieldBlur('password')}
              required
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
            />

            {#if formData.password}
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Password strength:</span>
                  <span class="text-sm font-medium" style="color: {passwordStrength.color === 'red' ? '#ef4444' : passwordStrength.color === 'orange' ? '#f97316' : passwordStrength.color === 'yellow' ? '#eab308' : passwordStrength.color === 'blue' ? '#3b82f6' : passwordStrength.color === 'green' ? '#22c55e' : '#6b7280'}">
                    {passwordStrength.text}
                  </span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full transition-all duration-300"
                    style="width: {(passwordStrength.score / 5) * 100}%; background-color: {passwordStrength.color === 'red' ? '#ef4444' : passwordStrength.color === 'orange' ? '#f97316' : passwordStrength.color === 'yellow' ? '#eab308' : passwordStrength.color === 'blue' ? '#3b82f6' : passwordStrength.color === 'green' ? '#22c55e' : '#6b7280'}"
                  ></div>
                </div>
              </div>
            {/if}

            <FormField
              type="password"
              name="confirm_password"
              label={$t('auth.confirmPassword')}
              bind:value={formData.confirm_password}
              error={getFieldError('confirm_password')}
              onblur={() => handleFieldBlur('confirm_password')}
              required
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
            />

            <div class="pt-2">
              <p class="text-xs text-gray-600 dark:text-gray-400">
                By creating an account, you agree to our 
                <a href="/terms" class="text-primary-600 hover:text-primary-500 dark:text-primary-400">Terms of Service</a> 
                and 
                <a href="/privacy" class="text-primary-600 hover:text-primary-500 dark:text-primary-400">Privacy Policy</a>
              </p>
            </div>
          </div>
        </div>
      {/if}

      <!-- Navigation Buttons -->
      <div class="flex justify-between pt-8 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="outline"
          onclick={prevStep}
          disabled={currentStep === 0}
        >
          Previous
        </Button>
        
        <div class="flex gap-2">
          {#if currentStep < 2}
            <Button
              variant="primary"
              onclick={nextStep}
              disabled={!canProceed}
            >
              Next
            </Button>
          {:else}
            <Button
              variant="primary"
              loading={loading}
              disabled={!canProceed}
              onclick={handleSubmit}
            >
              Create Account
            </Button>
          {/if}
        </div>
      </div>
    </div>
  </Card>

  <!-- Footer -->
  <div class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
    <p>
      Need help? <a href="/help" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">Contact Support</a>
    </p>
  </div>
</div>
</div>
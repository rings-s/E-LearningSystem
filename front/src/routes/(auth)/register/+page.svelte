<!-- front/src/routes/register/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.store.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { validators, validateForm } from '$lib/utils/validators.js';
  import { ROLES } from '$lib/utils/constants.js';
  import FormField from '$lib/components/auth/FormField.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Card from '$lib/components/common/Card.svelte';

  let currentStep = $state(0);
  let loading = $state(false);
  let formData = $state({
    // Step 1 - Account Type
    role: '',
    
    // Step 2 - Personal Info
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    date_of_birth: '',
    
    // Step 3 - Security
    password: '',
    confirm_password: ''
  });

  let errors = $state({});
  let touched = $state({});

  // Convert from $: to $derived for Svelte 5 runes mode
  const passwordStrength = $derived(getPasswordStrength(formData.password));

  function getPasswordStrength(password) {
    if (!password) return { score: 0, text: '', color: 'gray' };
    
    let score = 0;
    const checks = {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      numbers: /\d/.test(password),
      symbols: /[^A-Za-z0-9]/.test(password)
    };
    
    score = Object.values(checks).filter(Boolean).length;
    
    const levels = [
      { score: 0, text: '', color: 'gray' },
      { score: 1, text: 'Very Weak', color: 'red' },
      { score: 2, text: 'Weak', color: 'orange' },
      { score: 3, text: 'Fair', color: 'yellow' },
      { score: 4, text: 'Good', color: 'blue' },
      { score: 5, text: 'Strong', color: 'green' }
    ];
    
    return levels[score] || levels[0];
  }

  const roleOptions = [
    { 
      value: ROLES.STUDENT, 
      label: $t('auth.student'),
      description: 'Learn new skills and earn certificates',
      icon: '🎓'
    },
    { 
      value: ROLES.TEACHER, 
      label: $t('auth.teacher'),
      description: 'Create and teach courses to students',
      icon: '👨‍🏫'
    }
  ];

  const steps = [
    {
      title: 'Account Type',
      description: 'Choose your role',
      completed: currentStep > 0 || !!formData.role
    },
    {
      title: 'Personal Information',
      description: 'Tell us about yourself',
      completed: currentStep > 1
    },
    {
      title: 'Security',
      description: 'Secure your account',
      completed: currentStep > 2
    }
  ];

  const validationRules = {
    role: [
      { validator: validators.required, message: 'Please select an account type' }
    ],
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
    phone_number: [
      { validator: validators.phoneNumber, message: 'Invalid phone number format' }
    ],
    password: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.minLength(8), message: $t('errors.passwordTooShort') }
    ],
    confirm_password: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.matchField('password'), message: $t('errors.passwordsDoNotMatch') }
    ]
  };

  const getFieldError = (fieldName) => {
    return touched[fieldName] ? errors[fieldName] || '' : '';
  };

  const handleFieldBlur = (fieldName) => {
    touched[fieldName] = true;
    validateField(fieldName);
  };

  const handleFieldInput = (fieldName) => {
    if (touched[fieldName]) {
      validateField(fieldName);
    }
  };

  const validateField = (fieldName) => {
    const fieldValue = formData[fieldName];
    const rules = validationRules[fieldName] || [];
    
    for (const rule of rules) {
      if (!rule.validator(fieldValue, formData)) {
        errors[fieldName] = rule.message;
        return false;
      }
    }
    
    // Clear error if validation passes
    if (errors[fieldName]) {
      delete errors[fieldName];
      errors = { ...errors };
    }
    return true;
  };

  const validateStep = (step) => {
    const fieldsToValidate = step === 0 ? ['role'] 
      : step === 1 ? ['first_name', 'last_name', 'email']
      : ['password', 'confirm_password'];
    
    // Mark fields as touched
    fieldsToValidate.forEach(field => {
      touched[field] = true;
    });

    const stepData = Object.fromEntries(
      fieldsToValidate.map(field => [field, formData[field]])
    );
    
    const stepRules = Object.fromEntries(
      fieldsToValidate.map(field => [field, validationRules[field]])
    );
    
    const validation = validateForm(stepData, stepRules);
    errors = { ...errors, ...validation.errors };
    
    return validation.isValid;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      if (currentStep < 2) {
        currentStep++;
      }
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      currentStep--;
    }
  };

  const canProceed = $derived(() => {
    if (currentStep === 0) return !!formData.role;
    if (currentStep === 1) return formData.first_name && formData.last_name && formData.email;
    if (currentStep === 2) return formData.password && formData.confirm_password && formData.password === formData.confirm_password;
    return false;
  });

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!validateStep(2)) return;

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
</script>

<svelte:head>
<title>Register - {$t('common.appName')}</title>
</svelte:head>

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
    <!-- Custom Steps Component -->
    <div class="mb-8">
      <nav aria-label="Progress">
        <ol class="flex items-center">
          {#each steps as step, index}
            <li class="relative {index !== steps.length - 1 ? 'flex-1 pr-8 sm:pr-20' : ''}">
              <!-- Step indicator -->
              <div class="flex items-center">
                <div class="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 {
                  index < currentStep || step.completed
                    ? 'bg-primary-600 text-white'
                    : index === currentStep
                    ? 'border-2 border-primary-600 bg-white text-primary-600 dark:bg-gray-800'
                    : 'border-2 border-gray-300 bg-white text-gray-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400'
                }">
                  {#if index < currentStep || step.completed}
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
                oninput={() => handleFieldInput('first_name')}
                required
                icon='<path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />'
              />
              
              <FormField
                name="last_name"
                label={$t('auth.lastName')}
                bind:value={formData.last_name}
                error={getFieldError('last_name')}
                onblur={() => handleFieldBlur('last_name')}
                oninput={() => handleFieldInput('last_name')}
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
              oninput={() => handleFieldInput('email')}
              required
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
            />

            <FormField
              type="tel"
              name="phone_number"
              label={$t('auth.phoneNumber')}
              bind:value={formData.phone_number}
              error={getFieldError('phone_number')}
              onblur={() => handleFieldBlur('phone_number')}
              oninput={() => handleFieldInput('phone_number')}
              placeholder="+1234567890"
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />'
            />

            <FormField
              type="date"
              name="date_of_birth"
              label={$t('auth.dateOfBirth')}
              bind:value={formData.date_of_birth}
              error={getFieldError('date_of_birth')}
              onblur={() => handleFieldBlur('date_of_birth')}
              oninput={() => handleFieldInput('date_of_birth')}
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
              oninput={() => handleFieldInput('password')}
              required
              icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
            />

            {#if formData.password}
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Password strength:</span>
                  <span class="text-sm font-medium" class:text-red-600={passwordStrength.color === 'red'} class:text-orange-600={passwordStrength.color === 'orange'} class:text-yellow-600={passwordStrength.color === 'yellow'} class:text-blue-600={passwordStrength.color === 'blue'} class:text-green-600={passwordStrength.color === 'green'}>
                    {passwordStrength.text}
                  </span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full transition-all duration-300"
                    class:bg-red-500={passwordStrength.color === 'red'}
                    class:bg-orange-500={passwordStrength.color === 'orange'}
                    class:bg-yellow-500={passwordStrength.color === 'yellow'}
                    class:bg-blue-500={passwordStrength.color === 'blue'}
                    class:bg-green-500={passwordStrength.color === 'green'}
                    style="width: {(passwordStrength.score / 5) * 100}%"
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
              oninput={() => handleFieldInput('confirm_password')}
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
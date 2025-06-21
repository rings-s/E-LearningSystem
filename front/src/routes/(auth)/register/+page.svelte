<!-- front/src/routes/(auth)/register/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.store.js';
  import { uiStore } from '$lib/stores/ui.store.js';
  import { t } from '$lib/i18n/index.js';
  import { validators } from '$lib/utils/validators.js';
  import { ROLES } from '$lib/utils/constants.js';
  import { classNames } from '$lib/utils/helpers.js';
  import FormField from '$lib/components/auth/FormField.svelte';
  import Button from '$lib/components/common/Button.svelte';
  import Card from '$lib/components/common/Card.svelte';
  import Logo from '$lib/components/common/Logo.svelte';

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

  let errors = $state({});
  let touched = $state({});

  // --- Validation Logic ---
  const validationRules = {
    role: [{ validator: validators.required, message: $t('auth.selectAccountType') }],
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
    phone_number: [{ validator: validators.phoneNumber, message: $t('errors.invalidPhone') }],
    password: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.minLength(8), message: $t('errors.passwordTooShort') }
    ],
    confirm_password: [
      { validator: validators.required, message: $t('errors.requiredField') },
      { validator: validators.matchField('password'), message: $t('errors.passwordsDoNotMatch') }
    ]
  };

  const validateField = (fieldName) => {
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
  };

  const handleFieldBlur = (fieldName) => {
    touched[fieldName] = true;
    validateField(fieldName);
  };

  const getFieldError = (fieldName) => {
    return touched[fieldName] ? errors[fieldName] : '';
  };

  // --- Step Management ---
  const stepFields = [
    ['role'],
    ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth'],
    ['password', 'confirm_password']
  ];

  const isStepValid = (stepIndex) => {
    const fields = stepFields[stepIndex];
    if (!fields) return false;
    
    const requiredFields = fields.filter(field => 
      field !== 'phone_number' && field !== 'date_of_birth'
    );
    
    const allRequiredFieldsHaveValues = requiredFields.every(field => !!formData[field]);
    if (!allRequiredFieldsHaveValues) return false;

    const noErrorsForStep = fields.every(field => !errors[field]);
    return noErrorsForStep;
  };

  const nextStep = () => {
    const fieldsToValidate = stepFields[currentStep];
    fieldsToValidate.forEach(field => {
      touched[field] = true;
      validateField(field);
    });

    if (isStepValid(currentStep)) {
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
      { score: 0, text: '', color: '#6b7280' },
      { score: 1, text: $t('auth.veryWeak'), color: '#ef4444' },
      { score: 2, text: $t('auth.weak'), color: '#f97316' },
      { score: 3, text: $t('auth.fair'), color: '#eab308' },
      { score: 4, text: $t('auth.good'), color: '#3b82f6' },
      { score: 5, text: $t('auth.strong'), color: '#22c55e' }
    ];
    return levels[score];
  });

  const steps = $derived([
    {
      title: $t('auth.accountType'),
      description: $t('auth.chooseRole'),
      completed: isStepValid(0) && currentStep > 0
    },
    {
      title: $t('auth.personalInfo'),
      description: $t('auth.tellUsAboutYou'),
      completed: isStepValid(1) && currentStep > 1
    },
    {
      title: $t('auth.security'),
      description: $t('auth.secureAccount'),
      completed: false
    }
  ]);
  
  const canProceed = $derived(isStepValid(currentStep));

  // --- Form Submission ---
  const handleSubmit = async () => {
    stepFields.flat().forEach(field => {
      touched[field] = true;
      validateField(field);
    });

    const isFormValid = stepFields.every((_, index) => isStepValid(index));

    if (!isFormValid) {
      uiStore.showNotification({
        type: 'error',
        title: $t('errors.validationError'),
        message: $t('errors.fixErrors')
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
        message: $t('auth.checkEmailForCode')
      });
      goto(`/verify-email?email=${encodeURIComponent(formData.email)}`);
    } else {
      uiStore.showNotification({
        type: 'error',
        title: $t('common.error'),
        message: result.error || $t('auth.registrationFailed')
      });
    }
  };
  
  // --- UI Data ---
  const roleOptions = [
    { 
      value: ROLES.STUDENT, 
      label: $t('auth.student'), 
      description: $t('auth.studentDescription'), 
      icon: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5z" />
             <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
             <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />`,
      gradient: 'from-blue-500 to-indigo-600'
    },
    { 
      value: ROLES.TEACHER, 
      label: $t('auth.teacher'), 
      description: $t('auth.teacherDescription'), 
      icon: `<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />`,
      gradient: 'from-emerald-500 to-teal-600'
    }
  ];
</script>

<svelte:head>
  <title>{$t('auth.register')} - EduVerse</title>
</svelte:head>

<div class="min-h-screen  py-12 sm:py-16">
  <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="text-center mb-8">
      <Logo size="large" showText={false} class="mx-auto mb-6" />
      <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
        {$t('auth.createAccount')}
      </h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {$t('auth.alreadyHaveAccount')}
        <a href="/login" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 transition-colors">
          {$t('auth.login')}
        </a>
      </p>
    </div>

    <Card variant="bordered" padding="large" class="backdrop-blur-sm bg-white/90 dark:bg-gray-800/90">
      <!-- Progress Steps -->
      <div class="mb-8">
        <nav aria-label="Progress">
          <ol class="flex items-center">
            {#each steps as step, index}
              <li class="relative {index !== steps.length - 1 ? 'flex-1 pr-8 sm:pr-20' : ''}">
                <!-- Step indicator -->
                <div class="flex items-center">
                  <div class="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 transform {
                    index < currentStep
                      ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white scale-90'
                      : index === currentStep
                      ? 'border-2 border-primary-600 bg-white text-primary-600 dark:bg-gray-800 scale-110 ring-4 ring-primary-100 dark:ring-primary-900/30'
                      : 'border-2 border-gray-300 bg-white text-gray-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400'
                  }">
                    {#if index < currentStep}
                      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                    {:else}
                      <span class="text-sm font-bold">{index + 1}</span>
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
                  <div class="absolute top-5 left-10 w-full h-0.5 transition-all duration-500 {
                    index < currentStep 
                      ? 'bg-gradient-to-r from-primary-600 to-primary-500' 
                      : 'bg-gray-300 dark:bg-gray-600'
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
              {$t('auth.chooseAccountType')}
            </h3>
            
            <div class="grid gap-4">
              {#each roleOptions as option}
                <button
                  type="button"
                  onclick={() => formData.role = option.value}
                  class={classNames(
                    'relative p-6 border-2 rounded-2xl text-left transition-all duration-300 group transform',
                    formData.role === option.value 
                      ? 'border-primary-500 bg-gradient-to-br from-primary-50 to-primary-100/50 dark:from-primary-900/20 dark:to-primary-800/10 ring-4 ring-primary-500/20 scale-[1.02] shadow-xl' 
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-lg hover:scale-[1.01] hover:ring-2 hover:ring-gray-200 dark:hover:ring-gray-700'
                  )}
                >
                  <div class="flex items-start gap-4">
                    <div class={classNames(
                      'w-14 h-14 rounded-xl bg-gradient-to-br flex items-center justify-center transition-all duration-300 shadow-lg',
                      option.gradient,
                      formData.role === option.value ? 'shadow-xl scale-110 rotate-3' : 'group-hover:scale-105 group-hover:shadow-xl'
                    )}>
                      <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                        {@html option.icon}
                      </svg>
                    </div>
                    <div class="flex-1">
                      <h4 class="font-semibold text-gray-900 dark:text-white text-lg">
                        {option.label}
                      </h4>
                      <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {option.description}
                      </p>
                    </div>
                    {#if formData.role === option.value}
                      <div class="flex-shrink-0 animate-bounce">
                        <div class="w-6 h-6 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center shadow-lg ring-4 ring-primary-500/20">
                          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      </div>
                    {/if}
                  </div>
                </button>
              {/each}
            </div>
            
            {#if getFieldError('role')}
              <p class="text-sm text-red-600 dark:text-red-400 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {getFieldError('role')}
              </p>
            {/if}
          </div>
        {:else if currentStep === 1}
          <!-- Step 2: Personal Information -->
          <div class="space-y-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              {$t('auth.tellUsAboutYou')}
            </h3>
            
            <div class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FormField
                  name="first_name"
                  label={$t('auth.firstName')}
                  bind:value={formData.first_name}
                  error={getFieldError('first_name')}
                  onblur={() => handleFieldBlur('first_name')}
                  required
                  placeholder={$t('auth.enterFirstName')}
                  icon='<path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />'
                />
                
                <FormField
                  name="last_name"
                  label={$t('auth.lastName')}
                  bind:value={formData.last_name}
                  error={getFieldError('last_name')}
                  onblur={() => handleFieldBlur('last_name')}
                  required
                  placeholder={$t('auth.enterLastName')}
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
                placeholder={$t('auth.enterEmail')}
                icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
              />

              <FormField
                type="tel"
                name="phone_number"
                label="{$t('auth.phoneNumber')} ({$t('common.optional')})"
                bind:value={formData.phone_number}
                error={getFieldError('phone_number')}
                onblur={() => handleFieldBlur('phone_number')}
                placeholder="+1234567890"
                icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />'
              />

              <FormField
                type="date"
                name="date_of_birth"
                label="{$t('auth.dateOfBirth')} ({$t('common.optional')})"
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
              {$t('auth.secureAccount')}
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
                placeholder={$t('auth.enterPassword')}
                icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
              />

              {#if formData.password}
                <div class="space-y-2">
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600 dark:text-gray-400">{$t('auth.passwordStrength')}:</span>
                    <span class="text-sm font-medium" style="color: {passwordStrength.color}">
                      {passwordStrength.text}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div 
                      class="h-2 rounded-full transition-all duration-500 ease-out"
                      style="width: {(passwordStrength.score / 5) * 100}%; background-color: {passwordStrength.color}"
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
                placeholder={$t('auth.reenterPassword')}
                icon='<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />'
              />

              <div class="pt-4">
                <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    {$t('auth.termsAgreement')} 
                    <a href="/terms" class="text-primary-600 hover:text-primary-500 dark:text-primary-400 underline">{$t('auth.termsOfService')}</a> 
                    {$t('common.and')} 
                    <a href="/privacy" class="text-primary-600 hover:text-primary-500 dark:text-primary-400 underline">{$t('auth.privacyPolicy')}</a>
                  </p>
                </div>
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
            class="min-w-[100px]"
          >
            {$t('common.previous')}
          </Button>
          
          <div class="flex gap-2">
            {#if currentStep < 2}
              <Button
                variant="primary"
                onclick={nextStep}
                disabled={!canProceed}
                class="min-w-[100px]"
              >
                {$t('common.next')}
              </Button>
            {:else}
              <Button
                variant="primary"
                loading={loading}
                disabled={!canProceed || loading}
                onclick={handleSubmit}
                class="min-w-[150px]"
              >
                {loading ? $t('common.creating') : $t('auth.createAccount')}
              </Button>
            {/if}
          </div>
        </div>
      </div>
    </Card>

    <!-- Footer -->
    <div class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
      <p>
        {$t('auth.needHelp')} 
        <a href="/help" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 transition-colors">
          {$t('auth.contactSupport')}
        </a>
      </p>
    </div>
  </div>
</div>
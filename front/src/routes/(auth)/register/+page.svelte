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

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
  <!-- Background Elements -->
  <div class="absolute inset-0 overflow-hidden">
    <div class="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
    <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
    <div class="absolute top-40 left-40 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
  </div>

  <div class="relative w-full max-w-4xl mx-auto">
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4">
        <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
        </svg>
      </div>
      <h1 class="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-2">
        {$t('auth.createAccount')}
      </h1>
      <p class="text-gray-600">
        {$t('auth.alreadyHaveAccount')}
        <a href="/login" class="text-blue-600 hover:text-blue-800 font-semibold hover:underline transition-colors">
          {$t('auth.login')}
        </a>
      </p>
    </div>

    <!-- Main Card -->
    <div class="bg-white/80 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 p-8 relative overflow-hidden">
      <!-- Progress Steps -->
      <div class="mb-8">
        <nav aria-label="Progress" class="rtl:space-x-reverse">
          <ol class="flex items-center justify-between">
            {#each steps as step, index}
              <li class="relative flex-1 group">
                <!-- Step Content -->
                <div class="flex flex-col items-center text-center">
                  <!-- Step Circle -->
                  <div class="relative z-10 flex items-center justify-center w-12 h-12 rounded-full transition-all duration-300 transform mb-2 {
                    index < currentStep
                      ? 'bg-gradient-to-br from-blue-600 to-purple-700 text-white scale-100 shadow-xl'
                      : index === currentStep
                      ? 'border-2 border-blue-600 bg-white text-blue-600 scale-110 ring-4 ring-blue-500/20 shadow-lg'
                      : 'border-2 border-gray-300 bg-white text-gray-500 hover:border-gray-400 transition-colors'
                  }">
                    {#if index < currentStep}
                      <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                    {:else}
                      <span class="text-sm font-bold">{index + 1}</span>
                    {/if}
                  </div>
                  
                  <!-- Step Info -->
                  <div class="min-w-0">
                    <span class="text-sm font-semibold {
                      index === currentStep
                        ? 'text-blue-600'
                        : index < currentStep
                        ? 'text-gray-900'
                        : 'text-gray-500'
                    }">{step.title}</span>
                    <p class="text-xs text-gray-500 mt-1 hidden sm:block">{step.description}</p>
                  </div>
                </div>

                <!-- Connector Line -->
                {#if index !== steps.length - 1}
                  <div class="absolute top-6 left-1/2 w-full h-0.5 -translate-y-1/2 transition-all duration-500 rtl:right-1/2 rtl:left-auto {
                    index < currentStep 
                      ? 'bg-gradient-to-r from-blue-600 to-purple-500' 
                      : 'bg-gray-300'
                  } hidden sm:block"></div>
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
            <div class="text-center">
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                {$t('auth.chooseAccountType')}
              </h3>
              <p class="text-gray-600">{$t('auth.chooseRole')}</p>
            </div>
            
            <div class="grid gap-4 max-w-2xl mx-auto">
              {#each roleOptions as option}
                <button
                  type="button"
                  onclick={() => formData.role = option.value}
                  class={classNames(
                    'relative p-6 border-2 rounded-2xl text-left transition-all duration-300 group transform',
                    formData.role === option.value 
                      ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-purple-50 ring-4 ring-blue-500/20 scale-[1.02] shadow-xl' 
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-lg hover:scale-[1.01] hover:ring-2 hover:ring-gray-200'
                  )}
                >
                  <div class="flex items-start gap-4 rtl:flex-row-reverse">
                    <div class={classNames(
                      'w-14 h-14 rounded-xl bg-gradient-to-br flex items-center justify-center transition-all duration-300 shadow-lg',
                      option.gradient,
                      formData.role === option.value ? 'shadow-xl scale-110 rotate-3' : 'group-hover:scale-105 group-hover:shadow-xl'
                    )}>
                      <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                        {@html option.icon}
                      </svg>
                    </div>
                    <div class="flex-1 rtl:text-right">
                      <h4 class="font-semibold text-gray-900 text-lg">
                        {option.label}
                      </h4>
                      <p class="text-sm text-gray-600 mt-1">
                        {option.description}
                      </p>
                    </div>
                    {#if formData.role === option.value}
                      <div class="flex-shrink-0 animate-bounce">
                        <div class="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg ring-4 ring-blue-500/20">
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
              <div class="bg-red-50 border border-red-200 rounded-xl p-3 flex items-center space-x-2 rtl:space-x-reverse">
                <svg class="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-red-700 text-sm font-medium">{getFieldError('role')}</p>
              </div>
            {/if}
          </div>
        {:else if currentStep === 1}
          <!-- Step 2: Personal Information -->
          <div class="space-y-6">
            <div class="text-center">
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                {$t('auth.tellUsAboutYou')}
              </h3>
              <p class="text-gray-600">{$t('auth.personalInfo')}</p>
            </div>
            
            <div class="space-y-4 max-w-2xl mx-auto">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="relative">
                  <label class="block text-sm font-semibold text-gray-700 mb-2 rtl:text-right">{$t('auth.firstName')}</label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none rtl:right-0 rtl:left-auto rtl:pr-3 rtl:pl-0">
                      <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <input 
                      type="text"
                      bind:value={formData.first_name}
                      onblur={() => handleFieldBlur('first_name')}
                      required
                      class="w-full pl-10 pr-4 py-3 border-2 rounded-xl transition-all duration-200 border-gray-200 hover:border-gray-300
                             focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
                             bg-white/50 backdrop-blur-sm rtl:pr-10 rtl:pl-4"
                      placeholder={$t('auth.enterFirstName')}
                    />
                  </div>
                  {#if getFieldError('first_name')}
                    <p class="text-red-600 text-sm mt-1 flex items-center gap-1 rtl:flex-row-reverse">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {getFieldError('first_name')}
                    </p>
                  {/if}
                </div>
                
                <div class="relative">
                  <label class="block text-sm font-semibold text-gray-700 mb-2 rtl:text-right">{$t('auth.lastName')}</label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none rtl:right-0 rtl:left-auto rtl:pr-3 rtl:pl-0">
                      <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <input 
                      type="text"
                      bind:value={formData.last_name}
                      onblur={() => handleFieldBlur('last_name')}
                      required
                      class="w-full pl-10 pr-4 py-3 border-2 rounded-xl transition-all duration-200 border-gray-200 hover:border-gray-300
                             focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
                             bg-white/50 backdrop-blur-sm rtl:pr-10 rtl:pl-4"
                      placeholder={$t('auth.enterLastName')}
                    />
                  </div>
                  {#if getFieldError('last_name')}
                    <p class="text-red-600 text-sm mt-1 flex items-center gap-1 rtl:flex-row-reverse">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {getFieldError('last_name')}
                    </p>
                  {/if}
                </div>
              </div>

              <div class="relative">
                <label class="block text-sm font-semibold text-gray-700 mb-2 rtl:text-right">{$t('auth.email')}</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none rtl:right-0 rtl:left-auto rtl:pr-3 rtl:pl-0">
                    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <input 
                    type="email"
                    bind:value={formData.email}
                    onblur={() => handleFieldBlur('email')}
                    required
                    class="w-full pl-10 pr-4 py-3 border-2 rounded-xl transition-all duration-200 border-gray-200 hover:border-gray-300
                           focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
                           bg-white/50 backdrop-blur-sm rtl:pr-10 rtl:pl-4"
                    placeholder={$t('auth.enterEmail')}
                  />
                </div>
                {#if getFieldError('email')}
                  <p class="text-red-600 text-sm mt-1 flex items-center gap-1 rtl:flex-row-reverse">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {getFieldError('email')}
                  </p>
                {/if}
              </div>

              <div class="relative">
                <label class="block text-sm font-semibold text-gray-700 mb-2 rtl:text-right">{$t('auth.phoneNumber')} ({$t('common.optional')})</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none rtl:right-0 rtl:left-auto rtl:pr-3 rtl:pl-0">
                    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                  </div>
                  <input 
                    type="tel"
                    bind:value={formData.phone_number}
                    onblur={() => handleFieldBlur('phone_number')}
                    class="w-full pl-10 pr-4 py-3 border-2 rounded-xl transition-all duration-200 border-gray-200 hover:border-gray-300
                           focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
                           bg-white/50 backdrop-blur-sm rtl:pr-10 rtl:pl-4"
                    placeholder="+1234567890"
                  />
                </div>
                {#if getFieldError('phone_number')}
                  <p class="text-red-600 text-sm mt-1 flex items-center gap-1 rtl:flex-row-reverse">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {getFieldError('phone_number')}
                  </p>
                {/if}
              </div>

              <div class="relative">
                <label class="block text-sm font-semibold text-gray-700 mb-2 rtl:text-right">{$t('auth.dateOfBirth')} ({$t('common.optional')})</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none rtl:right-0 rtl:left-auto rtl:pr-3 rtl:pl-0">
                    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <input 
                    type="date"
                    bind:value={formData.date_of_birth}
                    onblur={() => handleFieldBlur('date_of_birth')}
                    class="w-full pl-10 pr-4 py-3 border-2 rounded-xl transition-all duration-200 border-gray-200 hover:border-gray-300
                           focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
                           bg-white/50 backdrop-blur-sm rtl:pr-10 rtl:pl-4"
                  />
                </div>
                {#if getFieldError('date_of_birth')}
                  <p class="text-red-600 text-sm mt-1 flex items-center gap-1 rtl:flex-row-reverse">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {getFieldError('date_of_birth')}
                  </p>
                {/if}
              </div>
            </div>
          </div>
        {:else if currentStep === 2}
          <!-- Step 3: Security -->
          <div class="space-y-6">
            <div class="text-center">
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                {$t('auth.secureAccount')}
              </h3>
              <p class="text-gray-600">{$t('auth.security')}</p>
            </div>
            
            <div class="space-y-4 max-w-2xl mx-auto">
              <div class="relative">
                <label class="block text-sm font-semibold text-gray-700 mb-2 rtl:text-right">{$t('auth.password')}</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none rtl:right-0 rtl:left-auto rtl:pr-3 rtl:pl-0">
                    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <input 
                    type="password"
                    bind:value={formData.password}
                    onblur={() => handleFieldBlur('password')}
                    required
                    class="w-full pl-10 pr-4 py-3 border-2 rounded-xl transition-all duration-200 border-gray-200 hover:border-gray-300
                           focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
                           bg-white/50 backdrop-blur-sm rtl:pr-10 rtl:pl-4"
                    placeholder={$t('auth.enterPassword')}
                  />
                </div>
                {#if getFieldError('password')}
                  <p class="text-red-600 text-sm mt-1 flex items-center gap-1 rtl:flex-row-reverse">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {getFieldError('password')}
                  </p>
                {/if}
              </div>

              {#if formData.password}
                <div class="space-y-2">
                  <div class="flex justify-between items-center rtl:flex-row-reverse">
                    <span class="text-sm text-gray-600">{$t('auth.passwordStrength')}:</span>
                    <span class="text-sm font-medium" style="color: {passwordStrength.color}">
                      {passwordStrength.text}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div 
                      class="h-2 rounded-full transition-all duration-500 ease-out"
                      style="width: {(passwordStrength.score / 5) * 100}%; background-color: {passwordStrength.color}"
                    ></div>
                  </div>
                </div>
              {/if}

              <div class="relative">
                <label class="block text-sm font-semibold text-gray-700 mb-2 rtl:text-right">{$t('auth.confirmPassword')}</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none rtl:right-0 rtl:left-auto rtl:pr-3 rtl:pl-0">
                    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <input 
                    type="password"
                    bind:value={formData.confirm_password}
                    onblur={() => handleFieldBlur('confirm_password')}
                    required
                    class="w-full pl-10 pr-4 py-3 border-2 rounded-xl transition-all duration-200 border-gray-200 hover:border-gray-300
                           focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
                           bg-white/50 backdrop-blur-sm rtl:pr-10 rtl:pl-4"
                    placeholder={$t('auth.reenterPassword')}
                  />
                </div>
                {#if getFieldError('confirm_password')}
                  <p class="text-red-600 text-sm mt-1 flex items-center gap-1 rtl:flex-row-reverse">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {getFieldError('confirm_password')}
                  </p>
                {/if}
              </div>

              <div class="pt-4">
                <div class="bg-gray-50 rounded-lg p-4">
                  <p class="text-xs text-gray-600 rtl:text-right">
                    {$t('auth.termsAgreement')} 
                    <a href="/terms" class="text-blue-600 hover:text-blue-800 underline">{$t('auth.termsOfService')}</a> 
                    {$t('common.and')} 
                    <a href="/privacy" class="text-blue-600 hover:text-blue-800 underline">{$t('auth.privacyPolicy')}</a>
                  </p>
                </div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Navigation Buttons -->
        <div class="flex justify-between pt-8 border-t border-gray-200 rtl:flex-row-reverse">
          <button
            onclick={prevStep}
            disabled={currentStep === 0}
            class="min-w-[100px] px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-xl
                   hover:bg-gray-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                   focus:outline-none focus:ring-4 focus:ring-gray-500/20"
          >
            {$t('common.previous')}
          </button>
          
          <div class="flex gap-2">
            {#if currentStep < 2}
              <button
                onclick={nextStep}
                disabled={!canProceed}
                class="min-w-[100px] bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-xl
                       hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02]
                       focus:outline-none focus:ring-4 focus:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed
                       disabled:hover:scale-100 shadow-lg hover:shadow-xl"
              >
                {$t('common.next')}
              </button>
            {:else}
              <button
                onclick={handleSubmit}
                disabled={!canProceed || loading}
                class="min-w-[150px] bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-xl
                       hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02]
                       focus:outline-none focus:ring-4 focus:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed
                       disabled:hover:scale-100 shadow-lg hover:shadow-xl"
              >
                {#if loading}
                  <div class="flex items-center justify-center rtl:flex-row-reverse">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white rtl:ml-3 rtl:mr-1" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {$t('common.creating')}
                  </div>
                {:else}
                  {$t('auth.createAccount')}
                {/if}
              </button>
            {/if}
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="mt-6 text-center text-sm text-gray-600">
      <p>
        {$t('auth.needHelp')} 
        <a href="/help" class="font-medium text-blue-600 hover:text-blue-800 transition-colors">
          {$t('auth.contactSupport')}
        </a>
      </p>
    </div>
  </div>
</div>

<style>
  @keyframes blob {
    0% {
      transform: translate(0px, 0px) scale(1);
    }
    33% {
      transform: translate(30px, -50px) scale(1.1);
    }
    66% {
      transform: translate(-20px, 20px) scale(0.9);
    }
    100% {
      transform: translate(0px, 0px) scale(1);
    }
  }
  
  .animate-blob {
    animation: blob 7s infinite;
  }
  
  .animation-delay-2000 {
    animation-delay: 2s;
  }
  
  .animation-delay-4000 {
    animation-delay: 4s;
  }
</style>
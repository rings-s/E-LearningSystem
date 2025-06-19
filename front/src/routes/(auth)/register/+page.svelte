<!-- front/src/routes/(auth)/register/+page.svelte -->
<script>
    import { goto } from '$app/navigation';
    import { authStore } from '$lib/stores/auth.store.js';
    import { uiStore } from '$lib/stores/ui.store.js';
    import { t } from '$lib/i18n/index.js';
    import { validators, validateForm } from '$lib/utils/validators.js';
    import { ROLES } from '$lib/utils/constants.js';
    import AuthLayout from '$lib/components/auth/AuthLayout.svelte';
    import FormField from '$lib/components/auth/FormField.svelte';
    import Button from '$lib/components/common/Button.svelte';
    import Steps from '$lib/components/common/Steps.svelte';
  
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
        content: () => StepAccountType
      },
      {
        title: 'Personal Information',
        description: 'Tell us about yourself',
        content: () => StepPersonalInfo
      },
      {
        title: 'Security',
        description: 'Secure your account',
        content: () => StepSecurity
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
  
    const validateStep = (step) => {
      const fieldsToValidate = step === 0 ? ['role'] 
        : step === 1 ? ['first_name', 'last_name', 'email', 'phone_number']
        : ['password', 'confirm_password'];
      
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
  
    const handleStepChange = (newStep) => {
      if (newStep > currentStep && !validateStep(currentStep)) {
        return;
      }
      currentStep = newStep;
    };
  
    const handleSubmit = async () => {
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
  
  <AuthLayout 
    title={$t('auth.register')}
    subtitle="{$t('auth.alreadyHaveAccount')} <a href='/login' class='font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400'>{$t('auth.login')}</a>"
  >
    <div class="space-y-6">
      <Steps 
        {steps} 
        {currentStep}
        onStepChange={handleStepChange}
        allowStepClick={false}
      />
    </div>
  
    {#snippet StepAccountType()}
      <div class="space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
          How do you want to use {$t('common.appName')}?
        </p>
        
        <div class="grid gap-4">
          {#each roleOptions as option}
            <button
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
                  <h3 class="font-semibold text-gray-900 dark:text-white">
                    {option.label}
                  </h3>
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
        
        {#if errors.role}
          <p class="text-sm text-red-600 dark:text-red-400">{errors.role}</p>
        {/if}
      </div>
    {/snippet}
  
    {#snippet StepPersonalInfo()}
      <form class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <FormField
            name="first_name"
            label={$t('auth.firstName')}
            bind:value={formData.first_name}
            error={errors.first_name}
            required
            icon='<path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />'
          />
          
          <FormField
            name="last_name"
            label={$t('auth.lastName')}
            bind:value={formData.last_name}
            error={errors.last_name}
            required
          />
        </div>
  
        <FormField
          type="email"
          name="email"
          label={$t('auth.email')}
          bind:value={formData.email}
          error={errors.email}
          required
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
        />
  
        <FormField
          type="tel"
          name="phone_number"
          label={$t('auth.phoneNumber')}
          bind:value={formData.phone_number}
          error={errors.phone_number}
          placeholder="+1234567890"
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />'
        />
  
        <FormField
          type="date"
          name="date_of_birth"
          label={$t('auth.dateOfBirth')}
          bind:value={formData.date_of_birth}
          error={errors.date_of_birth}
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />'
        />
      </form>
    {/snippet}
  
    {#snippet StepSecurity()}
      <form class="space-y-4" onsubmit|preventDefault={handleSubmit}>
        <FormField
          type="password"
          name="password"
          label={$t('auth.password')}
          bind:value={formData.password}
          error={errors.password}
          required
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
        />
  
        <FormField
          type="password"
          name="confirm_password"
          label={$t('auth.confirmPassword')}
          bind:value={formData.confirm_password}
          error={errors.confirm_password}
          required
          icon='<path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />'
        />
  
        <div class="pt-4">
          <p class="text-xs text-gray-600 dark:text-gray-400 mb-4">
            By creating an account, you agree to our 
            <a href="/terms" class="text-primary-600 hover:text-primary-500 dark:text-primary-400">Terms of Service</a> 
            and 
            <a href="/privacy" class="text-primary-600 hover:text-primary-500 dark:text-primary-400">Privacy Policy</a>
          </p>
  
          <Button
            type="submit"
            variant="primary"
            size="large"
            fullWidth
            loading={loading}
          >
            Create Account
          </Button>
        </div>
      </form>
    {/snippet}
  
    {@snippet footer()}
      <p>
        Need help? <a href="/help" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">Contact Support</a>
      </p>
    {/snippet}
  </AuthLayout>
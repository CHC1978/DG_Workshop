<template>
  <AuthLayout>
    <!-- Step 1: Username and Password -->
    <div v-if="step === 1">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Login</h2>

      <form @submit.prevent="handleStep1">
        <div class="space-y-4">
          <AppInput
            id="username"
            v-model="credentials.username"
            label="Username"
            placeholder="Enter your username"
            required
            autocomplete="username"
            :error="errors.username"
          />

          <AppInput
            id="password"
            v-model="credentials.password"
            type="password"
            label="Password"
            placeholder="Enter your password"
            required
            autocomplete="current-password"
            :error="errors.password"
          />
        </div>

        <div v-if="errorMessage" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ errorMessage }}</p>
        </div>

        <AppButton
          type="submit"
          variant="primary"
          size="lg"
          full-width
          :loading="loading"
          class="mt-6"
        >
          Continue
        </AppButton>
      </form>
    </div>

    <!-- Step 2: TOTP Code -->
    <div v-else-if="step === 2">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Two-Factor Authentication</h2>
      <p class="text-sm text-gray-600 mb-6">
        Enter the 6-digit code from your authenticator app
      </p>

      <form @submit.prevent="handleStep2">
        <div class="space-y-4">
          <AppInput
            id="totp-code"
            v-model="totpCode"
            label="TOTP Code"
            placeholder="000000"
            required
            maxlength="6"
            pattern="[0-9]{6}"
            autocomplete="one-time-code"
            :error="errors.totp"
          />
        </div>

        <div v-if="errorMessage" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ errorMessage }}</p>
        </div>

        <div class="mt-6 space-y-3">
          <AppButton
            type="submit"
            variant="primary"
            size="lg"
            full-width
            :loading="loading"
          >
            Login
          </AppButton>

          <AppButton
            type="button"
            variant="ghost"
            size="md"
            full-width
            @click="backToStep1"
          >
            Back
          </AppButton>
        </div>
      </form>
    </div>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import AuthLayout from '@/layouts/AuthLayout.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()

const step = ref(1)
const loading = ref(false)
const errorMessage = ref('')

const credentials = reactive({
  username: '',
  password: '',
})

const totpCode = ref('')

const errors = reactive({
  username: '',
  password: '',
  totp: '',
})

function clearErrors() {
  errors.username = ''
  errors.password = ''
  errors.totp = ''
  errorMessage.value = ''
}

async function handleStep1() {
  clearErrors()

  // Validate
  if (!credentials.username) {
    errors.username = 'Username is required'
    return
  }
  if (!credentials.password) {
    errors.password = 'Password is required'
    return
  }

  loading.value = true

  try {
    console.log('Attempting login step 1...')
    const response = await authStore.loginStep1(credentials)
    console.log('Login step 1 response:', response)

    if (response.totp_required) {
      console.log('2FA required, moving to step 2')
      step.value = 2
    } else {
      console.log('2FA not set up, redirecting to setup')
      // 2FA not set up, redirect to 2FA setup
      await router.push('/setup-2fa')
    }
  } catch (error: any) {
    console.error('Login step 1 failed:', error)
    console.error('Error details:', error.response)
    errorMessage.value = error.response?.data?.detail || error.message || 'Login failed'
  } finally {
    loading.value = false
  }
}

async function handleStep2() {
  clearErrors()

  // Validate
  if (!totpCode.value || totpCode.value.length !== 6) {
    errors.totp = 'Please enter 6-digit code'
    return
  }

  if (!authStore.tempToken) {
    errorMessage.value = 'Session expired, please login again'
    backToStep1()
    return
  }

  loading.value = true

  try {
    console.log('Attempting login step 2...')
    await authStore.loginStep2({
      temp_token: authStore.tempToken,
      totp_code: totpCode.value,
    })

    console.log('Login successful, redirecting to dashboard')
    uiStore.showNotification('success', 'Login successful')
    await router.push('/dashboard')
  } catch (error: any) {
    console.error('Login step 2 failed:', error)
    console.error('Error details:', error.response)
    errorMessage.value = error.response?.data?.detail || error.message || 'Invalid TOTP code'
  } finally {
    loading.value = false
  }
}

function backToStep1() {
  step.value = 1
  totpCode.value = ''
  clearErrors()
}
</script>

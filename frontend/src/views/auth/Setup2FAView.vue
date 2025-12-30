<template>
  <AuthLayout>
    <div v-if="!qrCodeData">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Setup Two-Factor Authentication</h2>

      <p class="text-sm text-gray-600 mb-6">
        Two-factor authentication adds an extra layer of security to your account.
      </p>

      <AppButton
        variant="primary"
        size="lg"
        full-width
        :loading="loading"
        @click="handleSetup"
      >
        Start Setup
      </AppButton>
    </div>

    <div v-else-if="!confirmed">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Scan QR Code</h2>
      <p class="text-sm text-gray-600 mb-6">
        Use Google Authenticator or Microsoft Authenticator to scan the QR code
      </p>

      <!-- QR Code -->
      <div class="flex justify-center mb-6">
        <img :src="qrCodeData.qr_code" alt="QR Code" class="w-64 h-64" />
      </div>

      <!-- Secret (manual entry) -->
      <div class="mb-6 p-4 bg-gray-50 rounded-lg">
        <p class="text-xs text-gray-500 mb-1">Manual Entry Key:</p>
        <p class="text-sm font-mono text-gray-900 break-all">
          {{ qrCodeData.secret }}
        </p>
      </div>

      <!-- Backup Codes -->
      <div class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p class="text-sm font-medium text-yellow-900 mb-2">
          Backup Codes (Save these!)
        </p>
        <div class="grid grid-cols-2 gap-2">
          <p
            v-for="code in qrCodeData.backup_codes"
            :key="code"
            class="text-sm font-mono text-yellow-800"
          >
            {{ code }}
          </p>
        </div>
      </div>

      <!-- Verification -->
      <form @submit.prevent="handleConfirm">
        <AppInput
          id="totp-verify"
          v-model="verifyCode"
          label="Enter code to verify"
          placeholder="000000"
          required
          maxlength="6"
          :error="errors.verify"
        />

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
          Verify and Enable
        </AppButton>
      </form>
    </div>

    <div v-else>
      <div class="text-center">
        <div class="text-6xl mb-4">✅</div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">2FA Enabled!</h2>
        <p class="text-sm text-gray-600 mb-6">
          Your account is now protected with two-factor authentication.
        </p>

        <AppButton
          variant="primary"
          size="lg"
          full-width
          @click="router.push('/login')"
        >
          Go to Login
        </AppButton>
      </div>
    </div>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import AuthLayout from '@/layouts/AuthLayout.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Setup2FAResponse } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()

// Debug: Check tempToken on mount
onMounted(() => {
  console.log('Setup2FAView mounted')
  console.log('tempToken exists:', !!authStore.tempToken)
  console.log('tempToken value:', authStore.tempToken?.substring(0, 50) + '...')
})

const loading = ref(false)
const qrCodeData = ref<Setup2FAResponse | null>(null)
const verifyCode = ref('')
const confirmed = ref(false)
const errorMessage = ref('')

const errors = reactive({
  verify: '',
})

async function handleSetup() {
  loading.value = true
  errorMessage.value = ''

  // Check if we have tempToken
  if (!authStore.tempToken) {
    console.error('No tempToken found, redirecting to login')
    errorMessage.value = 'Session expired. Please login again.'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    loading.value = false
    return
  }

  try {
    console.log('Starting 2FA setup with tempToken...')
    const response = await authStore.setup2FA()
    console.log('2FA setup successful, got QR code')
    qrCodeData.value = response
  } catch (error: any) {
    console.error('2FA setup failed:', error)
    console.error('Error response:', error.response)

    if (error.response?.status === 401) {
      errorMessage.value = 'Session expired. Please login again.'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      errorMessage.value = error.response?.data?.detail || error.message || '2FA setup failed'
    }
  } finally {
    loading.value = false
  }
}

async function handleConfirm() {
  errors.verify = ''
  errorMessage.value = ''

  if (!verifyCode.value || verifyCode.value.length !== 6) {
    errors.verify = 'Please enter 6-digit code'
    return
  }

  loading.value = true

  try {
    await authStore.confirm2FA(verifyCode.value)
    confirmed.value = true
    uiStore.showNotification('success', '2FA enabled successfully')
  } catch (error: any) {
    console.error('2FA confirmation failed:', error)
    errorMessage.value = error.response?.data?.detail || 'Invalid code'
  } finally {
    loading.value = false
  }
}
</script>

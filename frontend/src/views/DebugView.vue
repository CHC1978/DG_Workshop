<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-6">API Debug Tool</h1>

      <!-- Backend Status -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Backend Status</h2>
        <AppButton @click="checkBackend" :loading="checking">
          Check Backend
        </AppButton>
        <div v-if="backendStatus" class="mt-4">
          <pre class="bg-gray-50 p-4 rounded text-sm">{{ JSON.stringify(backendStatus, null, 2) }}</pre>
        </div>
      </div>

      <!-- Test Login Step 1 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Test Login Step 1</h2>
        <div class="space-y-4">
          <AppInput
            v-model="testUsername"
            label="Username"
            placeholder="admin"
          />
          <AppInput
            v-model="testPassword"
            type="password"
            label="Password"
            placeholder="admin123"
          />
          <AppButton @click="testLoginStep1" :loading="testing">
            Test Login
          </AppButton>
        </div>
        <div v-if="loginResult" class="mt-4">
          <p class="font-semibold mb-2">Result:</p>
          <pre class="bg-gray-50 p-4 rounded text-sm overflow-auto">{{ JSON.stringify(loginResult, null, 2) }}</pre>
        </div>
        <div v-if="loginError" class="mt-4 p-4 bg-red-50 border border-red-200 rounded">
          <p class="font-semibold text-red-900 mb-2">Error:</p>
          <pre class="text-sm text-red-800">{{ JSON.stringify(loginError, null, 2) }}</pre>
        </div>
      </div>

      <!-- Network Info -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Network Info</h2>
        <div class="space-y-2 text-sm">
          <p><strong>API Base URL:</strong> /api</p>
          <p><strong>Full URL:</strong> {{ window.location.origin }}/api</p>
          <p><strong>Current Path:</strong> {{ window.location.pathname }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'

const checking = ref(false)
const testing = ref(false)
const backendStatus = ref<any>(null)
const loginResult = ref<any>(null)
const loginError = ref<any>(null)
const testUsername = ref('admin')
const testPassword = ref('admin123')

async function checkBackend() {
  checking.value = true
  backendStatus.value = null

  try {
    const response = await axios.get('/api/', { timeout: 5000 })
    backendStatus.value = {
      status: 'OK',
      data: response.data,
      headers: response.headers,
    }
  } catch (error: any) {
    backendStatus.value = {
      status: 'ERROR',
      message: error.message,
      response: error.response?.data,
    }
  } finally {
    checking.value = false
  }
}

async function testLoginStep1() {
  testing.value = true
  loginResult.value = null
  loginError.value = null

  try {
    console.log('Testing login with:', { username: testUsername.value })

    const response = await axios.post(
      '/api/auth/login/step1',
      {
        username: testUsername.value,
        password: testPassword.value,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      }
    )

    console.log('Login response:', response)
    loginResult.value = {
      status: response.status,
      data: response.data,
      headers: response.headers,
    }
  } catch (error: any) {
    console.error('Login error:', error)
    loginError.value = {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        baseURL: error.config?.baseURL,
      },
    }
  } finally {
    testing.value = false
  }
}
</script>

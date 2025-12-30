<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo & Mobile Menu Button -->
          <div class="flex items-center space-x-4">
            <!-- Mobile Menu Button -->
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100"
            >
              <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              </svg>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>

            <!-- Logo -->
            <h1 class="text-lg sm:text-xl font-bold text-sky-900">
              海洋設備管理系統
            </h1>
          </div>

          <!-- Desktop Navigation -->
          <nav class="hidden md:flex items-center space-x-6">
            <router-link
              to="/dashboard"
              class="text-sm text-gray-700 hover:text-sky-600"
              active-class="text-sky-600 font-semibold"
            >
              Dashboard
            </router-link>
            <router-link
              to="/equipment"
              class="text-sm text-gray-700 hover:text-sky-600"
              active-class="text-sky-600 font-semibold"
            >
              Equipment
            </router-link>
            <router-link
              to="/calibrations"
              class="text-sm text-gray-700 hover:text-sky-600"
              active-class="text-sky-600 font-semibold"
            >
              Calibrations
            </router-link>
            <router-link
              v-if="authStore.isAdmin"
              to="/admin/users"
              class="text-sm text-gray-700 hover:text-sky-600"
              active-class="text-sky-600 font-semibold"
            >
              Users
            </router-link>
          </nav>

          <!-- User Menu -->
          <div class="flex items-center space-x-2 sm:space-x-4">
            <!-- User Info (hidden on small screens) -->
            <div class="hidden sm:block text-right">
              <p class="text-sm text-gray-700">
                {{ authStore.user?.full_name || authStore.user?.username }}
              </p>
              <p class="text-xs text-gray-500">
                {{ roleLabel }}
              </p>
            </div>

            <!-- Logout Button -->
            <button
              @click="handleLogout"
              class="text-sm text-gray-700 hover:text-sky-600 px-3 py-1.5 rounded hover:bg-gray-100"
            >
              Logout
            </button>
          </div>
        </div>

        <!-- Mobile Navigation Menu -->
        <div v-if="mobileMenuOpen" class="md:hidden py-4 border-t border-gray-200">
          <nav class="flex flex-col space-y-2">
            <router-link
              to="/dashboard"
              @click="mobileMenuOpen = false"
              class="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded"
              active-class="bg-sky-50 text-sky-600 font-semibold"
            >
              Dashboard
            </router-link>
            <router-link
              to="/equipment"
              @click="mobileMenuOpen = false"
              class="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded"
              active-class="bg-sky-50 text-sky-600 font-semibold"
            >
              Equipment
            </router-link>
            <router-link
              to="/calibrations"
              @click="mobileMenuOpen = false"
              class="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded"
              active-class="bg-sky-50 text-sky-600 font-semibold"
            >
              Calibrations
            </router-link>
            <router-link
              v-if="authStore.isAdmin"
              to="/admin/users"
              @click="mobileMenuOpen = false"
              class="px-3 py-2 text-gray-700 hover:bg-gray-100 rounded"
              active-class="bg-sky-50 text-sky-600 font-semibold"
            >
              Users
            </router-link>

            <!-- User Info for Mobile -->
            <div class="px-3 py-2 mt-4 border-t border-gray-200">
              <p class="text-sm font-medium text-gray-900">
                {{ authStore.user?.full_name || authStore.user?.username }}
              </p>
              <p class="text-xs text-gray-500">
                {{ roleLabel }}
              </p>
            </div>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const mobileMenuOpen = ref(false)

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    admin: 'Admin',
    manager: 'Manager',
    operator: 'Operator',
    viewer: 'Viewer',
  }
  return labels[authStore.userRole] || authStore.userRole
})

function handleLogout() {
  authStore.logout()
  mobileMenuOpen.value = false
  router.push('/login')
}
</script>

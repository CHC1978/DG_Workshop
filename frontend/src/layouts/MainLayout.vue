<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-sky-900">
              海洋設備管理系統
            </h1>
          </div>

          <!-- Navigation -->
          <nav class="flex items-center space-x-6">
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
              v-if="authStore.isAdmin"
              to="/admin/users"
              class="text-sm text-gray-700 hover:text-sky-600"
              active-class="text-sky-600 font-semibold"
            >
              Users
            </router-link>
          </nav>

          <!-- User menu -->
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-700">
              {{ authStore.user?.full_name || authStore.user?.username }}
            </span>
            <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {{ roleLabel }}
            </span>
            <button
              @click="handleLogout"
              class="text-sm text-gray-700 hover:text-sky-600"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

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
  router.push('/login')
}
</script>

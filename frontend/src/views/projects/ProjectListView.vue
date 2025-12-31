<template>
  <MainLayout>
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Projects</h1>
        <AppButton v-if="authStore.isManager" @click="router.push('/projects/new')">
          New Project
        </AppButton>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by code, name, or client..."
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              @input="debouncedSearch"
            />
          </div>

          <!-- Status Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              v-model="statusFilter"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              @change="handleFilter"
            >
              <option value="">All</option>
              <option value="planning">Planning</option>
              <option value="active">Active</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <!-- Active Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Active Status</label>
            <select
              v-model="activeFilter"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              @change="handleFilter"
            >
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="projectStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading projects...</p>
      </div>

      <!-- Projects List -->
      <div v-else-if="projectStore.projects.length > 0" class="space-y-4">
        <div
          v-for="project in projectStore.projects"
          :key="project.id"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer"
          @click="router.push(`/projects/${project.id}`)"
        >
          <div class="p-6">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-xl font-semibold text-gray-900">{{ project.name }}</h3>
                  <span :class="statusBadgeClass(project.status)" class="px-2 py-1 text-xs font-semibold rounded">
                    {{ statusLabel(project.status) }}
                  </span>
                  <span v-if="!project.is_active" class="px-2 py-1 text-xs font-semibold rounded bg-gray-100 text-gray-800">
                    Inactive
                  </span>
                </div>
                <p class="text-sm text-gray-600 font-mono mb-2">{{ project.code }}</p>
                <p v-if="project.description" class="text-sm text-gray-600 mb-3">
                  {{ project.description }}
                </p>
                <div class="flex flex-wrap gap-4 text-sm text-gray-500">
                  <div v-if="project.client_name" class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>{{ project.client_name }}</span>
                  </div>
                  <div v-if="project.start_date" class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>{{ formatDate(project.start_date) }}</span>
                    <span v-if="project.end_date">- {{ formatDate(project.end_date) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    <span>{{ project.vessel_count }} Vessels</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                    <span>{{ project.equipment_count }} Equipment</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="projectStore.totalPages > 1" class="flex justify-center gap-2 mt-6">
          <AppButton
            variant="secondary"
            size="sm"
            :disabled="projectStore.currentPage === 1"
            @click="handlePageChange(projectStore.currentPage - 1)"
          >
            Previous
          </AppButton>
          <span class="px-4 py-2 text-sm text-gray-700">
            Page {{ projectStore.currentPage }} of {{ projectStore.totalPages }}
          </span>
          <AppButton
            variant="secondary"
            size="sm"
            :disabled="projectStore.currentPage === projectStore.totalPages"
            @click="handlePageChange(projectStore.currentPage + 1)"
          >
            Next
          </AppButton>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500 mb-4">No projects found</p>
        <AppButton v-if="authStore.isManager" @click="router.push('/projects/new')">
          Create First Project
        </AppButton>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/projects'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const projectStore = useProjectStore()

const searchQuery = ref('')
const statusFilter = ref('')
const activeFilter = ref('')

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    planning: 'Planning',
    active: 'Active',
    on_hold: 'On Hold',
    completed: 'Completed',
    cancelled: 'Cancelled',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const variants: Record<string, string> = {
    planning: 'bg-yellow-100 text-yellow-800',
    active: 'bg-green-100 text-green-800',
    on_hold: 'bg-orange-100 text-orange-800',
    completed: 'bg-blue-100 text-blue-800',
    cancelled: 'bg-gray-100 text-gray-800',
  }
  return variants[status] || 'bg-gray-100 text-gray-800'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

function debouncedSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    handleFilter()
  }, 300)
}

function handleFilter() {
  const params: any = {
    skip: 0,
    limit: 20,
  }

  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  if (statusFilter.value) {
    params.status = statusFilter.value
  }
  if (activeFilter.value) {
    params.is_active = activeFilter.value === 'true'
  }

  projectStore.fetchProjects(params)
}

function handlePageChange(page: number) {
  const params: any = {
    skip: (page - 1) * projectStore.pageSize,
    limit: projectStore.pageSize,
  }

  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  if (statusFilter.value) {
    params.status = statusFilter.value
  }
  if (activeFilter.value) {
    params.is_active = activeFilter.value === 'true'
  }

  projectStore.fetchProjects(params)
}

onMounted(() => {
  projectStore.fetchProjects({ skip: 0, limit: 20 })
})
</script>

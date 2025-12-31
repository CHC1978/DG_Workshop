<template>
  <MainLayout>
    <div class="max-w-6xl mx-auto">
      <!-- Loading -->
      <div v-if="projectStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading...</p>
      </div>

      <!-- Project Details -->
      <div v-else-if="project">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ project.name }}</h1>
            <p class="mt-1 text-lg text-gray-600 font-mono">{{ project.code }}</p>
          </div>
          <div class="flex gap-2">
            <AppButton v-if="authStore.isManager" variant="secondary" size="sm" @click="handleEdit">
              Edit
            </AppButton>
            <AppButton v-if="authStore.isAdmin" variant="danger" size="sm" @click="handleDelete">
              Delete
            </AppButton>
          </div>
        </div>

        <!-- Status Badge -->
        <div class="mb-6 flex gap-2">
          <span :class="statusBadgeClass(project.status)" class="inline-flex px-3 py-1 text-sm font-semibold rounded-lg">
            {{ statusLabel(project.status) }}
          </span>
          <span v-if="!project.is_active" class="inline-flex px-3 py-1 text-sm font-semibold rounded-lg bg-gray-100 text-gray-800">
            Inactive
          </span>
        </div>

        <!-- Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Basic Information -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            <dl class="space-y-3">
              <div>
                <dt class="text-sm font-medium text-gray-500">Project Code</dt>
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ project.code }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Project Name</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ project.name }}</dd>
              </div>
              <div v-if="project.description">
                <dt class="text-sm font-medium text-gray-500">Description</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ project.description }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Created At</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDateTime(project.created_at) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDateTime(project.updated_at) }}</dd>
              </div>
            </dl>
          </div>

          <!-- Client Information -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Client Information</h2>
            <dl class="space-y-3">
              <div v-if="project.client_name">
                <dt class="text-sm font-medium text-gray-500">Client Name</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ project.client_name }}</dd>
              </div>
              <div v-if="project.client_contact">
                <dt class="text-sm font-medium text-gray-500">Contact Person</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ project.client_contact }}</dd>
              </div>
              <div v-if="project.client_phone">
                <dt class="text-sm font-medium text-gray-500">Phone</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ project.client_phone }}</dd>
              </div>
              <div v-if="project.client_email">
                <dt class="text-sm font-medium text-gray-500">Email</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  <a :href="`mailto:${project.client_email}`" class="text-sky-600 hover:text-sky-800">
                    {{ project.client_email }}
                  </a>
                </dd>
              </div>
              <div v-if="!project.client_name && !project.client_contact && !project.client_phone && !project.client_email">
                <p class="text-sm text-gray-500">No client information</p>
              </div>
            </dl>
          </div>

          <!-- Schedule -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Schedule</h2>
            <dl class="space-y-3">
              <div v-if="project.start_date">
                <dt class="text-sm font-medium text-gray-500">Start Date</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDate(project.start_date) }}</dd>
              </div>
              <div v-if="project.end_date">
                <dt class="text-sm font-medium text-gray-500">End Date</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDate(project.end_date) }}</dd>
              </div>
              <div v-if="project.start_date && project.end_date">
                <dt class="text-sm font-medium text-gray-500">Duration</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ calculateDuration(project.start_date, project.end_date) }}</dd>
              </div>
              <div v-if="!project.start_date && !project.end_date">
                <p class="text-sm text-gray-500">No schedule information</p>
              </div>
            </dl>
          </div>

          <!-- Statistics -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
            <dl class="space-y-3">
              <div>
                <dt class="text-sm font-medium text-gray-500">Vessels</dt>
                <dd class="mt-1 text-2xl font-bold text-sky-600">{{ project.vessel_count }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Equipment</dt>
                <dd class="mt-1 text-2xl font-bold text-sky-600">{{ project.equipment_count }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-12">
        <p class="text-gray-500">Project not found</p>
        <AppButton variant="secondary" class="mt-4" @click="router.push('/projects')">
          Back to Projects
        </AppButton>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/projects'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const projectStore = useProjectStore()

const projectId = computed(() => parseInt(route.params.id as string))
const project = computed(() => projectStore.currentProject)

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

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function calculateDuration(startDate: string, endDate: string): string {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return `${diffDays} days`
}

function handleEdit() {
  router.push(`/projects/${projectId.value}/edit`)
}

async function handleDelete() {
  if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
    return
  }

  try {
    await projectStore.deleteProject(projectId.value)
    alert('Project deleted successfully!')
    router.push('/projects')
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Failed to delete project')
  }
}

onMounted(() => {
  projectStore.fetchById(projectId.value)
})
</script>

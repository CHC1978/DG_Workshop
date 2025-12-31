<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Project' : 'New Project' }}
        </h1>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="bg-white rounded-lg shadow p-6 space-y-6">
        <!-- Basic Information -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Project Code -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Project Code <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.code"
                type="text"
                required
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="PROJ2025001"
              />
            </div>

            <!-- Project Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Project Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Ocean Survey 2025"
              />
            </div>

            <!-- Description -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="form.description"
                rows="3"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Project description..."
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Client Information -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Client Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Client Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Client Name</label>
              <input
                v-model="form.client_name"
                type="text"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Company Name"
              />
            </div>

            <!-- Contact Person -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Contact Person</label>
              <input
                v-model="form.client_contact"
                type="text"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="John Doe"
              />
            </div>

            <!-- Phone -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                v-model="form.client_phone"
                type="tel"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="+886 2 1234 5678"
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                v-model="form.client_email"
                type="email"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="contact@example.com"
              />
            </div>
          </div>
        </div>

        <!-- Project Schedule -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Project Schedule</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Start Date -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                v-model="form.start_date"
                type="date"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              />
            </div>

            <!-- End Date -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                v-model="form.end_date"
                type="date"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              />
            </div>
          </div>
        </div>

        <!-- Status -->
        <div>
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Status</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Project Status -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Project Status</label>
              <select
                v-model="form.status"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              >
                <option value="planning">Planning</option>
                <option value="active">Active</option>
                <option value="on_hold">On Hold</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <!-- Active Status (Edit mode only) -->
            <div v-if="isEditMode">
              <label class="block text-sm font-medium text-gray-700 mb-1">Active Status</label>
              <select
                v-model="form.is_active"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              >
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="projectStore.error" class="rounded-md bg-red-50 p-4">
          <p class="text-sm text-red-800">{{ projectStore.error }}</p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-6 border-t border-gray-200">
          <AppButton variant="secondary" @click="router.back()">
            Cancel
          </AppButton>
          <AppButton type="submit" :disabled="projectStore.loading">
            {{ projectStore.loading ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Project' }}
          </AppButton>
        </div>
      </form>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/projects'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()

const isEditMode = computed(() => !!route.params.id)
const projectId = computed(() => parseInt(route.params.id as string))

const form = ref({
  code: '',
  name: '',
  description: '',
  client_name: '',
  client_contact: '',
  client_phone: '',
  client_email: '',
  start_date: '',
  end_date: '',
  status: 'planning' as 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled',
  is_active: true,
})

async function handleSubmit() {
  try {
    if (isEditMode.value) {
      await projectStore.updateProject(projectId.value, form.value)
      alert('Project updated successfully!')
    } else {
      await projectStore.createProject(form.value)
      alert('Project created successfully!')
    }
    router.push('/projects')
  } catch (error) {
    console.error('Failed to save project:', error)
  }
}

onMounted(async () => {
  if (isEditMode.value) {
    const project = await projectStore.fetchById(projectId.value)
    if (project) {
      form.value = {
        code: project.code,
        name: project.name,
        description: project.description || '',
        client_name: project.client_name || '',
        client_contact: project.client_contact || '',
        client_phone: project.client_phone || '',
        client_email: project.client_email || '',
        start_date: project.start_date || '',
        end_date: project.end_date || '',
        status: project.status,
        is_active: project.is_active,
      }
    }
  }
})
</script>

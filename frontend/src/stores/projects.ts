import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectApi, type Project, type ProjectCreate, type ProjectUpdate } from '@/api/projects'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalPages = ref(0)

  // Fetch all projects with optional filters
  async function fetchProjects(params?: {
    skip?: number
    limit?: number
    status?: string
    search?: string
    is_active?: boolean
  }) {
    loading.value = true
    error.value = null
    try {
      const response = await projectApi.getAll(params)
      projects.value = response.data.projects
      total.value = response.data.total
      currentPage.value = response.data.page
      pageSize.value = response.data.page_size
      totalPages.value = response.data.total_pages
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch projects'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch project by ID
  async function fetchById(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await projectApi.getById(id)
      currentProject.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch project'
      currentProject.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create new project
  async function createProject(data: ProjectCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await projectApi.create(data)
      projects.value.unshift(response.data)
      total.value += 1
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create project'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update project
  async function updateProject(id: number, data: ProjectUpdate) {
    loading.value = true
    error.value = null
    try {
      const response = await projectApi.update(id, data)
      const index = projects.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        projects.value[index] = response.data
      }
      if (currentProject.value?.id === id) {
        currentProject.value = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update project'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete project (soft delete)
  async function deleteProject(id: number) {
    loading.value = true
    error.value = null
    try {
      await projectApi.delete(id)
      projects.value = projects.value.filter((p) => p.id !== id)
      total.value -= 1
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete project'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Clear current project
  function clearCurrentProject() {
    currentProject.value = null
  }

  // Clear error
  function clearError() {
    error.value = null
  }

  return {
    // State
    projects,
    currentProject,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    totalPages,

    // Actions
    fetchProjects,
    fetchById,
    createProject,
    updateProject,
    deleteProject,
    clearCurrentProject,
    clearError,
  }
})

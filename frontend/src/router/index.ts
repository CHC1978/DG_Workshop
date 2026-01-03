import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  // Public routes
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/setup-2fa',
    name: 'setup-2fa',
    component: () => import('@/views/auth/Setup2FAView.vue'),
    meta: { requiresTempToken: true },  // Special: requires temp token, not full auth
  },
  {
    path: '/debug',
    name: 'debug',
    component: () => import('@/views/DebugView.vue'),
    meta: { requiresAuth: false },
  },

  // QR Code scan entry (public - can view basic info without login)
  {
    path: '/e/:assetCode',
    name: 'equipment-scan',
    component: () => import('@/views/equipment/EquipmentScanView.vue'),
    meta: { requiresAuth: false },
  },

  // Protected routes
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/calibrations',
    name: 'calibrations',
    component: () => import('@/views/CalibrationListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/maintenance',
    name: 'maintenance',
    component: () => import('@/views/maintenance/MaintenanceListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/equipment',
    name: 'equipment-list',
    component: () => import('@/views/equipment/EquipmentListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/equipment/new',
    name: 'equipment-create',
    component: () => import('@/views/equipment/EquipmentFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/equipment/:id',
    name: 'equipment-detail',
    component: () => import('@/views/equipment/EquipmentDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/equipment/:id/edit',
    name: 'equipment-edit',
    component: () => import('@/views/equipment/EquipmentFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },

  // SubEquipment routes
  {
    path: '/sub-equipment/:id',
    name: 'sub-equipment-detail',
    component: () => import('@/views/subEquipment/SubEquipmentDetailView.vue'),
    meta: { requiresAuth: true },
  },

  // Location routes
  {
    path: '/locations',
    name: 'locations-list',
    component: () => import('@/views/locations/LocationListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/locations/new/vessel',
    name: 'location-create-vessel',
    component: () => import('@/views/locations/VesselFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/locations/new/person',
    name: 'location-create-person',
    component: () => import('@/views/locations/PersonFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/locations/new/warehouse',
    name: 'location-create-warehouse',
    component: () => import('@/views/locations/WarehouseFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/locations/:id',
    name: 'location-detail',
    component: () => import('@/views/locations/LocationDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/locations/:id/edit/vessel',
    name: 'location-edit-vessel',
    component: () => import('@/views/locations/VesselFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/locations/:id/edit/person',
    name: 'location-edit-person',
    component: () => import('@/views/locations/PersonFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/locations/:id/edit/warehouse',
    name: 'location-edit-warehouse',
    component: () => import('@/views/locations/WarehouseFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },

  // Project routes
  {
    path: '/projects',
    name: 'projects-list',
    component: () => import('@/views/projects/ProjectListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/projects/new',
    name: 'project-create',
    component: () => import('@/views/projects/ProjectFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/projects/:id',
    name: 'project-detail',
    component: () => import('@/views/projects/ProjectDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/projects/:id/edit',
    name: 'project-edit',
    component: () => import('@/views/projects/ProjectFormView.vue'),
    meta: { requiresAuth: true, requiresManager: true },
  },

  // Admin routes
  {
    path: '/admin/users',
    name: 'users-list',
    component: () => import('@/views/admin/UsersListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/users/new',
    name: 'user-create',
    component: () => import('@/views/admin/UserFormView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/users/:id',
    name: 'user-detail',
    component: () => import('@/views/admin/UserDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/users/:id/edit',
    name: 'user-edit',
    component: () => import('@/views/admin/UserFormView.vue'),
    meta: { requiresAuth: true },
  },

  // Fallback
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  // Special handling for setup-2fa (requires temp token in httpOnly cookie)
  if (to.meta.requiresTempToken) {
    if (authStore.needs2FASetup || authStore.totpRequired) {
      // User needs to set up 2FA, allow access
      next()
    } else {
      // No 2FA setup needed, redirect to login
      if (import.meta.env.DEV) {
        console.log('No 2FA setup required, redirecting to login')
      }
      next('/login')
    }
    return
  }

  // Normal auth check
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    if (import.meta.env.DEV) {
      console.log('Not authenticated, redirecting to login')
    }
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    // Redirect to dashboard if already authenticated
    if (import.meta.env.DEV) {
      console.log('Already authenticated, redirecting to dashboard')
    }
    next('/dashboard')
  } else {
    next()
  }
})

export default router

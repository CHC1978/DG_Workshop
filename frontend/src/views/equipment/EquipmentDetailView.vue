<template>
  <MainLayout>
    <div class="max-w-6xl mx-auto space-y-6">
      <!-- Loading -->
      <div v-if="equipmentStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading equipment details...</p>
      </div>

      <!-- Equipment Details -->
      <div v-else-if="equipment" class="space-y-6">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">{{ equipment.asset_code }}</h1>
            <p class="mt-1 text-base sm:text-lg text-gray-600">
              {{ equipment.manufacturer }} {{ equipment.model }}
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <AppButton
              v-if="authStore.isManager"
              variant="secondary"
              size="sm"
              @click="router.push(`/equipment/${equipment.id}/edit`)"
            >
              Edit
            </AppButton>
            <AppButton
              variant="secondary"
              size="sm"
              @click="downloadQRCode"
            >
              Download QR
            </AppButton>
            <AppButton
              v-if="authStore.isAdmin"
              variant="danger"
              size="sm"
              @click="handleDelete"
            >
              Delete
            </AppButton>
          </div>
        </div>

        <!-- Status Badge -->
        <div>
          <span :class="statusBadgeClass(equipment.status)" class="text-lg px-4 py-2">
            {{ statusLabel(equipment.status) }}
          </span>
        </div>

        <!-- Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Basic Information -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            <dl class="space-y-3">
              <div>
                <dt class="text-sm font-medium text-gray-500">Asset Code</dt>
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.asset_code }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Category</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ categoryLabel(equipment.category) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Manufacturer</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ equipment.manufacturer }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Model</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ equipment.model }}</dd>
              </div>
              <div v-if="equipment.serial_number">
                <dt class="text-sm font-medium text-gray-500">Serial Number</dt>
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.serial_number }}</dd>
              </div>
              <!-- Location Info -->
              <div v-if="equipment.current_location_name" class="pt-3 border-t border-gray-200">
                <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
                  <span>📍</span>
                  Current Location
                </dt>
                <dd class="mt-1 text-sm text-gray-900">
                  <span class="font-medium">{{ locationTypeLabel(equipment.current_location_type) }}:</span>
                  {{ equipment.current_location_name }}
                </dd>
              </div>
              <!-- Project Info -->
              <div v-if="equipment.project_code">
                <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
                  <span>📋</span>
                  Project
                </dt>
                <dd class="mt-1 text-sm text-gray-900">
                  <div class="font-medium text-sky-700">{{ equipment.project_code }}</div>
                  <div v-if="equipment.project_name" class="text-xs text-gray-600">{{ equipment.project_name }}</div>
                </dd>
              </div>
              <!-- Parent Equipment Info -->
              <div v-if="equipment.parent_equipment_id" class="pt-3 border-t border-gray-200">
                <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
                  <span>🔗</span>
                  Parent Equipment
                </dt>
                <dd class="mt-1 text-sm text-gray-900">
                  <router-link
                    :to="`/equipment/${equipment.parent_equipment_id}`"
                    class="font-medium text-sky-700 hover:text-sky-900 hover:underline"
                  >
                    {{ equipment.parent_asset_code }}
                  </router-link>
                  <div v-if="equipment.parent_model" class="text-xs text-gray-600 mt-1">{{ equipment.parent_model }}</div>
                </dd>
              </div>
              <!-- Children Count -->
              <div v-if="equipment.children_count && equipment.children_count > 0" class="pt-3 border-t border-gray-200">
                <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
                  <span>🔧</span>
                  Child Components
                </dt>
                <dd class="mt-1 text-sm text-gray-900 font-semibold">
                  {{ equipment.children_count }} component(s)
                </dd>
              </div>
            </dl>
          </div>

          <!-- Equipment Photo -->
          <div v-if="equipment.photo_url" class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Equipment Photo</h2>
            <div class="flex justify-center">
              <img
                :src="getFullUrl(equipment.photo_url)"
                alt="Equipment Photo"
                class="max-w-full h-auto max-h-96 rounded-lg border border-gray-200"
                @error="handleImageError"
              />
            </div>
          </div>

          <!-- Documents & Reports -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Documents & Reports</h2>
            <dl class="space-y-3">
              <div v-if="equipment.purchase_date">
                <dt class="text-sm font-medium text-gray-500">Purchase Date</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDate(equipment.purchase_date) }}</dd>
              </div>
              <div v-if="equipment.manual_url">
                <dt class="text-sm font-medium text-gray-500">Equipment Manual</dt>
                <dd class="mt-1">
                  <a :href="getFullUrl(equipment.manual_url)" target="_blank" class="inline-flex items-center text-sm text-sky-600 hover:text-sky-800">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Download Manual
                  </a>
                </dd>
              </div>
              <div v-if="equipment.calibration_report_url">
                <dt class="text-sm font-medium text-gray-500">Calibration Report</dt>
                <dd class="mt-1">
                  <a :href="getFullUrl(equipment.calibration_report_url)" target="_blank" class="inline-flex items-center text-sm text-sky-600 hover:text-sky-800">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Download Report
                  </a>
                </dd>
              </div>
            </dl>
          </div>

          <!-- QR Code -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">QR Code</h2>
            <div class="flex justify-center">
              <img
                v-if="qrCodeUrl"
                :src="qrCodeUrl"
                alt="QR Code"
                class="w-48 h-48 border border-gray-200 rounded"
              />
              <div v-else class="w-48 h-48 bg-gray-100 flex items-center justify-center rounded">
                <p class="text-gray-500 text-sm">Loading QR Code...</p>
              </div>
            </div>
            <p class="mt-2 text-xs text-gray-500 text-center break-all">
              {{ equipment.qr_code }}
            </p>
          </div>

          <!-- Specifications -->
          <div v-if="equipment.specifications" class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Specifications</h2>
            <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ equipment.specifications }}</p>
          </div>
        </div>

        <!-- Status Actions (Operator+) -->
        <div v-if="authStore.isOperator && canPerformActions" class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Status Actions</h2>
          <p class="text-sm text-gray-600 mb-4">Current Status: <span class="font-semibold">{{ statusLabel(equipment.status) }}</span></p>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Change Status To:
              </label>
              <select
                v-model="selectedStatusAction"
                class="w-full sm:w-auto px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="">-- Select Action --</option>
                <option value="deploy">Deploy Equipment</option>
                <option value="return">Return Equipment</option>
                <option value="repair">Send to Repair</option>
                <option value="calibration">Send to Calibration</option>
                <option value="in_stock">Set to In Stock</option>
                <option value="rented">Set to Rented</option>
              </select>
            </div>

            <AppButton
              :disabled="!selectedStatusAction"
              variant="primary"
              @click="executeStatusAction"
            >
              Execute Action
            </AppButton>
          </div>
        </div>

        <!-- Children Equipment Section -->
        <div v-if="childrenEquipment.length > 0 || authStore.isOperator" class="bg-white rounded-lg shadow overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Child Components</h2>
              <p class="text-xs text-gray-500 mt-1">{{ childrenEquipment.length }} component(s)</p>
            </div>
            <div v-if="authStore.isOperator" class="flex gap-2">
              <AppButton
                variant="secondary"
                size="sm"
                @click="openAttachEquipmentModal"
              >
                Attach Existing
              </AppButton>
              <AppButton
                variant="primary"
                size="sm"
                @click="router.push(`/equipment/new?parent_id=${equipment.id}`)"
              >
                Create New
              </AppButton>
            </div>
          </div>

          <div v-if="loadingChildren" class="text-center py-12 text-gray-500">
            Loading components...
          </div>

          <div v-else-if="childrenEquipment.length === 0" class="text-center py-12 text-gray-500">
            No child components yet
          </div>

          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="child in childrenEquipment"
              :key="child.id"
              class="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
              @click="router.push(`/equipment/${child.id}`)"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <h3 class="font-semibold text-gray-900">{{ child.asset_code }}</h3>
                    <span :class="statusBadgeClass(child.status)" class="px-2 py-1 text-xs rounded">
                      {{ statusLabel(child.status) }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-700">{{ child.model }}</p>
                  <p v-if="child.serial_number" class="text-xs text-gray-500 mt-1 font-mono">SN: {{ child.serial_number }}</p>
                  <div v-if="child.current_location_name" class="mt-2 text-xs text-gray-600">
                    📍 {{ locationTypeLabel(child.current_location_type) }}: {{ child.current_location_name }}
                  </div>
                </div>
                <div class="flex-shrink-0">
                  <button
                    v-if="authStore.isManager"
                    @click.stop="handleDetachChild(child)"
                    class="text-xs px-3 py-1 text-orange-600 hover:text-orange-800 hover:bg-orange-50 rounded transition-colors border border-orange-300"
                    title="Detach from parent (Manager+ only)"
                  >
                    Detach
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Log -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Activity Log</h2>
            <p class="text-xs text-gray-500 mt-1">Double-click a log to quick-edit status</p>
          </div>

          <div v-if="logs.length === 0" class="text-center py-12 text-gray-500">
            No activity logs yet
          </div>

          <!-- Desktop: Card-style Log -->
          <div v-else class="hidden md:block divide-y divide-gray-200">
            <div
              v-for="log in logs"
              :key="log.id"
              class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              @dblclick="handleLogDoubleClick(log)"
            >
              <div class="flex gap-4">
                <!-- Left: Date & Time (Vertical) -->
                <div class="flex-shrink-0 w-32 text-center border-r border-gray-200 pr-4">
                  <div class="text-xs font-medium text-gray-500 mb-1">
                    {{ new Date(log.created_at).toLocaleDateString('zh-TW') }}
                  </div>
                  <div class="text-sm font-semibold text-gray-900">
                    {{ new Date(log.created_at).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }) }}
                  </div>
                  <div class="mt-2">
                    <span :class="logTypeBadge(log.log_type)" class="px-2 py-1 text-xs font-semibold rounded inline-block">
                      {{ logTypeLabel(log.log_type) }}
                    </span>
                  </div>
                </div>

                <!-- Middle: Description & Details -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between mb-1">
                    <p class="text-sm font-medium text-gray-900">
                      {{ log.description }}
                      <span v-if="log.is_edited" class="ml-2 text-xs text-gray-400" :title="`Edited ${log.edit_count} time(s)`">
                        (edited ×{{ log.edit_count }})
                      </span>
                    </p>
                  </div>

                  <div class="text-xs text-gray-600 space-y-1">
                    <div v-if="log.created_by_username">
                      <span class="font-medium">User:</span> {{ log.created_by_username }}
                    </div>
                    <div v-if="log.new_value">
                      <span class="font-medium">Details:</span> {{ log.new_value }}
                    </div>
                    <div v-if="log.current_location_name" class="flex items-center gap-1">
                      <span>📍</span>
                      <span class="font-medium">{{ locationTypeLabel(log.current_location_type) }}:</span>
                      {{ log.current_location_name }}
                    </div>
                    <div v-if="log.project_code" class="flex items-center gap-1 text-sky-700">
                      <span>📋</span>
                      <span class="font-medium">Project:</span> {{ log.project_code }}
                    </div>
                    <div v-if="log.latitude && log.longitude" class="text-gray-500">
                      GPS: {{ log.latitude.toFixed(4) }}, {{ log.longitude.toFixed(4) }}
                    </div>
                  </div>
                </div>

                <!-- Right: View Attachments Button -->
                <div class="flex-shrink-0">
                  <button
                    @click.stop="viewLogAttachmentsQuick(log)"
                    class="text-xs px-2 py-1 text-sky-600 hover:text-sky-800 hover:bg-sky-50 rounded transition-colors"
                    title="View attachments and actions"
                  >
                    View
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Mobile: Simplified Card Log -->
          <div v-if="logs.length > 0" class="block md:hidden divide-y divide-gray-200">
            <div
              v-for="log in logs"
              :key="log.id"
              class="p-4 active:bg-gray-100"
              @dblclick="handleLogDoubleClick(log)"
            >
              <div class="flex items-start justify-between mb-2">
                <div class="flex-1">
                  <div class="text-xs text-gray-500 mb-1">
                    {{ formatDateTime(log.created_at) }}
                  </div>
                  <span :class="logTypeBadge(log.log_type)" class="px-2 py-1 text-xs font-semibold rounded">
                    {{ logTypeLabel(log.log_type) }}
                  </span>
                </div>
                <button
                  @click.stop="viewLogAttachmentsQuick(log)"
                  class="text-xs px-2 py-1 text-sky-600 hover:text-sky-800"
                >
                  View
                </button>
              </div>
              <p class="text-sm text-gray-900 mb-1">{{ log.description }}</p>
              <div v-if="log.current_location_name || log.project_code" class="text-xs text-gray-600 space-y-0.5">
                <div v-if="log.current_location_name">
                  📍 {{ locationTypeLabel(log.current_location_type) }}: {{ log.current_location_name }}
                </div>
                <div v-if="log.project_code" class="text-sky-700">
                  📋 {{ log.project_code }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Deploy Equipment Modal -->
        <div
          v-if="showDeployModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showDeployModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Deploy Equipment</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Deploy to Location
                </label>
                <select
                  v-model="deployForm.locationId"
                  class="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option :value="null">Select location...</option>
                  <option v-for="location in locations" :key="location.id" :value="location.id">
                    {{ location.name }} ({{ location.location_type }})
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
                <textarea
                  v-model="deployForm.notes"
                  class="w-full px-3 py-2 border rounded-lg"
                  rows="3"
                  placeholder="Enter deployment notes..."
                ></textarea>
              </div>

              <!-- Include Children Option -->
              <div v-if="childrenEquipment.length > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
                <label class="flex items-start gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="deployForm.includeChildren"
                    class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
                  />
                  <div class="flex-1">
                    <span class="text-sm font-medium text-gray-900">Move Child Components Together</span>
                    <p class="text-xs text-gray-600 mt-1">
                      Deploy all {{ childrenEquipment.length }} child component(s) to the same location
                    </p>
                  </div>
                </label>
              </div>

              <div class="flex justify-end gap-2 pt-4 border-t">
                <AppButton variant="secondary" @click="showDeployModal = false">Cancel</AppButton>
                <AppButton @click="handleDeploy" :disabled="!deployForm.locationId">Deploy</AppButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Return Equipment Modal -->
        <div
          v-if="showReturnModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showReturnModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Return Equipment</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Return to Location
                </label>
                <select
                  v-model="returnForm.locationId"
                  class="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option :value="null">Select location...</option>
                  <option v-for="location in warehouses" :key="location.id" :value="location.id">
                    {{ location.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
                <textarea
                  v-model="returnForm.notes"
                  class="w-full px-3 py-2 border rounded-lg"
                  rows="3"
                  placeholder="Enter return notes..."
                ></textarea>
              </div>

              <!-- Include Children Option -->
              <div v-if="childrenEquipment.length > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
                <label class="flex items-start gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="returnForm.includeChildren"
                    class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
                  />
                  <div class="flex-1">
                    <span class="text-sm font-medium text-gray-900">Return Child Components Together</span>
                    <p class="text-xs text-gray-600 mt-1">
                      Return all {{ childrenEquipment.length }} child component(s) to the same location
                    </p>
                  </div>
                </label>
              </div>

              <div class="flex justify-end gap-2 pt-4 border-t">
                <AppButton variant="secondary" @click="showReturnModal = false">Cancel</AppButton>
                <AppButton @click="handleReturn" :disabled="!returnForm.locationId">Return</AppButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Detach from Parent Modal -->
        <div
          v-if="showDetachModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showDetachModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Detach from Parent Equipment</h3>
            <div v-if="detachingChild" class="space-y-4">
              <!-- Equipment Info -->
              <div class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
                <p class="text-sm font-medium text-gray-900">{{ detachingChild.asset_code }}</p>
                <p class="text-xs text-gray-600">{{ detachingChild.manufacturer }} {{ detachingChild.model }}</p>
              </div>

              <!-- New Location -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Move to Location <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="detachForm.locationId"
                  class="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option :value="null">Select location...</option>
                  <option v-for="location in locations" :key="location.id" :value="location.id">
                    {{ location.name }} ({{ locationTypeLabel(location.location_type) }})
                  </option>
                </select>
              </div>

              <!-- New Status -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Set Status <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="detachForm.status"
                  class="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option value="in_stock">In Stock</option>
                  <option value="deployed">Deployed</option>
                  <option value="rented">Rented</option>
                  <option value="repair">Repair</option>
                  <option value="calibrating">Calibrating</option>
                </select>
              </div>

              <!-- Notes -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Reason for Detaching (optional)
                </label>
                <textarea
                  v-model="detachForm.notes"
                  class="w-full px-3 py-2 border rounded-lg"
                  rows="3"
                  placeholder="Enter reason for detaching this component..."
                ></textarea>
              </div>

              <div class="flex justify-end gap-2 pt-4 border-t">
                <AppButton variant="secondary" @click="showDetachModal = false">Cancel</AppButton>
                <AppButton @click="submitDetach" :disabled="!detachForm.locationId">Detach</AppButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Edit Log Modal -->
        <div
          v-if="showEditLogModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showEditLogModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Edit Activity Log</h3>
              <button @click="showEditLogModal = false" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>

            <div v-if="editingLog" class="space-y-4">
              <!-- Read-only Info -->
              <div class="p-3 bg-gray-50 rounded">
                <p class="text-xs text-gray-500 mb-1">Type: {{ logTypeLabel(editingLog.log_type) }}</p>
                <p class="text-xs text-gray-500">Created: {{ formatDateTime(editingLog.created_at) }} by {{ editingLog.created_by_username || 'System' }}</p>
                <p v-if="editingLog.is_edited" class="text-xs text-orange-600 mt-1">
                  Edited {{ editingLog.edit_count }} time(s), last at {{ formatDateTime(editingLog.edited_at) }} by {{ editingLog.edited_by_username }}
                </p>
              </div>

              <!-- Non-editable fields -->
              <div v-if="editingLog.old_value || editingLog.new_value" class="border-l-4 border-gray-300 pl-3">
                <p class="text-xs text-gray-500 mb-1">Change Record (read-only):</p>
                <p v-if="editingLog.old_value" class="text-sm text-gray-600">Old: {{ editingLog.old_value }}</p>
                <p v-if="editingLog.new_value" class="text-sm text-gray-600">New: {{ editingLog.new_value }}</p>
              </div>

              <!-- Editable fields -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Description <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="editLogForm.description"
                  class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sky-500"
                  rows="4"
                  placeholder="Enter description..."
                ></textarea>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Latitude (optional)</label>
                  <input
                    v-model.number="editLogForm.latitude"
                    type="number"
                    step="0.000001"
                    class="w-full px-3 py-2 border rounded-lg"
                    placeholder="e.g., 25.033671"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Longitude (optional)</label>
                  <input
                    v-model.number="editLogForm.longitude"
                    type="number"
                    step="0.000001"
                    class="w-full px-3 py-2 border rounded-lg"
                    placeholder="e.g., 121.564427"
                  />
                </div>
              </div>

              <!-- Actions -->
              <div class="flex justify-end gap-2 pt-4 border-t">
                <AppButton variant="secondary" @click="showEditLogModal = false">
                  Cancel
                </AppButton>
                <AppButton @click="handleUpdateLog" :loading="updatingLog">
                  Save Changes
                </AppButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Status Change Modal (from Log Double-Click) -->
        <div
          v-if="showQuickStatusModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showQuickStatusModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Quick Action</h3>
              <button @click="showQuickStatusModal = false" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>

            <!-- Tabs -->
            <div class="border-b border-gray-200 mb-4">
              <div class="flex gap-4">
                <button
                  @click="quickActionTab = 'status'"
                  :class="[
                    'pb-2 px-1 border-b-2 font-medium text-sm transition-colors',
                    quickActionTab === 'status'
                      ? 'border-sky-500 text-sky-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  ]"
                >
                  Status Change
                </button>
                <button
                  @click="quickActionTab = 'attachments'"
                  :class="[
                    'pb-2 px-1 border-b-2 font-medium text-sm transition-colors',
                    quickActionTab === 'attachments'
                      ? 'border-sky-500 text-sky-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  ]"
                >
                  Log Attachments
                </button>
                <button
                  @click="quickActionTab = 'edit'"
                  :class="[
                    'pb-2 px-1 border-b-2 font-medium text-sm transition-colors',
                    quickActionTab === 'edit'
                      ? 'border-sky-500 text-sky-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  ]"
                >
                  Edit Log
                </button>
              </div>
            </div>

            <!-- Status Change Tab -->
            <div v-if="quickActionTab === 'status'" class="space-y-4">
              <div class="mb-4 p-3 bg-gray-50 rounded">
                <p class="text-sm text-gray-600">Current Status:</p>
                <p class="text-lg font-semibold text-gray-900">{{ statusLabel(equipment?.status || '') }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Change To:
                </label>
                <select
                  v-model="quickStatusForm.action"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
                >
                  <option value="">-- Select Action --</option>
                  <option value="deploy">Deploy Equipment</option>
                  <option value="return">Return Equipment</option>
                  <option value="repair">Send to Repair</option>
                  <option value="calibration">Send to Calibration</option>
                  <option value="in_stock">Set to In Stock</option>
                  <option value="rented">Set to Rented</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Notes (optional):
                </label>
                <textarea
                  v-model="quickStatusForm.notes"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows="3"
                  placeholder="Enter notes..."
                ></textarea>
              </div>

              <!-- Include Children Option -->
              <div v-if="childrenEquipment.length > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
                <label class="flex items-start gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="quickStatusForm.includeChildren"
                    class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
                  />
                  <div class="flex-1">
                    <span class="text-sm font-medium text-gray-900">Include Child Components</span>
                    <p class="text-xs text-gray-600 mt-1">
                      Apply this change to all {{ childrenEquipment.length }} child component(s)
                    </p>
                  </div>
                </label>
              </div>

              <div class="flex justify-end gap-2 pt-4 border-t">
                <AppButton variant="secondary" @click="showQuickStatusModal = false">
                  Cancel
                </AppButton>
                <AppButton
                  :disabled="!quickStatusForm.action"
                  @click="executeQuickStatusChange"
                >
                  Execute
                </AppButton>
              </div>
            </div>

            <!-- Log Attachments Tab -->
            <div v-else-if="quickActionTab === 'attachments'" class="space-y-4">
              <div v-if="selectedLog" class="mb-4 p-3 bg-gray-50 rounded">
                <p class="text-sm font-medium">{{ selectedLog.description }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ formatDateTime(selectedLog.created_at) }}</p>
              </div>

              <div v-if="loadingAttachments" class="text-center py-8">
                <p class="text-gray-500">Loading attachments...</p>
              </div>

              <div v-else-if="currentAttachments.length === 0" class="text-center py-8">
                <p class="text-gray-500">No attachments yet</p>
              </div>

              <div v-else class="space-y-3 mb-4">
                <div
                  v-for="att in currentAttachments"
                  :key="att.id"
                  class="flex items-center justify-between p-3 border rounded hover:bg-gray-50"
                >
                  <div class="flex-1">
                    <a
                      :href="`http://localhost:8000${att.file_url}`"
                      target="_blank"
                      class="text-sm font-medium text-sky-600 hover:text-sky-800"
                    >
                      {{ att.file_name }}
                    </a>
                    <p class="text-xs text-gray-500">
                      {{ (att.file_size / 1024).toFixed(1) }} KB • {{ att.file_type }}
                    </p>
                    <p v-if="att.description" class="text-xs text-gray-600 mt-1">{{ att.description }}</p>
                  </div>
                  <button
                    @click="deleteAttachment(att.id)"
                    class="ml-4 text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div class="border-t pt-4">
                <h4 class="text-sm font-semibold mb-3">Upload New Attachment</h4>
                <div class="space-y-3">
                  <select
                    v-model="uploadAttachmentType"
                    class="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="calibration_report">Calibration Report</option>
                    <option value="damage_photo">Damage Photo</option>
                    <option value="repair_document">Repair Document</option>
                    <option value="maintenance_record">Maintenance Record</option>
                    <option value="other">Other</option>
                  </select>

                  <input
                    v-model="uploadDescription"
                    type="text"
                    placeholder="Description (optional)"
                    class="w-full px-3 py-2 border rounded-lg"
                  />

                  <div class="flex items-center gap-2">
                    <input
                      ref="attachmentFileInput"
                      type="file"
                      @change="handleAttachmentFileChange"
                      class="flex-1 text-sm"
                    />
                    <AppButton
                      v-if="selectedAttachmentFile"
                      @click="uploadAttachment"
                      :loading="uploadingAttachment"
                    >
                      Upload
                    </AppButton>
                  </div>
                </div>
              </div>
            </div>

            <!-- Edit Log Tab -->
            <div v-else-if="quickActionTab === 'edit'" class="space-y-4">
              <div v-if="selectedLog" class="p-3 bg-gray-50 rounded">
                <p class="text-xs text-gray-500 mb-1">Type: {{ logTypeLabel(selectedLog.log_type) }}</p>
                <p class="text-xs text-gray-500">Created: {{ formatDateTime(selectedLog.created_at) }} by {{ selectedLog.created_by_username || 'System' }}</p>
                <p v-if="selectedLog.is_edited" class="text-xs text-orange-600 mt-1">
                  Edited {{ selectedLog.edit_count }} time(s), last at {{ formatDateTime(selectedLog.edited_at) }}
                </p>
              </div>

              <div v-if="selectedLog && (selectedLog.old_value || selectedLog.new_value)" class="border-l-4 border-gray-300 pl-3">
                <p class="text-xs text-gray-500 mb-1">Change Record (read-only):</p>
                <p v-if="selectedLog.old_value" class="text-sm text-gray-600">Old: {{ selectedLog.old_value }}</p>
                <p v-if="selectedLog.new_value" class="text-sm text-gray-600">New: {{ selectedLog.new_value }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Description <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="editLogForm.description"
                  class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sky-500"
                  rows="4"
                  placeholder="Enter description..."
                ></textarea>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Latitude (optional)</label>
                  <input
                    v-model.number="editLogForm.latitude"
                    type="number"
                    step="0.000001"
                    class="w-full px-3 py-2 border rounded-lg"
                    placeholder="e.g., 25.033671"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Longitude (optional)</label>
                  <input
                    v-model.number="editLogForm.longitude"
                    type="number"
                    step="0.000001"
                    class="w-full px-3 py-2 border rounded-lg"
                    placeholder="e.g., 121.564427"
                  />
                </div>
              </div>

              <div class="flex justify-end gap-2 pt-4 border-t">
                <AppButton variant="secondary" @click="showQuickStatusModal = false">
                  Cancel
                </AppButton>
                <AppButton @click="handleUpdateLog" :loading="updatingLog">
                  Save Changes
                </AppButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Log Attachments Modal -->
        <div
          v-if="showAttachmentsModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showAttachmentsModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Log Attachments</h3>
              <button @click="showAttachmentsModal = false" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>

            <div v-if="selectedLog" class="mb-4 p-3 bg-gray-50 rounded">
              <p class="text-sm font-medium">{{ selectedLog.description }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ formatDateTime(selectedLog.created_at) }}</p>
            </div>

            <!-- Attachments List -->
            <div v-if="loadingAttachments" class="text-center py-8">
              <p class="text-gray-500">Loading attachments...</p>
            </div>

            <div v-else-if="currentAttachments.length === 0" class="text-center py-8">
              <p class="text-gray-500">No attachments yet</p>
            </div>

            <div v-else class="space-y-3 mb-4">
              <div
                v-for="att in currentAttachments"
                :key="att.id"
                class="flex items-center justify-between p-3 border rounded hover:bg-gray-50"
              >
                <div class="flex-1">
                  <a
                    :href="`http://localhost:8000${att.file_url}`"
                    target="_blank"
                    class="text-sm font-medium text-sky-600 hover:text-sky-800"
                  >
                    {{ att.file_name }}
                  </a>
                  <p class="text-xs text-gray-500">
                    {{ (att.file_size / 1024).toFixed(1) }} KB • {{ att.file_type }}
                  </p>
                  <p v-if="att.description" class="text-xs text-gray-600 mt-1">{{ att.description }}</p>
                </div>
                <button
                  @click="deleteAttachment(att.id)"
                  class="ml-4 text-red-600 hover:text-red-800 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>

            <!-- Upload Section -->
            <div class="border-t pt-4">
              <h4 class="text-sm font-semibold mb-3">Upload New Attachment</h4>
              <div class="space-y-3">
                <select
                  v-model="uploadAttachmentType"
                  class="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="calibration_report">Calibration Report</option>
                  <option value="damage_photo">Damage Photo</option>
                  <option value="repair_document">Repair Document</option>
                  <option value="maintenance_record">Maintenance Record</option>
                  <option value="other">Other</option>
                </select>

                <input
                  v-model="uploadDescription"
                  type="text"
                  placeholder="Description (optional)"
                  class="w-full px-3 py-2 border rounded-lg"
                />

                <div class="flex items-center gap-2">
                  <input
                    ref="attachmentFileInput"
                    type="file"
                    @change="handleAttachmentFileChange"
                    class="flex-1 text-sm"
                  />
                  <AppButton
                    v-if="selectedAttachmentFile"
                    @click="uploadAttachment"
                    :loading="uploadingAttachment"
                  >
                    Upload
                  </AppButton>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Attach Existing Equipment Modal -->
        <div
          v-if="showAttachEquipmentModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showAttachEquipmentModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Attach Existing Equipment</h3>
              <button @click="showAttachEquipmentModal = false" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>

            <p class="text-sm text-gray-600 mb-4">
              Select an existing standalone equipment to attach as a child component.
              Only equipment with the same category ({{ equipment?.category?.toUpperCase() }}) are shown.
            </p>

            <!-- Search Filter -->
            <div class="mb-4">
              <input
                v-model="attachEquipmentSearch"
                type="text"
                placeholder="Search by asset code, manufacturer, or model..."
                class="w-full px-3 py-2 border rounded-lg"
              />
            </div>

            <!-- Loading State -->
            <div v-if="loadingAvailableEquipment" class="text-center py-8">
              <p class="text-gray-500">Loading available equipment...</p>
            </div>

            <!-- No Equipment Available -->
            <div v-else-if="filteredAvailableEquipment.length === 0" class="text-center py-8">
              <p class="text-gray-500">No available equipment found</p>
            </div>

            <!-- Equipment List -->
            <div v-else class="space-y-2 mb-4 max-h-96 overflow-y-auto">
              <label
                v-for="eq in filteredAvailableEquipment"
                :key="eq.id"
                class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                :class="selectedEquipmentToAttach?.id === eq.id ? 'border-sky-500 bg-sky-50' : 'border-gray-200'"
              >
                <input
                  type="radio"
                  name="equipmentToAttach"
                  :value="eq"
                  v-model="selectedEquipmentToAttach"
                  class="w-4 h-4 text-sky-600"
                />
                <div class="flex-1">
                  <p class="font-semibold text-gray-900">{{ eq.asset_code }}</p>
                  <p class="text-sm text-gray-600">{{ eq.manufacturer }} {{ eq.model }}</p>
                  <p v-if="eq.serial_number" class="text-xs text-gray-500 font-mono">SN: {{ eq.serial_number }}</p>
                  <div v-if="eq.current_location_name" class="mt-1 text-xs text-gray-600">
                    📍 {{ eq.current_location_name }}
                  </div>
                </div>
                <span :class="statusBadgeClass(eq.status)" class="px-2 py-1 text-xs rounded">
                  {{ statusLabel(eq.status) }}
                </span>
              </label>
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-2 pt-4 border-t">
              <AppButton variant="secondary" @click="showAttachEquipmentModal = false">
                Cancel
              </AppButton>
              <AppButton
                @click="handleAttachEquipment"
                :disabled="!selectedEquipmentToAttach"
                :loading="attachingEquipment"
              >
                Attach Equipment
              </AppButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="equipment?.notes" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 class="text-sm font-semibold text-yellow-900 mb-2">Notes</h3>
        <p class="text-sm text-yellow-800 whitespace-pre-wrap">{{ equipment.notes }}</p>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { useUiStore } from '@/stores/ui'
import { equipmentApi } from '@/api/equipment'
import { locationApi } from '@/api/locations'
import axios from 'axios'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()
const uiStore = useUiStore()

const equipmentId = computed(() => parseInt(route.params.id as string))
const equipment = computed(() => equipmentStore.currentEquipment)

const qrCodeUrl = ref('')
const logs = ref<any[]>([])
const showDeployModal = ref(false)
const showReturnModal = ref(false)
const showRepairModal = ref(false)
const selectedStatusAction = ref('')
const showQuickStatusModal = ref(false)
const quickActionTab = ref('status')
const quickStatusForm = ref({
  action: '',
  notes: '',
  includeChildren: true  // Default to true for convenience
})

// Locations for deploy/return
const locations = ref<any[]>([])
const warehouses = computed(() => locations.value.filter(l => l.location_type === 'warehouse'))

// Deploy/Return forms
const deployForm = ref({
  locationId: null as number | null,
  notes: '',
  includeChildren: true
})

const returnForm = ref({
  locationId: null as number | null,
  notes: '',
  includeChildren: true
})

// Detach from Parent form
const showDetachModal = ref(false)
const detachingChild = ref<Equipment | null>(null)
const detachForm = ref({
  locationId: null as number | null,
  status: 'in_stock' as string,
  notes: ''
})

// Log Attachments
const showAttachmentsModal = ref(false)
const selectedLog = ref<any>(null)
const currentAttachments = ref<any[]>([])
const loadingAttachments = ref(false)
const uploadingAttachment = ref(false)
const uploadAttachmentType = ref('other')
const uploadDescription = ref('')
const selectedAttachmentFile = ref<File | null>(null)
const attachmentFileInput = ref<HTMLInputElement | null>(null)

// Attach Existing Equipment
const showAttachEquipmentModal = ref(false)
const availableEquipment = ref<any[]>([])
const loadingAvailableEquipment = ref(false)
const selectedEquipmentToAttach = ref<any>(null)
const attachEquipmentSearch = ref('')
const attachingEquipment = ref(false)

// Log Editing
const showEditLogModal = ref(false)
const editingLog = ref<any>(null)
const updatingLog = ref(false)
const editLogForm = ref({
  description: '',
  latitude: null as number | null,
  longitude: null as number | null,
})

// Children Equipment
const childrenEquipment = ref<Equipment[]>([])
const loadingChildren = ref(false)

const canPerformActions = computed(() => {
  return equipment.value?.status !== 'disposed' && equipment.value?.status !== 'lost'
})

// Filtered available equipment for attaching
const filteredAvailableEquipment = computed(() => {
  if (!attachEquipmentSearch.value) {
    return availableEquipment.value
  }

  const search = attachEquipmentSearch.value.toLowerCase()
  return availableEquipment.value.filter(eq =>
    eq.asset_code?.toLowerCase().includes(search) ||
    eq.manufacturer?.toLowerCase().includes(search) ||
    eq.model?.toLowerCase().includes(search)
  )
})

function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    mbes: 'MBES - Multibeam Echosounder',
    gnss: 'GNSS - Receiver',
    svp: 'SVP - Sound Velocity Profiler',
    sbp: 'SBP - Sub-bottom Profiler',
    usbl: 'USBL - Ultra-Short Baseline',
    rov: 'ROV - Remotely Operated Vehicle',
    ins: 'INS - Inertial Navigation System',
    magnetometer: 'Magnetometer',
    other: 'Other',
  }
  return labels[category] || category
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    ordering: 'Ordering',
    in_stock: 'In Stock',
    deployed: 'Deployed',
    rented: 'Rented',
    repair: 'Repair',
    disposed: 'Disposed',
    lost: 'Lost',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const base = 'inline-block font-semibold rounded'
  const variants: Record<string, string> = {
    ordering: 'bg-yellow-100 text-yellow-800',
    in_stock: 'bg-green-100 text-green-800',
    deployed: 'bg-blue-100 text-blue-800',
    rented: 'bg-purple-100 text-purple-800',
    repair: 'bg-orange-100 text-orange-800',
    disposed: 'bg-gray-100 text-gray-800',
    lost: 'bg-red-100 text-red-800',
  }
  return `${base} ${variants[status] || 'bg-gray-100 text-gray-800'}`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function logTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    status_change: 'Status',
    location_change: 'Location',
    rental_start: 'Rental Start',
    rental_end: 'Rental End',
    calibration: 'Calibration',
    maintenance: 'Maintenance',
    note: 'Note',
    created: 'Created',
    updated: 'Updated',
  }
  return labels[type] || type
}

function logTypeBadge(type: string): string {
  const base = 'inline-block'
  const variants: Record<string, string> = {
    status_change: 'bg-blue-100 text-blue-800',
    location_change: 'bg-purple-100 text-purple-800',
    rental_start: 'bg-green-100 text-green-800',
    rental_end: 'bg-orange-100 text-orange-800',
    calibration: 'bg-yellow-100 text-yellow-800',
    maintenance: 'bg-red-100 text-red-800',
    note: 'bg-gray-100 text-gray-800',
    created: 'bg-sky-100 text-sky-800',
    updated: 'bg-indigo-100 text-indigo-800',
  }
  return `${base} ${variants[type] || 'bg-gray-100 text-gray-800'}`
}

function getFullUrl(url: string): string {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

function handleImageError(event: Event) {
  console.error('Failed to load image')
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f3f4f6" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af"%3ENo Image%3C/text%3E%3C/svg%3E'
}

async function downloadQRCode() {
  if (!equipment.value) return

  try {
    // Use the authenticated API to get QR code
    const response = await equipmentApi.getQRCode(equipment.value.id)
    const qrCodeBase64 = response.data.qr_code_base64

    // Create a link and trigger download
    const link = document.createElement('a')
    link.href = qrCodeBase64
    link.download = `QR_${equipment.value.asset_code}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    uiStore.showNotification('success', 'QR Code downloaded successfully')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to download QR code')
  }
}

async function handleDelete() {
  if (!equipment.value) return

  const confirmed = confirm(
    `Delete equipment ${equipment.value.asset_code}?\n\n` +
    `This will deactivate the equipment (soft delete).\n` +
    `Are you sure?`
  )

  if (!confirmed) return

  try {
    await equipmentStore.remove(equipment.value.id)
    uiStore.showNotification('success', 'Equipment deleted successfully')
    router.push('/equipment')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to delete equipment')
  }
}

async function executeStatusAction() {
  if (!equipment.value || !selectedStatusAction.value) return

  switch (selectedStatusAction.value) {
    case 'deploy':
      showDeployModal.value = true
      break
    case 'return':
      showReturnModal.value = true
      break
    case 'repair':
      await handleSendToRepair()
      break
    case 'calibration':
      await handleSendToCalibration()
      break
    case 'in_stock':
      await handleSetStatus('in_stock')
      break
    case 'rented':
      await handleSetStatus('rented')
      break
  }

  // Reset selection after action
  selectedStatusAction.value = ''
}

async function handleSetStatus(status: string) {
  if (!equipment.value) return

  const notes = prompt(`Notes for setting status to "${statusLabel(status)}" (optional):`)
  if (notes === null) return

  try {
    // Use the update API to change status
    await equipmentApi.update(equipment.value.id, { status })
    uiStore.showNotification('success', `Equipment status changed to ${statusLabel(status)}`)
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to update status')
  }
}

async function handleSendToRepair() {
  if (!equipment.value) return

  const notes = prompt('Notes for repair (optional):')
  if (notes === null) return

  try {
    await equipmentApi.repair(equipment.value.id, notes || undefined)
    uiStore.showNotification('success', 'Equipment sent to repair')
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to send to repair')
  }
}

async function handleSendToCalibration() {
  if (!equipment.value) return

  const notes = prompt('Notes for calibration (optional):')
  if (notes === null) return

  try {
    await equipmentApi.sendToCalibration(equipment.value.id, notes || undefined)
    uiStore.showNotification('success', 'Equipment sent to calibration')
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to send to calibration')
  }
}

async function handleDeploy() {
  if (!equipment.value || !deployForm.value.locationId) return

  const includeChildren = deployForm.value.includeChildren && childrenEquipment.value.length > 0

  try {
    if (includeChildren) {
      // Use groupMove API to move parent and children together
      const response = await equipmentApi.groupMove(equipment.value.id, {
        location_id: deployForm.value.locationId,
        include_children: true,
        notes: deployForm.value.notes || undefined
      })
      uiStore.showNotification('success',
        `${response.data.moved_count} equipment(s) deployed to ${response.data.target_location}`
      )
    } else {
      // Original deploy API for single equipment
      await equipmentApi.deploy(
        equipment.value.id,
        deployForm.value.locationId,
        deployForm.value.notes || undefined
      )
      uiStore.showNotification('success', 'Equipment deployed successfully')
    }

    showDeployModal.value = false
    deployForm.value = { locationId: null, notes: '', includeChildren: true }
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
    await loadChildren()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to deploy equipment')
  }
}

async function handleReturn() {
  if (!equipment.value || !returnForm.value.locationId) return

  const includeChildren = returnForm.value.includeChildren && childrenEquipment.value.length > 0

  try {
    if (includeChildren) {
      // Use groupMove API to return parent and children together
      const response = await equipmentApi.groupMove(equipment.value.id, {
        location_id: returnForm.value.locationId,
        include_children: true,
        notes: returnForm.value.notes || undefined
      })
      uiStore.showNotification('success',
        `${response.data.moved_count} equipment(s) returned to ${response.data.target_location}`
      )
    } else {
      // Original return API for single equipment
      await equipmentApi.return(
        equipment.value.id,
        returnForm.value.locationId,
        returnForm.value.notes || undefined
      )
      uiStore.showNotification('success', 'Equipment returned successfully')
    }

    showReturnModal.value = false
    returnForm.value = { locationId: null, notes: '', includeChildren: true }
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
    await loadChildren()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to return equipment')
  }
}

function locationTypeLabel(type?: string): string {
  if (!type) return ''
  const labels: Record<string, string> = {
    warehouse: 'Warehouse',
    vessel: 'Vessel',
    person: 'Person',
    external: 'External',
    platform: 'Platform',
    vehicle: 'Vehicle',
  }
  return labels[type] || type
}

async function handleLogDoubleClick(log: any) {
  if (!authStore.isOperator) return

  selectedLog.value = log
  quickActionTab.value = 'status'
  quickStatusForm.value = {
    action: '',
    notes: log.description || '',
    includeChildren: true
  }
  editLogForm.value = {
    description: log.description || '',
    latitude: log.latitude,
    longitude: log.longitude,
  }

  // Load attachments
  await loadLogAttachments(log.id)

  showQuickStatusModal.value = true
}

async function viewLogAttachmentsQuick(log: any) {
  selectedLog.value = log
  quickActionTab.value = 'attachments'
  quickStatusForm.value = {
    action: '',
    notes: log.description || '',
    includeChildren: true
  }
  editLogForm.value = {
    description: log.description || '',
    latitude: log.latitude,
    longitude: log.longitude,
  }

  // Load attachments
  await loadLogAttachments(log.id)

  showQuickStatusModal.value = true
}

async function executeQuickStatusChange() {
  if (!equipment.value || !quickStatusForm.value.action) return

  const action = quickStatusForm.value.action
  const notes = quickStatusForm.value.notes || undefined
  const includeChildren = quickStatusForm.value.includeChildren && childrenEquipment.value.length > 0

  try {
    switch (action) {
      case 'deploy':
        showQuickStatusModal.value = false
        showDeployModal.value = true
        deployForm.value.notes = notes || ''
        deployForm.value.includeChildren = includeChildren
        break
      case 'return':
        showQuickStatusModal.value = false
        showReturnModal.value = true
        returnForm.value.notes = notes || ''
        returnForm.value.includeChildren = includeChildren
        break
      case 'repair':
      case 'calibration':
        // Use syncChildrenStatus API if includeChildren is enabled
        if (includeChildren) {
          const targetStatus = action === 'repair' ? 'repair' : 'calibrating'
          const response = await equipmentApi.syncChildrenStatus(equipment.value.id, {
            new_status: targetStatus as any,
            include_children: true,
            notes
          })
          uiStore.showNotification('success',
            `${response.data.updated_count} equipment(s) ${action === 'repair' ? 'sent to repair' : 'sent to calibration'}`
          )
        } else {
          // Original behavior for single equipment
          if (action === 'repair') {
            await equipmentApi.repair(equipment.value.id, notes)
            uiStore.showNotification('success', 'Equipment sent to repair')
          } else {
            await equipmentApi.sendToCalibration(equipment.value.id, notes)
            uiStore.showNotification('success', 'Equipment sent to calibration')
          }
        }
        showQuickStatusModal.value = false
        await equipmentStore.fetchById(equipmentId.value)
        await loadLogs()
        await loadChildren()
        break
      case 'in_stock':
      case 'rented':
        // Use syncChildrenStatus API if includeChildren is enabled
        if (includeChildren) {
          const response = await equipmentApi.syncChildrenStatus(equipment.value.id, {
            new_status: action as any,
            include_children: true,
            notes
          })
          uiStore.showNotification('success',
            `${response.data.updated_count} equipment(s) status changed to ${statusLabel(action)}`
          )
        } else {
          await equipmentApi.update(equipment.value.id, { status: action })
          uiStore.showNotification('success', `Equipment status changed to ${statusLabel(action)}`)
        }
        showQuickStatusModal.value = false
        await equipmentStore.fetchById(equipmentId.value)
        await loadLogs()
        await loadChildren()
        break
    }

    // Reset form
    quickStatusForm.value = { action: '', notes: '', includeChildren: true }
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to change status')
  }
}

async function loadLogs() {
  if (!equipmentId.value) return

  try {
    const response = await equipmentApi.getLogs(equipmentId.value)
    logs.value = response.data
  } catch (error) {
    console.error('Failed to load logs:', error)
  }
}

async function loadQRCode() {
  if (!equipmentId.value) return

  try {
    const response = await equipmentApi.getQRCode(equipmentId.value)
    qrCodeUrl.value = response.data.qr_code_base64
  } catch (error) {
    console.error('Failed to load QR code:', error)
  }
}

// ==================== Log Editing ====================

function openEditLogModal(log: any) {
  editingLog.value = log
  editLogForm.value = {
    description: log.description || '',
    latitude: log.latitude,
    longitude: log.longitude,
  }
  showEditLogModal.value = true
}

async function handleUpdateLog() {
  if (!editingLog.value || !equipment.value) return

  if (!editLogForm.value.description.trim()) {
    uiStore.showNotification('error', 'Description is required')
    return
  }

  updatingLog.value = true

  try {
    const response = await equipmentApi.updateLog(
      equipment.value.id,
      editingLog.value.id,
      editLogForm.value
    )

    // Update local log in the list
    const index = logs.value.findIndex(l => l.id === editingLog.value.id)
    if (index !== -1) {
      logs.value[index] = response.data
    }

    uiStore.showNotification('success', 'Log updated successfully')
    showEditLogModal.value = false
    editingLog.value = null
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Update failed')
  } finally {
    updatingLog.value = false
  }
}

// ==================== Log Attachments ====================

async function viewLogAttachments(log: any) {
  selectedLog.value = log
  showAttachmentsModal.value = true
  await loadLogAttachments(log.id)
}

async function loadLogAttachments(logId: number) {
  loadingAttachments.value = true
  try {
    const response = await axios.get(`/api/equipment-logs/${logId}/attachments`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('auth') ? JSON.parse(localStorage.getItem('auth')!).token : ''}`
      }
    })
    currentAttachments.value = response.data
  } catch (error) {
    console.error('Failed to load attachments:', error)
    currentAttachments.value = []
  } finally {
    loadingAttachments.value = false
  }
}

function handleAttachmentFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  selectedAttachmentFile.value = target.files?.[0] || null
}

async function uploadAttachment() {
  if (!selectedAttachmentFile.value || !selectedLog.value) return

  uploadingAttachment.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedAttachmentFile.value)
    formData.append('attachment_type', uploadAttachmentType.value)
    if (uploadDescription.value) {
      formData.append('description', uploadDescription.value)
    }

    const authData = localStorage.getItem('auth')
    const token = authData ? JSON.parse(authData).token : ''

    await axios.post(
      `/api/equipment-logs/${selectedLog.value.id}/attachments`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      }
    )

    uiStore.showNotification('success', 'Attachment uploaded successfully')
    selectedAttachmentFile.value = null
    uploadDescription.value = ''
    if (attachmentFileInput.value) {
      attachmentFileInput.value.value = ''
    }
    await loadLogAttachments(selectedLog.value.id)
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Upload failed')
  } finally {
    uploadingAttachment.value = false
  }
}

async function deleteAttachment(attachmentId: number) {
  if (!confirm('Delete this attachment?')) return

  try {
    const authData = localStorage.getItem('auth')
    const token = authData ? JSON.parse(authData).token : ''

    await axios.delete(`/api/log-attachments/${attachmentId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    uiStore.showNotification('success', 'Attachment deleted')
    if (selectedLog.value) {
      await loadLogAttachments(selectedLog.value.id)
    }
  } catch (error: any) {
    uiStore.showNotification('error', 'Delete failed')
  }
}

async function loadLocations() {
  try {
    const response = await locationApi.getAll({ limit: 100, is_active: true })
    locations.value = response.data.locations || []
  } catch (error) {
    console.error('Failed to load locations:', error)
  }
}

// ==================== Children Equipment Management ====================

async function loadChildren() {
  if (!equipmentId.value) return

  loadingChildren.value = true
  try {
    const response = await equipmentApi.getChildren(equipmentId.value)
    childrenEquipment.value = response.data
  } catch (error) {
    console.error('Failed to load children equipment:', error)
    childrenEquipment.value = []
  } finally {
    loadingChildren.value = false
  }
}

// Open attach equipment modal and load available equipment
async function openAttachEquipmentModal() {
  showAttachEquipmentModal.value = true
  await loadAvailableEquipment()
}

// Load available equipment for attaching
async function loadAvailableEquipment() {
  if (!equipment.value) return

  loadingAvailableEquipment.value = true
  try {
    // Load all equipment with same category, excluding children and current equipment
    const response = await equipmentApi.list({
      skip: 0,
      limit: 1000,
      category: equipment.value.category
    })

    // Filter to only show standalone equipment (not already children)
    availableEquipment.value = response.data.equipments.filter(
      (eq: any) => !eq.parent_equipment_id && eq.id !== equipment.value?.id
    )
  } catch (error) {
    console.error('Failed to load available equipment:', error)
    availableEquipment.value = []
  } finally {
    loadingAvailableEquipment.value = false
  }
}

// Handle attaching existing equipment as child
async function handleAttachEquipment() {
  if (!selectedEquipmentToAttach.value || !equipment.value) return

  console.log('[ATTACH] Starting attach process...')
  console.log('[ATTACH] Child equipment ID:', selectedEquipmentToAttach.value.id)
  console.log('[ATTACH] Child equipment:', selectedEquipmentToAttach.value.asset_code)
  console.log('[ATTACH] Parent equipment ID:', equipment.value.id)
  console.log('[ATTACH] Parent equipment:', equipment.value.asset_code)

  attachingEquipment.value = true
  try {
    const updateData = {
      parent_equipment_id: equipment.value.id
    }
    console.log('[ATTACH] Sending update request with data:', updateData)

    // Update the selected equipment to set its parent_equipment_id
    const response = await equipmentApi.update(selectedEquipmentToAttach.value.id, updateData)

    console.log('[ATTACH] Update response:', response.data)
    console.log('[ATTACH] Child status after attach:', response.data.status)
    console.log('[ATTACH] Child location after attach:', response.data.current_location_id)
    console.log('[ATTACH] Child project after attach:', response.data.project_id)

    uiStore.showNotification('success', `${selectedEquipmentToAttach.value.asset_code} attached successfully`)

    // Close modal and reset
    showAttachEquipmentModal.value = false
    selectedEquipmentToAttach.value = null
    attachEquipmentSearch.value = ''

    // Reload children list and current equipment
    console.log('[ATTACH] Reloading children and equipment...')
    await loadChildren()
    await equipmentStore.fetchById(equipmentId.value)
    console.log('[ATTACH] Attach process completed')
  } catch (error: any) {
    console.error('[ATTACH] Failed to attach equipment:', error)
    console.error('[ATTACH] Error details:', error.response?.data)
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to attach equipment')
  } finally {
    attachingEquipment.value = false
  }
}

function handleDetachChild(child: Equipment) {
  // Open detach modal for user to select location and status
  detachingChild.value = child
  detachForm.value = {
    locationId: null,
    status: 'in_stock',
    notes: ''
  }
  showDetachModal.value = true
}

async function submitDetach() {
  if (!detachingChild.value || !detachForm.value.locationId) return

  try {
    await equipmentApi.detachFromParent(detachingChild.value.id, {
      new_location_id: detachForm.value.locationId,
      new_status: detachForm.value.status,
      notes: detachForm.value.notes || undefined
    })
    uiStore.showNotification('success', `${detachingChild.value.asset_code} detached successfully`)

    // Close modal and reset
    showDetachModal.value = false
    detachingChild.value = null
    detachForm.value = { locationId: null, status: 'in_stock', notes: '' }

    // Reload children list and current equipment
    await loadChildren()
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to detach equipment')
  }
}

onMounted(async () => {
  await equipmentStore.fetchById(equipmentId.value)
  loadLogs()
  loadQRCode()
  loadLocations()
  loadChildren()
})
</script>

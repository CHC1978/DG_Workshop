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
            <!-- Parent Equipment (if exists) -->
            <div v-if="equipment.parent_equipment_id" class="mb-2">
              <p class="text-xs text-gray-500 mb-1">Parent Equipment</p>
              <h2
                class="text-3xl sm:text-4xl font-bold text-sky-700 hover:text-sky-900 hover:underline cursor-pointer"
                @click="router.push(`/equipment/${equipment.parent_equipment_id}`)"
              >
                {{ equipment.parent_asset_code }}
              </h2>
              <p v-if="equipment.parent_model" class="text-sm text-gray-600 mt-1">
                {{ equipment.parent_model }}
              </p>
            </div>

            <!-- Current Equipment -->
            <div>
              <p v-if="equipment.parent_equipment_id" class="text-xs text-gray-500 mb-1">Child Component</p>
              <h1 :class="equipment.parent_equipment_id ? 'text-xl sm:text-2xl' : 'text-2xl sm:text-3xl'" class="font-bold text-gray-900">
                {{ equipment.asset_code }}
              </h1>
              <p class="mt-1 text-base sm:text-lg text-gray-600">
                {{ equipment.manufacturer }} {{ equipment.model }}
              </p>
            </div>
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

        <!-- Status & Actions (Combined Card) -->
        <div class="bg-white rounded-lg shadow p-6">
          <!-- Status Badge -->
          <div class="mb-4">
            <span :class="statusBadgeClass(equipment.status)" class="text-lg px-4 py-2">
              {{ statusLabel(equipment.status) }}
            </span>
          </div>

          <!-- Status Actions (Operator+ only) -->
          <div v-if="authStore.isOperator && canPerformActions" class="pt-4 border-t border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Status Actions</h2>

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
                  <option value="maintenance">Add Maintenance Record</option>
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
        </div>

        <!-- Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                  <span
                    class="font-medium text-sky-700 hover:text-sky-900 hover:underline cursor-pointer"
                    @click="router.push(`/equipment/${equipment.parent_equipment_id}`)"
                  >
                    {{ equipment.parent_asset_code }}
                  </span>
                  <div v-if="equipment.parent_model" class="text-xs text-gray-600 mt-1">{{ equipment.parent_model }}</div>
                </dd>
              </div>
              <!-- Children Components List -->
              <div v-if="childrenEquipment.length > 0" class="pt-3 border-t border-gray-200">
                <dt class="text-sm font-medium text-gray-500 flex items-center gap-1 mb-2">
                  <span>🔧</span>
                  Child Components ({{ childrenEquipment.length }})
                </dt>
                <dd class="mt-1 space-y-1">
                  <div
                    v-for="child in childrenEquipment"
                    :key="child.id"
                    class="text-sm text-gray-900"
                  >
                    <span
                      class="font-medium text-sky-700 hover:text-sky-900 hover:underline cursor-pointer"
                      @click="router.push(`/equipment/${child.id}`)"
                    >
                      {{ child.asset_code }}
                    </span>
                    <span class="text-xs text-gray-500 ml-1">- {{ child.model }}</span>
                  </div>
                </dd>
              </div>
            </dl>
          </div>

          <!-- Children Equipment Section -->
          <ChildrenEquipmentSection
            v-if="equipment"
            :key="`children-${equipment.id}`"
            :parent-equipment-id="equipment.id"
            :parent-category="equipment.category"
            :can-edit="authStore.isOperator"
            :can-detach="authStore.isManager"
            @detach="handleDetachChild"
            @children-updated="handleChildrenUpdated"
            @children-loaded="childrenEquipment = $event"
            ref="childrenSection"
          />

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

        <!-- Activity Log -->
        <EquipmentLogSection
          v-if="equipmentId"
          :key="`logs-${equipmentId}`"
          :equipment-id="equipmentId"
          @log-double-clicked="handleLogDoubleClick"
          @view-attachments="viewLogAttachmentsQuick"
          ref="logSection"
        />

        <!-- Deploy Equipment Modal -->
        <DeployEquipmentModal
          :show="showDeployModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showDeployModal = false"
          @deployed="handleDeployed"
        />

        <!-- Return Equipment Modal -->
        <ReturnEquipmentModal
          :show="showReturnModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showReturnModal = false"
          @returned="handleReturned"
        />

        <!-- Detach from Parent Modal -->
        <DetachFromParentModal
          :show="showDetachModal"
          :equipment="detachingChild"
          :locations="locations"
          @close="handleDetachModalClose"
          @detached="handleDetached"
        />

        <!-- Add Maintenance Record Modal -->
        <AddMaintenanceRecordModal
          :show="showMaintenanceModal"
          :equipment="equipment"
          @close="showMaintenanceModal = false"
          @saved="handleMaintenanceSaved"
        />

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

        <!-- Attach Equipment Modal is now inside ChildrenEquipmentSection component -->
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { useUiStore } from '@/stores/ui'
import { equipmentApi } from '@/api/equipment'
import { locationApi } from '@/api/locations'
import axios from 'axios'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import DeployEquipmentModal from '@/components/equipment/modals/DeployEquipmentModal.vue'
import ReturnEquipmentModal from '@/components/equipment/modals/ReturnEquipmentModal.vue'
import DetachFromParentModal from '@/components/equipment/modals/DetachFromParentModal.vue'
import AddMaintenanceRecordModal from '@/components/equipment/modals/AddMaintenanceRecordModal.vue'
import EquipmentLogSection from '@/components/equipment/sections/EquipmentLogSection.vue'
import ChildrenEquipmentSection from '@/components/equipment/sections/ChildrenEquipmentSection.vue'
import type { Equipment } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()
const uiStore = useUiStore()

const equipmentId = computed(() => parseInt(route.params.id as string))
const equipment = computed(() => equipmentStore.currentEquipment)

const qrCodeUrl = ref('')
const showDeployModal = ref(false)
const showReturnModal = ref(false)
const showMaintenanceModal = ref(false)

// Section refs
const logSection = ref<InstanceType<typeof EquipmentLogSection> | null>(null)
const childrenSection = ref<InstanceType<typeof ChildrenEquipmentSection> | null>(null)
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

// Detach from Parent
const showDetachModal = ref(false)
const detachingChild = ref<Equipment | null>(null)

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

// Attach Existing Equipment - now managed by ChildrenEquipmentSection component

// Log Editing
const showEditLogModal = ref(false)
const editingLog = ref<any>(null)
const updatingLog = ref(false)
const editLogForm = ref({
  description: '',
  latitude: null as number | null,
  longitude: null as number | null,
})

// Children Equipment - list maintained for other components to access count
const childrenEquipment = ref<Equipment[]>([])

const canPerformActions = computed(() => {
  return equipment.value?.status !== 'disposed' && equipment.value?.status !== 'lost'
})

// filteredAvailableEquipment moved to ChildrenEquipmentSection component

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
  // When deployed to a Vessel, show "Operational" instead of "Deployed"
  if (status === 'deployed' && equipment.value?.current_location_type === 'vessel') {
    return 'Operational'
  }

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
    case 'maintenance':
      showMaintenanceModal.value = true
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

async function handleDeployed() {
  // Refresh equipment data after deployment
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleReturned() {
  // Refresh equipment data after return
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleMaintenanceSaved(data: any) {
  try {
    // Step 1: Add maintenance record (updates equipment and creates MAINTENANCE log)
    const response = await equipmentApi.addMaintenanceRecord(
      equipmentId.value,
      data.maintenance_notes,
      data.last_maintenance_date || undefined,
      data.next_maintenance_date || undefined
    )

    const logId = response.data.log_id

    // Step 2: If there are attachments, upload them to the maintenance log
    if (data.attachments && data.attachments.length > 0) {
      const authData = localStorage.getItem('auth')
      const token = authData ? JSON.parse(authData).token : ''

      for (const file of data.attachments) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('attachment_type', 'maintenance_record')
        formData.append('description', file.name)

        await axios.post(
          `/api/uploads/equipment-logs/${logId}/attachments`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${token}`
            }
          }
        )
      }

      uiStore.showNotification('success', `Maintenance record saved with ${data.attachments.length} attachment(s)`)
    } else {
      uiStore.showNotification('success', 'Maintenance record saved successfully')
    }

    showMaintenanceModal.value = false

    // Refresh equipment data and logs
    await equipmentStore.fetchById(equipmentId.value)
    logSection.value?.loadLogs()
  } catch (error: any) {
    console.error('Failed to save maintenance record:', error)
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to save maintenance record')
  }
}

async function handleChildrenUpdated() {
  // Refresh parent equipment data when children are updated
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
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
        logSection.value?.loadLogs()
        childrenSection.value?.loadChildren()
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
        logSection.value?.loadLogs()
        childrenSection.value?.loadChildren()
        break
    }

    // Reset form
    quickStatusForm.value = { action: '', notes: '', includeChildren: true }
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to change status')
  }
}

// loadLogs() moved to EquipmentLogSection component

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
    const response = await axios.get(`/api/uploads/equipment-logs/${logId}/attachments`, {
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
      `/api/uploads/equipment-logs/${selectedLog.value.id}/attachments`,
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

    await axios.delete(`/api/uploads/log-attachments/${attachmentId}`, {
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

// loadChildren(), openAttachEquipmentModal(), loadAvailableEquipment(), handleAttachEquipment()
// All moved to ChildrenEquipmentSection component

function handleDetachChild(child: Equipment) {
  // Open detach modal for user to select location and status
  detachingChild.value = child
  showDetachModal.value = true
}

function handleDetachModalClose() {
  showDetachModal.value = false
  detachingChild.value = null
}

async function handleDetached() {
  // Refresh equipment data after detachment
  childrenSection.value?.loadChildren()
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  detachingChild.value = null
}

// Watch for route parameter changes (when navigating between equipment pages)
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    // Reset state to avoid showing stale data
    childrenEquipment.value = []

    // Load new equipment data
    await equipmentStore.fetchById(parseInt(newId as string))
    loadQRCode()
    // Note: Logs and Children sections will auto-reload via their own watchers
  }
})

onMounted(async () => {
  await equipmentStore.fetchById(equipmentId.value)
  loadQRCode()
  loadLocations()
  // Note: Logs and Children are loaded automatically by their respective section components
})
</script>

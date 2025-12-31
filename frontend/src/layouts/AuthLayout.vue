<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-sky-50 to-blue-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <h1 class="text-3xl font-bold text-sky-900">
          Marine Equipment Management System
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          QR-Based Asset Tracking & Management
        </p>
      </div>

      <!-- Content -->
      <div class="bg-white shadow-xl rounded-lg p-8">
        <slot />
      </div>

      <!-- Footer -->
      <div class="text-center text-sm text-gray-500">
        <p>&copy; 2025 DG Workshop. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Auth layout for login, 2FA setup pages
</script>

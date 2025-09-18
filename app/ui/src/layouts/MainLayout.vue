<template>
    <div class="w-full flex flex-col min-h-screen bg-gray-100">
      <!-- Header will be provided by the user -->
      <slot name="header" class="w-full"></slot>
      
      <main class="w-full flex-grow container mx-auto py-6 px-4 md:px-6 lg:px-8">
        <slot></slot>
      </main>
      
      <footer class="bg-gray-800 text-white py-4">
        <div class="container mx-auto px-4 text-center">
          <p>&copy; 2025 Voice Analytics </p>
        </div>
      </footer>
    </div>
  </template>
  
  <script setup lang="ts">
  // No additional script is required
  </script>
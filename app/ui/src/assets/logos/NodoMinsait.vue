<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 14 14"
    class="fill-current stroke-current"
    :class="[size, color, customClass]"
  >
    <path
      fill="none"
      stroke="currentColor"
      stroke-width="0.5"
      d="M5 7 7 5 9 7 7 9 5 7 0 7M7 5 7 0M9 7 14 7M7 9 7 14"
    />
  </svg>
</template>


<script setup lang="ts">
defineProps({
  size: {
    type: String,
    default: 'w-6 h-6', // Tamaño por defecto usando clases de Tailwind
  },
  color: {
    type: String,
    default: 'text-black', // Color por defecto usando Tailwind
  },
  customClass: {
    type: String,
    default: '', // Para agregar clases personalizadas adicionales
  },
});
</script>
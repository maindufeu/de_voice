<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 7 7"
    class="fill-current stroke-current"
    v-bind="$props"
    :class="[size, color, customClass]"
    :style="style"
  >
    <path
      fill="none"
      stroke="currentColor"
      stroke-width="0.5"
      d="M0 7 0 3 3 0 7 0"
    />
  </svg>
</template>


<script setup lang="ts">
import { defineProps } from 'vue';
import type { CSSProperties } from 'vue';

import type { PropType } from 'vue';

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
  style: {
    type: [String, Object, Array] as PropType<CSSProperties>,
    default: '',
  },
});
</script>
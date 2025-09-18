<template>
  <!-- Header superior con logos -->
  <header class="text-base-200 body-font bg-base-200 w-full z-50">
    <div class="flex items-center justify-between pt-3 pb-2 pl-3">
      <!-- Contenedor para logo y botón home -->
      <div class="relative flex items-center gap-4 p-3 pl-3">
        <Chaflansofttek class="absolute top-2 left-2 transform -translate-x-2 -translate-y-2 z-10" size="w-3 h-3" color="#004254" />
        <Chaflansofttek class="absolute top-2 right-2 transform translate-x-2 -translate-y-2 rotate-90" size="w-3 h-3" color="#004254" />
        <Chaflansofttek class="absolute bottom-2 left-2 transform -translate-x-2 translate-y-2 -rotate-90" size="w-3 h-3" color="#004254" />
        <Chaflansofttek class="absolute bottom-2 right-2 transform translate-x-2 translate-y-2 rotate-180" size="w-3 h-3" color="#004254" />
        <a href="/">
            <img class="w-[130px]" src="../assets/logos/AF_SOFTTEKGROUP_LOG_RGB_POS.svg" alt="Logo" />
        </a>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import Chaflansofttek from '../assets/logos/Chaflansofttek.vue'
</script>

<style scoped>
.clip-path {
  clip-path: polygon(8px 0, calc(100% - 8px) 0, 100% 8px, 100% calc(100% - 8px), calc(100% - 8px) 100%, 8px 100%, 0 calc(100% - 8px), 0 8px);
}
/* Estilos para la transición de opacidad */
.transition-opacity {
  transition-property: opacity;
}

.duration-300 {
  transition-duration: 300ms;
}
</style>
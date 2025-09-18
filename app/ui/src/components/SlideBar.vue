<template>
  <!-- Contenedor principal con posición relativa para el sidebar -->
  <div class="relative h-full">
    <!-- Botón para mostrar/ocultar sidebar (solo visible cuando el sidebar está cerrado) -->
    <button 
      v-if="!isSidebarOpen"
      @click="toggleSidebar" 
      class="fixed top-20 left-4 z-30 text-softtek-primary p-2 rounded-full transition-all flex items-center justify-center"
    >
      <!-- SVG de flecha derecha -->
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
      </svg>
    </button>
    
    <!-- Sidebar (se desliza desde la izquierda) -->
    <div 
      class="sidebar fixed top-0 left-0 h-full bg-base-200 text-softtek-primary overflow-y-auto transition-all duration-300 shadow-xl z-40"
      :class="{ 'translate-x-0': isSidebarOpen, '-translate-x-full': !isSidebarOpen }"
      style="width: 280px"
    >
      <div class="p-5 pt-16">
        
        <!-- Opciones del sidebar -->
        <div class="sidebar-options space-y-3">
          <!-- Botón para cerrar el sidebar -->
          <div class="sidebar-option flex items-center p-2 rounded-lg hover:bg-gray-300 cursor-pointer" @click="toggleSidebar">
              <span class="mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-fuscia" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              </span>
          </div>
          
          <div class="sidebar-option flex items-center p-2 rounded-lg hover:bg-gray-300 cursor-pointer">
              <span class="mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              </span>
              <span>Nueva conversación</span>
          </div>
          
          <div class="sidebar-option flex items-center p-2 rounded-lg hover:bg-gray-300 cursor-pointer">
              <span class="mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              </span>
              <span>Historial</span>
          </div>
          
          <div class="sidebar-option flex items-center p-2 rounded-lg hover:bg-gray-300 cursor-pointer">
              <span class="mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              </span>
              <span>Configuración</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Chaflansofttek from '../assets/logos/Chaflansofttek.vue'
import { ref } from 'vue';

// Estado del sidebar
const isSidebarOpen = ref(false);

// Definir emits para comunicar con el componente padre
const emit = defineEmits(['toggle-sidebar']);

// Función para mostrar/ocultar el sidebar
const toggleSidebar = () => {
isSidebarOpen.value = !isSidebarOpen.value;
// Emitir evento al componente padre
emit('toggle-sidebar', isSidebarOpen.value);
};
</script>

<style scoped>
.clip-path {
clip-path: polygon(8px 0, calc(100% - 8px) 0, 100% 8px, 100% calc(100% - 8px), calc(100% - 8px) 100%, 8px 100%, 0 calc(100% - 8px), 0 8px);
}

/* Transiciones para el botón */
button {
transition: margin-left 0.3s ease;
}

/* Estilos para la transición de opacidad */
.transition-opacity {
transition-property: opacity;
}

.duration-300 {
transition-duration: 300ms;
}
</style>
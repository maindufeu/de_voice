<template>
  <div class="app-container h-screen flex flex-col overflow-hidden">
    <HeaderComponent/>
    <div class="flex flex-1 overflow-hidden">
      <Sidebar />
      <div class="flex-1 overflow-auto thin-scrollbar">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import HeaderComponent from './components/HeaderComponent.vue';
import Sidebar from './components/SlideBar.vue';
</script>

<style>
/* Variables globales de color */
:root {
  --softtek-primary: #004254;
  --softtek-primary-dark: #002532;
  --fuscia: #ff1a8a;
  --base-200: #F5F5F5;
}

/* Estilo personalizado para la barra de desplazamiento - aplicado globalmente */
.thin-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.thin-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-base-200;
  border-radius: 2px;
}

.thin-scrollbar::-webkit-scrollbar-track {
  background-color: transparent;
}

/* Para Firefox */
.thin-scrollbar {
  scrollbar-width: thin;
  /* scrollbar-color: rgba(38, 20, 20, 0.5) transparent; */ 
  @apply bg-softtek-primary-dark;
}

body {
  margin: 0;
  overflow: hidden; /* Evita scroll en el body */
  height: 100vh;
}

#app, .app-container {
  height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
}
</style>
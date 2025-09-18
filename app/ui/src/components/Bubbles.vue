<template>
  <!-- Suggestion bubbles container corregido para no causar overflow -->
  <div class="suggestion-container mt-10 w-full px-0 overflow-hidden">
    <!-- First row - horizontal scroll -->
    <div class="suggestion-row-wrapper mb-6 relative w-full overflow-hidden">
      <div class="suggestion-row flex animate-scroll-left pl-0">
        <button 
          v-for="(suggestion, index) in suggestionsRow1" 
          :key="'row1-'+index" 
          class="suggestion-bubble mx-3 px-5 py-3 bg-softtek-primary backdrop-blur-sm text-white text-lg font-medium rounded-full hover:softtek-primary transition-all whitespace-nowrap"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion }}
        </button>
        <!-- Duplicated for seamless looping -->
        <button 
          v-for="(suggestion, index) in suggestionsRow1" 
          :key="'row1-dup-'+index" 
          class="suggestion-bubble mx-3 px-5 py-3 bg-softtek-primary backdrop-blur-sm text-white text-lg font-medium rounded-full hover:softtek-primary transition-all whitespace-nowrap"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>
    
    <!-- Second row - horizontal scroll reverse -->
    <div class="suggestion-row-wrapper mb-6 relative w-full overflow-hidden">
      <div class="suggestion-row flex animate-scroll-right pr-0">
        <button 
          v-for="(suggestion, index) in suggestionsRow2" 
          :key="'row2-'+index" 
          class="suggestion-bubble mx-3 px-5 py-3 bg-softtek-primary backdrop-blur-sm text-white text-lg font-medium rounded-full hover:softtek-primary transition-all whitespace-nowrap"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion }}
        </button>
        <!-- Duplicated for seamless looping -->
        <button 
          v-for="(suggestion, index) in suggestionsRow2" 
          :key="'row2-dup-'+index" 
          class="suggestion-bubble mx-3 px-5 py-3 bg-softtek-primary backdrop-blur-sm text-white text-lg font-medium rounded-full hover:softtek-primary transition-all whitespace-nowrap"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import ImageDisplay from './ImageDisplay.vue'; // Assuming you have this component

export default {
name: 'Bubbles',
components: {
  ImageDisplay
},
emits: ['select-suggestion'],
setup(props, { emit }) {
  // Suggestion examples - you can replace these with your own
  const suggestionsRow1 = ref([
    "¿Cuáles son los productos y categorías más rentables?", 
    "Agrupa los pagos mensuales por la antiguedad del cliente (tenure) en meses, calcula el promedio. Realiza un forecast para los próximos 30 meses",
    "¿Qué segmentos de clientes tienen mayor valor de vida útil?"
  ]);

  const suggestionsRow2 = ref([
    "¿Cuál es la estacionalidad de las ventas por categoría?", 
    "¿Qué combinaciones de servicios tienen mayor retención?",
    "¿Cómo influyen los tipos de contrato en la retención?",
    "¿Cómo varía el comportamiento de compra por ubicación geográfica?"
  ]);

  // Function to handle suggestion selection with improved UX
  const selectSuggestion = (suggestion) => {
    emit('select-suggestion', suggestion);
  };

  return {
    suggestionsRow1,
    suggestionsRow2,
    selectSuggestion
  };
}
};
</script>

<style scoped>
/* Animaciones solo con movimiento horizontal */
@keyframes scrollLeft {
0% {
  transform: translateX(0);
}
100% {
  transform: translateX(-50%);
}
}

@keyframes scrollRight {
0% {
  transform: translateX(-50%);
}
100% {
  transform: translateX(0);
}
}

.animate-scroll-left {
animation: scrollLeft 30s linear infinite;
}

.animate-scroll-right {
animation: scrollRight 30s linear infinite;
}

/* Estilos corregidos para las burbujas - evitando overflow */
.suggestion-container {
max-width: 100%;
position: relative;
overflow: hidden;
}

.suggestion-row-wrapper {
max-width: 100%;
overflow: hidden;
}

/* Estilos para las burbujas */
.suggestion-bubble {
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
border: 1px solid rgba(255, 255, 255, 0.3);
transition: all 0.2s ease-in-out;
}

.suggestion-bubble:hover {
transform: translateY(-2px);
box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}
</style>
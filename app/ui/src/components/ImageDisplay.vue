<template>
  <div class="image-display">
    <!-- Loading indicator -->
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <span>Cargando imagen...</span>
    </div>
    
    <!-- Image with controls container -->
    <div v-else-if="!error && imageSource" class="image-container relative group">
      <!-- Main image -->
      <img 
        :src="imageSource" 
        :alt="altText"
        @load="handleImageLoaded"
        @error="handleImageError"
        class="rounded-lg max-w-full"
      />
      
      <!-- Image toolbar - appears on hover -->
      <div class="image-toolbar opacity-0 group-hover:opacity-100 transition-opacity duration-200 absolute top-2 right-2 bg-gray-800 bg-opacity-75 rounded-lg p-1.5 flex space-x-2">
        <!-- Save button -->
        <button 
          @click="saveImage" 
          class="toolbar-button text-white hover:text-blue-300 focus:outline-none"
          title="Guardar imagen"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>
        
        <!-- Copy button -->
        <button 
          @click="copyImage" 
          class="toolbar-button text-white hover:text-blue-300 focus:outline-none"
          title="Copiar imagen"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
          </svg>
        </button>
      </div>
      
      <!-- Feedback toast for copy operation -->
      <div v-if="showCopyFeedback" class="copy-feedback absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-3 py-1.5 rounded-full text-sm">
        {{ copyFeedbackText }}
      </div>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="error-message">
      <p>Error al cargar la imagen: {{ error }}</p>
      <button 
        @click="showDebugInfo = !showDebugInfo" 
        class="text-xs text-blue-600 hover:underline mt-1"
      >
        {{ showDebugInfo ? 'Ocultar detalles' : 'Mostrar detalles' }}
      </button>
      <pre v-if="showDebugInfo" class="mt-2 p-2 bg-gray-100 text-xs overflow-x-auto rounded">{{ debugInfo }}</pre>
    </div>
    
    <!-- Data display and controls (when data prop is provided) -->
    <div v-if="dataContent" class="data-display mt-4">
      <div class="data-controls flex justify-between items-center mb-2">
        <h3 class="text-sm font-medium text-gray-700">Datos asociados</h3>
        
        <!-- Data size warning for very large datasets -->
        <div v-if="isLargeDataset" class="text-amber-600 text-xs flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Conjunto de datos grande ({{ formatDataSize(dataSize) }})
        </div>
        
        <!-- Download as CSV button -->
        <button 
          @click="downloadDataAsCsv" 
          class="download-button bg-blue-600 hover:bg-blue-700 text-white text-xs rounded py-1 px-3 flex items-center transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Descargar CSV
        </button>
      </div>
      
      <!-- For large datasets, show download only option -->
      <div v-if="isLargeDataset" class="large-data-notice bg-gray-100 rounded-lg p-4 text-center">
        <p class="text-gray-800 mb-3">Este conjunto de datos es demasiado grande para visualizarse directamente.</p>
        <button 
          @click="downloadDataAsCsv" 
          class="download-button-large bg-blue-600 hover:bg-blue-700 text-white rounded-md py-2 px-4 flex items-center mx-auto transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Descargar datos ({{ formatDataSize(dataSize) }})
        </button>
      </div>
      
      <!-- Data table with scrollbar for smaller datasets -->
      <div v-else class="data-table-container max-h-80 overflow-y-auto border border-gray-200 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200 text-sm">
          <thead class="bg-gray-50 sticky top-0">
            <tr>
              <th v-for="(column, index) in tableColumns" :key="index" 
                  class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {{ column }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(row, rowIndex) in tableRows" :key="rowIndex" class="hover:bg-gray-50">
              <td v-for="(column, colIndex) in tableColumns" :key="colIndex" 
                  class="px-3 py-2 whitespace-nowrap text-gray-600">
                {{ formatCellValue(row[column]) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, onMounted, computed, watch } from 'vue';

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: 'Imagen de análisis'
  },
  data: {
    type: [Object, Array],
    default: null
  }
});

// State
const loading = ref(true);
const error = ref<string | null>(null);
const imageSource = ref<string | null>(null);
const altText = ref(props.alt || 'Imagen de análisis');
const debugInfo = ref('');
const showDebugInfo = ref(false);
const showCopyFeedback = ref(false);
const copyFeedbackText = ref('');
const dataContent = ref(null);
const dataSize = ref(0);

// Track attempts to fix the image
const attemptCount = ref(0);
const MAX_ATTEMPTS = 3;

// Computed properties
const isLargeDataset = computed(() => {
  return dataSize.value > 10 * 1024 * 1024; // 10MB in bytes
});

const tableColumns = computed(() => {
  if (!dataContent.value) return [];
  
  // Handle array of objects
  if (Array.isArray(dataContent.value) && dataContent.value.length > 0) {
    // Get keys from first object
    return Object.keys(dataContent.value[0] || {});
  }
  
  // Handle single object
  if (typeof dataContent.value === 'object' && dataContent.value !== null) {
    return Object.keys(dataContent.value);
  }
  
  return [];
});

const tableRows = computed(() => {
  if (!dataContent.value) return [];
  
  // Handle array of objects
  if (Array.isArray(dataContent.value)) {
    return dataContent.value;
  }
  
  // Handle single object
  if (typeof dataContent.value === 'object' && dataContent.value !== null) {
    return [dataContent.value];
  }
  
  return [];
});

// Image loading functions
const isBase64 = (str: string): boolean => {
  try {
    // Check if it's a valid base64 string
    return btoa(atob(str)) === str;
  } catch (e) {
    return false;
  }
};

const handleImageLoaded = () => {
  loading.value = false;
  error.value = null;
  console.log('Image loaded successfully');
};

const handleImageError = (e: Event) => {
  console.error('Error loading image:', e);
  
  // Try another fix attempt if we haven't reached the maximum
  if (attemptCount.value < MAX_ATTEMPTS) {
    attemptCount.value++;
    console.log(`Image load error, trying fix attempt ${attemptCount.value}`);
    
    // Try different formats
    tryAlternativeFormat();
  } else {
    // After maximum attempts, show error
    loading.value = false;
    error.value = 'No se pudo cargar la imagen después de varios intentos';
    
    // Add debug info
    debugInfo.value = `Source preview: ${props.src.substring(0, 100)}...\nAttempts: ${attemptCount.value}\nImage type: ${typeof props.src}`;
  }
};

const tryAlternativeFormat = () => {
  const srcStr = props.src;
  
  // Try different MIME types
  if (attemptCount.value === 1) {
    // First attempt: try as PNG
    imageSource.value = srcStr.startsWith('data:') 
      ? srcStr.replace(/^data:[^;]+;base64,/, 'data:image/png;base64,')
      : `data:image/png;base64,${srcStr}`;
  } else if (attemptCount.value === 2) {
    // Second attempt: try as JPEG
    imageSource.value = srcStr.startsWith('data:') 
      ? srcStr.replace(/^data:[^;]+;base64,/, 'data:image/jpeg;base64,')
      : `data:image/jpeg;base64,${srcStr}`;
  } else {
    // Third attempt: try directly with the string
    // This sometimes works when the other methods fail
    imageSource.value = srcStr;
  }
  
  console.log(`Attempt ${attemptCount.value}: Using format: ${imageSource.value?.substring(0, 30)}...`);
};

// Image action functions
const saveImage = () => {
  if (!imageSource.value) return;
  
  try {
    // Create a temporary link element
    const link = document.createElement('a');
    link.href = imageSource.value;
    link.download = `imagen_${new Date().getTime()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showFeedback('Imagen guardada correctamente');
  } catch (e) {
    console.error('Error saving image:', e);
    showFeedback('Error al guardar la imagen', true);
  }
};

const copyImage = async () => {
  if (!imageSource.value) return;
  
  try {
    // Create a temporary image element
    const img = new Image();
    img.src = imageSource.value;
    
    // Wait for image to load
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
    });
    
    // Create a canvas and draw the image
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    
    // Convert to blob and copy to clipboard
    canvas.toBlob(async (blob) => {
      try {
        if (blob) {
          const item = new ClipboardItem({ 'image/png': blob });
          await navigator.clipboard.write([item]);
          showFeedback('Imagen copiada al portapapeles');
        }
      } catch (e) {
        console.error('Error copying to clipboard:', e);
        showFeedback('Error al copiar la imagen', true);
      }
    });
  } catch (e) {
    console.error('Error preparing image for copy:', e);
    showFeedback('Error al copiar la imagen', true);
  }
};

const showFeedback = (message: string, isError = false) => {
  copyFeedbackText.value = message;
  showCopyFeedback.value = true;
  
  setTimeout(() => {
    showCopyFeedback.value = false;
  }, 2000);
};

// Data handling functions
const formatCellValue = (value: any): string => {
  if (value === null || value === undefined) return '-';
  
  // Format numbers with 2 decimal places
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toString() : value.toFixed(2);
  }
  
  // Format dates
  if (value instanceof Date) {
    return value.toLocaleDateString();
  }
  
  // Format objects/arrays
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  
  return String(value);
};

const formatDataSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const estimateDataSize = (data: any): number => {
  try {
    // Convert to JSON and measure
    const jsonString = JSON.stringify(data);
    return new Blob([jsonString]).size;
  } catch (e) {
    console.error('Error estimating data size:', e);
    return 0;
  }
};

const downloadDataAsCsv = () => {
  if (!dataContent.value) return;
  
  try {
    let csvContent = '';
    
    // Add headers
    csvContent += tableColumns.value.join(',') + '\n';
    
    // Add rows
    tableRows.value.forEach(row => {
      const rowValues = tableColumns.value.map(col => {
        let value = row[col];
        
        // Handle values with commas by wrapping in quotes
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        
        // Handle null/undefined
        if (value === null || value === undefined) {
          return '';
        }
        
        // Convert objects to JSON string
        if (typeof value === 'object') {
          return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
        }
        
        return value;
      });
      
      csvContent += rowValues.join(',') + '\n';
    });
    
    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `data_export_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showFeedback('Datos descargados correctamente');
  } catch (e) {
    console.error('Error downloading data as CSV:', e);
    showFeedback('Error al descargar los datos', true);
  }
};

// Image initialization
onMounted(() => {
  console.log('ImageDisplay mounted, processing source data');
  
  // Check if source is a valid string
  if (typeof props.src !== 'string') {
    error.value = 'Tipo de imagen no válido';
    loading.value = false;
    debugInfo.value = `Invalid source type: ${typeof props.src}`;
    return;
  }
  
  const srcStr = props.src;
  
  // Handle empty or too short src
  if (!srcStr || srcStr.length < 10) {
    error.value = 'Datos de imagen insuficientes';
    loading.value = false;
    debugInfo.value = `Source too short: ${srcStr}`;
    return;
  }
  
  try {
    // Log data for debugging
    console.log('Image source type:', typeof srcStr);
    console.log('Image source length:', srcStr.length);
    console.log('Image source preview:', srcStr.substring(0, 30) + '...');
    
    // Check if it's a proper data URL
    if (srcStr.startsWith('data:image/')) {
      // Valid format, use as is
      imageSource.value = srcStr;
      console.log('Using image source as is (valid data URL)');
      loading.value = false;
    } 
    // Check if it's a base64 string without prefix
    else if (srcStr.match(/^[A-Za-z0-9+/=]+$/) && srcStr.length > 100) {
      // Looks like a base64 string without the data URL prefix
      imageSource.value = `data:image/png;base64,${srcStr}`;
      console.log('Applied data URL prefix to base64 string');
    }
    // Check if it starts with a common base64 image pattern
    else if (srcStr.startsWith('iVBOR')) {
      // PNG signature detected
      imageSource.value = `data:image/png;base64,${srcStr}`;
      console.log('Detected PNG signature, applied proper prefix');
    }
    else if (srcStr.startsWith('/9j/')) {
      // JPEG signature detected
      imageSource.value = `data:image/jpeg;base64,${srcStr}`;
      console.log('Detected JPEG signature, applied proper prefix');
    }
    // Check for truncated or improperly formatted data URL
    else if (srcStr.includes('base64,')) {
      const base64Index = srcStr.indexOf('base64,');
      if (base64Index >= 0) {
        // Extract the base64 part and create a proper data URL
        const base64Data = srcStr.substring(base64Index + 7);
        imageSource.value = `data:image/png;base64,${base64Data}`;
        console.log('Extracted base64 data from malformed URL');
      }
    }
    // Fallback for other cases
    else {
      // Try as PNG by default
      imageSource.value = `data:image/png;base64,${srcStr}`;
      console.log('Fallback: treating source as base64 PNG data');
    }
    
    // Process data if provided
    if (props.data) {
      dataContent.value = props.data;
      dataSize.value = estimateDataSize(props.data);
      console.log(`Data provided with estimated size: ${formatDataSize(dataSize.value)}`);
    }
  } catch (e) {
    console.error('Error processing image source:', e);
    error.value = 'Error al procesar los datos de la imagen';
    loading.value = false;
    debugInfo.value = `Processing error: ${e instanceof Error ? e.message : String(e)}`;
  }
});

// Watch for prop changes
watch(() => props.data, (newData) => {
  if (newData) {
    dataContent.value = newData;
    dataSize.value = estimateDataSize(newData);
    console.log(`Data updated with estimated size: ${formatDataSize(dataSize.value)}`);
  } else {
    dataContent.value = null;
    dataSize.value = 0;
  }
});
</script>

<style scoped>
.image-display {
  margin: 0.5rem 0;
  position: relative;
}

.image-container {
  position: relative;
  display: inline-block;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: #f3f4f6;
  border-radius: 0.5rem;
  color: #6b7280;
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #d1d5db;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  padding: 0.5rem;
  background-color: #fee2e2;
  border-radius: 0.375rem;
}

.copy-feedback {
  transition: opacity 0.3s ease-in-out;
  opacity: 1;
}

.data-table-container {
  /* Custom scrollbar styling */
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.data-table-container::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.data-table-container::-webkit-scrollbar-track {
  background: transparent;
}

.data-table-container::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.large-data-notice {
  border: 1px dashed #cbd5e1;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
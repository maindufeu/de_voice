<template>
  <div class="chat-main-container relative flex flex-col h-[calc(100vh-8rem)] justify-end">
    <!-- Message container with scrollable area -->
    <div 
      ref="chatContainerRef"
      class="w-4/5 mx-auto h-full overflow-y-auto thin-scrollbar bg-base-200 rounded-lg shadow-lg p-4"
    >
      <!-- Messages with SVG icons -->
      <div 
        v-for="(message, index) in filteredMessages" 
        :key="index" 
        class="flex items-start mb-3"
      >
        <!-- softtek SVG -->
        <div v-if="!message.isUser" class="flex-shrink-0 mr-2 mt-2">
          <img src="../assets/logos/AF_SOFTTEK_SIM_POS.png" class="h-8 w-8 text-softtek-primary" />
        </div>
        <!-- Message Container -->
        <div 
          :class="[
            'relative message p-3 rounded-lg max-w-[80%]',
            message.isUser 
              ? 'user-message ml-auto bg-base-200 text-softtek-primary-dark' 
              : 'assistant-message mr-auto bg-base-200 text-softtek-primary shadow-md'
          ]"
        >
          <Chaflansofttek v-if="!message.isUser" class="absolute top-2 left-2 transform -translate-x-2 -translate-y-2 z-10" size="w-3 h-3" color="#004254" />
          <Nodosofttek v-if="message.isUser" class="absolute top-2 left-2 transform -translate-x-2 -translate-y-2 z-10" size="w-3 h-3" color="#004254" />
          <Chaflansofttek v-if="!message.isUser" class="absolute top-2 right-2 transform translate-x-2 -translate-y-2 rotate-90" size="w-3 h-3" color="#004254" />
          <Nodosofttek v-if="message.isUser" class="absolute top-2 right-2 transform translate-x-2 -translate-y-2 rotate-90" size="w-3 h-3" color="#004254" />
          <Chaflansofttek v-if="!message.isUser" class="absolute bottom-2 left-2 transform -translate-x-2 translate-y-2 -rotate-90" size="w-3 h-3" color="#004254" />
          <Nodosofttek v-if="message.isUser" class="absolute bottom-2 left-2 transform -translate-x-2 translate-y-2 -rotate-90" size="w-3 h-3" color="#004254" />
          <Chaflansofttek v-if="!message.isUser" class="absolute bottom-2 right-2 transform translate-x-2 translate-y-2 rotate-180" size="w-3 h-3" color="#004254" />
          <Nodosofttek v-if="message.isUser" class="absolute bottom-2 right-2 transform translate-x-2 translate-y-2 rotate-180" size="w-3 h-3" color="#004254" />
          
          <!-- Error state -->
          <div v-if="message.error" class="message-error mb-2 text-white-600 text-sm">
            <div class="flex items-center">
              <span class="material-icons text-white-600 mr-1 text-sm">error</span>
              {{ message.text || 'Error en la respuesta' }}
            </div>
            <div class="text-xs mt-1 text-white-500">{{ message.error }}</div>
          </div>
          
          <!-- Regular text content (not displayed if error) -->
          <div v-else-if="message.text && message.messageType !== 'backend_process'" class="message-text">
            {{ message.text }}
          </div>

          <!-- Improved Planning Content with Markdown -->
          <div v-if="message.messageType === 'backend_process' && message.processType === 'planning'" class="planning-content backdrop-blur-md bg-white/10 p-3 rounded-lg border border-fuscia/20">
            <!-- Markdown rendering of the plan -->
            <div class="plan-markdown prose prose-sm max-w-none my-2 plan-content">
              <MarkdownContent :content="message.text" />
            </div>
            
            <!-- Planning Details Accordion (if planningData is available) -->
            <div v-if="message.planningData" class="planning-details mt-4">
              <button 
                @click="togglePlanningDetails(index)" 
                class="process-toggle-button flex items-center justify-between w-full text-left px-3 py-2 rounded-md backdrop-blur-md bg-white/20 border border-gray-200 shadow-sm transition-colors hover:bg-white/30"
              >
                <span class="text-softtek-primary font-medium">
                  Ver detalles del plan
                </span>
                <svg 
                  class="h-5 w-5 text-softtek-primary transition-transform" 
                  :class="{ 'transform rotate-180': isPlanningDetailsVisible(index) }"
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <div 
                v-show="isPlanningDetailsVisible(index)"
                class="planning-details-content mt-2 transition-all duration-300 overflow-hidden bg-white/10 backdrop-blur-sm rounded-md p-4"
                :class="{ 'max-h-0 opacity-0': !isPlanningDetailsVisible(index), 'max-h-[500px] opacity-100': isPlanningDetailsVisible(index) }"
              >
                <!-- Required datasets -->
                <div v-if="message.planningData.required_datasets && message.planningData.required_datasets.length > 0" class="mb-3">
                  <h3 class="text-sm font-bold text-softtek-primary mb-1">Datasets requeridos:</h3>
                  <ul class="list-disc list-inside text-sm">
                    <li v-for="(dataset, idx) in message.planningData.required_datasets" :key="'dataset-'+idx" class="ml-2">
                      {{ dataset }}
                    </li>
                  </ul>
                </div>
                
                <!-- Required functions -->
                <div v-if="message.planningData.required_functions && message.planningData.required_functions.length > 0" class="mb-3">
                  <h3 class="text-sm font-bold text-softtek-primary mb-1">Funciones requeridas:</h3>
                  <ul class="list-disc list-inside text-sm">
                    <li v-for="(func, idx) in message.planningData.required_functions" :key="'func-'+idx" class="ml-2">
                      {{ func }}
                    </li>
                  </ul>
                </div>
                
                <!-- Expected outputs -->
                <div v-if="message.planningData.expected_outputs" class="mb-3">
                  <h3 class="text-sm font-bold text-softtek-primary mb-1">Resultados esperados:</h3>
                  
                  <!-- Data output -->
                  <div v-if="message.planningData.expected_outputs.data" class="mb-2">
                    <p class="text-sm font-medium text-softtek-primary">Datos:</p>
                    <p class="text-sm ml-2">{{ message.planningData.expected_outputs.data }}</p>
                  </div>
                  
                  <!-- Visualizations -->
                  <div v-if="message.planningData.expected_outputs.visualizations && message.planningData.expected_outputs.visualizations.length > 0" class="mb-2">
                    <p class="text-sm font-medium text-softtek-primary">Visualizaciones:</p>
                    <ul class="list-disc list-inside text-sm">
                      <li v-for="(viz, idx) in message.planningData.expected_outputs.visualizations" :key="'viz-'+idx" class="ml-2">
                        {{ viz }}
                      </li>
                    </ul>
                  </div>
                  
                  <!-- Insights -->
                  <div v-if="message.planningData.expected_outputs.insights && message.planningData.expected_outputs.insights.length > 0" class="mb-2">
                    <p class="text-sm font-medium text-softtek-primary">Insights:</p>
                    <ul class="list-disc list-inside text-sm">
                      <li v-for="(insight, idx) in message.planningData.expected_outputs.insights" :key="'insight-'+idx" class="ml-2">
                        {{ insight }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Backend Process Content for Code Generation -->
          <div v-if="message.messageType === 'backend_process' && message.processType === 'code_generation'" class="backend-process-container mt-2 mb-2">
            <div class="backend-process-header">
              <button 
                @click="toggleBackendProcess(index)" 
                class="process-toggle-button flex items-center justify-between w-full text-left px-3 py-2 rounded-md transition-colors bg-base-200 hover:bg-base-200/80 border border-gray-200 shadow-sm"
                :class="[isBackendProcessVisible(index) ? '' : 'animate-pulse-subtle']"
              >
                <span class="text-softtek-primary font-medium">
                  Ver código generado
                </span>
                <svg 
                  class="h-5 w-5 text-softtek-primary transition-transform" 
                  :class="{ 'transform rotate-180': isBackendProcessVisible(index) }"
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            <div 
              v-show="isBackendProcessVisible(index)"
              class="process-content mt-2 transition-all duration-300 overflow-hidden scroll-bottom"
              :class="{ 'max-h-0 opacity-0': !isBackendProcessVisible(index), 'max-h-[500px] opacity-100': isBackendProcessVisible(index) }"
            >
              <pre 
                class="backend-process-content p-3 rounded-md overflow-x-auto text-sm font-mono bg-gray-900 text-base-200 border-l-4 border-softtek-primary"
              >{{ message.text }}</pre>
            </div>
          </div>

          <!-- Images -->
          <div v-if="message.images && message.images.length > 0" class="message-images mt-3">
            <div v-for="(image, imgIndex) in message.images" :key="imgIndex" class="mb-2">
              <p class="text-xs text-gray-500 mb-1">Imagen {{imgIndex + 1}}</p>
              <ImageDisplay 
                :src="image" 
                :alt="`Imagen ${imgIndex + 1}`"
                class="max-w-full" 
              />
            </div>
          </div>

          <!-- Data results -->
          <div v-if="message.data" class="message-data mt-3">
            <details>
              <summary class="cursor-pointer text-blue-600 hover:text-blue-800">
                Ver datos ({{ Array.isArray(message.data) ? message.data.length + ' registros' : 'objeto' }})
              </summary>
              <div class="bg-gray-100 p-3 rounded mt-2 overflow-x-auto">
                <!-- Table for array data -->
                <table v-if="Array.isArray(message.data) && message.data.length > 0" class="w-full text-sm text-left">
                  <thead class="text-xs uppercase bg-gray-200">
                    <tr>
                      <th v-for="(_, key) in message.data[0]" :key="key" class="px-2 py-2 text-black font-medium">
                        {{ key }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in message.data" :key="index" class="border-b">
                      <td v-for="(value, key) in item" :key="key" class="px-2 py-2 text-gray-700">
                        {{ typeof value === 'number' ? formatNumber(value) : value }}
                      </td>
                    </tr>
                  </tbody>
                </table>
                <!-- Fallback for object data -->
                <pre v-else class="text-xs">{{ formatData(message.data) }}</pre>
              </div>
            </details>
          </div>
          
          <!-- Loading indicator for assets being loaded -->
          <div v-if="message.assetsLoading" class="loading-assets mt-3">
            <div class="loading-indicator mb-2">
              <div class="flex items-center">
                <div class="spinner mr-2"></div>
                <span class="text-sm">Cargando recursos...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- User SVG (right side) -->
        <div v-if="message.isUser" class="flex-shrink-0 ml-2 mt-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
      </div>
      
      <div v-if="isTyping" class="typing-indicator mr-auto p-3 bg-gray-200 rounded-lg inline-block">
        <div class="dot-flashing"></div>
      </div>
    </div>
    
    <!-- Fixed Bottom Progress Bar (separate from scrollable area) -->
    <div 
      v-show="progressState.visible" 
      class="progress-container fixed bottom-24 left-1/2 transform -translate-x-1/2 z-50 bg-white rounded-lg shadow-lg p-4 w-1/2 max-w-2xl transition-all duration-300"
      :class="{ 'translate-y-10 opacity-0': !progressState.visible, 'translate-y-0 opacity-100': progressState.visible }"
    >
      <div class="flex flex-col justify-end">
        <div class="flex justify-between items-center mb-2">
          <h3 class="text-lg font-medium text-gray-900">
            {{ progressState.message || 'Procesando...' }}
          </h3>
          <span class="text-sm font-medium text-gray-700">{{ progressState.progress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            class="bg-emerald-500 h-2.5 rounded-full transition-all duration-300 ease-out" 
            :style="{ width: `${progressState.progress}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import ImageDisplay from './ImageDisplay.vue';
import Chaflansofttek from '../assets/logos/Chaflansofttek.vue';
import Nodosofttek from '../assets/logos/Nodosofttek.vue';
import MarkdownContent from './MarkdownContent.vue'; // Nuevo componente para markdown

export default {
  name: 'ChatInterface',
  components: {
    ImageDisplay,
    Chaflansofttek,
    Nodosofttek,
    MarkdownContent,
  },
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    isTyping: {
      type: Boolean,
      default: false
    },
    filter: {
      type: String,
      default: ''
    },
    progressState: {
      type: Object,
      default: () => ({ visible: false, progress: 0, message: '' })
    }
  },
  emits: ['suggestion-selected'],
  setup(props, { emit }) {
    const chatContainerRef = ref(null);
    const visibleBackendProcesses = ref({});
    const visiblePlanningDetails = ref({});
    const userHasScrolled = ref(false);
    const isScrolling = ref(false);
    const lastScrollHeight = ref(0);
    const lastMessagesLength = ref(0);
    
    // Toggle backend process visibility
    const toggleBackendProcess = (index) => {
      visibleBackendProcesses.value[index] = !visibleBackendProcesses.value[index];
    };

    // Check if backend process is visible
    const isBackendProcessVisible = (index) => {
      return !!visibleBackendProcesses.value[index];
    };
    
    // Toggle planning details visibility
    const togglePlanningDetails = (index) => {
      visiblePlanningDetails.value[index] = !visiblePlanningDetails.value[index];
    };
    
    // Check if planning details are visible
    const isPlanningDetailsVisible = (index) => {
      return !!visiblePlanningDetails.value[index];
    };

    // Filtered messages based on search/filter
    const filteredMessages = computed(() => {
      if (!props.filter) return props.messages;
      return props.messages.filter(message => 
        message.text && message.text.toLowerCase().includes(props.filter.toLowerCase())
      );
    });

    // Format number for display
    const formatNumber = (num) => {
      // Check if the number is an integer
      if (Number.isInteger(num)) {
        return num.toString();
      }
      // Format decimal numbers to 2 decimal places
      return num.toFixed(2);
    };

    // Format data for display
    const formatData = (data) => {
      return JSON.stringify(data, null, 2);
    };
    
    // Check if we should auto-scroll based on user behavior
    const shouldAutoScroll = () => {
      if (!chatContainerRef.value) return true;
      
      // Always scroll if the user is at the bottom
      if (!userHasScrolled.value) return true;
      
      const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.value;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
      
      // Auto-scroll if user is close to bottom (within 100px)
      return distanceFromBottom < 100;
    };
    
    // Enhanced scroll to bottom function
    const scrollToBottom = (force = false) => {
      if (!chatContainerRef.value) return;
      
      // Only auto-scroll if appropriate or if forced
      if (force || shouldAutoScroll()) {
        isScrolling.value = true;
        
        // Use a small timeout to ensure DOM is fully updated
        setTimeout(() => {
          // Use requestAnimationFrame for smoother scrolling
          requestAnimationFrame(() => {
            if (chatContainerRef.value) {
              chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
              lastScrollHeight.value = chatContainerRef.value.scrollHeight;
              
              // Reset scroll flags after a short delay
              setTimeout(() => {
                isScrolling.value = false;
                if (force) userHasScrolled.value = false;
              }, 100);
            }
          });
        }, 10);
      }
    };
    
    // Check if user has scrolled up
    const handleScroll = () => {
      if (!chatContainerRef.value || isScrolling.value) return;
      
      const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.value;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50; // 50px threshold
      
      // Only update the userHasScrolled flag if we're not already at the bottom
      if (!isAtBottom) {
        userHasScrolled.value = true;
      } else {
        userHasScrolled.value = false;
      }
    };
    
    // Check for content changes that would affect scrolling
    const checkContentChanges = () => {
      if (!chatContainerRef.value) return;
      
      const currentScrollHeight = chatContainerRef.value.scrollHeight;
      
      // If scroll height has changed significantly, it likely means content has been added/updated
      if (currentScrollHeight > lastScrollHeight.value + 10) {
        scrollToBottom(false); // Try to scroll but respect user position
      }
      
      lastScrollHeight.value = currentScrollHeight;
    };
    
    // Watch for changes that should trigger scrolling
    watch(
      [
        () => props.messages.length,
        () => filteredMessages.value.length,
        () => props.isTyping
      ],
      ([newMessagesLength], [oldMessagesLength]) => {
        // Check if new messages were added
        const messagesAdded = newMessagesLength > lastMessagesLength.value;
        lastMessagesLength.value = newMessagesLength;
        
        // Use nextTick to ensure DOM is updated
        nextTick(() => {
          // Force scroll if new messages were added
          scrollToBottom(messagesAdded);
        });
      }
    );
    
    // Watch for changes in progress state
    watch(
      () => props.progressState.visible,
      (isVisible) => {
        if (isVisible) {
          // When progress appears, scroll to see it
          nextTick(() => {
            scrollToBottom(false);
          });
        }
      }
    );
    
    // Create a deep watcher for the messages content to detect updates
    watch(
      () => JSON.stringify(props.messages),
      () => {
        nextTick(() => {
          checkContentChanges();
        });
      }
    );
    
    // Watch for visibility changes in backend processes and planning details
    watch(
      [() => visibleBackendProcesses.value, () => visiblePlanningDetails.value],
      () => {
        nextTick(() => {
          checkContentChanges();
        });
      },
      { deep: true }
    );
    
    // Setup periodic content change detection (for updates that watchers might miss)
    let contentChangeInterval;
    
    // Set up and clean up event listeners and intervals
    onMounted(() => {
      if (chatContainerRef.value) {
        chatContainerRef.value.addEventListener('scroll', handleScroll);
        
        // Initial scroll to bottom
        scrollToBottom(true);
        lastScrollHeight.value = chatContainerRef.value.scrollHeight || 0;
        lastMessagesLength.value = props.messages.length;
      }
      
      // Setup interval to check for content changes every 1s
      contentChangeInterval = setInterval(checkContentChanges, 1000);
      
      // Debug progress state
      console.log("Initial progress state:", props.progressState);
    });
    
    onUnmounted(() => {
      if (chatContainerRef.value) {
        chatContainerRef.value.removeEventListener('scroll', handleScroll);
      }
      
      // Clear the content change interval
      if (contentChangeInterval) {
        clearInterval(contentChangeInterval);
      }
    });

    return {
      chatContainerRef,
      filteredMessages,
      formatNumber,
      formatData,
      toggleBackendProcess,
      isBackendProcessVisible,
      togglePlanningDetails,
      isPlanningDetailsVisible,
      scrollToBottom
    };
  }
};
</script>

<style scoped>
/* Root variables ya están definidas en App.vue de forma global */

.chat-main-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* Styling para el contenido del plan con efectos de blurry */
.planning-content {
  position: relative;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
}

.plan-content {
  line-height: 1.6;
  color: var(--softtek-primary);
}

/* Typing indicator animation */
.dot-flashing {
  position: relative;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #444;
  animation: dot-flashing 1s infinite linear alternate;
  animation-delay: 0.5s;
}

.dot-flashing::before, .dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
}

.dot-flashing::before {
  left: -15px;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #444;
  animation: dot-flashing 1s infinite alternate;
  animation-delay: 0s;
}

.dot-flashing::after {
  left: 15px;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #444;
  animation: dot-flashing 1s infinite alternate;
  animation-delay: 1s;
}

@keyframes dot-flashing {
  0% {
    background-color: #444;
  }
  50%, 100% {
    background-color: #ccc;
  }
}

/* Backend process styling with improved visual feedback */
.backend-process-content {
  max-height: 300px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Enhanced process toggle button with more vibrant colors */
.process-toggle-button {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.process-toggle-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Subtle pulse animation for the toggle button */
@keyframes pulse-subtle {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Process content transition */
.process-content, .planning-details-content {
  transition: max-height 0.3s ease, opacity 0.3s ease;
  border-radius: 0.375rem;
  overflow: hidden;
}

/* Spinner for loading assets */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e6e6e6;
  border-top-color: #004254;
  border-radius: 50%;
  animation: spinner 0.8s linear infinite;
}

@keyframes spinner {
  to {
    transform: rotate(360deg);
  }
}

/* Progress container styling */
.progress-container {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
}

/* Estilo para la parte con blur */
.backdrop-blur-md {
  backdrop-filter: blur(8px);
}

.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}
</style>
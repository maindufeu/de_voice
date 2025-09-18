<template>
  <form @submit.prevent="handleSubmit" class="mt-4">
    <!-- Contenedor principal con estilo Gemini -->
    <div class="flex items-center gap-2 bg-zinc-900 rounded-full p-2 border border-zinc-700 fixed bottom-5 w-[800px] mx-auto left-0 right-0">

      <!-- Input de mensaje -->
      <input
        v-model="inputMessage"
        type="text"
        class="flex-grow py-2 px-3 bg-transparent border-0 focus:ring-0 focus:outline-none text-white placeholder-gray-400"
        placeholder="Pregúntale a softtek..."
        :disabled="isWaiting || activeCall"
      />

      <!-- Botón de volumen (activar/desactivar voz) -->
      <button
        type="button"
        class="p-2 text-gray-400 focus:outline-none"
        @click="toggleVoice"
      >
        <!-- Ícono de volumen encendido -->
        <svg v-if="voiceEnabled" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
          <path d="M14 9.5 C16.5 9.5 16.5 14.5 14 14.5"></path>
          <path d="M16 7 C20 7 20 17 16 17"></path>
        </svg>
        
        <!-- Ícono de volumen apagado -->
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
          <line x1="23" y1="9" x2="17" y2="15"></line>
          <line x1="17" y1="9" x2="23" y2="15"></line>
        </svg>
      </button>

      <!-- Botón de micrófono (solo visible cuando voiceEnabled es true) -->
      <button
        v-if="voiceEnabled"
        type="button"
        class="p-2 text-gray-400 focus:outline-none"
        :disabled="isWaiting || activeCall || !isVoiceSupported"
        @click="toggleMic"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
        </svg>
      </button>

      <!-- Botón de ajustes (solo visible cuando voiceEnabled es true) -->
      <button
        v-if="voiceEnabled"
        type="button"
        class="p-2 text-gray-400 focus:outline-none"
        @click="toggleSettings"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 0 1 0-.255c.007-.378-.138-.75-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281Z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
      </button>

      <!-- Botón de enviar -->
      <button
        type="submit"
        class="p-2 text-gray-400 focus:outline-none"
        :disabled="isWaiting || !inputMessage.trim() || activeCall"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
        </svg>
      </button>
    </div>
    
    <!-- Modal de ajustes de voz -->
    <div v-if="showSettings" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="toggleSettings">
      <div class="bg-zinc-800 rounded-lg border border-zinc-700 p-6 max-w-md w-full mx-4 shadow-xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-white text-lg font-medium">Ajustes de voz</h3>
          <button @click="toggleSettings" class="text-gray-400 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="mb-4">
          <label for="voice-select" class="block text-white text-sm font-medium mb-2">Selecciona una voz:</label>
          <select 
            id="voice-select"
            v-model="selectedVoice"
            @change="handleVoiceChange"
            class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-zinc-700 text-white"
          >
            <option value="es-ES-ElviraNeural">Elvira (Español)</option>
            <option value="es-ES-AlvaroNeural">Álvaro (Español)</option>
            <option value="en-US-JennyMultilingualNeural">Jenny (Inglés)</option>
            <option value="en-US-GuyNeural">Guy (Inglés)</option>
          </select>
        </div>
        
        <div class="flex justify-end">
          <button 
            @click="toggleSettings" 
            class="px-4 py-2 bg-softtek-primary text-white rounded-lg hover:bg-opacity-90 transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mensaje de error -->
    <div v-if="error" class="mt-2 p-3 bg-red-100 text-red-700 rounded-lg border border-red-300">
      Error: {{ error }}
    </div>
  </form>
</template>
  
<script setup lang="ts">
import { ref, defineEmits, defineProps, watch } from 'vue';

const props = defineProps<{
  isWaiting: boolean;
  activeCall: boolean;
  voiceEnabled: boolean;
  isListening: boolean;
  micStatus: string;
  isVoiceSupported: boolean;
  connectionStatus: string;
  error: string | null;
}>();

const emit = defineEmits<{
  (e: 'send-message', message: string): void;
  (e: 'toggle-voice'): void;
  (e: 'toggle-mic'): void;
  (e: 'change-voice', voice: string): void;
  (e: 'end-call'): void;
}>();

const inputMessage = ref('');
const selectedVoice = ref('es-ES-ElviraNeural');
const showSettings = ref(false);

// Función para alternar el estado de voz
const toggleVoice = () => {
  emit('toggle-voice');
  console.log('Botón de voz clickeado.');
};

// Función para alternar el micrófono
const toggleMic = () => {
  emit('toggle-mic');
  console.log('Botón de micrófono clickeado.');
};

// Función para alternar visibilidad de ajustes
const toggleSettings = () => {
  showSettings.value = !showSettings.value;
  console.log(`Panel de ajustes ${showSettings.value ? 'mostrado' : 'ocultado'}.`);
};

// Función para cambiar la voz
const handleVoiceChange = () => {
  emit('change-voice', selectedVoice.value);
  console.log(`Voz cambiada a: ${selectedVoice.value}`);
};

// Función para finalizar la llamada
const endCall = () => {
  emit('end-call');
};

// Función para enviar mensaje
const handleSubmit = () => {
  if (inputMessage.value.trim() && !props.isWaiting && !props.activeCall) {
    emit('send-message', inputMessage.value);
    inputMessage.value = '';
  }
};
</script>

<style scoped>
button {
  appearance: none !important;
  -webkit-appearance: none !important;
  outline: none !important;
  border: none !important;
  box-shadow: none !important;
  background-color: transparent !important;
}

button:hover, button:focus, button:active {
  outline: none !important;
  border: none !important;
  box-shadow: none !important;
  background-color: transparent !important;
}
</style>
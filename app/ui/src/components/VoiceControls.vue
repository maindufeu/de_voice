<template>
  <div class="mt-4 space-y-4">
    <!-- Voice toggle and voice selection -->
    <div class="flex flex-wrap items-center gap-3">
      <button
        @click="toggleVoice"
        :class="[
          'px-4 py-2 rounded-lg text-white transition duration-200 ',
          voiceEnabled ? 'bg-red-500 hover:bg-red-600' : 'bg-fuscia hover:bg-fuscia'
        ]"
      >
        {{ voiceEnabled ? 'Desactivar voz' : 'Activar voz' }}
      </button>
      
      <select
        v-model="selectedVoice"
        class="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        :disabled="!voiceEnabled"
      >
        <option value="es-ES-ElviraNeural">Elvira (Español)</option>
        <option value="es-ES-AlvaroNeural">Álvaro (Español)</option>
        <option value="en-US-JennyMultilingualNeural">Jenny (Inglés)</option>
        <option value="en-US-GuyNeural">Guy (Inglés)</option>
      </select>
      
      <span class="text-base-200 italic">
        {{ connectionStatus }}
      </span>
    </div>
    
    <!-- Microphone and call controls -->
    <div class="flex flex-wrap items-center gap-3" v-if="voiceEnabled">
      <button
        @click="toggleMic"
        :class="[
          'px-4 py-2 rounded-lg text-white flex items-center gap-2 transition duration-200',
          isListening ? 'bg-red-600 hover:bg-red-700' : 'bg-red-500 hover:bg-red-600'
        ]"
        :disabled="!voiceEnabled || !isVoiceSupported || activeCall"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/>
          <path d="M10 8a2 2 0 1 1-4 0V3a2 2 0 1 1 4 0v5zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3z"/>
        </svg>
        {{ isListening ? 'Detener' : 'Hablar' }}
      </button>
      
      <button
        v-if="activeCall"
        @click="endCall"
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition duration-200 flex items-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M2.267.98a1.636 1.636 0 0 1 2.448.152l1.681 2.162c.309.396.418.913.296 1.4l-.513 2.053a.636.636 0 0 0 .167.604L8.65 9.654a.636.636 0 0 0 .604.167l2.052-.513a1.636 1.636 0 0 1 1.401.296l2.162 1.681c.777.604.849 1.753.153 2.448l-.97.97c-.693.693-1.73.998-2.697.658a17.47 17.47 0 0 1-6.571-4.144A17.47 17.47 0 0 1 .639 4.646c-.34-.967-.035-2.004.658-2.698l.97-.969z"/>
          <path fill-rule="evenodd" d="M11.146 1.646a.5.5 0 0 1 .708 0L13 2.793l1.146-1.147a.5.5 0 0 1 .708.708L13.707 3.5l1.147 1.146a.5.5 0 0 1-.708.708L13 4.207l-1.146 1.147a.5.5 0 0 1-.708-.708L12.293 3.5l-1.147-1.146a.5.5 0 0 1 0-.708z"/>
        </svg>
        Colgar
      </button>
      
      <span class="text-base-200 italic">
        {{ micStatus }}
      </span>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="p-3 bg-red-100 text-red-700 rounded-lg border border-red-300">
      Error: {{ error }}
    </div>
  </div>
</template>
  
<script setup lang="ts">
  import { ref, defineEmits, defineProps, watch } from 'vue';
  
  const props = defineProps<{
    voiceEnabled: boolean;
    isListening: boolean;
    micStatus: string;
    isVoiceSupported: boolean;
    connectionStatus: string;
    activeCall: boolean;
    error: string | null;
  }>();
  
  const emit = defineEmits<{
    (e: 'toggle-voice'): void;
    (e: 'toggle-mic'): void;
    (e: 'change-voice', voice: string): void;
    (e: 'end-call'): void;
  }>();
  
  const selectedVoice = ref('es-ES-ElviraNeural');
  
  // Watch for voice selection changes
  watch(selectedVoice, (newVoice) => {
    emit('change-voice', newVoice);
  });
  
  // Voice toggle function
  const toggleVoice = () => {
    emit('toggle-voice');
  };
  
  // Microphone toggle function
  const toggleMic = () => {
    emit('toggle-mic');
  };
  
  // End call function
  const endCall = () => {
    emit('end-call');
  };
</script>
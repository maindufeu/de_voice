// src/composables/useSharedState.ts
import { ref } from 'vue';

// Create shared reactive states
const voiceEnabled = ref(false);
const selectedVoice = ref('es-ES-ElviraNeural');

// Export the shared state
export function useSharedState() {
  return {
    voiceEnabled,
    selectedVoice
  };
}
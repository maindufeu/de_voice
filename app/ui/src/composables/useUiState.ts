import { ref } from 'vue';
import type { ProgressState } from '../types/chat';

export function useUiState() {
  // UI state flags
  const isTyping = ref(false);
  const isWaitingForResponse = ref(false);
  const currentError = ref<string | null>(null);
  const activeCall = ref(false);
  const currentInput = ref('');
  
  // Progress state with default values
  const progressState = ref<ProgressState>({
    visible: false,
    progress: 0,
    message: ''
  });
  
  /**
   * Update the progress state
   * @param progress Progress percentage (0-100)
   * @param message Progress message
   */
  const updateProgressState = (progress: number, message: string) => {
    console.log(`Updating progress: ${progress}%, message: ${message}`);
    progressState.value = {
      visible: true,
      progress,
      message
    };
  };
  
  /**
   * Hide the progress bar
   */
  const hideProgress = () => {
    console.log('Hiding progress bar');
    progressState.value.visible = false;
  };
  
  /**
   * Set UI state flags for typing, waiting, and active call
   * @param typing Whether the assistant is typing
   * @param waiting Whether we are waiting for a response
   * @param active Whether there is an active call
   */
  const setUiState = (state: { typing: boolean, waiting: boolean, active: boolean }) => {
    isTyping.value = state.typing;
    isWaitingForResponse.value = state.waiting;
    activeCall.value = state.active;
  };
  
  /**
   * Set the current error message
   * @param error Error message
   */
  const setError = (error: string | null) => {
    currentError.value = error;
  };
  
  /**
   * Set the current input text
   * @param input Input text
   */
  const setCurrentInput = (input: string) => {
    currentInput.value = input;
  };
  
  return {
    // State
    isTyping,
    isWaitingForResponse,
    currentError,
    activeCall,
    progressState,
    currentInput,
    
    // Methods
    updateProgressState,
    hideProgress,
    setUiState,
    setError,
    setCurrentInput
  };
}
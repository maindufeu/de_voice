import { ref, onUnmounted } from 'vue';
import { useSharedState } from './useSharedState';

export function useVoice() {
  const isListening = ref(false);
  const micStatus = ref('Micrófono inactivo');
  const { voiceEnabled, selectedVoice } = useSharedState();
  const isVoiceSupported = ref(!!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window));
  const recognition = ref<any>(null);
  const audioQueue = ref<Array<{content: string, text: string, final: boolean}>>([]);
  const isPlaying = ref(false);
  const currentAudio = ref<HTMLAudioElement | null>(null);
  
  // Initialize speech recognition
  const initRecognition = () => {
    if (!isVoiceSupported.value) {
      console.warn('Speech recognition not supported');
      return;
    }
    
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition.value = new SpeechRecognition();
      recognition.value.continuous = false;
      recognition.value.interimResults = false;
      recognition.value.lang = 'es-ES'; // Configurable
      
      console.log('Speech recognition initialized');
    } catch (error) {
      console.error('Error initializing speech recognition:', error);
      isVoiceSupported.value = false;
    }
  };
  
  // Start listening
  const startListening = (onResultCallback: (text: string) => void) => {
    if (!recognition.value) {
      initRecognition();
      if (!recognition.value) return;
    }
    
    try {
      // Set up event handlers
      recognition.value.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        micStatus.value = `Reconocido: "${transcript}"`;
        onResultCallback(transcript);
      };
      
      recognition.value.onerror = (event: any) => {
        micStatus.value = `Error: ${event.error}`;
        isListening.value = false;
        console.error('Speech recognition error:', event.error);
      };
      
      recognition.value.onend = () => {
        stopListening();
      };
      
      // Start recognition
      recognition.value.start();
      isListening.value = true;
      micStatus.value = 'Escuchando...';
      console.log('Speech recognition started');
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      micStatus.value = `Error: ${error}`;
      isListening.value = false;
    }
  };
  
  // Stop listening
  const stopListening = () => {
    if (!recognition.value) return;
    
    try {
      recognition.value.stop();
      console.log('Speech recognition stopped');
    } catch (error) {
      console.error('Error stopping speech recognition:', error);
    }
    
    isListening.value = false;
    micStatus.value = 'Micrófono inactivo';
  };
  
  // Toggle voice features
  const toggleVoice = () => {
    voiceEnabled.value = !voiceEnabled.value;
    console.log(`Voice ${voiceEnabled.value ? 'enabled' : 'disabled'}`);
    return voiceEnabled.value;
  };
  
  // Clear current audio
  const clearAudio = () => {
    if (currentAudio.value) {
      try {
        currentAudio.value.pause();
        currentAudio.value.remove();
      } catch (e) {
        console.error('Error stopping current audio:', e);
      }
      currentAudio.value = null;
    }
  };
  
  // Clear all audio queues and stop any playing audio
  const clearAllAudio = () => {
    // Stop and clear current audio
    clearAudio();
    
    // Clear the queue
    audioQueue.value = [];
    isPlaying.value = false;
    
    // Try to stop any other audio elements that might be playing
    try {
      const audioElements = document.querySelectorAll('audio');
      audioElements.forEach(audio => {
        audio.pause();
        audio.remove();
      });
    } catch (e) {
      console.error('Error stopping audio elements:', e);
    }
  };
  
  // Play audio from base64
  const playAudio = (base64Audio: string, text: string = '', final: boolean = true) => {
    // Add debugging information
    console.log(`Received audio data, first 50 chars: ${base64Audio.substring(0, 50)}...`);
    console.log(`Audio data length: ${base64Audio.length}`);
    console.log(`Text: ${text}, Final: ${final}`);
    
    // Check if data looks valid
    if (base64Audio.length < 100) {
      console.error('Audio data too short, likely invalid');
      return;
    }
    
    // Add the new audio to the queue
    audioQueue.value.push({ content: base64Audio, text, final });
    
    // If not currently playing anything, start playing
    if (!isPlaying.value) {
      playNextInQueue();
    }
  };

  // New function to play the next audio in queue
  const playNextInQueue = () => {
    // Check if queue is empty
    if (audioQueue.value.length === 0) {
      isPlaying.value = false;
      return;
    }
    
    // Set playing state
    isPlaying.value = true;
    
    // Get next audio from queue
    const nextAudio = audioQueue.value.shift();
    if (!nextAudio) {
      isPlaying.value = false;
      return;
    }
    
    try {
      // Clear any existing audio element first
      clearAudio();
      
      // Create audio URL
      const audioUrl = `data:audio/wav;base64,${nextAudio.content}`;
      
      // Create new audio element
      const audio = new Audio(audioUrl);
      currentAudio.value = audio;
      
      // Set up event handlers
      audio.oncanplay = () => console.log('Audio can play - format recognized');
      
      audio.onloadedmetadata = () => console.log('Audio metadata loaded:', { 
        duration: audio.duration, 
        paused: audio.paused 
      });
      
      audio.onplay = () => console.log('Audio started playing');
      
      // When audio completes, play next in queue
      audio.onended = () => {
        console.log('Audio playback completed successfully');
        clearAudio();
        
        // If this was the final audio for this segment, clean up
        if (nextAudio.final) {
          isPlaying.value = false;
          
          // Check if there are more items in the queue and play next if available
          if (audioQueue.value.length > 0) {
            // Eliminar o reducir drásticamente el retraso
            setTimeout(() => {
              playNextInQueue();
            }, 10); // Retraso mínimo de 10ms (prácticamente imperceptible)
          }
        } else {
          // If not final, continue immediately to next audio
          playNextInQueue();
        }
      };
      
      // Handle errors
      audio.onerror = (e) => {
        console.error('Audio play error:', e);
        console.error('Audio error code:', audio.error?.code);
        console.error('Audio error message:', audio.error?.message);
        clearAudio();
        
        // Continue to next audio despite error
        isPlaying.value = false;
        if (audioQueue.value.length > 0) {
          setTimeout(() => {
            playNextInQueue();
          }, 100);
        }
      };
      
      // Load audio
      audio.load();
      
      // Play with timeout to ensure proper loading
      setTimeout(() => {
        audio.play()
          .then(() => console.log('Audio playback started successfully'))
          .catch(error => {
            console.error('Error playing audio:', error);
            clearAudio();
            isPlaying.value = false;
            
            // Continue to next if available
            if (audioQueue.value.length > 0) {
              setTimeout(() => {
                playNextInQueue();
              }, 100);
            }
          });
      }, 100);
    } catch (error) {
      console.error('Error creating audio element:', error);
      isPlaying.value = false;
      
      // Continue to next if available
      if (audioQueue.value.length > 0) {
        setTimeout(() => {
          playNextInQueue();
        }, 100);
      }
    }
  };
  
  // Clean up on component unmount
  onUnmounted(() => {
    if (recognition.value && isListening.value) {
      stopListening();
    }
    clearAllAudio();
  });
  
  return {
    isListening,
    micStatus,
    voiceEnabled,
    selectedVoice,
    isVoiceSupported,
    startListening,
    stopListening,
    toggleVoice,
    playAudio,
    clearAllAudio,
  };
}
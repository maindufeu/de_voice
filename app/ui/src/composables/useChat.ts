import { useWebSocket } from './useWebSocket';
import { useSharedState } from './useSharedState';
import { useVoice } from './useVoice';
import { useMessageState } from './useMessageState';
import { useUiState } from './useUiState';
import { useAssetManager } from './useAssetManager';
import { apiService } from '../services/apiService';
import { createMessageProcessor } from '../services/messageProcessor';
import type { ApiMessage, AssetRefs } from '../types/chat';

/**
 * Genera un UUID v4 simple
 */
const generateSessionId = (): string => {
  // Usar crypto.randomUUID() si está disponible (navegadores modernos)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  
  // Fallback para navegadores más antiguos
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};


export function useChat() {
  // Generar un nuevo ID de sesión
  const sessionId = generateSessionId();
  console.log('Generated session ID:', sessionId);
  // Message state management
  const { 
    messages, 
    addMessage, 
    forceNewMessage, 
    updateMessage,
    getLastMessageIndex,
    setCurrentMessage,
    setCurrentBackendProcessMessage,
    getCurrentMessage,
    getCurrentBackendProcessMessage
  } = useMessageState();
  
  // UI state management
  const { 
    isTyping, 
    isWaitingForResponse, 
    currentError, 
    activeCall, 
    progressState,
    currentInput,
    updateProgressState, 
    hideProgress, 
    setUiState,
    setError,
    setCurrentInput
  } = useUiState();
  
  // WebSocket connection
  const { 
    socket, 
    isConnected, 
    connect, 
    disconnect, 
    sendMessage: sendWebSocketMessage, 
    setupMessageHandler 
  } = useWebSocket();
  
  // Shared state (like voice settings)
  const { voiceEnabled, selectedVoice } = useSharedState();
  
  // Voice functionality
  const { playAudio, clearAllAudio } = useVoice();
  
  // Asset management
  const { loadAssetsFromRefs } = useAssetManager(updateMessage);
  
  // Create message processor with callbacks
  const messageProcessor = createMessageProcessor({
    addMessage,
    updateProgress: updateProgressState,
    hideProgress,
    updateMessageState: setUiState,
    setCurrentMessage,
    setCurrentBackendProcessMessage,
    getCurrentMessage,
    getCurrentBackendProcessMessage,
    forceNewMessage,
    onAssetRefsReceived: (assetRefs) => {
      // Cuando se reciben referencias a assets, iniciar la carga inmediatamente
      const messageIndex = getLastMessageIndex();
      if (messageIndex >= 0) {
        loadAssetsFromRefs(assetRefs, messageIndex);
      }
    }
  });
  
  /**
   * Set up WebSocket message handling for voice chat
   */
  const setupVoiceChatHandling = () => {
    setupMessageHandler((data) => {
      console.log('Received WebSocket message:', data);
      
      try {
        // Special handling for start_response message
        if (data.type === 'start_response') {
          console.log('Starting response');
          // Reset progress state on new response
          updateProgressState(0, 'Iniciando...');
          return;
        }
        
        // Special handling for end_response message
        if (data.type === 'end_response') {
          console.log('Response completed');
          hideProgress(); // Hide progress when response is complete
          setUiState({ typing: false, waiting: false, active: false });
          return;
        }
        
        // Special handling for audio content
        if (data.type === 'audio' && voiceEnabled.value) {
          console.log('Audio message received');
          
          // Extract the audio content and text
          const audioContent = data.content;
          const textContent = data.text || '';
          const isFinal = data.final === true;
          
          if (audioContent) {
            // Play the audio
            console.log('Playing audio for text:', textContent);
            playAudio(audioContent, textContent, isFinal);
            
            // If this is the final audio chunk and we have no more messages coming,
            // reset the activeCall state
            if (isFinal) {
              setTimeout(() => {
                // Small delay to allow for any final messages
                if (!isTyping.value && !isWaitingForResponse.value) {
                  setUiState({ typing: false, waiting: false, active: false });
                }
              }, 500);
            }
          }
          
          // Don't process this as a regular message
          return;
        }
        
        // Handle different message formats
        if (data.progress !== undefined && data.message !== undefined) {
          // It's a data analysis progress message
          messageProcessor.handleRawServerMessage(data);
        } else if (data.type) {
          if (
            data.type === 'planning_token' || 
            data.type === 'code_token' ||
            data.type === 'planning_start' || 
            data.type === 'planning_complete' ||
            data.type === 'code_generation_start' || 
            data.type === 'code_generation_complete'
          ) {
            // Special backend process messages
            messageProcessor.handleRawServerMessage(data);
          } else {
            // Process as standard API message
            messageProcessor.processApiMessage(data as ApiMessage);
          }
        } else {
          // Generic object, try to handle it
          messageProcessor.handleRawServerMessage(data);
        }
        
        // Check for completion which should update UI state
        if (data.type === 'completion') {
          setUiState({ typing: false, waiting: false, active: false });
        }
      } catch (e) {
        console.error('Error processing WebSocket message:', e);
        setUiState({ typing: false, waiting: false, active: false });
        hideProgress(); // Hide progress on error
      }
    });
  };
  
  /**
   * Send a message via WebSocket (for voice)
   * @param message Message text
   */
  const sendVoiceMessage = async (message: string): Promise<void> => {
    if (!message.trim()) return;
    
    try {
      // Connect WebSocket if not already connected
      if (!isConnected.value) {
        connect();
        // Wait for connection to establish
        let connectionAttempts = 0;
        const maxAttempts = 10;
        while (!isConnected.value && connectionAttempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 100));
          connectionAttempts++;
        }
        
        // Check if still not connected after attempts
        await new Promise<boolean>(resolve => {
          const checkConnection = setInterval(() => {
            if (isConnected.value) {
              clearInterval(checkConnection);
              resolve(true);
            }
          }, 100);
          
          // Timeout after 5 seconds
          setTimeout(() => {
            clearInterval(checkConnection);
            resolve(false);
          }, 5000);
        });
        
        // If still not connected, handle the error
        if (!isConnected.value) {
          throw new Error('No se pudo establecer conexión WebSocket');
        }
      }
      
      // Clear any previous audio to prevent issues
      clearAllAudio();
      
      // Reset all message tracking for a fresh start
      forceNewMessage();
      
      // Setup message handler before sending the message
      setupVoiceChatHandling();
      
      // Initialize progress state
      updateProgressState(0, 'Iniciando...');
      
      // Update UI state
      setUiState({ typing: true, waiting: true, active: true });
      
      // Send message via WebSocket
      console.log('Sending Websocket Message type chat with content: ', message);
      sendWebSocketMessage('chat', { 
        message,
        voice: selectedVoice.value,
        sessionId: sessionId
      });
      
      console.log('Voice message sent:', message);
    } catch (error) {
      console.error('Error sending voice message:', error);
      setError(`Error al enviar mensaje: ${error}`);
      setUiState({ typing: false, waiting: false, active: false });
      hideProgress();
    }
  };
  
  /**
   * Send a message via REST API (for text-only)
   * @param message Message text
   */
  const sendTextMessage = async (message: string): Promise<void> => {
    if (!message.trim()) return;
    
    setUiState({ typing: true, waiting: true, active: false });
    
    // Initialize progress state
    updateProgressState(0, 'Iniciando...');
    
    try {
      // Reset all message tracking for a fresh start
      forceNewMessage();
      
      // Send message via API service
      await apiService.sendTextMessage(
        message,
        sessionId,
        {
          onProgress: (progress: number, message: string) => {
            updateProgressState(progress, message);
          },
          onMessage: (apiMessage: ApiMessage) => {
            messageProcessor.processApiMessage(apiMessage);
          },
          onError: (error: any) => {
            console.error('Error in text message response:', error);
            setError(`Error al comunicarse con el asistente: ${error}`);
            
            // Add error message to chat
            addMessage({ 
              isUser: false, 
              text: 'Error al comunicarse con el asistente. Por favor, intenta nuevamente.',
              error: error instanceof Error ? error.message : String(error)
            });
            
            // Hide progress on error
            hideProgress();
            
            // Reset state
            forceNewMessage();
            setUiState({ typing: false, waiting: false, active: false });
          },
          onComplete: () => {
            // Ensure progress is hidden at the end
            setTimeout(() => {
              hideProgress();
            }, 2000);
            
            // Reset state
            forceNewMessage();
            setUiState({ typing: false, waiting: false, active: false });
            
            console.log('Text message response complete');
          }
        }
      );
    } catch (error) {
      console.error('Error sending text message:', error);
      setError(`Error al comunicarse con el asistente: ${error}`);
      
      // Add error message to chat
      addMessage({ 
        isUser: false, 
        text: 'Error al comunicarse con el asistente. Por favor, intenta nuevamente.',
        error: error instanceof Error ? error.message : String(error)
      });
      
      // Hide progress on error
      hideProgress();
      
      // Reset state
      forceNewMessage();
      setUiState({ typing: false, waiting: false, active: false });
    }
  };
  
  /**
   * Send a chat message (either text or voice)
   * @param message Message text
   */
  const chatSendMessage = async (message: string): Promise<void> => {
    // Add user message to chat
    addMessage({ text: message, isUser: true });
    setCurrentInput('');
    console.log('Voice mode enabled:', voiceEnabled.value);

    if (voiceEnabled.value) {
      // Send voice message via WebSocket
      console.log('Sending voice message:', message);
      await sendVoiceMessage(message);
    } else {
      // Send text message via REST API
      console.log('Sending text message:', message);
      await sendTextMessage(message);
    }
  };
  
  /**
   * End current call (voice mode)
   */
  const endCall = (): void => {
    if (activeCall.value) {
      // Clear any playing audio
      clearAllAudio();
      
      // Disconnect the WebSocket
      disconnect();
      
      // Reset UI state
      setUiState({ typing: false, waiting: false, active: false });
      hideProgress();
      
      // Add message that call was ended
      addMessage({ isUser: false, text: 'Llamada finalizada por el usuario.' });
      console.log('Call ended by user');
      
      // Force reconnection on next message to ensure fresh connection
      socket.value = null;
      isConnected.value = false;
    }
  };
  
  /**
   * Process asset references in a message
   * @param assetRefs Asset references
   * @param messageIndex Index of the message
   */
  const processAssetRefs = async (assetRefs: AssetRefs, messageIndex: number): Promise<void> => {
    await loadAssetsFromRefs(assetRefs, messageIndex);
  };
  
  return {
    // State
    messages,
    isTyping,
    isWaitingForResponse,
    currentInput,
    currentError,
    activeCall,
    progressState,
    sessionId,
    
    // Actions
    chatSendMessage,
    endCall,
    processAssetRefs
  };
}
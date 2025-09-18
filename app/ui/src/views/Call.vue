<template>
  <div class="flex flex-col h-full">
    <!-- Contenido principal -->
    <div class="flex-1 bg-base-200 flex flex-col">
      <!-- Mensaje de bienvenida - solo visible cuando no hay mensajes -->
      <div v-if="messages.length === 0" class="flex flex-col items-center px-4 py-8">
        <h1 class="text-4xl font-bold mb-2 text-center">
          <span class="text-softtek-primary">Voice </span>
          <span class="text-fuscia">Analytics</span>
        </h1>

        <div class="w-full text-center mb-8 animate-pulse bg-gradient-to-r from-black to-fuscia bg-clip-text text-transparent text-4xl font-bold">
          ¿En qué puedo ayudarte?
        </div>
        
        <!-- Componente de burbujas con ancho controlado -->
        <div class="w-full max-w-6xl mx-auto">
          <Bubbles @select-suggestion="handleSuggestionSelected" />
        </div>
      </div>

      <!-- Chat container - visible solo cuando hay mensajes -->
      <div v-if="messages.length > 0" class="flex justify-center flex-1">
        <ChatContainer class="w-full max-w-6xl"
          :messages="messages"
          :is-typing="isTyping"
          @suggestion-selected="handleSuggestionSelected"
        />
      </div>
    </div>
    
    <!-- Input de mensajes - siempre visible -->
    <div class="bg-base-200">
      <MessageInput
        :is-waiting="isWaitingForResponse"
        :active-call="activeCall"
        :voice-enabled="voiceEnabled"
        :is-listening="isListening"
        :mic-status="micStatus"
        :is-voice-supported="isVoiceSupported"
        :connection-status="connectionStatus"
        :error="currentError"
        @send-message="handleSendMessage"
        @toggle-voice="handleToggleVoice"
        @toggle-mic="handleToggleMic"
        @change-voice="handleVoiceChange"
        @end-call="handleEndCall"
        class="px-4 py-3"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import ChatContainer from '../components/ChatContainer.vue';
import MessageInput from '../components/MessageInput.vue';
import Bubbles from '../components/Bubbles.vue';
import { useChat } from '../composables/useChat';
import { useVoice } from '../composables/useVoice';
import { useWebSocket } from '../composables/useWebSocket';

// Initialize composables
const { 
  messages, 
  isTyping, 
  isWaitingForResponse, 
  currentInput, 
  currentError, 
  activeCall,
  chatSendMessage: chatSendMessage,
  endCall: chatEndCall
} = useChat();

const {
  isListening,
  micStatus,
  voiceEnabled,
  selectedVoice,
  isVoiceSupported,
  startListening,
  stopListening,
  toggleVoice
} = useVoice();

const {
  connectionStatus,
  connect,
  isConnected
} = useWebSocket();

// Handle suggestion selected from ChatContainer
const handleSuggestionSelected = async (suggestion: string) => {
  console.log('Sugerencia seleccionada:', suggestion);
  // Use the same message handler as the input field
  await handleSendMessage(suggestion);
};

// Handle voice toggle
const handleToggleVoice = () => {
  const isEnabled = toggleVoice();
  console.log(`Voice ${isEnabled ? 'enabled' : 'disabled'}`);
 
  if (isEnabled && !isConnected.value) {
    connect();
  }
  
  if (isEnabled && isListening.value) {
    stopListening();
  }
};

// Handle microphone toggle
const handleToggleMic = () => {
  if (isListening.value) {
    stopListening();
  } else {
    console.log('Starting voice recognition...');
    startListening((text: string) => {
      // When speech is recognized, send the message
      if (text) {
        handleSendMessage(text);
      }
    });
  }
};

// Handle voice selection change
const handleVoiceChange = (voice: string) => {
  selectedVoice.value = voice;
  console.log(`Voice changed to: ${voice}`);
};

// Handle sending a message
const handleSendMessage = async (message: string) => {
  if (message.trim() && !isWaitingForResponse.value) {
    await chatSendMessage(message);
  }
};

// Handle ending a call
const handleEndCall = () => {
  chatEndCall();
  if (isListening.value) {
    stopListening();
  }
};

// Clean up error after some time
watch(currentError, (error) => {
  if (error) {
    setTimeout(() => {
      currentError.value = null;
    }, 5000);
  }
});

// Initialize on component mount
onMounted(() => {
  console.log('Call view mounted');
});
</script>
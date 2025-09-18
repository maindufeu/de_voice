import { ref } from 'vue';
import type { UIMessage } from '../types/chat';

export function useMessageState() {
  // Messages array for the chat history
  const messages = ref<UIMessage[]>([]);
  
  // Current message being composed (for text, data, etc.)
  const currentMessage = ref<UIMessage | null>(null);
  
  // Current backend process message (for planning, code generation, etc.)
  const currentBackendProcessMessage = ref<UIMessage | null>(null);
  
  // Flag to indicate a message update occurred
  const messageUpdated = ref(false);
  
  /**
   * Add a new message to the chat
   * @param message The message to add
   */
  const addMessage = (message: UIMessage) => {
    messages.value.push(message);
    messageUpdated.value = true;
  };
  
  /**
   * Force creation of a new message bubble
   */
  const forceNewMessage = () => {
    // Reset current message to force creation of a new one on next message
    currentMessage.value = null;
    // Reset current backend process message as well
    currentBackendProcessMessage.value = null;
    console.log('Forcing creation of new message bubble');
  };
  
  /**
   * Update a message at a specific index
   * @param index Index of the message to update
   * @param updates Partial updates to apply to the message
   */
  const updateMessage = (index: number, updates: Partial<UIMessage>) => {
    if (index >= 0 && index < messages.value.length) {
      messages.value[index] = { ...messages.value[index], ...updates };
      messageUpdated.value = true;
    } else {
      console.error('Tried to update message at invalid index:', index);
    }
  };
  
  /**
   * Get the index of the last message
   */
  const getLastMessageIndex = (): number => {
    return messages.value.length > 0 ? messages.value.length - 1 : -1;
  };
  
  /**
   * Set the current message
   * @param message The message to set as current
   */
  const setCurrentMessage = (message: UIMessage | null) => {
    currentMessage.value = message;
  };
  
  /**
   * Set the current backend process message
   * @param message The message to set as current backend process
   */
  const setCurrentBackendProcessMessage = (message: UIMessage | null) => {
    currentBackendProcessMessage.value = message;
  };
  
  /**
   * Get the current message
   */
  const getCurrentMessage = (): UIMessage | null => {
    return currentMessage.value;
  };
  
  /**
   * Get the current backend process message
   */
  const getCurrentBackendProcessMessage = (): UIMessage | null => {
    return currentBackendProcessMessage.value;
  };
  
  return {
    messages,
    messageUpdated,
    addMessage,
    forceNewMessage,
    updateMessage,
    getLastMessageIndex,
    setCurrentMessage,
    setCurrentBackendProcessMessage,
    getCurrentMessage,
    getCurrentBackendProcessMessage
  };
}
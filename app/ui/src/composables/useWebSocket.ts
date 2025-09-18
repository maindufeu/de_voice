import { ref, onUnmounted } from 'vue';

// API endpoints
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL as string;
const WS_ENDPOINT = `${API_BASE_URL}/ws/speech`;

export function useWebSocket() {
  const socket = ref<WebSocket | null>(null);
  const isConnected = ref(false);
  const connectionStatus = ref('Desconectado');
  const lastError = ref<string | null>(null);
  const clientId = ref<string>('client_' + Date.now());
  
  // Connect to WebSocket
  const connect = () => {
    console.log('Attempting to connect to WebSocket...');
    if (socket.value && (socket.value.readyState === WebSocket.OPEN || socket.value.readyState === WebSocket.CONNECTING)) {
      console.log('WebSocket already connected or connecting');
      return;
    }
    
    console.log(`Connecting to WebSocket: ${WS_ENDPOINT}/${clientId.value}`);
    
    try {
      socket.value = new WebSocket(`${WS_ENDPOINT}/${clientId.value}`);
      
      socket.value.onopen = () => {
        isConnected.value = true;
        connectionStatus.value = 'Conectado';
        lastError.value = null;
        console.log('WebSocket connected successfully');
      };
      
      socket.value.onclose = (event) => {
        isConnected.value = false;
        connectionStatus.value = 'Desconectado';
        console.log(`WebSocket closed: ${event.code} ${event.reason}`);
      };
      
      socket.value.onerror = (error) => {
        isConnected.value = false;
        connectionStatus.value = 'Error de conexión';
        lastError.value = 'Error en la conexión WebSocket';
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      lastError.value = `Error al crear conexión: ${error}`;
    }
  };
  
  // Disconnect WebSocket
  const disconnect = () => {
    if (socket.value) {
      try {
        socket.value.close();
        socket.value = null;
        isConnected.value = false;
        connectionStatus.value = 'Desconectado';
        console.log('WebSocket disconnected');
      } catch (error) {
        console.error('Error closing WebSocket:', error);
        lastError.value = `Error al cerrar conexión: ${error}`;
      }
    }
  };
  
  // Send message through WebSocket
  const sendMessage = (type: string, content: any) => {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
      console.log('WebSocket not connected, attempting to connect...');
      connect();
      
      // Wait for connection and retry
      setTimeout(() => {
        if (socket.value && socket.value.readyState === WebSocket.OPEN) {
          sendMessage(type, content);
        } else {
          console.error('Failed to connect and send message');
          lastError.value = 'Error al enviar mensaje: no se pudo conectar';
        }
      }, 1000);
      return;
    }
    
    try {
      const message = {
        type,
        ...content
      };
      
      console.log('Sending message:', message);
      socket.value.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending message:', error);
      lastError.value = `Error al enviar mensaje: ${error}`;
    }
  };
  
  // Set up message handler
  const setupMessageHandler = (callback: (data: any) => void) => {
    if (!socket.value) {
      console.error('WebSocket not connected, cannot set up message handler');
      return;
    }
    
    console.log('Setting up message handler for WebSocket');

    socket.value.onmessage = (event) => {
      //console.log('Message received:', event.data);
      try {
        const data = JSON.parse(event.data);
        //console.log('Message received:', data);
        callback(data);
      } catch (error) {
        console.error('Error processing message:', error);
        lastError.value = `Error al procesar mensaje: ${error}`;
      }
    };
  };
  
  // Clean up on component unmount
  onUnmounted(() => {
    disconnect();
  });
  
  // Generate a new client ID
  const resetClientId = () => {
    clientId.value = 'client_' + Date.now();
  };
  
  return {
    socket,
    isConnected,
    connectionStatus,
    lastError,
    clientId,
    connect,
    disconnect,
    sendMessage,
    setupMessageHandler,
    resetClientId,
  };
}
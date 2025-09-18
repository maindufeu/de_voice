import { CHAT_ENDPOINT, ASSETS_ENDPOINT } from '../types/chat';
import type { ApiMessage, UIMessage } from '../types/chat';
export const apiService = {
  /**
   * Send a text message to the chat API
   * @param message The message to send
   * @param sessionId Optional session ID for the chat
   * @param callbacks Object with callback functions for handling response
   */
  sendTextMessage: async (
    message: string,
    sessionId: string,
    callbacks: {
      onProgress: (progress: number, message: string) => void,
      onMessage: (apiMessage: ApiMessage) => void,
      onError: (error: any) => void,
      onComplete: () => void
    }
  ): Promise<void> => {
    try {
      const url = `${CHAT_ENDPOINT}?session_id=${encodeURIComponent(sessionId)}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          voice_enabled: false,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Set up to receive streaming response
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      
      // Process response chunks
      let isDone = false;
      while (!isDone) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            // Check for completion marker
            if (data === '[DONE]') {
              isDone = true;
              callbacks.onComplete();
              break;
            }
            
            // Try to parse as JSON first
            try {
              const jsonData = JSON.parse(data);
              
              // Handle direct progress format
              if (jsonData.progress !== undefined && jsonData.message !== undefined) {
                callbacks.onProgress(jsonData.progress, jsonData.message);
                continue;
              }
              
              // Process as standard ApiMessage
              callbacks.onMessage(jsonData as ApiMessage);
            } catch (parseError) {
              console.warn('Failed to parse as JSON, treating as raw text:', data);
              
              // Handle plain text
              const textMessage: ApiMessage = {
                type: 'text',
                content: { text: data }
              };
              callbacks.onMessage(textMessage);
            }
          }
        }
      }
    } catch (error) {
      callbacks.onError(error);
    }
  },
  
  /**
   * Get URL for an asset
   * @param assetType Type of asset (image, data)
   * @param assetId ID of the asset
   */
  getAssetUrl: (assetType: string, assetId: string): string => {
    return `${ASSETS_ENDPOINT}/${assetType}/${assetId}`;
  },
  
  /**
   * Load an image asset
   * @param imageId ID of the image to load
   */
  loadImageAsset: async (imageId: string): Promise<string | null> => {
    try {
      const response = await fetch(`${ASSETS_ENDPOINT}/image/${imageId}`);
      if (!response.ok) {
        throw new Error(`Failed to load image: ${response.statusText}`);
      }
      
      // Get the base64 data from the response
      const imageData = await response.text();
      return `data:image/png;base64,${imageData}`;
    } catch (err) {
      console.error(`Error loading image ${imageId}:`, err);
      return null;
    }
  },
  
  /**
   * Load a data asset
   * @param dataId ID of the data to load
   */
  loadDataAsset: async (dataId: string): Promise<any | null> => {
    try {
      const response = await fetch(`${ASSETS_ENDPOINT}/data/${dataId}`);
      if (!response.ok) {
        throw new Error(`Failed to load data: ${response.statusText}`);
      }
      
      // Get the JSON data from the response
      return await response.json();
    } catch (err) {
      console.error(`Error loading data ${dataId}:`, err);
      return null;
    }
  }
};
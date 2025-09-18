import type { ApiMessage, UIMessage, MessageType, MessageProcessorCallbacks } from '../types/chat';

export function createMessageProcessor(callbacks: MessageProcessorCallbacks) {
  // Acumulador para los tokens de planning JSON
  let planningJsonAccumulator = '';
  let planningJsonObject: any = null;
  
  /**
   * Process a standardized API message and update UI accordingly
   */
  const processApiMessage = (apiMessage: ApiMessage) => {
    //console.log('Processing API message:', apiMessage);
    
    // Create a new message when message type changes to prevent overwriting
    // Store the current message type to detect type changes
    const currentMessage = callbacks.getCurrentMessage();
    const currentMessageType = currentMessage ? currentMessage.messageType : null;
    
    switch (apiMessage.type) {
      case 'break_of_message':
        if (currentMessage && currentMessage.messageType !== 'progress' && 
            currentMessage.messageType !== 'backend_process') {
          callbacks.forceNewMessage();
          // Reiniciar acumuladores cuando forzamos un nuevo mensaje
          planningJsonAccumulator = '';
          planningJsonObject = null;
        }
        break;
      // Handle planning and code token streaming
      case 'planning_token':
      case 'code_token':
        handlePlanningOrCodeToken(apiMessage);
        break;
      
      // Handle backend process messages (from legacy/existing code)
      case 'backend_process':
        handleBackendProcessMessage(apiMessage);
        break;
      
      // Handle planning/code generation start/complete events
      case 'planning_start':
      case 'planning_complete':
      case 'code_generation_start':
      case 'code_generation_complete':
        handleStageEvent(apiMessage);
        break;
        
      case 'text':
        handleTextMessage(apiMessage, currentMessageType);
        break;
        
      case 'progress':
        handleProgressMessage(apiMessage);
        break;
        
      case 'data':
        handleDataMessage(apiMessage, currentMessageType);
        break;
        
      case 'completion':
        handleCompletionMessage(apiMessage);
        break;
        
      case 'error':
        handleErrorMessage(apiMessage);
        break;
    }
  };
  
  /**
   * Procesa los tokens de planning y construye un objeto JSON
   * También mantiene el formato markdown para el plan
   */
  const processJsonToken = (token: string): { plainText: string, jsonObject: any | null } => {
    // Acumular tokens para construir el JSON completo
    planningJsonAccumulator += token;
    
    let plainText = '';
    let jsonObject = null;
    
    try {
      // Intentar parsear el JSON acumulado
      const jsonText = planningJsonAccumulator.trim();
      
      // Si parece ser el inicio de un JSON válido o un JSON completo
      if ((jsonText.startsWith('{') && jsonText.includes('"plan"')) || 
          (jsonText.startsWith('{') && jsonText.endsWith('}'))) {
        
        try {
          // Intentar parsear como JSON completo
          jsonObject = JSON.parse(jsonText);
          
          // Si conseguimos un objeto JSON con un plan, extraer el texto plano
          if (jsonObject && jsonObject.plan) {
            plainText = jsonObject.plan;
            planningJsonObject = jsonObject;
          } else {
            // Si no tiene plan, seguir acumulando
            jsonObject = null;
          }
        } catch (e) {
          // JSON incompleto, extraer solo el texto visible del plan
          const planMatch = jsonText.match(/"plan"\s*:\s*"([^"]*)(?:"|$)/);
          if (planMatch && planMatch[1]) {
            plainText = planMatch[1]
              .replace(/\\n/g, '\n')  // Convertir escape de nueva línea a nueva línea real
              .replace(/\\\\/g, '\\'); // Manejar escapes de backslash
          }
        }
      } else {
        // Si no es un JSON válido todavía, mostrar el token tal cual
        plainText = token.replace(/\\n/g, '\n').replace(/\\\\/g, '\\');
      }
    } catch (e) {
      console.error('Error processing JSON token:', e);
      plainText = token;
    }
    
    return { plainText, jsonObject };
  };
  
  /**
   * Handle planning or code token messages
   */
  const handlePlanningOrCodeToken = (apiMessage: ApiMessage) => {
    const processType = apiMessage.type === 'planning_token' ? 'planning' : 'code_generation';
    const currentBackendProcessMessage = callbacks.getCurrentBackendProcessMessage();
    const newTokenText = apiMessage.content?.text || '';
    
    // Procesar de manera diferente los tokens de planning y código
    if (processType === 'planning') {
      // Para tokens de planning, procesar como JSON
      const { plainText, jsonObject } = processJsonToken(newTokenText);
      
      // Usar el mensaje dedicado para procesos de backend
      if (!currentBackendProcessMessage || 
          currentBackendProcessMessage.processType !== processType) {
        // Crear un nuevo mensaje de proceso de backend
        const newMessage: UIMessage = { 
          isUser: false, 
          text: plainText,
          messageType: 'backend_process',
          processType,
          // Almacenar el objeto JSON completo si está disponible
          planningData: jsonObject
        };
        callbacks.setCurrentBackendProcessMessage(newMessage);
        callbacks.addMessage(newMessage);
      } else {
        // Actualizar el mensaje existente con el nuevo texto
        currentBackendProcessMessage.text = plainText;
        
        // Si tenemos un objeto JSON completo, almacenarlo
        if (jsonObject) {
          currentBackendProcessMessage.planningData = jsonObject;
        }
      }
    } else {
      // Para tokens de código, mantener el comportamiento original
      if (!currentBackendProcessMessage || 
          currentBackendProcessMessage.processType !== processType) {
        // Crear un nuevo mensaje de proceso de backend
        const newMessage: UIMessage = { 
          isUser: false, 
          text: newTokenText,
          messageType: 'backend_process',
          processType
        };
        callbacks.setCurrentBackendProcessMessage(newMessage);
        callbacks.addMessage(newMessage);
      } else {
        // Actualizar mensaje existente con nuevo texto
        const originalText = currentBackendProcessMessage.text || '';
        currentBackendProcessMessage.text = originalText + newTokenText;
      }
    }
  };
  
  /**
   * Handle backend process messages
   */
  const handleBackendProcessMessage = (apiMessage: ApiMessage) => {
    const backendProcessType = apiMessage.content?.metadata?.process_type || 'unknown';
    const currentBackendProcessMessage = callbacks.getCurrentBackendProcessMessage();
    
    // Use the dedicated backend process message reference
    if (!currentBackendProcessMessage || 
        currentBackendProcessMessage.processType !== backendProcessType) {
      // Create a new backend process message
      const newMessage: UIMessage = { 
        isUser: false, 
        text: apiMessage.content?.text || '',
        messageType: 'backend_process',
        processType: backendProcessType
      };
      callbacks.setCurrentBackendProcessMessage(newMessage);
      callbacks.addMessage(newMessage);
    } else {
      // Update existing backend process message with new text
      const originalText = currentBackendProcessMessage.text || '';
      const newText = apiMessage.content?.text || '';
      currentBackendProcessMessage.text = originalText + newText;
    }
  };
  
  /**
   * Handle stage events (planning start/complete, code generation start/complete)
   */
  const handleStageEvent = (apiMessage: ApiMessage) => {
    // Reset planning JSON accumulator on planning start
    if (apiMessage.type === 'planning_start') {
      planningJsonAccumulator = '';
      planningJsonObject = null;
    }
    
    // Update progress based on stage
    let progressValue = 0;
    if (apiMessage.type === 'planning_start') progressValue = 10;
    else if (apiMessage.type === 'planning_complete') progressValue = 25;
    else if (apiMessage.type === 'code_generation_start') progressValue = 40;
    else if (apiMessage.type === 'code_generation_complete') progressValue = 60;
    
    // Update the progress bar
    callbacks.updateProgress(progressValue, apiMessage.content?.text || '');
  };
  
  /**
   * Handle text messages
   */
  const handleTextMessage = (apiMessage: ApiMessage, currentMessageType: string | null | undefined) => {
    const currentMessage = callbacks.getCurrentMessage();
    
    // If we're switching from a different message type or there's no current message,
    // start a new message instead of modifying the existing one
    if (!currentMessage || currentMessageType !== 'text') {
      // Don't reset backend process message
      // Only reset current text message
      callbacks.setCurrentMessage(null);
      
      // Create a brand new message for this text
      const newMessage: UIMessage = { 
        isUser: false, 
        text: apiMessage.content?.text || '',
        messageType: 'text' // Track message type
      };
      // Add message to the chat
      callbacks.setCurrentMessage(newMessage);
      callbacks.addMessage(newMessage);
      console.log('Added new text message:', newMessage.text);
    } else {
      // Update existing text message with new text
      const originalText = currentMessage.text || '';
      const newText = apiMessage.content?.text || '';
      currentMessage.text = originalText + newText;
      //console.log('Updated existing message with text:', newText);
    }
  };
  
  /**
   * Handle progress messages
   */
  const handleProgressMessage = (apiMessage: ApiMessage) => {
    // Handle progress messages by updating the progress state
    const progressPercent = apiMessage.content?.progress || 0;
    const progressMsg = apiMessage.content?.text || '';
    
    // Update the global progress state
    callbacks.updateProgress(progressPercent, progressMsg);
  };
  
  /**
   * Handle data messages
   */
  const handleDataMessage = (apiMessage: ApiMessage, currentMessageType: string | null | undefined) => {
    const currentMessage = callbacks.getCurrentMessage();
    
    // Data-containing message - create a new message if type has changed
    if (!currentMessage || currentMessageType !== 'data') {
      // Don't reset backend process message
      // Only reset current data message
      callbacks.setCurrentMessage(null);
      
      // Create a new data message
      const newMessage: UIMessage = { 
        isUser: false, 
        text: apiMessage.content?.text,
        data: apiMessage.content?.data,
        messageType: 'data'
      };
      callbacks.setCurrentMessage(newMessage);
      callbacks.addMessage(newMessage);
      console.log('Added new data message');
    } else {
      // Add data to existing message
      currentMessage.data = apiMessage.content?.data;
      if (apiMessage.content?.text) {
        currentMessage.text = apiMessage.content.text;
      }
    }
  };
  
  /**
   * Handle completion messages
   */
  const handleCompletionMessage = (apiMessage: ApiMessage) => {
    // Update progress to 100% and then hide after delay
    callbacks.updateProgress(100, apiMessage.content?.text || 'Completado');
    // Hide progress after a short delay
    setTimeout(() => {
      callbacks.hideProgress();
    }, 2000);
    
    // Create a completion message
    if (apiMessage.content?.text || apiMessage.content?.asset_refs) {
      // Don't reset backend process message
      // Only reset current text message
      callbacks.setCurrentMessage(null);
      
      // Create a new completion message
      const newMessage: UIMessage = { 
        isUser: false,
        messageType: 'completion',
        text: apiMessage.content?.text || '',
        assetsLoading: apiMessage.content?.asset_refs ? true : false
      };
      
      // Add all content from completion
      if (apiMessage.content) {
        if (apiMessage.content.data) {
          newMessage.data = apiMessage.content.data;
        }
        
        // Add asset references if available
        if (apiMessage.content.asset_refs) {
          console.log('Asset references found:', apiMessage.content.asset_refs);
          newMessage.asset_refs = apiMessage.content.asset_refs;
        }
        
        // Add legacy images if available (for backward compatibility)
        if (apiMessage.content.images && apiMessage.content.images.length > 0) {
          newMessage.images = apiMessage.content.images;
        }
      }
      
      // Add the message
      callbacks.addMessage(newMessage);
      
      // Notify that we have assets to load
      if (apiMessage.content?.asset_refs) {
        if (typeof callbacks.onAssetRefsReceived === 'function') {
          callbacks.onAssetRefsReceived(apiMessage.content.asset_refs);
        }
      }
      
      // Reset for next message (but keep backend process intact)
      callbacks.setCurrentMessage(null);
    }
    
    // Update UI state
    callbacks.updateMessageState({ typing: false, waiting: false, active: false });
  };
  
  /**
   * Handle error messages
   */
  const handleErrorMessage = (apiMessage: ApiMessage) => {
    // Hide the progress on error
    callbacks.hideProgress();
    
    // Reset all message tracking
    callbacks.forceNewMessage();

    planningJsonAccumulator = '';
    planningJsonObject = null;
    
    // Create a new error message
    const newMessage: UIMessage = { 
      isUser: false, 
      text: apiMessage.content?.text || 'Error en la comunicación',
      error: apiMessage.content?.error,
      messageType: 'error'
    };
    callbacks.addMessage(newMessage);
    console.log('Added error message');
    
    // Reset for next message and update UI state
    callbacks.forceNewMessage();
    callbacks.updateMessageState({ typing: false, waiting: false, active: false });
  };
  
  /**
   * Handle WebSocket messages for voice chat - special handling for direct message objects
   */
  const handleRawServerMessage = (data: any) => {
    try {
      console.log('Handling raw server message:', data);
      
      // Extract type and content from different formats
      let messageType = data.type;
      let messageContent = null;
      
      // Handle progress message in the format: { progress: X, message: Y, result: Z }
      if (data.progress !== undefined && data.message !== undefined) {
        messageType = 'progress';
        messageContent = {
          progress: data.progress,
          text: data.message,
          data: data.result // Include data property in initial object creation
        };
      }
      // Handle planning tokens: { type: "planning_token", content: { text: X } }
      else if (data.type === 'planning_token' || data.type === 'code_token') {
        messageType = data.type;
        messageContent = data.content;
      }
      // Handle other formatted messages
      else if (data.content !== undefined) {
        messageContent = data.content;
      }
      
      // Process as ApiMessage
      const apiMessage: ApiMessage = {
        type: messageType as MessageType,
      };
      
      if (messageContent) {
        apiMessage.content = messageContent;
      }
      
      console.log('Converted to API message:', apiMessage);
      processApiMessage(apiMessage);
      
    } catch (err) {
      console.error('Error handling raw server message:', err);
    }
  };
  
  /**
   * Process tokens as they arrive via SSE
   */
  const processStreamingTokens = (data: string): boolean => {
    // End of stream marker
    if (data === '[DONE]') {
      callbacks.updateMessageState({ typing: false, waiting: false, active: false });
      callbacks.hideProgress(); // Hide progress when stream ends
      return true; // Signal completion
    }
    
    try {
      // Try to parse as JSON
      if (data.startsWith('{') && data.endsWith('}')) {
        try {
          const jsonData = JSON.parse(data);
          
          // Handle direct progress format - must come before ApiMessage format check
          if (jsonData.progress !== undefined && jsonData.message !== undefined) {
            handleRawServerMessage(jsonData);
            return false;
          }
          
          // Handle messages with type field - could be ApiMessage or other format
          if (jsonData.type) {
            // Handle special types that might not fit ApiMessage format
            if (
              jsonData.type === 'planning_token' || 
              jsonData.type === 'code_token' ||
              jsonData.type === 'planning_start' || 
              jsonData.type === 'planning_complete' ||
              jsonData.type === 'code_generation_start' || 
              jsonData.type === 'code_generation_complete'
            ) {
              handleRawServerMessage(jsonData);
              return false;
            }
            
            // Process as standard ApiMessage
            processApiMessage(jsonData as ApiMessage);
            return false;
          }
          
          // If we can't determine format, treat as general object
          handleRawServerMessage(jsonData);
          return false;
        } catch (parseError) {
          console.warn('JSON parse error, will treat as plain text:', parseError);
          // Continue to fallback handling
        }
      }
      
      // If we reach here, either it wasn't JSON-formatted or parsing failed
      console.warn('Treating content as raw text token');
      
      // Create a text type message for simple strings
      const textMessage: ApiMessage = {
        type: 'text',
        content: {
          text: data
        }
      };
      
      processApiMessage(textMessage);
    } catch (e) {
      console.error('Error processing streaming token:', e);
      
      // Last resort - try to display the raw text
      const currentMessage = callbacks.getCurrentMessage();
      if (!currentMessage) {
        const newMessage: UIMessage = { isUser: false, text: String(data) };
        callbacks.setCurrentMessage(newMessage);
        callbacks.addMessage(newMessage);
      } else {
        // Append to current message
        currentMessage.text = (currentMessage.text || '') + String(data);
      }
    }
    
    return false; // Not done yet
  };
  
  return {
    processApiMessage,
    handleRawServerMessage,
    processStreamingTokens
  };
}
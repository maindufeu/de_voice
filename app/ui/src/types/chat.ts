// Define all interfaces and types used across modules

// API endpoints
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL as string;
export const CHAT_ENDPOINT = `${API_BASE_URL}/chat`;
export const ASSETS_ENDPOINT = `${API_BASE_URL}/assets`;

// Standardized message types
export type MessageType = 'text' | 'progress' | 'data' | 'completion' | 'break' | 'error' | 
                         'break_of_message' | 'start_response' | 'end_response' | 'audio' | 
                         'backend_process' | 'planning_token' | 'code_token' | 'planning_start' | 
                         'planning_complete' | 'code_generation_start' | 'code_generation_complete';

// Asset references format
export interface AssetRefs {
  image_ids?: string[];
  data_id?: string;
}

// Planning data interface
export interface PlanningData {
  plan: string;
  required_functions: string[];
  required_datasets: string[];
  expected_outputs: {
    data: string;
    visualizations: string[];
    insights: string[];
    [key: string]: any;
  };
  [key: string]: any;
}

// Standardized message format
export interface ApiMessage {
  type: MessageType;
  content?: {
    text?: string;
    progress?: number;
    data?: any;
    images?: string[];
    error?: string;
    asset_refs?: AssetRefs;
    metadata?: {
      process_type?: string;
      facialExpression?: string;
      animation?: string;
      [key: string]: any;
    }
  }
}

// UI message format
export interface UIMessage {
  isUser: boolean;
  text?: string;
  progress?: number;
  data?: any;
  images?: string[];
  asset_refs?: AssetRefs;
  error?: string;
  // Track message type to prevent overwriting different message types
  messageType?: 'text' | 'progress' | 'data' | 'completion' | 'error' | 'backend_process';
  processType?: string;
  // Flag to indicate if assets are still loading
  assetsLoading?: boolean;
  // Planning data for frontend visualization
  planningData?: PlanningData;
}

// Progress tracking interface
export interface ProgressState {
  visible: boolean;
  progress: number;
  message: string;
}

// Callback types for message processor
export interface MessageProcessorCallbacks {
  addMessage: (message: UIMessage) => void;
  updateProgress: (progress: number, message: string) => void;
  hideProgress: () => void;
  updateMessageState: (state: { typing: boolean, waiting: boolean, active: boolean }) => void;
  setCurrentMessage: (message: UIMessage | null) => void;
  setCurrentBackendProcessMessage: (message: UIMessage | null) => void;
  getCurrentMessage: () => UIMessage | null;
  getCurrentBackendProcessMessage: () => UIMessage | null;
  forceNewMessage: () => void;
  onAssetRefsReceived?: (assetRefs: AssetRefs) => void;
}
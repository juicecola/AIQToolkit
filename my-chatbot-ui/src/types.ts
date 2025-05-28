// src/types.ts
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string; // Optional
  isError?: boolean;  // Optional for error messages
}

// For the backend API request/response (match your backend)
export interface ChatApiRequest {
  message: string;
  session_id: string;
  model?: string; // Optional
  temperature?: number; // Optional
}

export interface ChatApiResponse {
  reply: string;
  session_id: string;
}

export interface ClearHistoryApiRequest {
  session_id: string;
}

export interface ClearHistoryApiResponse {
  message: string;
}

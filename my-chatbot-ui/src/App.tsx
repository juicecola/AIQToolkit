// src/App.tsx
import React, { useState, useEffect, useRef, FormEvent } from 'react';
import axios, { AxiosError } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { PaperAirplaneIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import type { Message, ChatApiRequest, ChatApiResponse, ClearHistoryApiRequest, ClearHistoryApiResponse } from './types';

const API_BASE_URL = 'http://localhost:8000/api'; // Replace with your backend URL

function App(): JSX.Element {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null); // For auto-resizing textarea

  useEffect(() => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    setMessages([
      { role: 'assistant', content: 'Hello! How can I assist you today?', id: uuidv4() }
    ]);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(scrollToBottom, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  const handleSendMessage = async (e?: FormEvent<HTMLFormElement>) => { // Optional event for form submission
    if (e) e.preventDefault();
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage: Message = { role: 'user', content: input, id: uuidv4() };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input; // Capture input before clearing
    setInput('');
    setIsLoading(true);

    try {
      const requestBody: ChatApiRequest = {
        message: currentInput, // Use captured input
        session_id: sessionId,
      };
      const response = await axios.post<ChatApiResponse>(`${API_BASE_URL}/chat`, requestBody);
      const aiMessage: Message = { role: 'assistant', content: response.data.reply, id: uuidv4() };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      let errorMessageContent = 'Sorry, I encountered an error. Please try again.';
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ detail?: string }>; // Type assertion for FastAPI error
        errorMessageContent = `Error: ${axiosError.response?.data?.detail || axiosError.message}`;
      } else if (error instanceof Error) {
        errorMessageContent = `Error: ${error.message}`;
      }
      const errorMessage: Message = {
        role: 'assistant',
        content: errorMessageContent,
        id: uuidv4(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // Focus back on textarea after sending
      textareaRef.current?.focus();
    }
  };

  const handleClearHistory = async () => {
    if (!sessionId || isLoading) return;
    setIsLoading(true);
    try {
      const requestBody: ClearHistoryApiRequest = { session_id: sessionId };
      await axios.post<ClearHistoryApiResponse>(`${API_BASE_URL}/clear_history`, requestBody);
      setMessages([{ role: 'assistant', content: 'Chat history cleared! How can I help you now?', id: uuidv4() }]);
    } catch (error) {
      console.error("Error clearing history:", error);
      let errorMessageContent = 'Failed to clear history.';
       if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ detail?: string }>;
        errorMessageContent = `Failed to clear history: ${axiosError.response?.data?.detail || axiosError.message}`;
      } else if (error instanceof Error) {
        errorMessageContent = `Failed to clear history: ${error.message}`;
      }
      setMessages(prev => [...prev, {
          role: 'assistant',
          content: errorMessageContent,
          id: uuidv4(),
          isError: true
      }]);
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-100 font-sans">
      <header className="bg-gray-800 p-4 shadow-md flex justify-between items-center sticky top-0 z-10">
        <h1 className="text-xl font-semibold">NVIDIA Chatbot (TS)</h1>
        <button
            onClick={handleClearHistory}
            className="p-2 rounded-md text-gray-300 hover:bg-gray-700 hover:text-white transition-colors disabled:opacity-50"
            disabled={isLoading}
            title="Clear Chat History"
        >
            <ArrowPathIcon className="h-6 w-6" />
        </button>
      </header>

      <main className="flex-grow p-4 md:p-6 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xl lg:max-w-2xl px-4 py-3 rounded-2xl shadow-md break-words ${ // Added break-words
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-lg'
                  : msg.isError ? 'bg-red-700 text-white rounded-bl-lg' : 'bg-gray-700 text-gray-200 rounded-bl-lg'
              }`}
            >
              {typeof msg.content === 'string' && msg.content.split('\n').map((line, i, arr) => (
                <span key={i}>
                  {line}
                  {i < arr.length - 1 && <br />}
                </span>
              ))}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      <footer className="p-4 bg-gray-800 border-t border-gray-700 sticky bottom-0 z-10">
        <form onSubmit={handleSendMessage} className="flex items-start space-x-3"> {/* Changed to items-start for textarea */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
              if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Type your message... (Shift+Enter for new line)"
            className="flex-grow p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white placeholder-gray-400 resize-none min-h-[48px] max-h-40 leading-tight" // Adjusted max-h
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="p-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center w-[48px] h-[48px] self-end mb-[1px]" // Aligned button with textarea bottom
            title="Send Message"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <PaperAirplaneIcon className="h-6 w-6" />
            )}
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;
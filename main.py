from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# --- Environment Variable Check & LLM Initialization ---
# (Similar to your Streamlit app, but for the API)
if "NVIDIA_API_KEY" not in os.environ:
    print("ERROR: NVIDIA_API_KEY not found in environment variables.")
    # In a real app, you might raise an exception or handle this more gracefully
    exit()

# Global instance for the LLM (or a more sophisticated management system)
# This example uses a single global LLM. For production, consider per-request or session-based LLM instances
# if model configurations need to vary or for better resource management.
try:
    LLM_INSTANCE = ChatNVIDIA(model="meta/llama3-8b-instruct", temperature=0.7) # Default model
    print(f"Successfully initialized global NVIDIA LLM: {LLM_INSTANCE.model}")
except Exception as e:
    print(f"FATAL: Error initializing global ChatNVIDIA instance: {e}")
    LLM_INSTANCE = None # Ensure it's None if failed
    # Consider raising an error that FastAPI can catch to return a 500 at startup or on first request
    # For now, we'll check LLM_INSTANCE before using it in endpoints.

# --- Memory Management ---
# For a multi-user chat, you need to manage memory per user/session.
# A simple dictionary can work for demonstration, but for production, consider:
# - A more robust session management (e.g., using Redis, database-backed sessions)
# - Clearing out old sessions to prevent memory leaks.
CONVERSATION_SESSIONS = {} # Key: session_id, Value: ConversationChain instance

def get_or_create_conversation_chain(session_id: str, model_name: str = "meta/llama3-8b-instruct", temperature: float = 0.7):
    if session_id not in CONVERSATION_SESSIONS:
        try:
            # You might want to allow model selection per session if the client can specify it
            current_llm = ChatNVIDIA(model=model_name, temperature=temperature)
            memory = ConversationBufferMemory()
            CONVERSATION_SESSIONS[session_id] = ConversationChain(
                llm=current_llm,
                memory=memory,
                verbose=False # Set True for server-side logging of prompts if needed
            )
            print(f"Created new conversation chain for session_id: {session_id} with model {model_name}")
        except Exception as e:
            print(f"Error creating conversation chain for session {session_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Could not initialize chat session: {e}")
    return CONVERSATION_SESSIONS[session_id]

app = FastAPI()

# --- CORS (Cross-Origin Resource Sharing) ---
# Allow your React frontend (running on a different port) to make requests
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost:3000",  # Default for create-react-app
    "http://localhost:5173",  # Default for Vite
    # Add any other origins you might use
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request/Response ---
class ChatRequest(BaseModel):
    message: str
    session_id: str # To maintain conversation context for different users/tabs
    model: str | None = "meta/llama3-8b-instruct" # Optional model override
    temperature: float | None = 0.7 # Optional temperature override

class ChatResponse(BaseModel):
    reply: str
    session_id: str # Echo back the session_id

# --- API Endpoint ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if LLM_INSTANCE is None and request.model is None: # Check if global LLM failed and no model specified in request
        raise HTTPException(status_code=500, detail="LLM not available. Server configuration issue.")
    
    try:
        # Use model and temperature from request if provided, otherwise defaults
        model_to_use = request.model if request.model else "meta/llama3-8b-instruct"
        temp_to_use = request.temperature if request.temperature is not None else 0.7

        conversation_chain = get_or_create_conversation_chain(
            request.session_id,
            model_name=model_to_use,
            temperature=temp_to_use
        )
        
        # Get AI response
        ai_response = await conversation_chain.ainvoke({"input": request.message}) # Use ainvoke for async
        
        return ChatResponse(reply=ai_response['response'], session_id=request.session_id)
    except HTTPException as e: # Re-raise HTTPExceptions
        raise e
    except Exception as e:
        print(f"Error processing chat request: {e}") # Log the full error server-side
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@app.post("/api/clear_history")
async def clear_history(session_id_payload: dict): # Expecting {"session_id": "some_id"}
    session_id = session_id_payload.get("session_id")
    if session_id and session_id in CONVERSATION_SESSIONS:
        del CONVERSATION_SESSIONS[session_id]
        print(f"Cleared history for session_id: {session_id}")
        return {"message": f"Chat history cleared for session {session_id}"}
    elif session_id:
        return {"message": f"No active session found for {session_id} to clear."}
    else:
        raise HTTPException(status_code=400, detail="session_id not provided")


# To run: uvicorn main:app --reload
# (main is the filename main.py, app is the FastAPI instance)

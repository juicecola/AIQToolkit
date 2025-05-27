import streamlit as st
import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# --- Environment Variable Check ---
# Best practice: Ensure NVIDIA_API_KEY is set as an environment variable
# You can also allow users to input it, but be mindful of security for shared apps.
if "NVIDIA_API_KEY" not in os.environ:
    st.error("NVIDIA_API_KEY not found in environment variables. Please set it to run the chatbot.")
    st.stop()

# --- Page Configuration (Optional) ---
st.set_page_config(page_title="NVIDIA Powered Chatbot", layout="wide")

# --- LangChain Backend Setup ---

# Use st.cache_resource to cache the LLM and chain initialization
# This prevents re-initializing on every user interaction if the underlying resource hasn't changed.
@st.cache_resource
def get_llm(model_name="meta/llama3-8b-instruct", temperature=0.7):
    """Initializes and returns the ChatNVIDIA LLM."""
    try:
        llm = ChatNVIDIA(model=model_name, temperature=temperature)
        print(f"Successfully initialized NVIDIA LLM: {llm.model}") # For server-side logging
        return llm
    except Exception as e:
        st.error(f"Error initializing ChatNVIDIA: {e}")
        st.error("Ensure your NVIDIA_API_KEY is set and valid, and the model name is correct.")
        st.stop() # Stop the app if LLM can't be initialized
        return None


# Function to initialize or get the conversation chain from session state
def get_conversation_chain(llm_instance):
    """
    Initializes and returns a ConversationChain with memory.
    Uses Streamlit's session state to maintain the chain (and its memory) across interactions.
    """
    if "conversation_chain" not in st.session_state:
        # Initialize memory
        memory = ConversationBufferMemory()
        # Initialize ConversationChain
        st.session_state.conversation_chain = ConversationChain(
            llm=llm_instance,
            memory=memory,
            verbose=False  # Set to True for server-side logging of prompts if needed
        )
        print("Initialized new ConversationChain with memory.") # For server-side logging
    return st.session_state.conversation_chain

# --- Streamlit UI ---

st.title("️ NVIDIA NIMs Chatbot with Memory")
st.caption("Powered by LangChain and Streamlit")

# Sidebar for model selection (optional)
with st.sidebar:
    st.subheader("Model Configuration")
    # You can list available NVIDIA NIM models here
    # For simplicity, we'll use a default or let the user input one if they know it
    available_models = ["meta/llama3-8b-instruct", "mistralai/mixtral-8x7b-instruct-v0.1", "nvidia/nemotron-3-8b-chat"] # Add more as needed
    selected_model = st.selectbox("Choose an NVIDIA Model:", available_models, index=0)
    temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.05)

    if st.button("Clear Chat History and Reinitialize Model"):
        st.session_state.messages = []
        if "conversation_chain" in st.session_state:
            del st.session_state.conversation_chain # This will force re-initialization with new settings
        st.rerun()


# Initialize LLM instance (this will be cached if model/temp doesn't change)
llm_instance = get_llm(model_name=selected_model, temperature=temperature)

if llm_instance: # Proceed only if LLM was initialized successfully
    # Initialize or get the conversation chain
    conversation_chain = get_conversation_chain(llm_instance)

    # Initialize chat history in Streamlit's session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # You can add an initial greeting from the assistant if you like
        # st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I help you today?"})


    # Display past chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input using st.chat_input
    if prompt := st.chat_input("What would you like to ask?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display AI response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty() # For a "Thinking..." effect or streaming
            full_response_content = ""
            try:
                with st.spinner("AI is thinking..."): # Show a spinner during LLM call
                    # Get AI response from the LangChain conversation chain
                    ai_response = conversation_chain.invoke({"input": prompt})
                    full_response_content = ai_response['response']

                message_placeholder.markdown(full_response_content)
            except Exception as e:
                st.error(f"Error during LLM invocation: {e}")
                full_response_content = "Sorry, I encountered an error."
                message_placeholder.markdown(full_response_content)

        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response_content})
else:
    st.warning("LLM could not be initialized. Please check configurations.")

import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA # Or NVIDIAEmbeddings for embeddings
from langchain_core.messages import HumanMessage, SystemMessage

# Ensure your NVIDIA_API_KEY is set as an environment variable
# If not, you can set it here (less recommended for production):
# os.environ["NVIDIA_API_KEY"] = "your_nvidia_api_key_here"

# Define the model identifier
# Find available models at build.nvidia.com or the NIM documentation.
# Example: "meta/llama3-8b-instruct" or "mistralai/mixtral-8x7b-instruct-v0.1"
nvidia_model_id = "meta/llama3-8b-instruct" # Adjust model name as needed

try:
    # CORRECTION: Use 'model' instead of 'model_name' for the constructor argument
    llm = ChatNVIDIA(model=nvidia_model_id)
except Exception as e:
    print(f"Error initializing ChatNVIDIA: {e}")
    print("Ensure your NVIDIA_API_KEY is set and valid, and the model name is correct.")
    print("Available models can be found on build.nvidia.com")
    exit()


# Prepare messages for the chat model
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What are three key benefits of using GPUs for AI?"),
]

# Invoke the model
# CORRECTION: Access the model name using 'llm.model'
print(f"Sending request to NVIDIA NIMs (model: {llm.model})...")
try:
    response = llm.invoke(messages)

    # Print the response
    print("\nResponse from NVIDIA NIMs:")
    print(response.content)
except Exception as e:
    print(f"Error during model invocation: {e}")

print("\nLet's try another way with a simple prompt string (using LCEL):")
# LangChain Expression Language (LCEL) for chaining
try:
    chain = llm
    response_simple = chain.invoke("Explain the concept of an AI inference server.")
    print(response_simple.content)
except Exception as e:
    print(f"Error during simple prompt invocation: {e}")

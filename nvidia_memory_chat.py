import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
# from langchain_core.messages import HumanMessage, SystemMessage # Not strictly needed for this basic ConversationChain

# 1. Initialize your NVIDIA LLM
# Ensure your NVIDIA_API_KEY is set as an environment variable
nvidia_model_id = "meta/llama3-8b-instruct"  # Or another model like "mistralai/mixtral-8x7b-instruct-v0.1"
try:
    llm = ChatNVIDIA(model=nvidia_model_id, temperature=0.7) # You can adjust temperature
    print(f"Successfully initialized NVIDIA LLM: {llm.model}")
except Exception as e:
    print(f"Error initializing ChatNVIDIA: {e}")
    print("Ensure your NVIDIA_API_KEY is set and valid, and the model name is correct.")
    print("Available models can be found on build.nvidia.com")
    exit()

# 2. Initialize the Memory
# ConversationBufferMemory stores messages in a buffer and extracts them as a variable.
# The default memory key is "history" which ConversationChain expects.
memory = ConversationBufferMemory()
# If you wanted a different memory key (e.g., for a custom prompt):
# memory = ConversationBufferMemory(memory_key="chat_log")

# 3. Initialize the ConversationChain
# This chain is specifically designed for conversational interactions.
# It will automatically use the "history" from the memory object
# and the "input" from your call.
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True  # Set to True to see the prompt and history being sent to the LLM
)

# 4. Interact with the chain (it will now use memory)
print("\nLet's start a conversation with memory!")

# First interaction
print("\n--- Interaction 1 ---")
user_input1 = "Hi there, I'm working on a project about renewable energy sources."
response1 = conversation.invoke({"input": user_input1})
print(f"Human: {user_input1}")
print(f"AI: {response1['response']}")

# Second interaction - AI should remember the project topic
print("\n--- Interaction 2 ---")
user_input2 = "What are two common types of sources I might be looking into?"
response2 = conversation.invoke({"input": user_input2})
print(f"Human: {user_input2}")
print(f"AI: {response2['response']}")

# Third interaction - AI should still remember the context
print("\n--- Interaction 3 ---")
user_input3 = "And which of those is generally more suitable for urban environments?"
response3 = conversation.invoke({"input": user_input3})
print(f"Human: {user_input3}")
print(f"AI: {response3['response']}")


# 5. You can inspect the memory buffer (optional)
print("\n--- Current Memory Buffer ---")
# For ConversationBufferMemory, the formatted history is often available via load_memory_variables
# The raw messages might be in memory.chat_memory.messages
print(memory.load_memory_variables({})) # Pass empty dict as context

# To see raw messages:
if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
    print("\n--- Raw Messages in Memory ---")
    for msg in memory.chat_memory.messages:
        print(f"- {msg.type.upper()}: {msg.content}")
else:
    print("\nRaw message buffer not directly accessible in this memory configuration.")

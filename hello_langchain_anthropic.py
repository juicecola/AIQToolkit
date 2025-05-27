import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

# LangChain will automatically look for the ANTHROPIC_API_KEY environment variable.
# If you haven't set it as an environment variable (not recommended for production),
# you could uncomment and set it directly here:
# os.environ["ANTHROPIC_API_KEY"] = "your_anthropic_api_key_here"

# Initialize the ChatAnthropic model
# You need to specify which Anthropic model you want to use.
# Common models include:
# - "claude-3-opus-20240229" (most powerful)
# - "claude-3-sonnet-20240229" (good balance of performance and speed)
# - "claude-3-haiku-20240307" (fastest and most compact)
# - "claude-2.1"
# - "claude-instant-1.2"
# Check Anthropic's documentation for the latest model names and availability.
model_name = "claude-3-sonnet-20240229" # Choose your desired model

try:
    llm = ChatAnthropic(model=model_name)
    # You can also specify other parameters like temperature, max_tokens_to_sample, etc.
    # llm = ChatAnthropic(model=model_name, temperature=0.7, max_tokens_to_sample=500)
except Exception as e:
    print(f"Error initializing ChatAnthropic: {e}")
    print("Please ensure your ANTHROPIC_API_KEY is set correctly as an environment variable.")
    print(f"Also, verify that the model name '{model_name}' is valid and available for your API key.")
    print("Check Anthropic's documentation for available models.")
    exit()

# Prepare messages for the chat model
messages = [
    SystemMessage(content="You are a philosophical assistant, skilled in explaining complex ideas simply."),
    HumanMessage(content="Explain the concept of 'emergence' in a few sentences."),
]

# Invoke the model
print(f"Sending request to Anthropic (model: {model_name})...")
try:
    response = llm.invoke(messages)
    # Print the response
    print("\nResponse from Anthropic:")
    print(response.content)
except Exception as e:
    print(f"Error during model invocation: {e}")

print("\nLet's try another way with a simple prompt string (using LCEL):")
# LangChain Expression Language (LCEL) for chaining
try:
    chain = llm
    response_simple = chain.invoke("What is the main difference between weather and climate?")
    print(response_simple.content)
except Exception as e:
    print(f"Error during simple prompt invocation: {e}")

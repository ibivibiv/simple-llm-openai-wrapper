from openai_wrapper.wrapper import OpenAIWrapper

# Configuration for the wrapper
config = {
    "models": ["gpt-4", "gpt-3.5-turbo"],
    "api_key": "your-api-key-here",
    "base_url": "https://api.openai.com/v1",  # Or your proxy-compatible base URL
    "json_only": True,
    "remove_thinking_sections": True,
    "default_params": {
        "temperature": 0.7,
        "max_tokens": 256
    },
    "max_attempts": 3
}

# Initialize the wrapper
client = OpenAIWrapper(config)

# Example 1: Chat-style prompt
chat_messages = [
    {"role": "user", "content": "Give me a <think>JSON</think> object describing a fictional animal."}
]

try:
    chat_response = client.chat(chat_messages)
    print("Chat Response:")
    print(chat_response)
except Exception as e:
    print(f"Chat failed: {e}")

# Example 2: Completion-style prompt
prompt = "Write a JSON object that describes a futuristic city."

try:
    gen_response = client.generate(prompt)
    print("\nGenerated Text:")
    print(gen_response)
except Exception as e:
    print(f"Generation failed: {e}")

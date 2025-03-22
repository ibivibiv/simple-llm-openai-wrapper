from openai_wrapper.wrapper import OpenAIWrapper

# Global configuration with per-model overrides.
config = {
    "models": [
        {
            "model": "gpt-4",
            "api_key": "your-gpt4-api-key",          # Optional; if omitted, global api_key is used.
            "base_url": "https://api.openai.com/v1",   # Optional; if omitted, global base_url is used.
            "default_params": {"temperature": 0.6}       # Model-specific hyperparameters.
        },
        {
            "model": "gpt-3.5-turbo",
            # This model uses the global API key and base URL.
            "default_params": {"temperature": 0.7}
        }
    ],
    "api_key": "your-global-api-key",               # Global API key
    "base_url": "https://api.openai.com/v1",          # Global base URL
    "json_only": True,                                # Enforce valid JSON output
    "remove_thinking_sections": True,                 # Remove <think>...</think> sections from responses
    "default_params": {"max_tokens": 256},            # Global default hyperparameters
    "max_attempts": 3                                 # Retry each model up to 3 times
}

client = OpenAIWrapper(config)

# Example 1: Chat-style request.
chat_messages = [
    {"role": "user", "content": "Give me a <think>JSON</think> object describing a futuristic vehicle."}
]

try:
    chat_response = client.chat(chat_messages)
    print("Chat Response:")
    print(chat_response)
except Exception as e:
    print(f"Chat failed: {e}")

# Example 2: Completion-style request.
prompt = "Write a JSON object that describes a new innovative gadget."

try:
    gen_response = client.generate(prompt)
    print("\nGenerated Text:")
    print(gen_response)
except Exception as e:
    print(f"Generation failed: {e}")

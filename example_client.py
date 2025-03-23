from openai_wrapper.wrapper import OpenAIWrapper

# Global configuration with per-model overrides.
# Note: Global values act as fallbacks if a model config doesn't supply its own.
config = {
    "models": [
        {
            "model": "gpt-4",
            "api_key": "your-gpt4-api-key",           # Overrides global API key for this model
            "base_url": "https://api.provider1.com/v1", # Overrides global base URL for this model
            "json_only": True,                         # Enforce JSON repair for this model
            "remove_thinking_sections": True,          # Remove <think>...</think> tags for this model
            "default_params": {"temperature": 0.6}       # Model-specific hyperparameters
        },
        {
            "model": "gpt-3.5-turbo",
            # Uses global API key and base_url if not provided here.
            "json_only": True,                         # Enforce JSON repair
            "remove_thinking_sections": False,         # Do not remove <think>...</think> tags
            "default_params": {"temperature": 0.7}       # Model-specific hyperparameters
        }
    ],
    "api_key": "your-global-api-key",               # Global API key (fallback)
    "base_url": "https://api.openai.com/v1",          # Global base URL (fallback)
    "json_only": False,                             # Global JSON flag (overridden per model)
    "remove_thinking_sections": False,              # Global thinking tag removal (overridden per model)
    "default_params": {"max_tokens": 256},          # Global default hyperparameters
    "max_attempts": 3                               # Retry each model up to 3 times
}

client = OpenAIWrapper(config)

# Example 1: Chat-style request.
chat_messages = [
    {"role": "user", "content": "Tell me a <think>JSON</think> formatted joke about computers."}
]

try:
    chat_response = client.chat(chat_messages)
    print("Chat Response:")
    print(chat_response)
except Exception as e:
    print(f"Chat failed: {e}")

# Example 2: Completion-style request.
prompt = "Generate a JSON object describing a futuristic city with advanced technology."

try:
    gen_response = client.generate(prompt)
    print("\nGenerated Text:")
    print(gen_response)
except Exception as e:
    print(f"Generation failed: {e}")

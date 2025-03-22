# simple-llm-openai-wrapper

---

**OpenAI Wrapper** is a highly configurable Python library designed to simplify your interactions with the OpenAI API. It addresses common challenges such as:

- **Multiple Model Fallbacks:** Seamlessly try a list of models (e.g., `gpt-4`, `gpt-3.5-turbo`) so that if one fails, the next is attempted.
- **Robust Retry Mechanism:** Uses [tenacity](https://github.com/jd/tenacity) to automatically retry calls to the API per model.
- **Output Post-Processing:** Optionally enforces valid JSON responses with [json_repair](https://pypi.org/project/json-repair/) and cleans up unwanted thinking sections (e.g., `<think>...</think>` tags).
- **Dual Interface:** Supports both chat-style and text generation (completion) interactions using a unified interface.

---

## Features

- **Model Fallback:** Define a prioritized list of models. The library will attempt each model (with retries) until one returns a valid response.
- **Retry on Failure:** Automatically retry API calls up to a configurable number of attempts for each model.
- **JSON Enforcement:** Optionally repair and enforce JSON output using `json_repair`.
- **Thinking Tag Removal:** Optionally remove custom `<think>...</think>` sections from the API output.
- **Unified API Interface:** Use the same wrapper to call both chat and completion endpoints.

---

## Installation

You can install **OpenAI Wrapper** directly from GitHub using pip:

```bash
pip install git+https://github.com/yourusername/openai-wrapper.git
```

For example, to install the latest version from the `main` branch:

```bash
pip install git+https://github.com/yourusername/openai-wrapper.git@main
```

---

## Usage

Below is a quick example to get you started:

```python
from openai_wrapper.wrapper import OpenAIWrapper

# Configure the wrapper
config = {
    "models": ["gpt-4", "gpt-3.5-turbo"],
    "api_key": "your-api-key-here",
    "base_url": "https://api.openai.com/v1",
    "json_only": True,
    "remove_thinking_sections": True,
    "default_params": {
        "temperature": 0.7,
        "max_tokens": 256
    },
    "max_attempts": 3
}

# Initialize the client
client = OpenAIWrapper(config)

# Example 1: Chat-style interaction
chat_messages = [
    {"role": "user", "content": "Give me a <think>JSON</think> object describing a fictional animal."}
]

try:
    chat_response = client.chat(chat_messages)
    print("Chat Response:")
    print(chat_response)
except Exception as e:
    print(f"Chat failed: {e}")

# Example 2: Completion-style interaction
prompt = "Write a JSON object that describes a futuristic city."

try:
    gen_response = client.generate(prompt)
    print("\nGenerated Text:")
    print(gen_response)
except Exception as e:
    print(f"Generation failed: {e}")
```

---

## How It Works

The wrapper operates in two main phases:

1. **Model Selection & Retry:**  
   For each API call (chat or generate), it cycles through your list of models. Each model call is wrapped in a retry mechanism:
   - Try a model up to `max_attempts` times.
   - If it fails, move on to the next model.

2. **Post-Processing:**  
   After a successful API call, the response is post-processed:
   - If enabled, `<think>...</think>` sections are removed.
   - If JSON enforcement is enabled, the response is repaired to produce valid JSON.

### Mermaid Diagram: Model Fallback Flow

```mermaid
flowchart TD
    A[Start: Receive API Request] --> B[Loop through Model List]
    B --> C[Call API with Model]
    C --> D{Successful Response?}
    D -- Yes --> E[Post-Process Response]
    E --> F[Return Cleaned Response]
    D -- No --> G[Retry (max_attempts)]
    G -- Exceeded --> H[Try Next Model]
    H --> B
    G -- Success on Retry --> E
```

This diagram illustrates how the wrapper attempts each model, retries on failure, and applies post-processing before returning the final output.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. When contributing, please ensure:
- Code follows the established style and includes tests.
- New features or bug fixes are documented in the README or code comments.
- Any external dependencies are added to the configuration files.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Support

If you encounter any issues or have suggestions, please open an issue on GitHub or contact the maintainers.

---

With this setup, you're ready to use **OpenAI Wrapper** to simplify your interactions with the OpenAI API, handle common issues, and quickly switch between models without hassle. Enjoy!

---

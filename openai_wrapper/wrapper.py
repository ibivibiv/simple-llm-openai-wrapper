import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from json_repair import repair_json
from typing import List, Dict, Any, Optional, Union
import re

def remove_think_sections(text: str) -> str:
    """
    Removes all occurrences of <think> ... </think> (including the tags) from the input text.
    The regex uses a non-greedy match and the DOTALL flag so that newlines are included.
    """
    pattern = r"<think>.*?</think>"
    return re.sub(pattern, "", text, flags=re.DOTALL)

class OpenAIWrapper:
    def __init__(self, config: Dict[str, Any]):
        """
        Global config keys:
          - models: List of dicts; each dict must include 'model' and optionally 'api_key', 'base_url', and 'default_params'
          - api_key: Global API key (fallback if a model config does not include its own)
          - base_url: Global base URL (fallback if a model config does not include its own)
          - json_only: If True, repair the output via repair_json
          - remove_thinking_sections: If True, remove any <think>...</think> sections from responses
          - default_params: Global default hyperparameters (overridden by per-model defaults if provided)
          - max_attempts: Number of retry attempts per model
        """
        self.models: List[Dict[str, Any]] = config.get("models", [])
        self.api_key: str = config.get("api_key")
        self.base_url: Optional[str] = config.get("base_url")
        self.json_only: bool = config.get("json_only", False)
        self.remove_thinking_sections: bool = config.get("remove_thinking_sections", False)
        self.default_params: Dict[str, Any] = config.get("default_params", {})
        self.max_attempts: int = config.get("max_attempts", 3)

        if not self.models:
            raise ValueError("You must provide at least one model in the 'models' list.")
        if not self.api_key:
            raise ValueError("You must provide a global OpenAI API key in the 'api_key' field.")

        if not all(isinstance(m, dict) and "model" in m for m in self.models):
            raise ValueError("Each model must be provided as a dict with at least a 'model' key.")

    def _post_process(self, text: str) -> str:
        if self.remove_thinking_sections:
            text = remove_think_sections(text)
        if self.json_only:
            text = repair_json(text)
        return text

    def _chat_completion(self, client, model: str, messages: List[Dict[str, str]], params: Dict[str, Any]) -> str:
        response = client.chat.completions.create(model=model, messages=messages, **params)
        return response.choices[0].message.content

    def _completion(self, client, model: str, prompt: str, params: Dict[str, Any]) -> str:
        response = client.completions.create(model=model, prompt=prompt, **params)
        return response.choices[0].text

    def _retry_wrapper(self, func, *args, **kwargs) -> str:
        @retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(openai.OpenAIError)
        )
        def wrapped():
            return func(*args, **kwargs)
        return wrapped()

    def chat(self, messages: List[Dict[str, str]], params: Optional[Dict[str, Any]] = None) -> str:
        """
        Iterate through the model configurations.
        For each, create a local client using the model's own API key and base URL (falling back to global settings),
        combine hyperparameters (global defaults overridden by model-specific defaults and then per-call params),
        then attempt to get a chat response.
        """
        last_exception = None

        for model_config in self.models:
            # Prepare local API credentials and endpoint.
            local_api_key = model_config.get("api_key", self.api_key)
            local_base_url = model_config.get("base_url", self.base_url)
            # Build a new client for this model.
            local_client = openai.OpenAI(api_key=local_api_key, base_url=local_base_url)
            # Combine hyperparameters: global defaults, then model-specific, then per-call params.
            effective_params = {**self.default_params, **model_config.get("default_params", {}), **(params or {})}

            try:
                response = self._retry_wrapper(self._chat_completion, local_client, model_config["model"], messages, effective_params)
                return self._post_process(response)
            except Exception as e:
                last_exception = e
        raise last_exception

    def generate(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Similar to chat(), but calls the completions endpoint for basic generation.
        """
        last_exception = None

        for model_config in self.models:
            local_api_key = model_config.get("api_key", self.api_key)
            local_base_url = model_config.get("base_url", self.base_url)
            local_client = openai.OpenAI(api_key=local_api_key, base_url=local_base_url)
            effective_params = {**self.default_params, **model_config.get("default_params", {}), **(params or {})}

            try:
                response = self._retry_wrapper(self._completion, local_client, model_config["model"], prompt, effective_params)
                return self._post_process(response)
            except Exception as e:
                last_exception = e
        raise last_exception

import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from json_repair import repair_json
from typing import List, Dict, Any, Optional
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
          - models: List of dicts; each dict must include 'model' and optionally:
              - 'api_key'
              - 'base_url'
              - 'json_only'
              - 'remove_thinking_sections'
              - 'default_params'
          - api_key: Global API key (fallback if a model config does not include its own)
          - base_url: Global base URL (fallback if a model config does not include its own)
          - json_only: Global default for JSON enforcement (overridden by model config)
          - remove_thinking_sections: Global default for thinking tag removal (overridden by model config)
          - default_params: Global default hyperparameters (overridden by model-specific defaults)
          - max_attempts: Number of retry attempts per model (global)
        """
        self.models: List[Dict[str, Any]] = config.get("models", [])
        self.global_api_key: str = config.get("api_key")
        self.global_base_url: Optional[str] = config.get("base_url")
        self.global_json_only: bool = config.get("json_only", False)
        self.global_remove_thinking_sections: bool = config.get("remove_thinking_sections", False)
        self.global_default_params: Dict[str, Any] = config.get("default_params", {})
        self.max_attempts: int = config.get("max_attempts", 3)

        if not self.models:
            raise ValueError("You must provide at least one model in the 'models' list.")
        if not self.global_api_key:
            raise ValueError("You must provide a global OpenAI API key in the 'api_key' field.")
        if not all(isinstance(m, dict) and "model" in m for m in self.models):
            raise ValueError("Each model must be provided as a dict with at least a 'model' key.")

    def _post_process(self, text: str, json_only: bool, remove_thinking_sections: bool) -> str:
        if remove_thinking_sections:
            text = remove_think_sections(text)
        if json_only:
            text = repair_json(text)
        return text

    def _chat_completion(self, client, model: str, messages: List[Dict[str, str]], params: Dict[str, Any]) -> str:
        response = client.chat.completions.create(model=model, messages=messages, **params)
        return response.choices[0].message.content

    def _completion(self, client, model: str, prompt: str, params: Dict[str, Any]) -> str:
        response = client.completions.create(model=model, prompt=prompt, **params)
        return response.choices[0].text

    def _call_chat(self, client, model: str, messages: List[Dict[str, str]], params: Dict[str, Any],
                   json_only: bool, remove_thinking_sections: bool) -> str:
        response = self._chat_completion(client, model, messages, params)
        return self._post_process(response, json_only, remove_thinking_sections)

    def _call_completion(self, client, model: str, prompt: str, params: Dict[str, Any],
                         json_only: bool, remove_thinking_sections: bool) -> str:
        response = self._completion(client, model, prompt, params)
        return self._post_process(response, json_only, remove_thinking_sections)

    def _retry_wrapper(self, func, *args, **kwargs) -> str:
        @retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((openai.OpenAIError, ValueError))
        )
        def wrapped():
            return func(*args, **kwargs)
        return wrapped()

    def chat(self, messages: List[Dict[str, str]], params: Optional[Dict[str, Any]] = None) -> str:
        last_exception = None
        for model_config in self.models:
            effective_api_key = model_config.get("api_key", self.global_api_key)
            effective_base_url =

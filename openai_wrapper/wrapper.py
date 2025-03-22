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
        self.models: List[str] = config.get("models", [])
        self.api_key: str = config.get("api_key")
        self.base_url: Optional[str] = config.get("base_url")
        self.json_only: bool = config.get("json_only", False)
        self.remove_thinking_sections: bool = config.get("remove_thinking_sections", False)
        self.default_params: Dict[str, Any] = config.get("default_params", {})
        self.max_attempts: int = config.get("max_attempts", 3)

        if not self.models:
            raise ValueError("You must provide at least one model in the 'models' list.")
        if not self.api_key:
            raise ValueError("You must provide an OpenAI API key in the 'api_key' field.")

        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _post_process(self, text: str) -> str:
        if self.remove_thinking_sections:
            text = remove_thinking_sections(text)
        if self.json_only:
            text = repair_json(text)
        return text

    def _chat_completion(self, model: str, messages: List[Dict[str, str]], params: Dict[str, Any]) -> str:
        response = self.client.chat.completions.create(model=model, messages=messages, **params)
        return response.choices[0].message.content

    def _completion(self, model: str, prompt: str, params: Dict[str, Any]) -> str:
        response = self.client.completions.create(model=model, prompt=prompt, **params)
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
        combined_params = {**self.default_params, **(params or {})}
        last_exception = None
        for model in self.models:
            try:
                response = self._retry_wrapper(self._chat_completion, model, messages, combined_params)
                return self._post_process(response)
            except Exception as e:
                last_exception = e
        raise last_exception

    def generate(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        combined_params = {**self.default_params, **(params or {})}
        last_exception = None
        for model in self.models:
            try:
                response = self._retry_wrapper(self._completion, model, prompt, combined_params)
                return self._post_process(response)
            except Exception as e:
                last_exception = e
        raise last_exception

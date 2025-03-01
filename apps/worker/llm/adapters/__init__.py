from typing import Dict, Optional
from config.settings import config
import importlib
import os
import json


class LlmAdapter:
    client: Optional[object] = None
    client_class: Optional[str] = None
    model_name: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_api_key: Optional[str] = None

    def __init__(self,
                 model: Optional[str] = None,
                 system_prompt: Optional[str] = None,
                 client_class: Optional[str] = None,
                 llm_api_key: Optional[str] = None) -> None:
        """The class constructor

        Args:
            model (Optional[str]): Model name. Defaults to None.
            system_prompt (Optional[str]): System prompt. Defaults to None.
            client_class (Optional[str]): Client class name. Defaults to None.
            llm_api_key (Optional[str]): LLM API key. Defaults to None.
        """
        if model is None and system_prompt is None and client_class is None:
            self.model_name = config.MODEL_NAME
            self.client_class = config.ADAPTER_CLASS
            self.system_prompt = config.SYSTEM_PROMPT
        else:
            self.system_prompt = system_prompt
            self.model_name = model
            self.client_class = client_class

        self.load_client_class()

    def load_client_class(self) -> None:
        """Loads the client class dynamically based on the client_class attribute."""
        try:
            module_name = f'llm.adapters.{self.client_class.lower().replace("adapter", "")}'
            module = importlib.import_module(module_name)
            class_ = getattr(module, self.client_class)
            self.client = class_(model=self.model_name, system_prompt=self.system_prompt)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import {self.client_class} from {module_name}: {e}")

    def get_client(self) -> Optional[object]:
        """Returns the client instance.

        Returns:
            Optional[object]: The client instance.
        """
        return self.client

    def completions(self, user_prompt: str) -> str:
        """Generates completions for the given user prompt.

        Args:
            user_prompt (str): The user prompt.

        Returns:
            str: The generated completion.
        """
        if self.client:
            return self.client.completions(user_prompt)
        raise ValueError("Client is not initialized")

    def generation(self, user_prompt: str) -> Dict:
        """Generates a response for the given user prompt.

        Args:
            user_prompt (str): The user prompt.

        Returns:
            Dict: The generated response.
        """
        if self.client:
            return self.client.generation(user_prompt)
        raise ValueError("Client is not initialized")

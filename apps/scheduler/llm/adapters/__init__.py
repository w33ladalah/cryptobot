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
        module = importlib.import_module(f'llm.adapters.{self.client_class.lower().replace('adapter', '')}')
        class_ = getattr(module, f'{self.client_class}')

        self.client = class_(model=self.model_name, system_prompt=self.system_prompt)

    def get_client(self) -> object:
        return self.client

    def completions(self, user_prompt):
        return self.client.completions(user_prompt)

    def generation(self, user_prompt) -> Dict:
        return self.client.generation(user_prompt)

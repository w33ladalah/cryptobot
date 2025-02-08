from ollama import Client as Ollama
from config.settings import config
from devtools import debug
import json


class LlamaAdapter:
    client: Ollama
    system_prompt: str
    model: str

    def __init__(self, model, system_prompt) -> None:
        self.client = Ollama(host=config.API_OLLAMA_URL)
        self.model = model
        self.system_prompt = system_prompt

    def completions(self, user_message):
        completion = self.client.chat(model=self.model, messages=[
            {
                'role': 'system', 'content': self.system_prompt,
            },
            {
                'role': 'user', 'content': user_message,
            }
        ])

        return completion['message']['content']

    def generation(self):
        pass

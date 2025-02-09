from ollama import Client as Ollama
from config.settings import config
from typing import Optional
import traceback


class LlamaAdapter:
    """Llama adapter class for text generation tasks.

    Attributes:
        client: The Ollama API client instance.
        model: The model to use for text generation.
        system_prompt: The system prompt for the adapter.
        api_key: The API key required for connecting to the Ollama API.

    Methods:
        __init__(self, model, system_prompt): Initializes the adapter with a model name, system prompt, and API key.
        completions(self, user_message): Generates a completion based on the provided user message using the current model and API key.
    """

    def __init__(self, model: str, system_prompt: str = "") -> None:
        self.client = Ollama(host=config.API_OLLAMA_URL)
        self.model = model
        self.system_prompt = system_prompt

    def completions(self, user_message: str) -> Optional[str]:
        """Generate a completion based on the provided user message using the current API key and model.

        Args:
            user_message: The text to generate a completion for.

        Returns:
            Optional[str]: The generated completion if successful; otherwise, returns None.
        """

        try:
            completion = self.client.chat(model=self.model, messages=[
                {
                    'role': 'system', 'content': self.system_prompt,
                },
                {
                    'role': 'user', 'content': user_message,
                }
            ])

            return completion['message']['content']
        except Exception as e:
            traceback.print_exc()
            return None

    def generation(self):
        pass

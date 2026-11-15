from config.settings import config
from openai import OpenAI as OpenAIClient
from typing import Optional
from devtools import debug
from urllib.parse import urlparse
import traceback
import uuid

OPENCODE_HOST = "opencode.ai"
OPENCODE_USER_AGENT = "cryptobot-worker/0.1"


class OpenAiAdapter:
    """OpenAI adapter class for generating completions and text generation tasks.

    Attributes:
        client: The OpenAI API client instance.
        model: The model to use for generation.
        system_prompt: The system prompt for the adapter.
        api_key: The API key required for connecting to the OpenAI API.

    Methods:
        __init__(self, model, system_prompt, api_key): Initializes the adapter with a model name, system prompt, and API key.
        completions(self, user_message): Generates a completion based on the provided user message using the current model and API key.
    """

    base_url: str
    client: OpenAIClient
    system_prompt: str
    model: str

    def __init__(self, model: str, system_prompt: str = "") -> None:
        base_url = config.LLM_BASE_URL
        client_kwargs = {
            "api_key": config.LLM_API_KEY.get_secret_value(),
            "base_url": base_url,
        }
        if isinstance(base_url, str) and base_url:
            hostname = urlparse(base_url).hostname
            if hostname and hostname.lower() == OPENCODE_HOST:
                self.session_id = str(uuid.uuid4())
                client_kwargs["default_headers"] = {
                    "x-opencode-session": self.session_id,
                    "User-Agent": OPENCODE_USER_AGENT,
                }
        self.client = OpenAIClient(**client_kwargs)
        self.model = model
        self.system_prompt = system_prompt
        self.base_url = base_url

    def completions(self, user_message) -> Optional[str]:
        """Generate a completion based on the provided user message using the current API key and model.

        Args:
            user_message: The text to generate a completion for.

        Returns:
            Optional[str]: The generated completion if successful; otherwise, returns None.
        """
        try:
            # Generate completion
            completion = self.client.chat.completions.create(
                model=self.model,
                extra_body={},
                messages=[
                {
                    'role': 'system', 'content': self.system_prompt,
                },
                {
                    'role': 'user', 'content': user_message,
                }
            ])

            completion_content = completion.choices[0] \
                .message \
                .content \
                .replace("```json", "") \
                .replace("```", "") \
                .strip()

            debug(completion_content)

            return completion_content
        except Exception as e:
            traceback.print_exc()
            return None

    def generation(self):
        pass

from config.settings import config
from typing import Optional
import replicate
import traceback


class ReplicateAdapter:
    """Replicate adapter class for generating completions via Replicate-hosted models.

    Attributes:
        client: The Replicate API client instance.
        model: The Replicate model identifier to run (e.g. "owner/model-name" or "owner/model-name:version").
        system_prompt: The system prompt for the adapter.

    Methods:
        __init__(self, model, system_prompt): Initializes the adapter with a model identifier and system prompt.
        completions(self, user_message): Generates a completion based on the provided user message using the current model.
    """

    model: str
    system_prompt: str

    def __init__(self, model: str, system_prompt: str = "") -> None:
        self.client = replicate.Client(api_token=config.LLM_API_KEY.get_secret_value())
        self.model = model
        self.system_prompt = system_prompt

    def completions(self, user_message: str) -> Optional[str]:
        """Generate a completion based on the provided user message using the current model.

        Args:
            user_message: The text to generate a completion for.

        Returns:
            Optional[str]: The generated completion if successful; otherwise, returns None.
        """
        try:
            output = self.client.run(
                self.model,
                input={
                    "prompt": user_message,
                    "system_prompt": self.system_prompt,
                }
            )

            # replicate.Client.run() returns an iterator of string chunks for most
            # text-generation models — join them into a single string. google/gemini-2.5-flash
            # is the model actually being used now (see Context above) — confirm this
            # join logic actually matches its real return shape via a live test call
            # (see acceptance criteria), and adjust if it returns a single string or a
            # list instead of a generator, rather than leaving it as an assumption.
            if isinstance(output, str):
                completion_content = output
            else:
                completion_content = "".join(str(chunk) for chunk in output)

            return completion_content.replace("```json", "").replace("```", "").strip()
        except Exception as e:
            traceback.print_exc()
            return None

    def generation(self):
        pass

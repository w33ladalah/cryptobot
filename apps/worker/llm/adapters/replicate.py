from config.settings import config
from typing import Optional
import replicate
import traceback
import time


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

        Uses Replicate's async prediction API directly (predictions.create + poll)
        rather than client.run()'s internal polling, so a caller-configurable timeout
        and explicit terminal-state handling (succeeded/failed/canceled) are possible.
        client.run() blocks indefinitely with no timeout and collapses all failure
        modes (timeout, model failure, network error) into the same generic exception.

        Args:
            user_message: The text to generate a completion for.

        Returns:
            Optional[str]: The generated completion if successful; otherwise, returns None.
        """
        try:
            prediction = self.client.predictions.create(
                model=self.model,
                input={
                    "prompt": user_message,
                    "system_instruction": self.system_prompt,
                }
            )

            timeout_seconds = config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS
            poll_interval_seconds = 1
            elapsed = 0

            while prediction.status not in ("succeeded", "failed", "canceled"):
                if elapsed >= timeout_seconds:
                    print(
                        f"ReplicateAdapter: prediction {prediction.id} timed out after "
                        f"{timeout_seconds}s (last status: {prediction.status})"
                    )
                    return None
                time.sleep(poll_interval_seconds)
                elapsed += poll_interval_seconds
                prediction.reload()

            if prediction.status == "failed":
                print(f"ReplicateAdapter: prediction {prediction.id} failed: {prediction.error}")
                return None

            if prediction.status == "canceled":
                print(f"ReplicateAdapter: prediction {prediction.id} was canceled")
                return None

            output = prediction.output

            # Confirmed against google/gemini-2.5-flash's published output schema
            # (https://replicate.com/google/gemini-2.5-flash/api/schema): Output type
            # is string[] — an array of strings, not a single string. The join below
            # handles that correctly. If ADAPTER_CLASS is ever pointed at a different
            # Replicate model, re-check that model's own output schema — the shape is
            # not guaranteed to be the same across models.
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

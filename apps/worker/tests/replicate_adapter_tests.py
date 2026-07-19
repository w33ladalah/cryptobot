import unittest
from unittest.mock import patch, MagicMock
from llm.adapters.replicate import ReplicateAdapter


class TestReplicateAdapter(unittest.TestCase):
    """Test ReplicateAdapter implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = "google/gemini-2.5-flash"
        self.system_prompt = "You are a helpful assistant."

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    @patch('llm.adapters.replicate.time.sleep')
    @patch('llm.adapters.replicate.print')
    def test_completions_succeeded_with_list_output(self, mock_print, mock_sleep, mock_client_class, mock_config):
        """Test that completions() succeeds with output as a list of strings and strips json fences."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS = 120

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_prediction = MagicMock()
        mock_prediction.id = "pred-123"
        mock_prediction.status = "succeeded"
        mock_prediction.output = ["```json", '{"decision": "BUY"}', "```"]
        mock_client.predictions.create.return_value = mock_prediction

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertEqual(result, '{"decision": "BUY"}')

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    @patch('llm.adapters.replicate.time.sleep')
    @patch('llm.adapters.replicate.print')
    def test_completions_succeeded_with_string_output(self, mock_print, mock_sleep, mock_client_class, mock_config):
        """Test that completions() succeeds with output as a single string."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS = 120

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_prediction = MagicMock()
        mock_prediction.id = "pred-123"
        mock_prediction.status = "succeeded"
        mock_prediction.output = "BUY"
        mock_client.predictions.create.return_value = mock_prediction

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertEqual(result, "BUY")

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    @patch('llm.adapters.replicate.time.sleep')
    @patch('llm.adapters.replicate.print')
    def test_completions_timeout_returns_none(self, mock_print, mock_sleep, mock_client_class, mock_config):
        """Test that completions() returns None when prediction times out."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS = 2

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_prediction = MagicMock()
        mock_prediction.id = "pred-123"
        mock_prediction.status = "processing"  # Never reaches terminal state
        mock_client.predictions.create.return_value = mock_prediction

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertIsNone(result)

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    @patch('llm.adapters.replicate.time.sleep')
    @patch('llm.adapters.replicate.print')
    def test_completions_failed_returns_none(self, mock_print, mock_sleep, mock_client_class, mock_config):
        """Test that completions() returns None when prediction status is failed."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS = 120

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_prediction = MagicMock()
        mock_prediction.id = "pred-123"
        mock_prediction.status = "failed"
        mock_prediction.error = "Model error"
        mock_client.predictions.create.return_value = mock_prediction

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertIsNone(result)

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    @patch('llm.adapters.replicate.time.sleep')
    @patch('llm.adapters.replicate.print')
    def test_completions_canceled_returns_none(self, mock_print, mock_sleep, mock_client_class, mock_config):
        """Test that completions() returns None when prediction status is canceled."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS = 120

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_prediction = MagicMock()
        mock_prediction.id = "pred-123"
        mock_prediction.status = "canceled"
        mock_client.predictions.create.return_value = mock_prediction

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertIsNone(result)

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    @patch('llm.adapters.replicate.time.sleep')
    @patch('llm.adapters.replicate.traceback.print_exc')
    def test_completions_exception_returns_none(self, mock_print_exc, mock_sleep, mock_client_class, mock_config):
        """Test that completions() returns None when client.predictions.create raises an exception."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS = 120

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.predictions.create.side_effect = Exception("API error")

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertIsNone(result)

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    @patch('llm.adapters.replicate.time.sleep')
    @patch('llm.adapters.replicate.print')
    def test_completions_calls_create_with_correct_input_dict(self, mock_print, mock_sleep, mock_client_class, mock_config):
        """Test that completions() calls predictions.create with correct input dict containing prompt and system_instruction."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS = 120

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_prediction = MagicMock()
        mock_prediction.id = "pred-123"
        mock_prediction.status = "succeeded"
        mock_prediction.output = "BUY"
        mock_client.predictions.create.return_value = mock_prediction

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        adapter.completions("What should I do?")

        mock_client.predictions.create.assert_called_once()
        call_args = mock_client.predictions.create.call_args

        self.assertEqual(call_args.kwargs['model'], self.model)
        self.assertIn('input', call_args.kwargs)
        self.assertEqual(call_args.kwargs['input']['prompt'], "What should I do?")
        self.assertEqual(call_args.kwargs['input']['system_instruction'], self.system_prompt)

    @patch('llm.adapters.replicate.config')
    @patch('llm.adapters.replicate.replicate.Client')
    def test_generation_returns_none(self, mock_client_class, mock_config):
        """Test that generation() returns None (placeholder method)."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"

        adapter = ReplicateAdapter(self.model, self.system_prompt)
        result = adapter.generation()

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

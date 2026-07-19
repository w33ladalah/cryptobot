import unittest
from unittest.mock import patch, MagicMock
from llm.adapters.openai import OpenAiAdapter


class TestOpenAiAdapter(unittest.TestCase):
    """Test OpenAiAdapter implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = "gpt-4"
        self.system_prompt = "You are a helpful assistant."

    @patch('llm.adapters.openai.config')
    @patch('llm.adapters.openai.OpenAIClient')
    @patch('llm.adapters.openai.debug')
    def test_completions_happy_path_strips_json_fences(self, mock_debug, mock_client_class, mock_config):
        """Test that completions() strips ```json``` fences and surrounding whitespace from the response."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_BASE_URL = "https://api.openai.com/v1"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "```json\n{\"decision\": \"BUY\"}\n```"
        mock_client.chat.completions.create.return_value = mock_completion

        adapter = OpenAiAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertEqual(result, "{\"decision\": \"BUY\"}")

    @patch('llm.adapters.openai.config')
    @patch('llm.adapters.openai.OpenAIClient')
    @patch('llm.adapters.openai.debug')
    def test_completions_calls_client_with_correct_args(self, mock_debug, mock_client_class, mock_config):
        """Test that completions() calls the client with correct model and two-message structure."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_BASE_URL = "https://api.openai.com/v1"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "BUY"
        mock_client.chat.completions.create.return_value = mock_completion

        adapter = OpenAiAdapter(self.model, self.system_prompt)
        adapter.completions("What should I do?")

        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args

        self.assertEqual(call_args.kwargs['model'], self.model)
        self.assertEqual(len(call_args.kwargs['messages']), 2)
        self.assertEqual(call_args.kwargs['messages'][0]['role'], 'system')
        self.assertEqual(call_args.kwargs['messages'][0]['content'], self.system_prompt)
        self.assertEqual(call_args.kwargs['messages'][1]['role'], 'user')
        self.assertEqual(call_args.kwargs['messages'][1]['content'], "What should I do?")

    @patch('llm.adapters.openai.config')
    @patch('llm.adapters.openai.OpenAIClient')
    @patch('llm.adapters.openai.traceback.print_exc')
    def test_completions_exception_returns_none(self, mock_print_exc, mock_client_class, mock_config):
        """Test that completions() returns None when client raises an exception."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_BASE_URL = "https://api.openai.com/v1"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")

        adapter = OpenAiAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertIsNone(result)

    @patch('llm.adapters.openai.config')
    @patch('llm.adapters.openai.OpenAIClient')
    def test_generation_returns_none(self, mock_client_class, mock_config):
        """Test that generation() returns None (placeholder method)."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_BASE_URL = "https://api.openai.com/v1"

        adapter = OpenAiAdapter(self.model, self.system_prompt)
        result = adapter.generation()

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from llm.adapters.llama import LlamaAdapter


class TestLlamaAdapter(unittest.TestCase):
    """Test LlamaAdapter implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = "llama2"
        self.system_prompt = "You are a helpful assistant."

    @patch('llm.adapters.llama.config')
    @patch('llm.adapters.llama.Ollama')
    @patch('llm.adapters.llama.logger')
    def test_completions_happy_path_returns_content(self, mock_logger, mock_client_class, mock_config):
        """Test that completions() returns the content string from the response."""
        mock_config.API_OLLAMA_URL = "http://localhost:11434"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.chat.return_value = {
            'message': {
                'content': 'BUY'
            }
        }

        adapter = LlamaAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertEqual(result, 'BUY')

    @patch('llm.adapters.llama.config')
    @patch('llm.adapters.llama.Ollama')
    @patch('llm.adapters.llama.logger')
    def test_completions_calls_client_with_correct_args(self, mock_logger, mock_client_class, mock_config):
        """Test that completions() calls the client with correct model and two-message structure."""
        mock_config.API_OLLAMA_URL = "http://localhost:11434"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.chat.return_value = {
            'message': {
                'content': 'BUY'
            }
        }

        adapter = LlamaAdapter(self.model, self.system_prompt)
        adapter.completions("What should I do?")

        mock_client.chat.assert_called_once()
        call_args = mock_client.chat.call_args

        self.assertEqual(call_args.kwargs['model'], self.model)
        self.assertEqual(len(call_args.kwargs['messages']), 2)
        self.assertEqual(call_args.kwargs['messages'][0]['role'], 'system')
        self.assertEqual(call_args.kwargs['messages'][0]['content'], self.system_prompt)
        self.assertEqual(call_args.kwargs['messages'][1]['role'], 'user')
        self.assertEqual(call_args.kwargs['messages'][1]['content'], "What should I do?")

    @patch('llm.adapters.llama.config')
    @patch('llm.adapters.llama.Ollama')
    @patch('llm.adapters.llama.logger')
    def test_completions_keyerror_returns_none(self, mock_logger, mock_client_class, mock_config):
        """Test that completions() catches KeyError and returns None."""
        mock_config.API_OLLAMA_URL = "http://localhost:11434"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.chat.return_value = {
            'message': {}  # Missing 'content' key
        }

        adapter = LlamaAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertIsNone(result)

    @patch('llm.adapters.llama.config')
    @patch('llm.adapters.llama.Ollama')
    @patch('llm.adapters.llama.logger')
    def test_completions_generic_exception_returns_none(self, mock_logger, mock_client_class, mock_config):
        """Test that completions() catches generic exceptions and returns None."""
        mock_config.API_OLLAMA_URL = "http://localhost:11434"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.side_effect = Exception("Network error")

        adapter = LlamaAdapter(self.model, self.system_prompt)
        result = adapter.completions("What should I do?")

        self.assertIsNone(result)

    @patch('llm.adapters.llama.config')
    @patch('llm.adapters.llama.Ollama')
    def test_generation_returns_none(self, mock_client_class, mock_config):
        """Test that generation() returns None (placeholder method)."""
        mock_config.API_OLLAMA_URL = "http://localhost:11434"

        adapter = LlamaAdapter(self.model, self.system_prompt)
        result = adapter.generation()

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

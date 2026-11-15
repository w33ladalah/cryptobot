import unittest
import uuid
from unittest.mock import patch, MagicMock

import httpx
from openai import OpenAI as RealOpenAIClient

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
    def test_opencode_host_adds_session_and_user_agent_headers(self, mock_client_class, mock_config):
        """Test that an opencode.ai base URL adds the session and user agent headers."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_BASE_URL = "https://opencode.ai/zen/go/v1"

        adapter = OpenAiAdapter(self.model, self.system_prompt)

        mock_client_class.assert_called_once()
        client_kwargs = mock_client_class.call_args.kwargs
        default_headers = client_kwargs["default_headers"]

        self.assertEqual(default_headers["User-Agent"], "cryptobot-worker/0.1")
        self.assertEqual(default_headers["x-opencode-session"], adapter.session_id)
        uuid.UUID(default_headers["x-opencode-session"])

    @patch('llm.adapters.openai.config')
    @patch('llm.adapters.openai.OpenAIClient')
    @patch('llm.adapters.openai.debug')
    def test_opencode_session_id_is_stable_per_adapter_instance(self, mock_debug, mock_client_class, mock_config):
        """Test that one adapter reuses its session id and separate adapters get different ids."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_BASE_URL = "https://opencode.ai/zen/go/v1"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "BUY"
        mock_client.chat.completions.create.return_value = mock_completion

        first_adapter = OpenAiAdapter(self.model, self.system_prompt)
        first_session_id = first_adapter.session_id
        first_adapter.completions("What should I do?")
        first_adapter.completions("What should I do?")

        second_adapter = OpenAiAdapter(self.model, self.system_prompt)

        self.assertEqual(first_adapter.session_id, first_session_id)
        self.assertNotEqual(first_adapter.session_id, second_adapter.session_id)
        self.assertEqual(mock_client_class.call_count, 2)
        self.assertEqual(
            mock_client_class.call_args_list[0].kwargs["default_headers"]["x-opencode-session"],
            first_session_id,
        )
        self.assertEqual(
            mock_client_class.call_args_list[1].kwargs["default_headers"]["x-opencode-session"],
            second_adapter.session_id,
        )

    @patch('llm.adapters.openai.config')
    @patch('llm.adapters.openai.OpenAIClient')
    def test_non_opencode_hosts_do_not_add_default_headers(self, mock_client_class, mock_config):
        """Test that non-opencode.ai base URLs do not receive default_headers."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        base_urls = [
            "https://openrouter.ai/api/v1",
            "https://api.openai.com/v1",
            "https://opencode.ai.evil.example/v1",
            "https://notopencode.ai/v1",
        ]

        for base_url in base_urls:
            with self.subTest(base_url=base_url):
                mock_config.LLM_BASE_URL = base_url
                OpenAiAdapter(self.model, self.system_prompt)

        self.assertEqual(mock_client_class.call_count, len(base_urls))
        for call in mock_client_class.call_args_list:
            self.assertNotIn("default_headers", call.kwargs)

    @patch('llm.adapters.openai.config')
    @patch('llm.adapters.openai.OpenAIClient')
    @patch('llm.adapters.openai.debug')
    def test_opencode_headers_are_sent_on_wire(self, mock_debug, mock_client_class, mock_config):
        """Test that the real OpenAI SDK sends the OpenCode headers on the request."""
        mock_config.LLM_API_KEY.get_secret_value.return_value = "test-api-key"
        mock_config.LLM_BASE_URL = "https://opencode.ai/zen/go/v1"
        recorded_requests = []

        def handler(request):
            recorded_requests.append(dict(request.headers))
            return httpx.Response(
                200,
                json={
                    "id": "chatcmpl-test",
                    "object": "chat.completion",
                    "created": 0,
                    "model": self.model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "BUY"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                },
            )

        def client_factory(*args, **kwargs):
            kwargs["http_client"] = httpx.Client(transport=httpx.MockTransport(handler))
            return RealOpenAIClient(*args, **kwargs)

        mock_client_class.side_effect = client_factory

        adapter = OpenAiAdapter(self.model, self.system_prompt)
        result = adapter.completions("test")
        adapter.client.close()

        self.assertEqual(result, "BUY")
        self.assertEqual(len(recorded_requests), 1)
        self.assertEqual(recorded_requests[0]["x-opencode-session"], adapter.session_id)
        self.assertEqual(recorded_requests[0]["user-agent"], "cryptobot-worker/0.1")

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

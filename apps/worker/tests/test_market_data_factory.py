import unittest
from unittest.mock import patch, MagicMock
from pydantic import SecretStr
from core.market_data import _get_market_data_provider, get_historical_data


class TestMarketDataFactory(unittest.TestCase):
    """Test the market data provider factory function."""

    @patch('core.market_data.config')
    def test_factory_loads_geckoterminal_provider(self, mock_config):
        """Test that factory loads GeckoTerminalProvider when configured."""
        mock_config.MARKET_DATA_PROVIDER_CLASS = "GeckoTerminalProvider"
        mock_config.GECKOTERMINAL_API = "https://api.geckoterminal.com/api/v2"

        provider = _get_market_data_provider()

        self.assertIsNotNone(provider)
        self.assertEqual(provider.__class__.__name__, "GeckoTerminalProvider")

    @patch('core.market_data.config')
    def test_factory_loads_dexscreener_provider(self, mock_config):
        """Test that factory loads DexScreenerProvider when configured."""
        mock_config.MARKET_DATA_PROVIDER_CLASS = "DexScreenerProvider"
        mock_config.DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/"

        provider = _get_market_data_provider()

        self.assertIsNotNone(provider)
        self.assertEqual(provider.__class__.__name__, "DexScreenerProvider")

    @patch('core.market_data.config')
    def test_factory_raises_error_for_unknown_provider(self, mock_config):
        """Test that factory raises ImportError for unknown provider."""
        mock_config.MARKET_DATA_PROVIDER_CLASS = "UnknownProvider"

        with self.assertRaises(ImportError):
            _get_market_data_provider()


class TestGetHistoricalData(unittest.TestCase):
    """Test get_historical_data function, specifically header construction."""

    @patch('core.market_data.httpx.get')
    @patch('core.market_data.config')
    def test_no_api_key_no_authorization_header(self, mock_config, mock_get):
        """Test that no Authorization header is sent when COINGECKO_API_KEY is None."""
        mock_config.COINGECKO_API_KEY = None
        mock_config.COINGECKO_API = "https://api.coingecko.com/api/v3"
        mock_get.return_value.json.return_value = {"prices": [[1234567890000, 100.0]]}

        result = get_historical_data("bitcoin")

        # Verify httpx.get was called with empty headers dict (no Authorization)
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        self.assertEqual(call_kwargs['headers'], {})
        self.assertIsNotNone(result)

    @patch('core.market_data.httpx.get')
    @patch('core.market_data.config')
    def test_with_api_key_sends_bearer_header(self, mock_config, mock_get):
        """Test that Authorization header with Bearer token is sent when COINGECKO_API_KEY is set."""
        mock_config.COINGECKO_API_KEY = SecretStr("test-api-key-12345")
        mock_config.COINGECKO_API = "https://api.coingecko.com/api/v3"
        mock_get.return_value.json.return_value = {"prices": [[1234567890000, 100.0]]}

        result = get_historical_data("ethereum")

        # Verify httpx.get was called with proper Authorization header
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        self.assertIn("Authorization", call_kwargs['headers'])
        self.assertEqual(call_kwargs['headers']['Authorization'], "Bearer test-api-key-12345")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()

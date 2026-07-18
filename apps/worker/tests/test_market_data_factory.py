import unittest
from unittest.mock import patch, MagicMock
from core.market_data import _get_market_data_provider


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


if __name__ == '__main__':
    unittest.main()

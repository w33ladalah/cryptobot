import unittest
from unittest.mock import patch, MagicMock
from core.market_data_providers.dexscreener import DexScreenerProvider


class TestDexScreenerProvider(unittest.TestCase):
    """Test DexScreenerProvider implementation of MarketDataProvider."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = DexScreenerProvider("https://api.dexscreener.com/latest/dex/")

    @patch('core.market_data_providers.dexscreener.httpx.get')
    def test_search_token_pairs_returns_pairs(self, mock_get):
        """Test that search_token_pairs returns pairs from DexScreener API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "pairs": [
                {
                    "chainId": "ethereum",
                    "pairAddress": "0x1234567890123456789012345678901234567890",
                    "baseToken": {
                        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                        "symbol": "USDC",
                        "name": "USD Coin"
                    },
                    "quoteToken": {
                        "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                        "symbol": "WETH",
                        "name": "Wrapped Ether"
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.search_token_pairs("USDC")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["chainId"], "ethereum")
        self.assertEqual(result[0]["pairAddress"], "0x1234567890123456789012345678901234567890")

    @patch('core.market_data_providers.dexscreener.httpx.get')
    def test_search_token_pairs_handles_empty_response(self, mock_get):
        """Test that search_token_pairs handles empty response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"pairs": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.search_token_pairs("NONEXISTENT")

        self.assertEqual(len(result), 0)

    @patch('core.market_data_providers.dexscreener.httpx.get')
    def test_get_realtime_data_returns_correct_format(self, mock_get):
        """Test that get_realtime_data returns data in the correct format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "pairs": [
                {
                    "priceUsd": "1843.24",
                    "liquidity": {"usd": "92526625.6817"},
                    "priceChange": {"h1": "-0.038"}
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.provider.get_realtime_data("ethereum", "0x1234567890123456789012345678901234567890")

        self.assertIsNotNone(result)
        self.assertEqual(result["price"], 1843.24)
        self.assertEqual(result["liquidity"], 92526625.6817)
        self.assertEqual(result["price_change_1h"], -0.038)

    @patch('core.market_data_providers.dexscreener.httpx.get')
    def test_get_realtime_data_returns_none_for_no_pairs(self, mock_get):
        """Test that get_realtime_data returns None when no pairs found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"pairs": []}
        mock_get.return_value = mock_response

        result = self.provider.get_realtime_data("ethereum", "0x1234567890123456789012345678901234567890")

        self.assertIsNone(result)

    @patch('core.market_data_providers.dexscreener.httpx.get')
    def test_get_realtime_data_handles_missing_h1(self, mock_get):
        """Test that get_realtime_data handles missing h1 price change."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "pairs": [
                {
                    "priceUsd": "1843.24",
                    "liquidity": {"usd": "92526625.6817"},
                    "priceChange": {}
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.provider.get_realtime_data("ethereum", "0x1234567890123456789012345678901234567890")

        self.assertIsNotNone(result)
        self.assertEqual(result["price_change_1h"], 0.0)


if __name__ == '__main__':
    unittest.main()

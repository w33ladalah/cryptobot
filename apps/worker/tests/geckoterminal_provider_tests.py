import unittest
from unittest.mock import patch, MagicMock
from core.market_data_providers.geckoterminal import GeckoTerminalProvider


class TestGeckoTerminalProvider(unittest.TestCase):
    """Test GeckoTerminalProvider implementation of MarketDataProvider."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = GeckoTerminalProvider("https://api.geckoterminal.com/api/v2")

    @patch('core.market_data_providers.geckoterminal.httpx.get')
    def test_search_token_pairs_returns_pools_with_enriched_addresses(self, mock_get):
        """Test that search_token_pairs returns pools with extracted token addresses."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "eth_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
                    "type": "pool",
                    "attributes": {
                        "address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
                        "name": "WETH / USDC 0.05%"
                    },
                    "relationships": {
                        "base_token": {
                            "data": {
                                "id": "eth_0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                                "type": "token"
                            }
                        },
                        "quote_token": {
                            "data": {
                                "id": "eth_0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                                "type": "token"
                            }
                        }
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.search_token_pairs("USDC")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["base_token_address"], "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
        self.assertEqual(result[0]["quote_token_address"], "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")

    @patch('core.market_data_providers.geckoterminal.httpx.get')
    def test_search_token_pairs_with_network_filter(self, mock_get):
        """Test that search_token_pairs can filter by network."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.search_token_pairs("USDC", network="sepolia-testnet")

        # Verify the network parameter was passed
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("params", call_args.kwargs)
        self.assertEqual(call_args.kwargs["params"]["network"], "sepolia-testnet")

    @patch('core.market_data_providers.geckoterminal.httpx.get')
    def test_get_realtime_data_returns_correct_format(self, mock_get):
        """Test that get_realtime_data returns data in the correct format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "base_token_price_usd": "1843.24",
                    "reserve_in_usd": "92526625.6817",
                    "price_change_percentage": {
                        "h1": "-0.038"
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.get_realtime_data("mainnet", "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")

        self.assertIsNotNone(result)
        self.assertEqual(result["price"], 1843.24)
        self.assertEqual(result["liquidity"], 92526625.6817)
        self.assertEqual(result["price_change_1h"], -0.038)

    @patch('core.market_data_providers.geckoterminal.httpx.get')
    def test_get_realtime_data_maps_chain_to_network(self, mock_get):
        """Test that get_realtime_data maps chain names to GeckoTerminal network IDs."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "base_token_price_usd": "1843.24",
                    "reserve_in_usd": "92526625.6817",
                    "price_change_percentage": {"h1": "-0.038"}
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Test mainnet -> eth mapping
        self.provider.get_realtime_data("mainnet", "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
        call_args = mock_get.call_args
        self.assertIn("networks/eth/pools", call_args.args[0])

        # Test sepolia -> sepolia-testnet mapping
        self.provider.get_realtime_data("sepolia", "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
        call_args = mock_get.call_args
        self.assertIn("networks/sepolia-testnet/pools", call_args.args[0])

    @patch('core.market_data_providers.geckoterminal.httpx.get')
    def test_get_realtime_data_returns_none_for_no_data(self, mock_get):
        """Test that get_realtime_data returns None when no data found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.get_realtime_data("mainnet", "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")

        self.assertIsNone(result)

    @patch('core.market_data_providers.geckoterminal.httpx.get')
    def test_get_realtime_data_handles_missing_h1(self, mock_get):
        """Test that get_realtime_data handles missing h1 price change."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "base_token_price_usd": "1843.24",
                    "reserve_in_usd": "92526625.6817",
                    "price_change_percentage": {}
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.get_realtime_data("mainnet", "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")

        self.assertIsNotNone(result)
        self.assertEqual(result["price_change_1h"], 0.0)

    @patch('core.market_data_providers.geckoterminal.httpx.get')
    def test_get_realtime_data_uses_quote_price_when_base_missing(self, mock_get):
        """Test that get_realtime_data falls back to quote token price when base is missing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "quote_token_price_usd": "0.9996",
                    "reserve_in_usd": "92526625.6817",
                    "price_change_percentage": {"h1": "-0.038"}
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.provider.get_realtime_data("mainnet", "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")

        self.assertIsNotNone(result)
        self.assertEqual(result["price"], 0.9996)

    def test_extract_token_address(self):
        """Test that _extract_token_address correctly extracts address from token ID."""
        # Test with network prefix
        self.assertEqual(
            self.provider._extract_token_address("eth_0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"),
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        )

        # Test without network prefix
        self.assertEqual(
            self.provider._extract_token_address("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"),
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        )

    def test_map_chain_to_network(self):
        """Test that _map_chain_to_network correctly maps chain names."""
        self.assertEqual(self.provider._map_chain_to_network("mainnet"), "eth")
        self.assertEqual(self.provider._map_chain_to_network("sepolia"), "sepolia-testnet")
        self.assertEqual(self.provider._map_chain_to_network("ethereum"), "eth")
        self.assertEqual(self.provider._map_chain_to_network("unknown"), "unknown")


if __name__ == '__main__':
    unittest.main()

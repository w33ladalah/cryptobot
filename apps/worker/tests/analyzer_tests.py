import unittest
from tasks.analyzer import _resolve_token_address, _get_pair_chain_and_address


class TestAnalyzerTokenAddressResolution(unittest.TestCase):
    """Test token address resolution logic for different provider formats."""

    def test_dexscreener_base_token_match_by_address(self):
        """Test resolving token address matches base token by address (DexScreener format)."""
        pair = {
            "chainId": "ethereum",
            "pairAddress": "0x123...",
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
        
        result = _resolve_token_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", pair)
        self.assertEqual(result, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    def test_dexscreener_quote_token_match_by_address(self):
        """Test resolving token address matches quote token by address (DexScreener format)."""
        pair = {
            "chainId": "ethereum",
            "pairAddress": "0x123...",
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
        
        result = _resolve_token_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", pair)
        self.assertEqual(result, "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    def test_dexscreener_base_token_match_by_symbol_case_insensitive(self):
        """Test resolving token address matches base token by symbol, case-insensitive."""
        pair = {
            "chainId": "ethereum",
            "pairAddress": "0x123...",
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
        
        result = _resolve_token_address("usdc", pair)
        self.assertEqual(result, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    def test_dexscreener_no_match_returns_none(self):
        """Test that no match returns None (DexScreener format)."""
        pair = {
            "chainId": "ethereum",
            "pairAddress": "0x123...",
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
        
        result = _resolve_token_address("NONEXISTENT", pair)
        self.assertIsNone(result)

    def test_geckoterminal_base_token_match_by_address(self):
        """Test resolving token address matches base token by address (GeckoTerminal format)."""
        pair = {
            "id": "eth_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "base_token_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "base_token_symbol": "WETH",
            "quote_token_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "quote_token_symbol": "USDC"
        }
        
        result = _resolve_token_address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", pair)
        self.assertEqual(result, "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    def test_geckoterminal_quote_token_match_by_symbol(self):
        """Test resolving token address matches quote token by symbol (GeckoTerminal format)."""
        pair = {
            "id": "eth_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "base_token_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "base_token_symbol": "WETH",
            "quote_token_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "quote_token_symbol": "USDC"
        }
        
        result = _resolve_token_address("usdc", pair)
        self.assertEqual(result, "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")

    def test_geckoterminal_no_match_returns_none(self):
        """Test that no match returns None (GeckoTerminal format)."""
        pair = {
            "id": "eth_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "base_token_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "base_token_symbol": "WETH",
            "quote_token_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "quote_token_symbol": "USDC"
        }
        
        result = _resolve_token_address("NONEXISTENT", pair)
        self.assertIsNone(result)


class TestAnalyzerPairExtraction(unittest.TestCase):
    """Test chain and address extraction from different provider formats."""

    def test_dexscreener_format_extraction(self):
        """Test extracting chain and address from DexScreener format."""
        pair = {
            "chainId": "ethereum",
            "pairAddress": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
        }
        
        chain, address = _get_pair_chain_and_address(pair)
        self.assertEqual(chain, "ethereum")
        self.assertEqual(address, "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")

    def test_geckoterminal_format_extraction(self):
        """Test extracting chain and address from GeckoTerminal format."""
        pair = {
            "address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
        }
        
        chain, address = _get_pair_chain_and_address(pair)
        self.assertEqual(chain, "mainnet")  # Defaults to mainnet for GeckoTerminal
        self.assertEqual(address, "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")

    def test_unknown_format_returns_none(self):
        """Test that unknown format returns None for both values."""
        pair = {
            "unknown_field": "value"
        }
        
        chain, address = _get_pair_chain_and_address(pair)
        self.assertIsNone(chain)
        self.assertIsNone(address)


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock, call
from tasks.analyzer import _resolve_token_address, _get_pair_chain_and_address, _map_chain_to_executor_network


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

    # NOTE: base_token_symbol/quote_token_symbol are not currently populated by GeckoTerminalProvider
    # - this test exercises _resolve_token_address's handling of that shape in case a future provider
    #   or enrichment step adds it; see the symbol-resolution follow-up prompt for the real fix
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


class TestAnalyzerChainMapping(unittest.TestCase):
    """Test chain to network mapping for EthereumExecutor compatibility."""

    def test_map_ethereum_to_mainnet(self):
        """Test mapping 'ethereum' to 'mainnet'."""
        self.assertEqual(_map_chain_to_executor_network('ethereum'), 'mainnet')

    def test_map_mainnet_to_mainnet(self):
        """Test mapping 'mainnet' to 'mainnet'."""
        self.assertEqual(_map_chain_to_executor_network('mainnet'), 'mainnet')

    def test_map_eth_to_mainnet(self):
        """Test mapping 'eth' to 'mainnet'."""
        self.assertEqual(_map_chain_to_executor_network('eth'), 'mainnet')

    def test_map_sepolia_to_sepolia(self):
        """Test mapping 'sepolia' to 'sepolia'."""
        self.assertEqual(_map_chain_to_executor_network('sepolia'), 'sepolia')

    def test_map_sepolia_testnet_to_sepolia(self):
        """Test mapping 'sepolia-testnet' to 'sepolia'."""
        self.assertEqual(_map_chain_to_executor_network('sepolia-testnet'), 'sepolia')

    def test_map_unknown_to_mainnet(self):
        """Test mapping unknown chain defaults to 'mainnet'."""
        self.assertEqual(_map_chain_to_executor_network('unknown'), 'mainnet')


class TestAnalyzerExecutionWiring(unittest.TestCase):
    """Test BUY/SELL execution wiring in perform_llm_analysis."""

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_buy_decision_triggers_execution(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that BUY decision triggers EthereumExecutor.execute() with correct parameters."""
        # Setup mocks
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]
        mock_search.return_value = [
            {
                'chainId': 'ethereum',
                'pairAddress': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                'baseToken': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'symbol': 'USDC'},
                'quoteToken': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'symbol': 'WETH'}
            }
        ]
        mock_realtime.return_value = {'price': 1843.24, 'liquidity': 92526625.68, 'price_change_1h': -0.038}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'BUY', 'confidence': 0.85}

        # Setup executor mock
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor

        # Import and call the function
        from tasks.analyzer import perform_llm_analysis
        perform_llm_analysis('USDC', store_results=False, network='ethereum')

        # Verify executor was instantiated with correct parameters
        mock_executor_class.assert_called_once_with(
            token_address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
            network='mainnet',
            provider='infura'
        )

        # Verify execute was called with BUY decision
        mock_executor.execute.assert_called_once_with(decision='BUY', amount_eth=0.001)

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_sell_decision_triggers_execution(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that SELL decision triggers EthereumExecutor.execute() with correct parameters."""
        # Setup mocks
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]
        mock_search.return_value = [
            {
                'chainId': 'ethereum',
                'pairAddress': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                'baseToken': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'symbol': 'USDC'},
                'quoteToken': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'symbol': 'WETH'}
            }
        ]
        mock_realtime.return_value = {'price': 1843.24, 'liquidity': 92526625.68, 'price_change_1h': -0.038}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'SELL', 'confidence': 0.75}

        # Setup executor mock
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor

        # Import and call the function
        from tasks.analyzer import perform_llm_analysis
        perform_llm_analysis('USDC', store_results=False, network='ethereum')

        # Verify executor was instantiated with correct parameters
        mock_executor_class.assert_called_once_with(
            token_address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
            network='mainnet',
            provider='infura'
        )

        # Verify execute was called with SELL decision
        mock_executor.execute.assert_called_once_with(decision='SELL', amount_tokens=None)

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_hold_decision_skips_execution(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that HOLD decision does not trigger execution."""
        # Setup mocks
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]
        mock_search.return_value = [
            {
                'chainId': 'ethereum',
                'pairAddress': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                'baseToken': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'symbol': 'USDC'},
                'quoteToken': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'symbol': 'WETH'}
            }
        ]
        mock_realtime.return_value = {'price': 1843.24, 'liquidity': 92526625.68, 'price_change_1h': -0.038}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function
        from tasks.analyzer import perform_llm_analysis
        perform_llm_analysis('USDC', store_results=False, network='ethereum')

        # Verify executor was never instantiated
        mock_executor_class.assert_not_called()

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_network_required_raises_error(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that missing network parameter raises ValueError."""
        # Setup mocks
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]

        # Import and call the function without network parameter
        from tasks.analyzer import perform_llm_analysis
        with self.assertRaises(ValueError) as context:
            perform_llm_analysis('USDC', store_results=False)

        self.assertIn("network parameter is required", str(context.exception))

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_sepolia_chain_maps_correctly(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that sepolia chain maps to sepolia network for executor."""
        # Setup mocks
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {'address': '0x1c7d4b196cb0c7b01d743fbc6116a902379c7238', 'symbol': 'USDC'},
                'quoteToken': {'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14', 'symbol': 'WETH'}
            }
        ]
        mock_realtime.return_value = {'price': 0.0949, 'liquidity': 4472909.23, 'price_change_1h': 0}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'BUY', 'confidence': 0.9}

        # Setup executor mock
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor

        # Import and call the function
        from tasks.analyzer import perform_llm_analysis
        perform_llm_analysis('USDC', store_results=False, network='sepolia')

        # Verify executor was instantiated with sepolia network
        mock_executor_class.assert_called_once_with(
            token_address='0x1c7d4b196cb0c7b01d743fbc6116a902379c7238',
            network='sepolia',
            provider='infura'
        )


if __name__ == '__main__':
    unittest.main()

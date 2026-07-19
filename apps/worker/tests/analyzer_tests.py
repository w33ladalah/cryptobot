import unittest
from unittest.mock import patch, MagicMock, call
from tasks.analyzer import _resolve_token_address, _get_pair_chain_and_address, _map_chain_to_executor_network, perform_llm_analysis, _is_price_plausible
import logging


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
                'baseToken': {'address': '0xbe72e441bf55620febc26715db68d3494213d8cb', 'symbol': 'USDC'},  # Correct Sepolia USDC from allowlist
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
            token_address='0xbe72e441bf55620febc26715db68d3494213d8cb',
            network='sepolia',
            provider='infura'
        )


class TestAnalyzerAddressVerification(unittest.TestCase):
    """Test token address verification against known allowlist (issue #31)."""

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_address_match_allowlist_proceeds(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that matching allowlist address proceeds to analysis."""
        # Setup mocks
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0xbe72e441bf55620febc26715db68d3494213d8cb',  # Correct Sepolia USDC
                    'symbol': 'USDC'
                },
                'quoteToken': {
                    'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                    'symbol': 'WETH'
                }
            }
        ]
        mock_realtime.return_value = {'price': 0.9998, 'liquidity': 4472909.23}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function
        perform_llm_analysis('USDC', store_results=False, network='sepolia')

        # Verify analysis proceeded (combine_data and analyze_with_llm were called)
        mock_combine.assert_called_once()
        mock_analyze.assert_called_once()

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    @patch('tasks.analyzer.logger')
    def test_address_mismatch_allowlist_skips_with_warning(self, mock_logger, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that mismatched address skips pair and logs warning (issue #31 scenario)."""
        # Setup mocks
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0x1c7d4b196cb0c7b01d743fbc6116a902379c7238',  # Wrong address (not Sepolia USDC)
                    'symbol': 'USDC'
                },
                'quoteToken': {
                    'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                    'symbol': 'WETH'
                }
            }
        ]
        mock_realtime.return_value = {'price': 0.111551, 'liquidity': 4472909.23}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function
        perform_llm_analysis('USDC', store_results=False, network='sepolia')

        # Verify analysis was skipped (combine_data and analyze_with_llm were NOT called)
        mock_combine.assert_not_called()
        mock_analyze.assert_not_called()

        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        self.assertIn('Token address mismatch', warning_call)
        self.assertIn('USDC', warning_call)
        self.assertIn('sepolia', warning_call)
        self.assertIn('0xbe72e441bf55620febc26715db68d3494213d8cb', warning_call)  # Expected
        self.assertIn('0x1c7d4b196cb0c7b01d743fbc6116a902379c7238', warning_call)  # Resolved

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_token_not_in_allowlist_proceeds(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that token not in allowlist proceeds without blocking."""
        # Setup mocks - using a token not in KNOWN_TOKEN_ADDRESSES
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 1000}]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0x1234567890123456789012345678901234567890',  # Some random token
                    'symbol': 'TOKENX'
                },
                'quoteToken': {
                    'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                    'symbol': 'WETH'
                }
            }
        ]
        mock_realtime.return_value = {'price': 1.5, 'liquidity': 4472909.23}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function
        perform_llm_analysis('TOKENX', store_results=False, network='sepolia')

        # Verify analysis proceeded (allowlist doesn't block unknown tokens)
        mock_combine.assert_called_once()
        mock_analyze.assert_called_once()


class TestAnalyzerPricePlausibility(unittest.TestCase):
    """Test price plausibility check for stablecoins (issue #34)."""

    def test_is_price_plausible_stablecoin_within_threshold(self):
        """Test that stablecoin price within threshold is considered plausible."""
        historical_data = [
            {'date': '2024-01-01', 'price': 0.9998},
            {'date': '2024-01-02', 'price': 1.0000},
            {'date': '2024-01-03', 'price': 0.9999}
        ]
        real_time_price = 1.005  # 0.5% deviation - well within threshold

        is_plausible, deviation, reference_price = _is_price_plausible(
            historical_data, real_time_price, 'USDC'
        )

        self.assertTrue(is_plausible)
        self.assertAlmostEqual(deviation, 0.5, places=1)
        self.assertEqual(reference_price, 0.9999)

    def test_is_price_plausible_stablecoin_exceeds_threshold(self):
        """Test that stablecoin price exceeding threshold is considered implausible (issue #34 scenario)."""
        historical_data = [
            {'date': '2024-01-01', 'price': 0.9998},
            {'date': '2024-01-02', 'price': 1.0000},
            {'date': '2024-01-03', 'price': 0.9999}
        ]
        real_time_price = 0.11  # ~89% deviation - reproduces the live issue #34 scenario

        is_plausible, deviation, reference_price = _is_price_plausible(
            historical_data, real_time_price, 'USDC'
        )

        self.assertFalse(is_plausible)
        self.assertGreater(deviation, 50.0)  # Exceeds 50% threshold
        self.assertEqual(reference_price, 0.9999)

    def test_is_price_plausible_non_stablecoin_exempt(self):
        """Test that non-stablecoins like WETH are exempt from plausibility check."""
        historical_data = [
            {'date': '2024-01-01', 'price': 2000.0},
            {'date': '2024-01-02', 'price': 2100.0},
            {'date': '2024-01-03', 'price': 2200.0}
        ]
        real_time_price = 1100.0  # 50% deviation - would fail for stablecoin, but WETH is exempt

        is_plausible, deviation, reference_price = _is_price_plausible(
            historical_data, real_time_price, 'WETH'
        )

        # WETH is exempt - should return True with None deviation
        self.assertTrue(is_plausible)
        self.assertIsNone(deviation)
        self.assertIsNone(reference_price)

    def test_is_price_plausible_empty_historical_data(self):
        """Test that empty historical data skips the check."""
        historical_data = []
        real_time_price = 0.11

        is_plausible, deviation, reference_price = _is_price_plausible(
            historical_data, real_time_price, 'USDC'
        )

        # No historical data - skip check
        self.assertTrue(is_plausible)
        self.assertIsNone(deviation)
        self.assertIsNone(reference_price)

    def test_is_price_plausible_invalid_reference_price(self):
        """Test that invalid reference price (None or zero) skips the check."""
        historical_data = [
            {'date': '2024-01-01', 'price': None},  # Invalid price
        ]
        real_time_price = 0.11

        is_plausible, deviation, reference_price = _is_price_plausible(
            historical_data, real_time_price, 'USDC'
        )

        # Invalid reference - skip check
        self.assertTrue(is_plausible)
        self.assertIsNone(deviation)
        self.assertIsNone(reference_price)

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    @patch('tasks.analyzer.logger')
    def test_implausible_price_skips_with_warning(self, mock_logger, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that implausible stablecoin price skips pair and logs warning (issue #34 scenario)."""
        # Setup mocks - reproduce the live scenario: ~$1.00 historical vs. ~$0.11 real-time
        mock_historical.return_value = [
            {'date': '2024-01-01', 'price': 0.9998},
            {'date': '2024-01-02', 'price': 1.0000},
            {'date': '2024-01-03', 'price': 0.9999}
        ]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',  # Correct Sepolia USDC
                    'symbol': 'USDC'
                },
                'quoteToken': {
                    'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                    'symbol': 'WETH'
                }
            }
        ]
        mock_realtime.return_value = {'price': 0.1096, 'liquidity': 4472909.23}  # ~89% deviation
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function
        perform_llm_analysis('USDC', store_results=False, network='sepolia')

        # Verify analysis was skipped (combine_data and analyze_with_llm were NOT called)
        mock_combine.assert_not_called()
        mock_analyze.assert_not_called()

        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        self.assertIn('Price implausibility detected', warning_call)
        self.assertIn('USDC', warning_call)
        self.assertIn('sepolia', warning_call)
        self.assertIn('0.9999', warning_call)  # Reference price
        self.assertIn('0.1096', warning_call)  # Real-time price
        self.assertIn('89.0', warning_call)  # Deviation (approximately)

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_plausible_price_proceeds_normally(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that plausible stablecoin price proceeds to analysis normally."""
        # Setup mocks - plausible price within threshold
        mock_historical.return_value = [
            {'date': '2024-01-01', 'price': 0.9998},
            {'date': '2024-01-02', 'price': 1.0000},
            {'date': '2024-01-03', 'price': 0.9999}
        ]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
                    'symbol': 'USDC'
                },
                'quoteToken': {
                    'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                    'symbol': 'WETH'
                }
            }
        ]
        mock_realtime.return_value = {'price': 1.005, 'liquidity': 4472909.23}  # 0.5% deviation - plausible
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function
        perform_llm_analysis('USDC', store_results=False, network='sepolia')

        # Verify analysis proceeded (combine_data and analyze_with_llm were called)
        mock_combine.assert_called_once()
        mock_analyze.assert_called_once()

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_weth_price_deviation_exempt(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """Test that WETH (non-stablecoin) is exempt from plausibility check even with large deviation."""
        # Setup mocks - large deviation for WETH, but should proceed since it's exempt
        mock_historical.return_value = [
            {'date': '2024-01-01', 'price': 2000.0},
            {'date': '2024-01-02', 'price': 2100.0},
            {'date': '2024-01-03', 'price': 2200.0}
        ]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                    'symbol': 'WETH'
                },
                'quoteToken': {
                    'address': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
                    'symbol': 'USDC'
                }
            }
        ]
        mock_realtime.return_value = {'price': 1100.0, 'liquidity': 4472909.23}  # 50% deviation - would fail for stablecoin
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function
        perform_llm_analysis('WETH', store_results=False, network='sepolia')

        # Verify analysis proceeded (WETH is exempt from plausibility check)
        mock_combine.assert_called_once()
        mock_analyze.assert_called_once()


if __name__ == '__main__':
    unittest.main()

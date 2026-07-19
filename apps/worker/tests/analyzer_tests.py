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


class TestAnalyzerSymbolResolutionViaAllowlist(unittest.TestCase):
    """Test symbol-based resolution using KNOWN_TOKEN_ADDRESSES (issue #33)."""

    def test_geckoterminal_usdc_symbol_resolves_via_allowlist_sepolia(self):
        """Test that 'USDC' symbol resolves via allowlist for Sepolia GeckoTerminal data."""
        # Real GeckoTerminal format: only addresses, no symbol fields
        pair = {
            "id": "sepolia-testnet_0x6418eec70f50913ff0d756b48d32ce7c02b47c47",
            "base_token_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",  # Sepolia USDC from allowlist
            "quote_token_address": "0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
            "relationships": {
                "base_token": {
                    "data": {
                        "id": "sepolia-testnet_0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
                        "type": "token"
                    }
                },
                "quote_token": {
                    "data": {
                        "id": "sepolia-testnet_0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
                        "type": "token"
                    }
                }
            }
        }

        # This should now resolve via the allowlist (previously returned None)
        result = _resolve_token_address("USDC", pair, network="sepolia")
        self.assertEqual(result, "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238")

    def test_geckoterminal_weth_symbol_resolves_via_allowlist_sepolia(self):
        """Test that 'WETH' symbol resolves via allowlist for Sepolia GeckoTerminal data."""
        pair = {
            "id": "sepolia-testnet_0x6418eec70f50913ff0d756b48d32ce7c02b47c47",
            "base_token_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            "quote_token_address": "0xfff9976782d46cc05630d1f6ebab18b2324d6b14",  # Sepolia WETH from allowlist
            "relationships": {
                "base_token": {
                    "data": {
                        "id": "sepolia-testnet_0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
                        "type": "token"
                    }
                },
                "quote_token": {
                    "data": {
                        "id": "sepolia-testnet_0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
                        "type": "token"
                    }
                }
            }
        }

        result = _resolve_token_address("WETH", pair, network="sepolia")
        self.assertEqual(result, "0xfff9976782d46cc05630d1f6ebab18b2324d6b14")

    def test_geckoterminal_usdc_symbol_resolves_via_allowlist_mainnet(self):
        """Test that 'USDC' symbol resolves via allowlist for mainnet GeckoTerminal data."""
        pair = {
            "id": "eth_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "base_token_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # Mainnet USDC from allowlist
            "quote_token_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "relationships": {
                "base_token": {
                    "data": {
                        "id": "eth_0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                        "type": "token"
                    }
                },
                "quote_token": {
                    "data": {
                        "id": "eth_0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                        "type": "token"
                    }
                }
            }
        }

        result = _resolve_token_address("USDC", pair, network="mainnet")
        self.assertEqual(result, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    def test_geckoterminal_symbol_not_in_allowlist_returns_none(self):
        """Test that symbol not in allowlist returns None (existing behavior preserved)."""
        pair = {
            "id": "sepolia-testnet_0x6418eec70f50913ff0d756b48d32ce7c02b47c47",
            "base_token_address": "0x1234567890123456789012345678901234567890",  # Random token
            "quote_token_address": "0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
            "relationships": {
                "base_token": {
                    "data": {
                        "id": "sepolia-testnet_0x1234567890123456789012345678901234567890",
                        "type": "token"
                    }
                },
                "quote_token": {
                    "data": {
                        "id": "sepolia-testnet_0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
                        "type": "token"
                    }
                }
            }
        }

        # TOKENX is not in KNOWN_TOKEN_ADDRESSES, so should return None
        result = _resolve_token_address("TOKENX", pair, network="sepolia")
        self.assertIsNone(result)

    def test_geckoterminal_symbol_resolution_without_network_returns_none(self):
        """Test that symbol resolution without network parameter returns None."""
        pair = {
            "id": "sepolia-testnet_0x6418eec70f50913ff0d756b48d32ce7c02b47c47",
            "base_token_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            "quote_token_address": "0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
            "relationships": {
                "base_token": {
                    "data": {
                        "id": "sepolia-testnet_0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
                        "type": "token"
                    }
                },
                "quote_token": {
                    "data": {
                        "id": "sepolia-testnet_0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
                        "type": "token"
                    }
                }
            }
        }

        # Without network parameter, allowlist resolution cannot work
        result = _resolve_token_address("USDC", pair, network=None)
        self.assertIsNone(result)

    def test_geckoterminal_address_input_still_works_with_network_param(self):
        """Test that address-based resolution still works when network parameter is provided."""
        pair = {
            "id": "sepolia-testnet_0x6418eec70f50913ff0d756b48d32ce7c02b47c47",
            "base_token_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            "quote_token_address": "0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
            "relationships": {
                "base_token": {
                    "data": {
                        "id": "sepolia-testnet_0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
                        "type": "token"
                    }
                },
                "quote_token": {
                    "data": {
                        "id": "sepolia-testnet_0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
                        "type": "token"
                    }
                }
            }
        }

        # Address-based resolution should still work (takes precedence over allowlist)
        result = _resolve_token_address("0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238", pair, network="sepolia")
        self.assertEqual(result, "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238")


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
        # Setup mocks - use WETH (non-stablecoin) to avoid price plausibility check
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 2000.0}, {'date': '2024-01-02', 'price': 2100.0}]
        mock_search.return_value = [
            {
                'chainId': 'ethereum',
                'pairAddress': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                'baseToken': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'symbol': 'WETH'},
                'quoteToken': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'symbol': 'USDC'}
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
        perform_llm_analysis('WETH', store_results=False, network='ethereum')

        # Verify executor was instantiated with correct parameters
        mock_executor_class.assert_called_once_with(
            token_address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
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
        # Setup mocks - use WETH (non-stablecoin) to avoid price plausibility check
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 2000.0}, {'date': '2024-01-02', 'price': 2100.0}]
        mock_search.return_value = [
            {
                'chainId': 'ethereum',
                'pairAddress': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                'baseToken': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'symbol': 'WETH'},
                'quoteToken': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'symbol': 'USDC'}
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
        perform_llm_analysis('WETH', store_results=False, network='ethereum')

        # Verify executor was instantiated with correct parameters
        mock_executor_class.assert_called_once_with(
            token_address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
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
        # Setup mocks - use WETH (non-stablecoin) to avoid price plausibility check
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 2000.0}, {'date': '2024-01-02', 'price': 2100.0}]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {'address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14', 'symbol': 'WETH'},  # Sepolia WETH from allowlist
                'quoteToken': {'address': '0xbe72e441bf55620febc26715db68d3494213d8cb', 'symbol': 'USDC'}
            }
        ]
        mock_realtime.return_value = {'price': 1843.24, 'liquidity': 4472909.23, 'price_change_1h': 0}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'BUY', 'confidence': 0.9}

        # Setup executor mock
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor

        # Import and call the function
        from tasks.analyzer import perform_llm_analysis
        perform_llm_analysis('WETH', store_results=False, network='sepolia')

        # Verify executor was instantiated with sepolia network
        mock_executor_class.assert_called_once_with(
            token_address='0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
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
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 0.9998}, {'date': '2024-01-02', 'price': 1.0000}]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',  # Correct Sepolia USDC from allowlist
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
        # Setup mocks - use plausible price to avoid triggering #34 check before #31 check
        mock_historical.return_value = [{'date': '2024-01-01', 'price': 0.9998}, {'date': '2024-01-02', 'price': 1.0000}]
        mock_search.return_value = [
            {
                'chainId': 'sepolia',
                'pairAddress': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'baseToken': {
                    'address': '0xbe72e441bf55620febc26715db68d3494213d8cb',  # Wrong address (not the Sepolia USDC in allowlist)
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

        # Verify analysis was skipped (combine_data and analyze_with_llm were NOT called)
        mock_combine.assert_not_called()
        mock_analyze.assert_not_called()

        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        self.assertIn('Token address mismatch', warning_call)
        self.assertIn('USDC', warning_call)
        self.assertIn('sepolia', warning_call)
        self.assertIn('0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238', warning_call)  # Expected from allowlist
        self.assertIn('0xbe72e441bf55620febc26715db68d3494213d8cb', warning_call)  # Resolved from pair

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


class TestAnalyzerSymbolResolutionIntegration(unittest.TestCase):
    """End-to-end integration test confirming #31 and #34 are reachable (issue #33)."""

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_geckoterminal_symbol_resolution_reaches_checks_31_and_34(self, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """
        End-to-end test: with symbol resolution fix, a realistic GeckoTerminal-shaped pair
        reaches get_realtime_data, the #31 address verification check, and the #34 price-plausibility check.

        This is the critical test that proves both prior fixes are actually reachable in a live run.
        Before the issue #33 fix, this would have been dropped at the first 'if not token_address: continue'.
        """
        # Setup mocks - realistic GeckoTerminal format (no symbol fields, only addresses)
        mock_historical.return_value = [
            {'date': '2024-01-01', 'price': 0.9998},
            {'date': '2024-01-02', 'price': 1.0000},
            {'date': '2024-01-03', 'price': 0.9999}
        ]
        mock_search.return_value = [
            {
                'id': 'sepolia-testnet_0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'attributes': {
                    'address': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                    'name': 'USDC / WETH 1%'
                },
                'base_token_address': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',  # Sepolia USDC from allowlist
                'quote_token_address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                'relationships': {
                    'base_token': {
                        'data': {
                            'id': 'sepolia-testnet_0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
                            'type': 'token'
                        }
                    },
                    'quote_token': {
                        'data': {
                            'id': 'sepolia-testnet_0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                            'type': 'token'
                        }
                    }
                }
            }
        ]
        # Plausible price within threshold (so #34 check passes)
        mock_realtime.return_value = {'price': 1.005, 'liquidity': 4472909.23}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function with symbol-based token_id
        perform_llm_analysis('USDC', store_results=False, network='sepolia')

        # CRITICAL: Verify that get_realtime_data was called
        # This proves the pair was NOT dropped at the resolution stage
        mock_realtime.assert_called_once()

        # Verify that combine_data and analyze_with_llm were called
        # This proves the pair passed both #31 address verification and #34 price-plausibility checks
        mock_combine.assert_called_once()
        mock_analyze.assert_called_once()

        # Verify the resolved address was passed correctly to the executor
        # (even though this is a HOLD decision, executor should not be instantiated)
        mock_executor_class.assert_not_called()

    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    @patch('tasks.analyzer.logger')
    def test_geckoterminal_symbol_resolution_with_implausible_price_triggers_34_check(self, mock_logger, mock_executor_class, mock_analyze, mock_combine, mock_realtime, mock_search, mock_historical):
        """
        End-to-end test: with symbol resolution fix, an implausible price triggers the #34 check
        and skips the pair with a warning (proving #34 is reachable).
        """
        # Setup mocks - realistic GeckoTerminal format with implausible price
        mock_historical.return_value = [
            {'date': '2024-01-01', 'price': 0.9998},
            {'date': '2024-01-02', 'price': 1.0000},
            {'date': '2024-01-03', 'price': 0.9999}
        ]
        mock_search.return_value = [
            {
                'id': 'sepolia-testnet_0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                'attributes': {
                    'address': '0x6418eec70f50913ff0d756b48d32ce7c02b47c47',
                    'name': 'USDC / WETH 1%'
                },
                'base_token_address': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',  # Sepolia USDC from allowlist
                'quote_token_address': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                'relationships': {
                    'base_token': {
                        'data': {
                            'id': 'sepolia-testnet_0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
                            'type': 'token'
                        }
                    },
                    'quote_token': {
                        'data': {
                            'id': 'sepolia-testnet_0xfff9976782d46cc05630d1f6ebab18b2324d6b14',
                            'type': 'token'
                        }
                    }
                }
            }
        ]
        # Implausible price - should trigger #34 check
        mock_realtime.return_value = {'price': 0.1096, 'liquidity': 4472909.23}
        mock_combine.return_value = MagicMock()
        mock_analyze.return_value = {'decision': 'HOLD', 'confidence': 0.5}

        # Import and call the function with symbol-based token_id
        perform_llm_analysis('USDC', store_results=False, network='sepolia')

        # CRITICAL: Verify that get_realtime_data was called (resolution succeeded)
        mock_realtime.assert_called_once()

        # Verify that combine_data and analyze_with_llm were NOT called
        # This proves the #34 price-plausibility check was triggered and skipped the pair
        mock_combine.assert_not_called()
        mock_analyze.assert_not_called()

        # Verify warning was logged for price implausibility
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        self.assertIn('Price implausibility detected', warning_call)


if __name__ == '__main__':
    unittest.main()

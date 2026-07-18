import unittest
from unittest.mock import patch, MagicMock, Mock
from tasks.analyzer import perform_llm_analysis


class TestAnalyzerTokenAddressResolution(unittest.TestCase):
    """Test token_address resolution from DexScreener pair data."""

    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_token_id_matches_baseToken_resolves_to_baseToken_address(
        self, mock_executor_class, mock_analyze_llm, mock_combine_data,
        mock_get_realtime_data, mock_get_historical_data, mock_search_token_pairs
    ):
        """Test that token_id matching baseToken.symbol resolves to baseToken.address."""
        # Mock data
        mock_historical_data = [{"date": 1234567890000, "price": 1.0}]
        mock_get_historical_data.return_value = mock_historical_data

        mock_realtime_data = {"price": 1.0, "liquidity": 1000000, "price_change_1h": 0.01}
        mock_get_realtime_data.return_value = mock_realtime_data

        mock_combined_data = MagicMock()
        mock_combine_data.return_value = mock_combined_data

        mock_analyze_llm.return_value = {"decision": "BUY"}

        # Pair with USDC as baseToken
        mock_search_token_pairs.return_value = [
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

        mock_executor_instance = MagicMock()
        mock_executor_class.return_value = mock_executor_instance

        # Execute with token_id matching baseToken symbol
        perform_llm_analysis("usdc", store_results=False)

        # Verify EthereumExecutor was called with baseToken address
        mock_executor_class.assert_called_once()
        call_kwargs = mock_executor_class.call_args[1]
        self.assertEqual(call_kwargs['token_address'], "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_token_id_matches_quoteToken_resolves_to_quoteToken_address(
        self, mock_executor_class, mock_analyze_llm, mock_combine_data,
        mock_get_realtime_data, mock_get_historical_data, mock_search_token_pairs
    ):
        """Test that token_id matching quoteToken.symbol resolves to quoteToken.address."""
        # Mock data
        mock_historical_data = [{"date": 1234567890000, "price": 1.0}]
        mock_get_historical_data.return_value = mock_historical_data

        mock_realtime_data = {"price": 1.0, "liquidity": 1000000, "price_change_1h": 0.01}
        mock_get_realtime_data.return_value = mock_realtime_data

        mock_combined_data = MagicMock()
        mock_combine_data.return_value = mock_combined_data

        mock_analyze_llm.return_value = {"decision": "BUY"}

        # Pair with USDC as quoteToken
        mock_search_token_pairs.return_value = [
            {
                "chainId": "ethereum",
                "pairAddress": "0x1234567890123456789012345678901234567890",
                "baseToken": {
                    "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "symbol": "WETH",
                    "name": "Wrapped Ether"
                },
                "quoteToken": {
                    "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    "symbol": "USDC",
                    "name": "USD Coin"
                }
            }
        ]

        mock_executor_instance = MagicMock()
        mock_executor_class.return_value = mock_executor_instance

        # Execute with token_id matching quoteToken symbol
        perform_llm_analysis("usdc", store_results=False)

        # Verify EthereumExecutor was called with quoteToken address
        mock_executor_class.assert_called_once()
        call_kwargs = mock_executor_class.call_args[1]
        self.assertEqual(call_kwargs['token_address'], "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_token_id_matches_baseToken_name_case_insensitive(
        self, mock_executor_class, mock_analyze_llm, mock_combine_data,
        mock_get_realtime_data, mock_get_historical_data, mock_search_token_pairs
    ):
        """Test that token_id matching baseToken.name (case-insensitive) resolves correctly."""
        # Mock data
        mock_historical_data = [{"date": 1234567890000, "price": 1.0}]
        mock_get_historical_data.return_value = mock_historical_data

        mock_realtime_data = {"price": 1.0, "liquidity": 1000000, "price_change_1h": 0.01}
        mock_get_realtime_data.return_value = mock_realtime_data

        mock_combined_data = MagicMock()
        mock_combine_data.return_value = mock_combined_data

        mock_analyze_llm.return_value = {"decision": "BUY"}

        # Pair with USDC as baseToken
        mock_search_token_pairs.return_value = [
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

        mock_executor_instance = MagicMock()
        mock_executor_class.return_value = mock_executor_instance

        # Execute with token_id matching baseToken name (different case)
        perform_llm_analysis("USD COIN", store_results=False)

        # Verify EthereumExecutor was called with baseToken address
        mock_executor_class.assert_called_once()
        call_kwargs = mock_executor_class.call_args[1]
        self.assertEqual(call_kwargs['token_address'], "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_neither_side_matches_skips_pair_safely(
        self, mock_executor_class, mock_analyze_llm, mock_combine_data,
        mock_get_realtime_data, mock_get_historical_data, mock_search_token_pairs
    ):
        """Test that pair is skipped when token_id matches neither baseToken nor quoteToken."""
        # Mock data
        mock_historical_data = [{"date": 1234567890000, "price": 1.0}]
        mock_get_historical_data.return_value = mock_historical_data

        mock_realtime_data = {"price": 1.0, "liquidity": 1000000, "price_change_1h": 0.01}
        mock_get_realtime_data.return_value = mock_realtime_data

        mock_combined_data = MagicMock()
        mock_combine_data.return_value = mock_combined_data

        mock_analyze_llm.return_value = {"decision": "BUY"}

        # Pair with WETH/USDT, neither matches "usdc"
        mock_search_token_pairs.return_value = [
            {
                "chainId": "ethereum",
                "pairAddress": "0x1234567890123456789012345678901234567890",
                "baseToken": {
                    "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "symbol": "WETH",
                    "name": "Wrapped Ether"
                },
                "quoteToken": {
                    "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    "symbol": "USDT",
                    "name": "Tether USD"
                }
            }
        ]

        # Execute with token_id that doesn't match either side
        result = perform_llm_analysis("usdc", store_results=False)

        # Verify EthereumExecutor was NOT called (pair was skipped)
        mock_executor_class.assert_not_called()

        # Verify no exception was raised
        self.assertIsNotNone(result)

    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_buy_decision_triggers_execution_with_resolved_address(
        self, mock_executor_class, mock_analyze_llm, mock_combine_data,
        mock_get_realtime_data, mock_get_historical_data, mock_search_token_pairs
    ):
        """Test that BUY decision triggers EthereumExecutor.execute with resolved token address."""
        # Mock data
        mock_historical_data = [{"date": 1234567890000, "price": 1.0}]
        mock_get_historical_data.return_value = mock_historical_data

        mock_realtime_data = {"price": 1.0, "liquidity": 1000000, "price_change_1h": 0.01}
        mock_get_realtime_data.return_value = mock_realtime_data

        mock_combined_data = MagicMock()
        mock_combine_data.return_value = mock_combined_data

        mock_analyze_llm.return_value = {"decision": "BUY"}

        mock_search_token_pairs.return_value = [
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

        mock_executor_instance = MagicMock()
        mock_executor_class.return_value = mock_executor_instance

        # Execute with BUY decision
        perform_llm_analysis("usdc", store_results=False)

        # Verify EthereumExecutor.execute was called with BUY decision
        mock_executor_instance.execute.assert_called_once()
        call_kwargs = mock_executor_instance.execute.call_args[1]
        self.assertEqual(call_kwargs['decision'], 'BUY')
        self.assertEqual(call_kwargs['amount_eth'], 0.001)

    @patch('tasks.analyzer.search_token_pairs')
    @patch('tasks.analyzer.get_historical_data')
    @patch('tasks.analyzer.get_realtime_data')
    @patch('tasks.analyzer.combine_data')
    @patch('tasks.analyzer.analyze_with_llm')
    @patch('tasks.analyzer.EthereumExecutor')
    def test_sell_decision_triggers_execution_with_resolved_address(
        self, mock_executor_class, mock_analyze_llm, mock_combine_data,
        mock_get_realtime_data, mock_get_historical_data, mock_search_token_pairs
    ):
        """Test that SELL decision triggers EthereumExecutor.execute with resolved token address."""
        # Mock data
        mock_historical_data = [{"date": 1234567890000, "price": 1.0}]
        mock_get_historical_data.return_value = mock_historical_data

        mock_realtime_data = {"price": 1.0, "liquidity": 1000000, "price_change_1h": 0.01}
        mock_get_realtime_data.return_value = mock_realtime_data

        mock_combined_data = MagicMock()
        mock_combine_data.return_value = mock_combined_data

        mock_analyze_llm.return_value = {"decision": "SELL"}

        mock_search_token_pairs.return_value = [
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

        mock_executor_instance = MagicMock()
        mock_executor_class.return_value = mock_executor_instance

        # Execute with SELL decision
        perform_llm_analysis("usdc", store_results=False)

        # Verify EthereumExecutor.execute was called with SELL decision
        mock_executor_instance.execute.assert_called_once()
        call_kwargs = mock_executor_instance.execute.call_args[1]
        self.assertEqual(call_kwargs['decision'], 'SELL')
        self.assertIsNone(call_kwargs['amount_tokens'])


if __name__ == '__main__':
    unittest.main()

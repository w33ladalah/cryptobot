import unittest
from unittest.mock import MagicMock, patch, Mock
from web3 import Web3
from web3.eth import Contract
from pydantic import SecretStr
from core.trading.ethereum import EthereumExecutor
from config.settings import config


class TestEthereumExecutor(unittest.TestCase):
    def setUp(self):
        self.token_address = "0x1234567890123456789012345678901234567890"
        self.network = "mainnet"
        self.provider = "infura"
        self.executor = EthereumExecutor(self.token_address, self.network, self.provider)

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_buy_with_amount_eth(self, mock_web3_class, mock_config):
        """Test that execute() with BUY decision and amount_eth calls _execute_buy with correct args."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x
        mock_web3.to_wei.return_value = 1000000000000000

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ETH_GAS_LIMIT = 200000
        mock_config.ETH_GAS_PRICE = 5
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        mock_web3.eth.get_transaction_count.return_value = 1

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"

        self.executor.execute("BUY", amount_eth=0.001)

        # Verify that sign_transaction was called with the secret value, not the SecretStr object
        call_args = mock_account.sign_transaction.call_args
        private_key_arg = call_args[0][1]
        self.assertEqual(private_key_arg, "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        self.assertNotIsInstance(private_key_arg, SecretStr)

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_buy_without_amount_eth_raises_value_error(self, mock_web3_class, mock_config):
        """Test that execute() with BUY decision and no amount_eth raises ValueError."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract

        with self.assertRaises(ValueError) as context:
            self.executor.execute("BUY")
        self.assertEqual(str(context.exception), "amount_eth must be provided and greater than 0 for BUY orders")

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_buy_with_zero_amount_eth_raises_value_error(self, mock_web3_class, mock_config):
        """Test that execute() with BUY decision and zero amount_eth raises ValueError."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract

        with self.assertRaises(ValueError) as context:
            self.executor.execute("BUY", amount_eth=0)
        self.assertEqual(str(context.exception), "amount_eth must be provided and greater than 0 for BUY orders")

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_sell_without_amount_eth(self, mock_web3_class, mock_config):
        """Test that execute() with SELL decision works without amount_eth parameter."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x
        mock_web3.to_wei.return_value = 1000000000000000000

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ERC20_ABI = []
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        mock_contract.functions.allowance.return_value.call.return_value = 1000000000000000000
        mock_contract.functions.balanceOf.return_value.call.return_value = 1000000000000000000

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock()

        # Should not raise ValueError for SELL without amount_eth
        self.executor.execute("SELL")

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_sell_insufficient_allowance_triggers_approve(self, mock_web3_class, mock_config):
        """Test that execute() with SELL decision triggers approve when allowance is insufficient."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x
        mock_web3.to_wei.return_value = 1000000000000000000

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ERC20_ABI = []
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        # Mock allowance below amount_tokens to trigger approve path
        mock_contract.functions.allowance.return_value.call.return_value = 500000000000000000  # 0.5 tokens, less than 1 token
        mock_contract.functions.balanceOf.return_value.call.return_value = 1000000000000000000

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock()

        # Execute SELL - should trigger approve path
        self.executor.execute("SELL")

        # Verify that approve was called (since allowance was insufficient)
        mock_contract.functions.approve.assert_called_once()

        # Verify that sign_transaction was called with the secret value, not the SecretStr object
        # This should be called twice: once for approve, once for sell
        self.assertEqual(mock_account.sign_transaction.call_count, 2)

        # Check the approve call (first call)
        approve_call_args = mock_account.sign_transaction.call_args_list[0]
        private_key_arg = approve_call_args[0][1]
        self.assertEqual(private_key_arg, "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        self.assertNotIsInstance(private_key_arg, SecretStr)

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_setup_web3_unwraps_wallet_address_secret(self, mock_web3_class, mock_config):
        """Test that _setup_web3_and_uniswap unwraps WALLET_ADDRESS SecretStr before passing to to_checksum_address."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        # Don't use side_effect = lambda x: x - we want to see what's actually passed
        mock_web3.to_checksum_address.side_effect = lambda x: x  # Still return the input for now

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract

        # Call _setup_web3_and_uniswap
        web3, my_address, uniswap_router = self.executor._setup_web3_and_uniswap()

        # Verify that to_checksum_address was called with the plain string value, not the SecretStr object
        # The first call should be for WALLET_ADDRESS
        call_args = mock_web3.to_checksum_address.call_args_list[0]
        wallet_address_arg = call_args[0][0]
        self.assertEqual(wallet_address_arg, "0xabcdef1234567890abcdef1234567890abcdef12")
        self.assertNotIsInstance(wallet_address_arg, SecretStr)

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_buy_dry_run_does_not_send_transaction(self, mock_web3_class, mock_config):
        """Test that execute() with BUY decision and DRY_RUN=True does not sign or send transaction."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x
        mock_web3.to_wei.return_value = 1000000000000000

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ETH_GAS_LIMIT = 200000
        mock_config.ETH_GAS_PRICE = 5
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = True

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        mock_web3.eth.get_transaction_count.return_value = 1

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"

        self.executor.execute("BUY", amount_eth=0.001)

        # Verify that sign_transaction and send_raw_transaction were NOT called
        mock_account.sign_transaction.assert_not_called()
        mock_web3.eth.send_raw_transaction.assert_not_called()

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_sell_dry_run_does_not_send_transaction(self, mock_web3_class, mock_config):
        """Test that execute() with SELL decision and DRY_RUN=True does not sign or send transaction."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x
        mock_web3.to_wei.return_value = 1000000000000000000

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ERC20_ABI = []
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = True

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        mock_contract.functions.allowance.return_value.call.return_value = 1000000000000000000
        mock_contract.functions.balanceOf.return_value.call.return_value = 1000000000000000000

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock()

        self.executor.execute("SELL")

        # Verify that sign_transaction and send_raw_transaction were NOT called
        mock_account.sign_transaction.assert_not_called()
        mock_web3.eth.send_raw_transaction.assert_not_called()

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_sell_dry_run_with_insufficient_allowance_skips_approve_send(self, mock_web3_class, mock_config):
        """Test that execute() with SELL decision, insufficient allowance, and DRY_RUN=True does not sign or send approval or swap."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x
        mock_web3.to_wei.return_value = 1000000000000000000

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ERC20_ABI = []
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = True

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        # Mock allowance below amount_tokens to trigger approve path
        mock_contract.functions.allowance.return_value.call.return_value = 500000000000000000  # 0.5 tokens, less than 1 token
        mock_contract.functions.balanceOf.return_value.call.return_value = 1000000000000000000

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock()

        self.executor.execute("SELL")

        # Verify that sign_transaction and send_raw_transaction were NOT called for either approval or swap
        mock_account.sign_transaction.assert_not_called()
        mock_web3.eth.send_raw_transaction.assert_not_called()

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_sell_with_amount_tokens_uses_specified_amount(self, mock_web3_class, mock_config):
        """Test that execute() with SELL decision and amount_tokens parameter uses the specified amount."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x
        mock_web3.to_wei.return_value = 500000000000000000  # 0.5 tokens in wei

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ERC20_ABI = []
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        mock_contract.functions.allowance.return_value.call.return_value = 1000000000000000000
        mock_contract.functions.balanceOf.return_value.call.return_value = 1000000000000000000  # Full balance is 1 token

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock()

        # Execute SELL with 0.5 tokens specified
        self.executor.execute("SELL", amount_tokens=0.5)

        # Verify that swap was called with the specified amount (0.5 tokens)
        swap_call = mock_contract.functions.swapExactTokensForETH.call_args
        self.assertEqual(swap_call[0][0], 500000000000000000)

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_sell_without_amount_tokens_uses_full_balance(self, mock_web3_class, mock_config):
        """Test that execute() with SELL decision and no amount_tokens parameter uses full balance."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ERC20_ABI = []
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        mock_contract.functions.allowance.return_value.call.return_value = 1000000000000000000
        # Mock balanceOf to return 0.379 tokens (the actual balance from the live test)
        mock_contract.functions.balanceOf.return_value.call.return_value = 379574074366507758

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock()

        # Execute SELL without amount_tokens - should use full balance
        self.executor.execute("SELL")

        # Verify that balanceOf was called to fetch the balance
        mock_contract.functions.balanceOf.assert_called_once()

        # Verify that swap was called with the full balance amount
        swap_call = mock_contract.functions.swapExactTokensForETH.call_args
        self.assertEqual(swap_call[0][0], 379574074366507758)

    @patch('core.trading.ethereum.config')
    @patch('core.trading.ethereum.Web3')
    def test_execute_sell_with_zero_balance_raises_value_error(self, mock_web3_class, mock_config):
        """Test that execute() with SELL decision and zero balance raises ValueError before on-chain calls."""
        mock_web3 = MagicMock(spec=Web3)
        mock_web3_class.return_value = mock_web3
        mock_web3.is_connected.return_value = True
        mock_web3.to_checksum_address.side_effect = lambda x: x

        mock_config.WALLET_ADDRESS = SecretStr("0xabcdef1234567890abcdef1234567890abcdef12")
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"
        mock_config.UNISWAP_ROUTER_ABI = []
        mock_config.ERC20_ABI = []
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        mock_config.DRY_RUN = False

        mock_web3.eth = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_web3.eth.contract.return_value = mock_contract
        # Mock balanceOf to return 0
        mock_contract.functions.balanceOf.return_value.call.return_value = 0

        mock_account = MagicMock()
        mock_web3.eth.account = mock_account
        mock_account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed_tx")
        mock_web3.eth.send_raw_transaction.return_value = MagicMock()
        mock_web3.to_hex.return_value = "0xhash123"
        mock_web3.eth.get_transaction_count.return_value = 1

        with self.assertRaises(ValueError) as context:
            self.executor.execute("SELL")
        self.assertEqual(str(context.exception), "No tokens available to sell")

        # Verify that sign_transaction and send_raw_transaction were NOT called
        mock_account.sign_transaction.assert_not_called()
        mock_web3.eth.send_raw_transaction.assert_not_called()


if __name__ == '__main__':
    unittest.main()

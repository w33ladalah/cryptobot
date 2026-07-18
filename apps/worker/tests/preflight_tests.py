import unittest
from unittest.mock import patch, MagicMock
from pydantic import SecretStr

from core.preflight import check_sepolia_env


class TestSepoliaPreflight(unittest.TestCase):

    def setUp(self):
        """Set up mock config with valid defaults."""
        self.mock_config = MagicMock()
        self.mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        self.mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        self.mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        self.mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        self.mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

    @patch('core.preflight.config')
    def test_all_checks_pass(self, mock_config):
        """Test that all checks pass when every field is well-formed."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertEqual(problems, [])

    @patch('core.preflight.config')
    def test_wallet_private_key_none(self, mock_config):
        """Test that WALLET_PRIVATE_KEY = None produces a problem message."""
        mock_config.WALLET_PRIVATE_KEY = None
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("WALLET_PRIVATE_KEY is not set", problems)

    @patch('core.preflight.config')
    def test_wallet_private_key_malformed_wrong_length(self, mock_config):
        """Test that a malformed private key (wrong length) produces a distinct problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890")  # Too short
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("WALLET_PRIVATE_KEY must be 64 hex characters (66 with 0x prefix)", problems)
        self.assertNotIn("WALLET_PRIVATE_KEY is not set", problems)

    @patch('core.preflight.config')
    def test_wallet_private_key_malformed_non_hex(self, mock_config):
        """Test that a malformed private key (non-hex) produces a distinct problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xghijklmnopqrstuvwxyz1234567890abcdef1234567890abcdef1234567890abcdef12")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("WALLET_PRIVATE_KEY contains non-hex characters", problems)

    @patch('core.preflight.config')
    def test_wallet_private_key_missing_prefix(self, mock_config):
        """Test that a private key missing 0x prefix produces a distinct problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("WALLET_PRIVATE_KEY must be 0x-prefixed", problems)

    @patch('core.preflight.config')
    def test_wallet_address_none(self, mock_config):
        """Test that WALLET_ADDRESS = None produces a problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = None
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("WALLET_ADDRESS is not set", problems)

    @patch('core.preflight.config')
    def test_wallet_address_fails_checksum(self, mock_config):
        """Test that a valid hex address that fails EIP-55 checksum produces a distinct message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7b9a4e38802a711f36776cf481f1007a5790f453")  # All lowercase, fails checksum
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("WALLET_ADDRESS fails EIP-55 checksum validation (likely a copy-paste error)", problems)
        self.assertNotIn("WALLET_ADDRESS does not look like a valid hex address", problems)

    @patch('core.preflight.config')
    def test_wallet_address_not_hex(self, mock_config):
        """Test that a non-hex address produces a distinct message from checksum failure."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0xghijklmnopqrstuvwxyz1234567890abcdef123456")  # Invalid hex
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("WALLET_ADDRESS does not look like a valid hex address", problems)
        self.assertNotIn("WALLET_ADDRESS fails EIP-55 checksum validation", problems)

    @patch('core.preflight.config')
    def test_infura_url_placeholder(self, mock_config):
        """Test that INFURA_URL_TESTNET with placeholder produces a problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/your_infura_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("INFURA_URL_TESTNET still contains placeholder 'your_infura_project_id'", problems)

    @patch('core.preflight.config')
    def test_infura_url_non_sepolia(self, mock_config):
        """Test that a non-Sepolia URL (e.g., mainnet) produces a problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://mainnet.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("INFURA_URL_TESTNET must start with 'https://sepolia.' (for Sepolia testnet)", problems)

    @patch('core.preflight.config')
    def test_uniswap_router_mainnet_address_original_case(self, mock_config):
        """Test that the mainnet router address (original case) produces the specific warning."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"  # Mainnet address
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("UNISWAP_ROUTER_ADDRESS is the mainnet Uniswap V2 Router02 address (0x7a250d5630b4cf539739df2c5dAcb4c659F2488D) - this should be the Sepolia address (0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3)", problems)

    @patch('core.preflight.config')
    def test_uniswap_router_mainnet_address_lowercase(self, mock_config):
        """Test that the mainnet router address (all lowercase) produces the specific warning."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"  # Mainnet address, all lowercase
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("UNISWAP_ROUTER_ADDRESS is the mainnet Uniswap V2 Router02 address (0x7a250d5630b4cf539739df2c5dAcb4c659F2488D) - this should be the Sepolia address (0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3)", problems)

    @patch('core.preflight.config')
    def test_uniswap_router_none(self, mock_config):
        """Test that UNISWAP_ROUTER_ADDRESS = None produces a problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = None
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("UNISWAP_ROUTER_ADDRESS is not set", problems)

    @patch('core.preflight.config')
    def test_uniswap_router_fails_checksum(self, mock_config):
        """Test that UNISWAP_ROUTER_ADDRESS failing checksum produces a problem message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xee567fe1712faf6149d80da1e6934e354124cfe3"  # All lowercase, fails checksum
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertIn("UNISWAP_ROUTER_ADDRESS fails checksum validation", problems)

    @patch('core.preflight.config')
    def test_uniswap_router_abi_empty(self, mock_config):
        """Test that empty UNISWAP_ROUTER_ABI produces a warning message."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = []

        problems = check_sepolia_env()
        self.assertIn("WARNING: UNISWAP_ROUTER_ABI is empty - this is a known gap but should be filled in", problems)

    @patch('core.preflight.config')
    def test_uniswap_router_abi_non_empty(self, mock_config):
        """Test that non-empty UNISWAP_ROUTER_ABI does not produce a warning."""
        mock_config.WALLET_PRIVATE_KEY = SecretStr("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        mock_config.WALLET_ADDRESS = SecretStr("0x7B9a4e38802a711F36776CF481F1007a5790f453")
        mock_config.INFURA_URL_TESTNET = "https://sepolia.infura.io/v3/real_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = "0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3"
        mock_config.UNISWAP_ROUTER_ABI = [{"name": "swapExactETHForTokens"}]

        problems = check_sepolia_env()
        self.assertNotIn("WARNING: UNISWAP_ROUTER_ABI is empty - this is a known gap but should be filled in", problems)

    @patch('core.preflight.config')
    def test_multiple_problems_reported(self, mock_config):
        """Test that multiple problems are reported independently (no short-circuit)."""
        mock_config.WALLET_PRIVATE_KEY = None
        mock_config.WALLET_ADDRESS = None
        mock_config.INFURA_URL_TESTNET = "https://mainnet.infura.io/v3/your_infura_project_id"
        mock_config.UNISWAP_ROUTER_ADDRESS = None
        mock_config.UNISWAP_ROUTER_ABI = []

        problems = check_sepolia_env()
        self.assertGreater(len(problems), 1)
        self.assertIn("WALLET_PRIVATE_KEY is not set", problems)
        self.assertIn("WALLET_ADDRESS is not set", problems)
        self.assertIn("INFURA_URL_TESTNET still contains placeholder 'your_infura_project_id'", problems)
        self.assertIn("INFURA_URL_TESTNET must start with 'https://sepolia.' (for Sepolia testnet)", problems)
        self.assertIn("UNISWAP_ROUTER_ADDRESS is not set", problems)
        self.assertIn("WARNING: UNISWAP_ROUTER_ABI is empty - this is a known gap but should be filled in", problems)


if __name__ == '__main__':
    unittest.main()

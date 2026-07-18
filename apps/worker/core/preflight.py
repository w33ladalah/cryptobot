from config.settings import config
from eth_utils import is_hex, is_checksum_address
import sys


_UNISWAP_V2_ROUTER_MAINNET = "0x7a250d5630b4cf539739df2c5dAcb4c659F2488D"


def check_sepolia_env() -> list[str]:
    """Validate Sepolia environment configuration.
    
    Returns a list of human-readable problem descriptions. Empty list means all checks pass.
    """
    problems = []
    
    # Check 1: WALLET_PRIVATE_KEY
    if config.WALLET_PRIVATE_KEY is None:
        problems.append("WALLET_PRIVATE_KEY is not set")
    else:
        private_key = config.WALLET_PRIVATE_KEY.get_secret_value()
        if not private_key.startswith("0x"):
            problems.append("WALLET_PRIVATE_KEY must be 0x-prefixed")
        elif not is_hex(private_key):
            problems.append("WALLET_PRIVATE_KEY contains non-hex characters")
        elif len(private_key) != 66:  # 0x + 64 hex chars
            problems.append("WALLET_PRIVATE_KEY must be 64 hex characters (66 with 0x prefix)")
    
    # Check 2: WALLET_ADDRESS
    if config.WALLET_ADDRESS is None:
        problems.append("WALLET_ADDRESS is not set")
    else:
        address = config.WALLET_ADDRESS.get_secret_value()
        if not is_hex(address):
            problems.append("WALLET_ADDRESS does not look like a valid hex address")
        elif len(address) != 42:  # 0x + 40 hex chars
            problems.append("WALLET_ADDRESS must be 40 hex characters (42 with 0x prefix)")
        elif not is_checksum_address(address):
            problems.append("WALLET_ADDRESS fails EIP-55 checksum validation (likely a copy-paste error)")
    
    # Check 3: INFURA_URL_TESTNET
    if "your_infura_project_id" in config.INFURA_URL_TESTNET:
        problems.append("INFURA_URL_TESTNET still contains placeholder 'your_infura_project_id'")
    if not config.INFURA_URL_TESTNET.startswith("https://sepolia."):
        problems.append("INFURA_URL_TESTNET must start with 'https://sepolia.' (for Sepolia testnet)")
    
    # Check 4: UNISWAP_ROUTER_ADDRESS
    if config.UNISWAP_ROUTER_ADDRESS is None:
        problems.append("UNISWAP_ROUTER_ADDRESS is not set")
    else:
        router_address = config.UNISWAP_ROUTER_ADDRESS
        if not is_checksum_address(router_address):
            problems.append("UNISWAP_ROUTER_ADDRESS fails checksum validation")
        elif router_address.lower() == _UNISWAP_V2_ROUTER_MAINNET.lower():
            problems.append(f"UNISWAP_ROUTER_ADDRESS is the mainnet Uniswap V2 Router02 address ({_UNISWAP_V2_ROUTER_MAINNET}) - this should be the Sepolia address (0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3)")
    
    # Check 5: UNISWAP_ROUTER_ABI (warning level)
    if not config.UNISWAP_ROUTER_ABI:
        problems.append("WARNING: UNISWAP_ROUTER_ABI is empty - this is a known gap but should be filled in")
    
    return problems


if __name__ == "__main__":
    problems = check_sepolia_env()
    if problems:
        print("Sepolia environment preflight check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)
    else:
        print("All Sepolia environment checks passed.")
        sys.exit(0)

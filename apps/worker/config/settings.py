from pydantic_settings import BaseSettings
from pydantic import SecretStr

from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    """Configuration settings for the application. This class contains all default values and constants used throughout the application. It allows for easy configuration by defining standard settings that can be adjusted as needed.

    Args:
        DEXSCREener_API: The API endpoint for accessing data related to DexScreener. Defaults to "https://api.dexscreener.com/latest/dex/pairs".
        COINGECKO_API: The API endpoint for CoinGecko API requests. Defaults to "https://api.coingecko.com/api/v3".
        DISCORD_BOT_TOKEN: Discord bot token used for authentication and authorization. Defaults to a secret string.
        # Wallet & Uniswap settings
        WALLET_PRIVATE_KEY: Private key for wallet encryption or access control. Defaults to a secret string.
        WALLET_ADDRESS: Address of the wallet used for transactions or access. Defaults to a secret string.
        DRY_RUN: When True, EthereumExecutor logs intended trades instead of signing/broadcasting them. Defaults to True.
        API_OLLAMA_URL: URL for rolling without loss (ollama) API requests. Defaults to "http://localhost:11434".
        OPENROUTER_API_URL: URL for openrouter.io API requests. Defaults to "https://api.openrouter.io/v1".
    """

    DEXSCREENER_API: str = "https://api.dexscreener.com/latest/dex/"
    COINGECKO_API: str = "https://api.coingecko.com/api/v3"
    DISCORD_BOT_TOKEN: SecretStr = "your_discord_bot_token_here"

    # Wallet & Uniswap settings
    WALLET_CURRENCY: str = "ETH"  # Default wallet currency
    WALLET_PRIVATE_KEY: SecretStr = None  # Private key for wallet access control
    WALLET_ADDRESS: SecretStr = None   # Address for wallet access control
    DRY_RUN: bool = True  # When True, EthereumExecutor logs intended trades instead of signing/broadcasting them

    API_OLLAMA_URL: str = "http://localhost:11434"
    OPENROUTER_API_URL: str = "https://api.openrouter.io/v1"

    # LLM settings
    SYSTEM_PROMPT: str = "You are a crypto trading analyst."
    MODEL_NAME: str = "GPT-4"
    ADAPTER_CLASS: str = "OpenAiAdapter"
    LLM_API_KEY: SecretStr = None
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_COMPLETION_RETRY_LIMIT: int = 5

    # Dispatch bot settings
    DISCORD_BOT_TOKEN: SecretStr = "your_discord_bot_token_here"

    # Celery settings
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: SecretStr = None

    # API settings
    COINGECKO_API_KEY: SecretStr = None
    API_URL: str = "http://api:8000"

    # Infura settings
    INFURA_URL_MAINNET: str = "https://mainnet.infura.io/v3/your_infura_project_id"
    INFURA_URL_TESTNET: str = "https://sepolia.infura.io/v3/your_infura_project_id"

    # Moralis settings
    MORALIS_URL_MAINNET: str = "https://deep-index.moralis.io/api/v2"
    MORALIS_URL_TESTNET: str = "https://deep-index.moralis.io/api/v2"

    ETH_GAS_FEE: float = 0.000000000000000001  # Default gas fee for Ethereum transactions
    ETH_GAS_LIMIT: int = 200000  # Default gas limit for Ethereum transactions
    ETH_GAS_PRICE: int = 5  # Default gas price for Ethereum transactions

    # Uniswap settings
    UNISWAP_ROUTER_ADDRESS: str  # Required — set via .env; must be the router address for the target network (see env_vars/.env.example)
    WETH_ADDRESS: str  # Required — set via .env; WETH contract address for the target network (mainnet vs Sepolia WETH differ)
    UNISWAP_ROUTER_ABI: list = [
        {
            "inputs": [
                {"internalType": "address", "name": "_factory", "type": "address"},
                {"internalType": "address", "name": "_WETH", "type": "address"}
            ],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "inputs": [],
            "name": "WETH",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "tokenA", "type": "address"},
                {"internalType": "address", "name": "tokenB", "type": "address"},
                {"internalType": "uint256", "name": "amountADesired", "type": "uint256"},
                {"internalType": "uint256", "name": "amountBDesired", "type": "uint256"},
                {"internalType": "uint256", "name": "amountAMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountBMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "addLiquidity",
            "outputs": [
                {"internalType": "uint256", "name": "amountA", "type": "uint256"},
                {"internalType": "uint256", "name": "amountB", "type": "uint256"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"}
            ],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "token", "type": "address"},
                {"internalType": "uint256", "name": "amountTokenDesired", "type": "uint256"},
                {"internalType": "uint256", "name": "amountTokenMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETHMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "addLiquidityETH",
            "outputs": [
                {"internalType": "uint256", "name": "amountToken", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETH", "type": "uint256"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"}
            ],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "factory",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                {"internalType": "uint256", "name": "reserveIn", "type": "uint256"},
                {"internalType": "uint256", "name": "reserveOut", "type": "uint256"}
            ],
            "name": "getAmountIn",
            "outputs": [{"internalType": "uint256", "name": "amountIn", "type": "uint256"}],
            "stateMutability": "pure",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "reserveIn", "type": "uint256"},
                {"internalType": "uint256", "name": "reserveOut", "type": "uint256"}
            ],
            "name": "getAmountOut",
            "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
            "stateMutability": "pure",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"}
            ],
            "name": "getAmountsIn",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"}
            ],
            "name": "getAmountsOut",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountA", "type": "uint256"},
                {"internalType": "uint256", "name": "reserveA", "type": "uint256"},
                {"internalType": "uint256", "name": "reserveB", "type": "uint256"}
            ],
            "name": "quote",
            "outputs": [{"internalType": "uint256", "name": "amountB", "type": "uint256"}],
            "stateMutability": "pure",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "tokenA", "type": "address"},
                {"internalType": "address", "name": "tokenB", "type": "address"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                {"internalType": "uint256", "name": "amountAMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountBMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "removeLiquidity",
            "outputs": [
                {"internalType": "uint256", "name": "amountA", "type": "uint256"},
                {"internalType": "uint256", "name": "amountB", "type": "uint256"}
            ],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "token", "type": "address"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                {"internalType": "uint256", "name": "amountTokenMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETHMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "removeLiquidityETH",
            "outputs": [
                {"internalType": "uint256", "name": "amountToken", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETH", "type": "uint256"}
            ],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "token", "type": "address"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                {"internalType": "uint256", "name": "amountTokenMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETHMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "removeLiquidityETHSupportingFeeOnTransferTokens",
            "outputs": [{"internalType": "uint256", "name": "amountETH", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "token", "type": "address"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                {"internalType": "uint256", "name": "amountTokenMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETHMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                {"internalType": "bool", "name": "approveMax", "type": "bool"},
                {"internalType": "uint8", "name": "v", "type": "uint8"},
                {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                {"internalType": "bytes32", "name": "s", "type": "bytes32"}
            ],
            "name": "removeLiquidityETHWithPermit",
            "outputs": [
                {"internalType": "uint256", "name": "amountToken", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETH", "type": "uint256"}
            ],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "token", "type": "address"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                {"internalType": "uint256", "name": "amountTokenMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountETHMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                {"internalType": "bool", "name": "approveMax", "type": "bool"},
                {"internalType": "uint8", "name": "v", "type": "uint8"},
                {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                {"internalType": "bytes32", "name": "s", "type": "bytes32"}
            ],
            "name": "removeLiquidityETHWithPermitSupportingFeeOnTransferTokens",
            "outputs": [{"internalType": "uint256", "name": "amountETH", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "tokenA", "type": "address"},
                {"internalType": "address", "name": "tokenB", "type": "address"},
                {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                {"internalType": "uint256", "name": "amountAMin", "type": "uint256"},
                {"internalType": "uint256", "name": "amountBMin", "type": "uint256"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                {"internalType": "bool", "name": "approveMax", "type": "bool"},
                {"internalType": "uint8", "name": "v", "type": "uint8"},
                {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                {"internalType": "bytes32", "name": "s", "type": "bytes32"}
            ],
            "name": "removeLiquidityWithPermit",
            "outputs": [
                {"internalType": "uint256", "name": "amountA", "type": "uint256"},
                {"internalType": "uint256", "name": "amountB", "type": "uint256"}
            ],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapETHForExactTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactETHForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactETHForTokensSupportingFeeOnTransferTokens",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForETH",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForETHSupportingFeeOnTransferTokens",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokensSupportingFeeOnTransferTokens",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                {"internalType": "uint256", "name": "amountInMax", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapTokensForExactETH",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                {"internalType": "uint256", "name": "amountInMax", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapTokensForExactTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {"stateMutability": "payable", "type": "receive"}
    ]  # Source: @uniswap/v2-periphery@1.1.0-beta.0 (https://unpkg.com/@uniswap/v2-periphery@1.1.0-beta.0/build/UniswapV2Router02.json)

    # ERC20 ABI (minimal standard)
    ERC20_ABI: list = [
        {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    ]


config = Config()

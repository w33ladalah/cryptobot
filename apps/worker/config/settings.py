from pydantic_settings import BaseSettings
from pydantic import MySQLDsn, SecretStr, model_validator, IPvAnyAddress, field_serializer

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
        API_OLLAMA_URL: URL for rolling without loss (ollama) API requests. Defaults to "http://localhost:11434".
        OPENROUTER_API_URL: URL for openrouter.io API requests. Defaults to "https://api.openrouter.io/v1".
    """

    DEXSCREENER_API: str = "https://api.dexscreener.com/latest/dex/"
    COINGECKO_API: str = "https://api.coingecko.com/api/v3"
    DISCORD_BOT_TOKEN: SecretStr

    # Wallet & Uniswap settings
    WALLET_PRIVATE_KEY: SecretStr = None  # Private key for wallet access control
    WALLET_ADDRESS: SecretStr = None   # Address for wallet access control

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

    COINGECKO_API_KEY: SecretStr = None

    API_URL: str = "http://api:8000"

    WEB3_PLATFORM: str = 'moralis'
    WEB3_PROVIDER_URL: str = 'https://speedy-nodes-nyc.moralis.io/your_moralis_project_id/mainnet'
    WEB3_CHAIN_ID: int = 1
    WEB3_WALLET_ADDRESS: str = None
    WEB3_WALLET_PRIVATE_KEY: SecretStr = None


config = Config()

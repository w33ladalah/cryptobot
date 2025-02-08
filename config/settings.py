from pydantic_settings import BaseSettings
from pydantic import MySQLDsn, SecretStr, model_validator, IPvAnyAddress, field_serializer

from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    DEXSCREENER_API: str = "https://api.dexscreener.com/latest/dex/pairs"
    COINGECKO_API: str = "https://api.coingecko.com/api/v3"
    DISCORD_BOT_TOKEN: SecretStr

    # Wallet & Uniswap settings
    WALLET_PRIVATE_KEY: SecretStr
    WALLET_ADDRESS: SecretStr

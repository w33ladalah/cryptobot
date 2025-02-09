from pydantic_settings import BaseSettings
from pydantic import MySQLDsn, SecretStr, model_validator, IPvAnyAddress, field_serializer

from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    # Database settings
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: SecretStr
    MYSQL_PORT: int
    MYSQL_HOST: str

    # API settings
    API_RATE_LIMIT: str = "60/minute"

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        return f"mysql+pymysql://{self.MYSQL_USER}:" \
                + f"{self.MYSQL_PASSWORD.get_secret_value()}@" \
                + f"{self.MYSQL_HOST}:" \
                + f"{self.MYSQL_PORT}/" \
                + f"{self.MYSQL_DATABASE}"

config = Config()

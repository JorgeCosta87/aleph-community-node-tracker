from email.policy import default
from pathlib import Path
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from decouple import config

ROOT_DIR = Path(__file__).parent.parent.parent
POSTGRES_USER: str = config('POSTGRES_USER')
POSTGRES_PASSWORD: str = config('POSTGRES_PASSWORD')
POSTGRES_DB: str = config('POSTGRES_DB')
DB_HOST: str = config('DB_HOST')
DB_PORT: int = config('DB_PORT', default=5432, cast=int)
EMAIL_VERIFY_DOMAIN: str = config('EMAIL_VERIFY_DOMAIN', default="localhost:8000", cast=str)
STREAMLIT_HOST: str = config('STREAMLIT_HOST', default="http://localhost:8501", cast=str)
DAYS_METRICS_STORED: int = config('DAYS_METRICS_STORED', default=5, cast=int)
TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', cast=str)


class BaseConfig(BaseSettings):
    root_dir: Path = ROOT_DIR
    email_verify_domain: str = EMAIL_VERIFY_DOMAIN
    postgres_user: str = POSTGRES_USER
    postgres_password: str = POSTGRES_PASSWORD
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    postgres_db_name: str = POSTGRES_DB
    streamlit_host: str = STREAMLIT_HOST
    days_metrics_stored: int = DAYS_METRICS_STORED
    telegram_bot_token: str = TELEGRAM_BOT_TOKEN

class DatabaseSettings(BaseConfig):
    @property
    def db_url(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.db_host,
            port=self.db_port,
            path=self.postgres_db_name
        )

class Settings(DatabaseSettings):
    pass

settings = Settings()
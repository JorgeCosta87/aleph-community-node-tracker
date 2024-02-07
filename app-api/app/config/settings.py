from pathlib import Path
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from decouple import config

ROOT_DIR = Path(__file__).parent.parent.parent
FASTAPI_HOST: str = config('FASTAPI_HOST', default="127.0.0.1")
FASTAPI_PORT: int = config('FASTAPI_PORT', default=8000)
POSTGRES_USER: str = config('POSTGRES_USER')
POSTGRES_PASSWORD: str = config('POSTGRES_PASSWORD')
POSTGRES_DB: str = config('POSTGRES_DB')
DB_HOST: str = config('DB_HOST')
DB_PORT: int = config('DB_PORT', default=5432, cast=int)


class BaseConfig(BaseSettings):
    root_dir: Path = ROOT_DIR
    fastapi_host: str = FASTAPI_HOST
    fast_api_port: str = FASTAPI_PORT
    postgres_user: str = POSTGRES_USER
    postgres_password: str = POSTGRES_PASSWORD
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    postgres_db_name: str = POSTGRES_DB

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
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    VERSION: Optional[str] = "9.9.9.9"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    REDIRECT_URI: str
    ACCOUNT_SID: str
    AUTH_TOKEN: str
    VERIFY_SERVICE_SID: str
    DATABASE_URL: str
    OLD_DATABASE_URL: str

    PROJECT_NAME: str = "virtual wallet"

    PYDEVD: bool = False
    PYDEVD_PORT: Optional[int] = None
    PYDEVD_HOST: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

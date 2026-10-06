from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./backend/.data/taskchecker.db"
    session_secret: str = "development-only-change-me"
    storage_root: str = "./backend/storage"
    debug: bool = False
    session_https_only: bool = False
    session_max_age_seconds: int = 3600
    max_upload_bytes: int = 10 * 1024 * 1024
    auth_rate_limit: int = 10

    model_config = SettingsConfigDict(
        env_prefix="TASKCHECKER_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

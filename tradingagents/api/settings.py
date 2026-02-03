"""Application settings loaded from environment."""

from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover - fallback for pydantic v1
    from pydantic import BaseSettings


class Settings(BaseSettings):
    api_prefix: str = "/api/v1"
    api_title: str = "TradingAgents Market Access API"
    api_version: str = "0.1.0"

    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30

    redis_url: Optional[str] = None

    auth_per_minute: int = 60
    auth_per_day: int = 20000
    anon_per_minute: int = 10
    anon_per_day: int = 1000

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()

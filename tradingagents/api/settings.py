"""Application settings loaded from environment."""

from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover - fallback for pydantic v1
    from pydantic import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    api_prefix: str = "/api/v1"
    api_title: str = "TradingAgents Market Access API"
    api_version: str = "0.1.0"

    jwt_secret: str = "dev-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 1440

    api_clients_json: Optional[str] = None
    dev_client_id: str = "dev-client"
    dev_client_secret: str = "dev-secret"

    redis_url: Optional[str] = None

    eodhd_api_key: Optional[str] = None
    eodhd_base_url: str = "https://eodhd.com/api"
    eodhd_cache_dir: str = "tradingagents/api/data_cache"
    eodhd_cache_ttl_seconds: int = 3600
    historical_cache_ttl_seconds: int = 3600
    intraday_cache_ttl_seconds: int = 300
    snapshot_cache_ttl_seconds: int = 5
    snapshot_stale_ttl_seconds: int = 300

    analytics_reports_dir: str = "./results"
    analytics_reports_egx_dir: Optional[str] = None

    auth_per_minute: int = 60
    auth_per_day: int = 20000
    anon_per_minute: int = 10
    anon_per_day: int = 1000

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()

"""EODHD client wrapper with caching."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from tradingagents.api.settings import settings
from tradingagents.api.services.eodhd_cache import (
    load_cached_payload,
    save_cached_payload,
)


class EodhdClient:
    """Thin client for EODHD exchange and symbol discovery."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        cache_ttl_seconds: Optional[int] = None,
    ) -> None:
        self.api_key = api_key or settings.eodhd_api_key
        self.base_url = (base_url or settings.eodhd_base_url).rstrip("/")
        self.cache_ttl_seconds = (
            settings.eodhd_cache_ttl_seconds
            if cache_ttl_seconds is None
            else cache_ttl_seconds
        )

    def get_exchange_details(self, exchange_code: str) -> Dict[str, Any]:
        cache_key = f"exchange_details_{exchange_code}"
        return self._get_json(
            endpoint=f"exchange-details/{exchange_code}",
            params={},
            cache_key=cache_key,
        )

    def get_exchange_symbols(self, exchange_code: str) -> List[Dict[str, Any]]:
        cache_key = f"exchange_symbols_{exchange_code}"
        return self._get_json(
            endpoint=f"exchange-symbol-list/{exchange_code}",
            params={},
            cache_key=cache_key,
        )

    def get_eod_series(
        self,
        symbol: str,
        exchange_code: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        cache_key = f"eod_{exchange_code}_{symbol}_{start_date}_{end_date}"
        return self._get_json(
            endpoint=f"eod/{symbol}.{exchange_code}",
            params={"from": start_date, "to": end_date},
            cache_key=cache_key,
        )

    def get_quote(self, symbol: str, exchange_code: str) -> Dict[str, Any]:
        cache_key = f"snapshot_{exchange_code}_{symbol}"
        return self._get_json(
            endpoint=f"real-time/{symbol}.{exchange_code}",
            params={},
            cache_key=cache_key,
        )

    def _get_json(self, endpoint: str, params: Dict[str, Any], cache_key: str) -> Any:
        cached = load_cached_payload(cache_key, ttl_seconds=self.cache_ttl_seconds)
        if cached is not None:
            return cached

        if not self.api_key:
            raise RuntimeError(
                "EODHD API key is required (set EODHD_API_KEY) to fetch data and no cached data was found."
            )

        request_params = {**params, "api_token": self.api_key, "fmt": "json"}
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(url, params=request_params, timeout=30)
        if response.status_code != 200:
            raise ValueError(
                f"EODHD request failed with status {response.status_code}: {response.text}"
            )

        payload = response.json()
        save_cached_payload(cache_key, payload)
        return payload

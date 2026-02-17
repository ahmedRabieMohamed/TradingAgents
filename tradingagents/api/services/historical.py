"""Historical price and corporate actions services."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Iterable, Optional

from fastapi import status

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.schemas.historical import (
    DailyBar,
    DailyHistoryResponse,
    HistoricalFreshness,
)
from tradingagents.api.services import market_registry
from tradingagents.api.services.eodhd_cache import load_cached_payload_with_meta
from tradingagents.api.services.eodhd_client import EodhdClient
from tradingagents.api.settings import settings

_MARKET_EXCHANGES = {
    "US": "US",
    "EGX": "EGX",
}


def _extract_value(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    lowered = {str(key).lower(): value for key, value in payload.items()}
    for key in keys:
        value = lowered.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def _coerce_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _get_market_context(market_id: str) -> tuple[str, str, dict[str, Any]]:
    market_key = market_id.upper()
    exchange_code = _MARKET_EXCHANGES.get(market_key)
    if not exchange_code:
        raise ValueError(f"Unknown market_id: {market_id}")
    market = market_registry.get_market(market_key)
    if not market:
        raise ValueError(f"Unknown market_id: {market_id}")
    return market_key, exchange_code, market


def _build_freshness(
    cache_meta: Optional[dict[str, Any]],
    fetch_time: Optional[datetime],
    cache_status: str,
) -> HistoricalFreshness:
    fetched_at = (
        cache_meta.get("fetched_at")
        if cache_meta
        else fetch_time or datetime.now(timezone.utc)
    )
    age_seconds = int(cache_meta.get("age_seconds", 0)) if cache_meta else 0
    return HistoricalFreshness(
        as_of=fetched_at,
        age_seconds=age_seconds,
        cache_status=cache_status,
    )


def _normalize_daily_bars(rows: Iterable[dict[str, Any]]) -> list[DailyBar]:
    bars: list[DailyBar] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        parsed_date = _parse_date(_extract_value(row, "date", "Date"))
        if parsed_date is None:
            continue
        bar = DailyBar(
            date=parsed_date,
            open=_coerce_float(_extract_value(row, "open", "Open")),
            high=_coerce_float(_extract_value(row, "high", "High")),
            low=_coerce_float(_extract_value(row, "low", "Low")),
            close=_coerce_float(_extract_value(row, "close", "Close")),
            adjusted_close=_coerce_float(
                _extract_value(row, "adjusted_close", "Adjusted_close")
            )
            if _extract_value(row, "adjusted_close", "Adjusted_close") is not None
            else None,
            volume=_coerce_int(_extract_value(row, "volume", "Volume")),
        )
        bars.append(bar)
    bars.sort(key=lambda item: item.date)
    return bars


def get_daily_history(
    market_id: str,
    symbol: str,
    start_date: date,
    end_date: date,
) -> DailyHistoryResponse:
    market_key, exchange_code, market = _get_market_context(market_id)
    symbol_key = symbol.upper()
    start_value = start_date.isoformat()
    end_value = end_date.isoformat()
    cache_key = f"eod_{exchange_code}_{symbol_key}_{start_value}_{end_value}"
    cache_meta = load_cached_payload_with_meta(
        cache_key, ttl_seconds=settings.historical_cache_ttl_seconds
    )
    cache_status = "fresh" if cache_meta else "miss"

    provider_payload: list[dict[str, Any]] | None = None
    fetch_time: datetime | None = None
    if cache_meta is None:
        try:
            provider_payload = EodhdClient(cache_ttl_seconds=0).get_eod_series(
                symbol_key, exchange_code, start_value, end_value
            )
            fetch_time = datetime.now(timezone.utc)
        except Exception as exc:
            raise ApiError(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                code="HISTORICAL_UNAVAILABLE",
                message="Historical data unavailable",
            ) from exc
        cache_meta = load_cached_payload_with_meta(
            cache_key, ttl_seconds=settings.historical_cache_ttl_seconds
        )
        if cache_meta is None:
            cache_meta = {
                "data": provider_payload or [],
                "fetched_at": fetch_time or datetime.now(timezone.utc),
                "age_seconds": 0,
            }

    payload = cache_meta.get("data") if cache_meta else []
    if not isinstance(payload, list):
        payload = []

    bars = _normalize_daily_bars(payload)
    adjusted_available = any(bar.adjusted_close is not None for bar in bars)
    freshness = _build_freshness(cache_meta, fetch_time, cache_status)

    return DailyHistoryResponse(
        market_id=market_key,
        symbol=symbol_key,
        currency=str(market.get("currency", "")),
        start_date=start_date,
        end_date=end_date,
        bars=bars,
        adjusted_close_available=adjusted_available,
        freshness=freshness,
    )

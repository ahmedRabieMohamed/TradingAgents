"""Snapshot quote retrieval with freshness labels."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import status

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.schemas.snapshots import (
    SnapshotEntitlement,
    SnapshotFreshness,
    SnapshotQuote,
    SnapshotResponse,
    SnapshotSession,
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
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
    else:
        cleaned = value
    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _build_session(market: dict[str, Any]) -> SnapshotSession:
    status_value = str(market.get("status", "closed"))
    return SnapshotSession(
        status=status_value,
        is_open=status_value == "open",
        next_open=_parse_iso_datetime(market.get("next_open")),
        next_close=_parse_iso_datetime(market.get("next_close")),
        timezone=str(market.get("timezone", "UTC")),
    )


def _build_entitlement(
    market: dict[str, Any], is_authenticated: bool
) -> SnapshotEntitlement:
    realtime_available = bool(market.get("realtime_available", False))
    delay_minutes = int(market.get("data_delay_minutes") or 0)
    effective_label = (
        "realtime" if realtime_available and is_authenticated else "delayed"
    )
    return SnapshotEntitlement(
        realtime_available=realtime_available,
        delay_minutes=delay_minutes,
        effective_label=effective_label,
    )


def _build_quote(
    payload: dict[str, Any],
    market_id: str,
    symbol: str,
    currency: str,
) -> SnapshotQuote:
    last_price = _coerce_float(_extract_value(payload, "close", "Close"))
    change = _coerce_float(_extract_value(payload, "change", "Change"))
    change_percent = _coerce_float(
        _extract_value(
            payload, "change_p", "changeP", "change_percent", "ChangePercent"
        )
    )
    session_high = _coerce_float(_extract_value(payload, "high", "High"))
    session_low = _coerce_float(_extract_value(payload, "low", "Low"))
    volume = _coerce_int(_extract_value(payload, "volume", "Volume"))
    previous_close = _extract_value(
        payload, "previousClose", "previous_close", "PreviousClose"
    )
    bid = _extract_value(payload, "bid", "Bid")
    ask = _extract_value(payload, "ask", "Ask")
    bid_value = _coerce_float(bid) if bid is not None else None
    ask_value = _coerce_float(ask) if ask is not None else None
    spread = None
    if bid_value is not None and ask_value is not None:
        spread = ask_value - bid_value

    return SnapshotQuote(
        market_id=market_id,
        symbol=symbol,
        currency=currency,
        last_price=last_price,
        change=change,
        change_percent=change_percent,
        session_high=session_high,
        session_low=session_low,
        volume=volume,
        previous_close=_coerce_float(previous_close, default=0.0)
        if previous_close is not None
        else None,
        bid=bid_value if bid_value is not None and ask_value is not None else None,
        ask=ask_value if bid_value is not None and ask_value is not None else None,
        spread=spread,
    )


def get_snapshot(
    market_id: str,
    symbol: str,
    is_authenticated: bool,
) -> SnapshotResponse:
    market_key = market_id.upper()
    exchange_code = _MARKET_EXCHANGES.get(market_key)
    if not exchange_code:
        raise ValueError(f"Unknown market_id: {market_id}")
    market = market_registry.get_market(market_key)
    if not market:
        raise ValueError(f"Unknown market_id: {market_id}")

    symbol_key = symbol.upper()
    cache_key = f"snapshot_{exchange_code}_{symbol_key}"
    cache_meta = load_cached_payload_with_meta(
        cache_key, ttl_seconds=settings.snapshot_cache_ttl_seconds
    )
    cache_status = "fresh" if cache_meta else "miss"

    provider_payload: dict[str, Any] | None = None
    if cache_meta is None:
        try:
            provider_payload = EodhdClient(cache_ttl_seconds=0).get_quote(
                symbol_key, exchange_code
            )
        except Exception as exc:
            cache_meta = load_cached_payload_with_meta(
                cache_key, ttl_seconds=settings.snapshot_stale_ttl_seconds
            )
            if cache_meta is None:
                raise ApiError(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    code="SNAPSHOT_UNAVAILABLE",
                    message="Snapshot data unavailable",
                ) from exc
            cache_status = "stale"
        else:
            cache_meta = load_cached_payload_with_meta(
                cache_key, ttl_seconds=settings.snapshot_cache_ttl_seconds
            )
            if cache_meta is None:
                cache_meta = {
                    "data": provider_payload or {},
                    "fetched_at": datetime.now(timezone.utc),
                    "age_seconds": 0,
                }

    payload = cache_meta.get("data") if cache_meta else {}
    if not isinstance(payload, dict):
        payload = {}

    fetched_at = cache_meta.get("fetched_at") if cache_meta else None
    if fetched_at is None:
        fetched_at = datetime.now(timezone.utc)
    age_seconds = int(cache_meta.get("age_seconds", 0)) if cache_meta else 0

    entitlement = _build_entitlement(market, is_authenticated)
    freshness_label = (
        "stale" if cache_status == "stale" else entitlement.effective_label
    )

    freshness = SnapshotFreshness(
        as_of=fetched_at,
        age_seconds=age_seconds,
        label=freshness_label,
        is_stale=cache_status == "stale",
        cache_status=cache_status,
    )

    session = _build_session(market)
    quote = _build_quote(
        payload,
        market_id=market_key,
        symbol=symbol_key,
        currency=str(market.get("currency", "")),
    )

    return SnapshotResponse(
        quote=quote,
        session=session,
        freshness=freshness,
        entitlement=entitlement,
    )

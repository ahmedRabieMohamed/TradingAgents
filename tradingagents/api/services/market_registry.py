"""Market registry service for discovery endpoints."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from tradingagents.api.services.eodhd_cache import load_cached_payload
from tradingagents.api.services.eodhd_client import EodhdClient
from tradingagents.api.settings import settings

_MARKET_EXCHANGES = {
    "US": "US",
    "EGX": "EGX",
}

_MARKET_SCHEDULES = {
    "US": {
        "timezone": "America/New_York",
        "session_open": "09:30",
        "session_close": "16:00",
        "trading_days": [0, 1, 2, 3, 4],
        "data_delay_minutes": 15,
        "realtime_available": True,
    },
    "EGX": {
        "timezone": "Africa/Cairo",
        "session_open": "10:00",
        "session_close": "14:30",
        "trading_days": [0, 1, 2, 3, 4],
        "data_delay_minutes": 15,
        "realtime_available": False,
    },
}

_MARKET_METADATA_DEFAULTS = {
    "US": {"name": "United States", "mic": "XNYS", "currency": "USD"},
    "EGX": {"name": "Egypt", "mic": "XCAI", "currency": "EGP"},
}

_EODHD_FALLBACK_TTL_SECONDS = 60 * 60 * 24 * 365 * 10


def _parse_time(value: str) -> time:
    return time.fromisoformat(value)


def _next_trading_date(start_date: date, trading_days: list[int]) -> date:
    current = start_date
    for _ in range(8):
        if current.weekday() in trading_days:
            return current
        current += timedelta(days=1)
    return start_date


def _normalize_provider_key(value: str) -> str:
    return value.replace("_", "").replace(" ", "").lower()


def _extract_provider_value(payload: dict, field: str) -> str | None:
    normalized_field = _normalize_provider_key(field)
    for key, value in payload.items():
        if _normalize_provider_key(str(key)) == normalized_field:
            return value
    return None


def _extract_exchange_metadata(exchange_details: dict) -> dict:
    if not isinstance(exchange_details, dict):
        return {}
    return {
        "name": _extract_provider_value(exchange_details, "Name"),
        "mic": _extract_provider_value(exchange_details, "MIC"),
        "currency": _extract_provider_value(exchange_details, "Currency"),
        "timezone": _extract_provider_value(exchange_details, "Timezone"),
    }


def _fetch_exchange_details(exchange_code: str, defaults: dict) -> dict:
    client = EodhdClient()
    details = None

    if settings.eodhd_api_key:
        try:
            details = client.get_exchange_details(exchange_code)
        except Exception:
            details = None

    if details is None:
        cache_key = f"exchange_details_{exchange_code}"
        details = load_cached_payload(
            cache_key,
            ttl_seconds=_EODHD_FALLBACK_TTL_SECONDS,
        )

    if details is None:
        return defaults

    return details


def _compute_session_status(market: dict) -> dict[str, datetime | str]:
    timezone = ZoneInfo(market["timezone"])
    trading_days = market["trading_days"]
    open_time = _parse_time(market["session_open"])
    close_time = _parse_time(market["session_close"])

    now = datetime.now(timezone)
    today = now.date()
    is_trading_day = today.weekday() in trading_days
    open_dt = datetime.combine(today, open_time, tzinfo=timezone)
    close_dt = datetime.combine(today, close_time, tzinfo=timezone)

    if is_trading_day and now < open_dt:
        status = "closed"
        next_open = open_dt
        next_close = close_dt
    elif is_trading_day and open_dt <= now < close_dt:
        status = "open"
        next_close = close_dt
        next_open_date = _next_trading_date(today + timedelta(days=1), trading_days)
        next_open = datetime.combine(next_open_date, open_time, tzinfo=timezone)
    else:
        status = "closed"
        next_open_date = _next_trading_date(today + timedelta(days=1), trading_days)
        next_open = datetime.combine(next_open_date, open_time, tzinfo=timezone)
        next_close = datetime.combine(next_open_date, close_time, tzinfo=timezone)

    return {
        "status": status,
        "next_open": next_open,
        "next_close": next_close,
    }


def _build_market(market_id: str) -> dict:
    schedule = _MARKET_SCHEDULES[market_id].copy()
    defaults = _MARKET_METADATA_DEFAULTS[market_id]
    exchange_code = _MARKET_EXCHANGES[market_id]
    exchange_details = _fetch_exchange_details(exchange_code, defaults)
    provider_metadata = _extract_exchange_metadata(exchange_details)
    name = provider_metadata.get("name") or defaults["name"]
    mic = provider_metadata.get("mic") or defaults["mic"]
    currency = provider_metadata.get("currency") or defaults["currency"]
    timezone = provider_metadata.get("timezone") or schedule["timezone"]
    return {
        "market_id": market_id,
        "exchange_code": exchange_code,
        "name": name,
        "mic": mic,
        "timezone": timezone,
        "currency": currency,
        "session_open": schedule["session_open"],
        "session_close": schedule["session_close"],
        "trading_days": schedule["trading_days"],
        "data_delay_minutes": schedule["data_delay_minutes"],
        "realtime_available": schedule["realtime_available"],
    }


def _serialize_market(market: dict) -> dict:
    session = _compute_session_status(market)
    payload = {**market}
    payload.update(
        {
            "status": session["status"],
            "next_open": session["next_open"].isoformat(),
            "next_close": session["next_close"].isoformat(),
        }
    )
    return payload


def list_markets() -> list[dict]:
    markets = [_build_market(market_id) for market_id in _MARKET_EXCHANGES]
    return [_serialize_market(market) for market in markets]


def get_market(market_id: str) -> dict | None:
    market_key = market_id.upper()
    if market_key not in _MARKET_EXCHANGES:
        return None
    market = _build_market(market_key)
    return _serialize_market(market)

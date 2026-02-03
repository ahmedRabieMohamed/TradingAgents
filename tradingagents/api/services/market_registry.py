"""Market registry service for discovery endpoints."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from tradingagents.api.services.eodhd_cache import load_cached_payload
from tradingagents.api.services.eodhd_client import EodhdClient


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


def _parse_time(value: str) -> time:
    return time.fromisoformat(value)


def _next_trading_date(start_date: date, trading_days: list[int]) -> date:
    current = start_date
    for _ in range(8):
        if current.weekday() in trading_days:
            return current
        current += timedelta(days=1)
    return start_date


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


def _extract_detail(
    details: dict, *keys: str, default: str | None = None
) -> str | None:
    for key in keys:
        if key in details and details[key] not in (None, ""):
            return str(details[key])
    lowered = {str(key).lower(): value for key, value in details.items()}
    for key in keys:
        value = lowered.get(key.lower())
        if value not in (None, ""):
            return str(value)
    return default


def _load_cached_exchange_details(exchange_code: str) -> dict | None:
    cache_key = f"exchange_details_{exchange_code}"
    cached = load_cached_payload(cache_key, ttl_seconds=60 * 60 * 24 * 365 * 10)
    if isinstance(cached, dict):
        return cached
    return None


def _fetch_exchange_details(exchange_code: str) -> dict:
    client = EodhdClient()
    try:
        payload = client.get_exchange_details(exchange_code)
    except Exception as exc:  # pragma: no cover - network failure fallback
        cached = _load_cached_exchange_details(exchange_code)
        if cached is not None:
            return cached
        raise ValueError(
            f"Unable to fetch exchange details for {exchange_code}; no cached data available."
        ) from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Exchange details for {exchange_code} must be a dictionary")
    return payload


def _build_market(market_id: str) -> dict:
    exchange_code = _MARKET_EXCHANGES[market_id]
    schedule = _MARKET_SCHEDULES[market_id].copy()
    defaults = _MARKET_METADATA_DEFAULTS[market_id]
    details = _fetch_exchange_details(exchange_code)
    name = _extract_detail(details, "Name", "name", default=defaults["name"])
    mic = _extract_detail(
        details, "MIC", "Mic", "mic", "Exchange", "exchange", default=defaults["mic"]
    )
    currency = _extract_detail(
        details, "Currency", "currency", default=defaults["currency"]
    )
    return {
        "market_id": market_id,
        "name": name,
        "mic": mic,
        "timezone": schedule["timezone"],
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

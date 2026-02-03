"""Market registry service for discovery endpoints."""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


_MARKETS_PATH = Path(__file__).resolve().parents[1] / "data" / "markets.json"


def _load_markets() -> list[dict]:
    with _MARKETS_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("markets.json must contain a list of markets")
    return payload


_MARKETS = _load_markets()
_MARKET_INDEX = {market["market_id"].upper(): market for market in _MARKETS}


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
    return [_serialize_market(market) for market in _MARKETS]


def get_market(market_id: str) -> dict | None:
    market = _MARKET_INDEX.get(market_id.upper())
    if not market:
        return None
    return _serialize_market(market)

"""Symbol discovery service helpers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

from tradingagents.api.services import market_registry
from tradingagents.api.services.eodhd_cache import load_cached_payload
from tradingagents.api.services.eodhd_client import EodhdClient


_MARKET_EXCHANGES = {
    "US": "US",
    "EGX": "EGX",
}

_METRICS_CACHE: dict[tuple[str, str], dict[str, float]] = {}


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


def _coerce_float(value: Any, default: float | None = 0.0) -> float | None:
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


def _load_cached_exchange_symbols(exchange_code: str) -> list[dict[str, Any]] | None:
    cache_key = f"exchange_symbols_{exchange_code}"
    cached = load_cached_payload(cache_key, ttl_seconds=60 * 60 * 24 * 365 * 10)
    if isinstance(cached, list):
        return cached
    return None


def _fetch_exchange_symbols(exchange_code: str) -> list[dict[str, Any]]:
    client = EodhdClient()
    try:
        payload = client.get_exchange_symbols(exchange_code)
    except Exception as exc:  # pragma: no cover - network failure fallback
        cached = _load_cached_exchange_symbols(exchange_code)
        if cached is not None:
            return cached
        raise ValueError(
            f"Unable to fetch exchange symbols for {exchange_code}; no cached data available."
        ) from exc
    if not isinstance(payload, list):
        raise ValueError(f"Symbol dataset for {exchange_code} must be a list")
    return payload


def _parse_series_date(item: dict[str, Any]) -> date:
    value = item.get("date") or item.get("Date") or ""
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return date.min


def _get_metrics(
    market_id: str,
    exchange_code: str,
    symbol_code: str,
    payload: dict[str, Any],
    allow_series: bool = False,
) -> dict[str, float]:
    cache_key = (market_id, symbol_code.upper())
    cached = _METRICS_CACHE.get(cache_key)
    if cached is not None:
        return cached

    provider_volume = _extract_value(
        payload, "Volume", "volume", "AvgVolume", "AverageVolume"
    )
    provider_change = _extract_value(
        payload, "ChangePercent", "change_percent", "ChangeP", "change_p", "Change%"
    )
    avg_volume = _coerce_float(provider_volume, default=None)
    change_pct = _coerce_float(provider_change, default=None)

    if (avg_volume is None or change_pct is None) and allow_series:
        client = EodhdClient()
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        try:
            series = client.get_eod_series(
                symbol_code,
                exchange_code,
                start_date.isoformat(),
                end_date.isoformat(),
            )
        except Exception:  # pragma: no cover - network failure fallback
            series = []
        if series:
            sorted_series = sorted(series, key=_parse_series_date)
            volumes = [
                _coerce_float(item.get("volume") or item.get("Volume"), default=0.0)
                for item in sorted_series
            ]
            valid_volumes = [volume for volume in volumes if volume is not None]
            computed_volume = (
                sum(valid_volumes) / len(valid_volumes) if valid_volumes else 0.0
            )
            first_close = None
            last_close = None
            for item in sorted_series:
                close_value = _coerce_float(
                    item.get("close") or item.get("Close"), default=None
                )
                if close_value is not None:
                    first_close = close_value
                    break
            for item in reversed(sorted_series):
                close_value = _coerce_float(
                    item.get("close") or item.get("Close"), default=None
                )
                if close_value is not None:
                    last_close = close_value
                    break
            computed_change = (
                ((last_close - first_close) / first_close) * 100
                if first_close and last_close
                else 0.0
            )
            if avg_volume is None:
                avg_volume = computed_volume
            if change_pct is None:
                change_pct = computed_change

    if avg_volume is None:
        avg_volume = 0.0
    if change_pct is None:
        change_pct = 0.0

    metrics = {
        "avg_volume_1w": float(avg_volume or 0.0),
        "price_change_pct_1w": float(change_pct or 0.0),
    }
    _METRICS_CACHE[cache_key] = metrics
    return metrics


def load_symbol_data(market_id: str) -> list[dict[str, Any]]:
    market_key = market_id.upper()
    exchange_code = _MARKET_EXCHANGES.get(market_key)
    if not exchange_code:
        raise ValueError(f"Unknown market_id: {market_id}")
    market = market_registry.get_market(market_key)
    if not market:
        raise ValueError(f"Unknown market_id: {market_id}")
    currency = market.get("currency") or ""

    payload = _fetch_exchange_symbols(exchange_code)
    symbols: list[dict[str, Any]] = []
    for raw in payload:
        symbol_code = _extract_value(
            raw, "Code", "code", "Symbol", "symbol", "Ticker", "ticker"
        )
        if not symbol_code:
            continue
        symbol_key = str(symbol_code).upper()
        name = _extract_value(raw, "Name", "name") or str(symbol_code)
        sector = _extract_value(raw, "Sector", "sector", "Industry", "industry")
        market_cap_value = _extract_value(
            raw,
            "MarketCapitalization",
            "market_cap",
            "marketCap",
            "Capitalization",
            "capitalization",
        )
        market_cap = _coerce_float(market_cap_value, default=0.0) or 0.0
        metrics = _get_metrics(
            market_key,
            exchange_code,
            symbol_key,
            raw,
            allow_series=False,
        )
        symbols.append(
            {
                "ticker": symbol_key,
                "name": str(name),
                "sector": str(sector) if sector else "Unknown",
                "market_cap": float(market_cap),
                "avg_volume_1w": metrics["avg_volume_1w"],
                "price_change_pct_1w": metrics["price_change_pct_1w"],
                "currency": str(currency),
            }
        )
    return symbols


def _paginate(
    items: list[dict[str, Any]],
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int, Optional[int]]:
    total = len(items)
    start = max(offset, 0)
    end = start + limit
    page = items[start:end]
    next_offset = end if end < total else None
    return page, total, next_offset


def search_symbols(
    market_id: str,
    query: str,
    limit: int = 25,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int, Optional[int]]:
    query_value = query.strip().lower()
    if not query_value:
        return [], 0, None
    data = load_symbol_data(market_id)
    matches: list[tuple[int, dict[str, Any]]] = []
    for symbol in data:
        ticker = str(symbol.get("ticker", ""))
        name = str(symbol.get("name", ""))
        ticker_lower = ticker.lower()
        name_lower = name.lower()
        if ticker_lower.startswith(query_value) or name_lower.startswith(query_value):
            matches.append((0, symbol))
        elif query_value in ticker_lower or query_value in name_lower:
            matches.append((1, symbol))
    matches.sort(key=lambda item: (item[0], -float(item[1].get("avg_volume_1w", 0))))
    ordered = [symbol for _, symbol in matches]
    return _paginate(ordered, limit, offset)


def filter_symbols(
    market_id: str,
    sector: Optional[str] = None,
    market_cap_min: Optional[float] = None,
    market_cap_max: Optional[float] = None,
    sort: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int, Optional[int]]:
    data = load_symbol_data(market_id)
    filtered: list[dict[str, Any]] = []
    for symbol in data:
        if sector and symbol.get("sector"):
            if str(symbol["sector"]).lower() != sector.lower():
                continue
        if market_cap_min is not None and symbol.get("market_cap") is not None:
            if float(symbol["market_cap"]) < market_cap_min:
                continue
        if market_cap_max is not None and symbol.get("market_cap") is not None:
            if float(symbol["market_cap"]) > market_cap_max:
                continue
        filtered.append(symbol)
    if sort == "most_active":
        filtered.sort(
            key=lambda item: float(item.get("avg_volume_1w", 0)), reverse=True
        )
    else:
        filtered.sort(key=lambda item: str(item.get("ticker", "")))
    return _paginate(filtered, limit, offset)


def get_most_active(
    market_id: str,
    limit: int = 25,
    offset: int = 0,
    window: str = "1w",
) -> tuple[list[dict[str, Any]], int, Optional[int], dict[str, str]]:
    data = load_symbol_data(market_id)
    ordered = sorted(
        data, key=lambda item: float(item.get("avg_volume_1w", 0)), reverse=True
    )
    items, total, next_offset = _paginate(ordered, limit, offset)
    meta = {"definition": "volume", "window": window}
    return items, total, next_offset, meta


def get_trending(
    market_id: str,
    limit: int = 25,
    offset: int = 0,
    window: str = "1w",
) -> tuple[list[dict[str, Any]], int, Optional[int], dict[str, str]]:
    data = load_symbol_data(market_id)
    ordered = sorted(
        data,
        key=lambda item: float(item.get("price_change_pct_1w", 0)),
        reverse=True,
    )
    items, total, next_offset = _paginate(ordered, limit, offset)
    meta = {"definition": "price_change_pct", "window": window}
    return items, total, next_offset, meta

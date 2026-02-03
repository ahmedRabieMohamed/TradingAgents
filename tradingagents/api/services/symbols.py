"""Symbol discovery service helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


_MARKET_FILES = {
    "US": "symbols_us.json",
    "EGX": "symbols_egx.json",
}


def load_symbol_data(market_id: str) -> list[dict[str, Any]]:
    market_key = market_id.upper()
    filename = _MARKET_FILES.get(market_key)
    if not filename:
        raise ValueError(f"Unknown market_id: {market_id}")
    data_path = Path(__file__).resolve().parents[1] / "data" / filename
    with data_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"Symbol dataset for {market_id} must be a list")
    return payload


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

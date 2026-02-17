"""Historical price and corporate actions services."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Iterable, Optional

from fastapi import status

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.schemas.historical import (
    CorporateActionsResponse,
    DailyBar,
    DailyHistoryResponse,
    DividendAction,
    HistoricalFreshness,
    IntradayCandle,
    IntradayHistoryResponse,
    SplitAction,
)
from tradingagents.api.services import market_registry
from tradingagents.api.services.eodhd_cache import load_cached_payload_with_meta
from tradingagents.api.services.eodhd_client import EodhdClient
from tradingagents.api.settings import settings

_MARKET_EXCHANGES = {
    "US": "US",
    "EGX": "EGX",
}

_INTRADAY_RANGE_CONFIG = {
    "1D": {"interval": "1m", "days": 1},
    "1W": {"interval": "5m", "days": 7},
    "1M": {"interval": "5m", "days": 30},
    "1Y": {"interval": "1h", "days": 365},
}

_INTRADAY_INTERVAL_LIMITS = {
    "1m": 120,
    "5m": 600,
    "1h": 7200,
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


def _coerce_optional_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    if isinstance(value, str):
        if value.isdigit():
            return datetime.fromtimestamp(int(value), tz=timezone.utc)
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def _get_market_context(market_id: str) -> tuple[str, str, dict[str, Any]]:
    market_key = market_id.upper()
    market = market_registry.get_market(market_key)
    if not market:
        raise ValueError(f"Unknown market_id: {market_id}")
    exchange_code = market.get("exchange_code") or _MARKET_EXCHANGES.get(market_key)
    if not exchange_code:
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
            adjusted_close=_coerce_optional_float(
                _extract_value(row, "adjusted_close", "Adjusted_close")
            ),
            volume=_coerce_int(_extract_value(row, "volume", "Volume")),
        )
        bars.append(bar)
    bars.sort(key=lambda item: item.date)
    return bars


def _normalize_intraday_candles(rows: Iterable[dict[str, Any]]) -> list[IntradayCandle]:
    candles: list[IntradayCandle] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        timestamp = _parse_timestamp(
            _extract_value(row, "timestamp", "date", "Datetime")
        )
        if timestamp is None:
            continue
        candles.append(
            IntradayCandle(
                timestamp=timestamp.astimezone(timezone.utc),
                open=_coerce_float(_extract_value(row, "open", "Open")),
                high=_coerce_float(_extract_value(row, "high", "High")),
                low=_coerce_float(_extract_value(row, "low", "Low")),
                close=_coerce_float(_extract_value(row, "close", "Close")),
                volume=_coerce_int(_extract_value(row, "volume", "Volume")),
            )
        )
    candles.sort(key=lambda item: item.timestamp)
    return candles


def _normalize_dividends(rows: Iterable[dict[str, Any]]) -> list[DividendAction]:
    dividends: list[DividendAction] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        ex_date = _parse_date(_extract_value(row, "date", "ex_date", "exDate"))
        amount_value = _extract_value(row, "value", "amount", "dividend")
        if ex_date is None or amount_value in (None, ""):
            continue
        dividends.append(
            DividendAction(
                ex_date=ex_date,
                amount=_coerce_float(amount_value),
                declaration_date=_parse_date(
                    _extract_value(row, "declarationDate", "declaration_date")
                ),
                record_date=_parse_date(
                    _extract_value(row, "recordDate", "record_date")
                ),
                payment_date=_parse_date(
                    _extract_value(row, "paymentDate", "payment_date")
                ),
                currency=_extract_value(row, "currency", "Currency"),
            )
        )
    return dividends


def _normalize_splits(rows: Iterable[dict[str, Any]]) -> list[SplitAction]:
    splits: list[SplitAction] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        split_date = _parse_date(_extract_value(row, "date", "split_date", "splitDate"))
        if split_date is None:
            continue
        before_value = _extract_value(row, "before", "Before")
        after_value = _extract_value(row, "after", "After")
        splits.append(
            SplitAction(
                date=split_date,
                ratio=_extract_value(row, "split", "ratio", "Split", "Ratio"),
                before=_coerce_float(before_value)
                if before_value not in (None, "")
                else None,
                after=_coerce_float(after_value)
                if after_value not in (None, "")
                else None,
            )
        )
    return splits


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


def get_intraday_history(
    market_id: str,
    symbol: str,
    range_key: str,
    is_authenticated: bool,
) -> IntradayHistoryResponse:
    if not is_authenticated:
        raise ApiError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="INTRADAY_NOT_ENTITLED",
            message="Intraday data requires authentication",
        )

    market_key, exchange_code, market = _get_market_context(market_id)
    symbol_key = symbol.upper()
    range_value = range_key.upper()
    range_config = _INTRADAY_RANGE_CONFIG.get(range_value)
    if not range_config:
        raise ValueError(f"Unknown intraday range: {range_key}")
    interval = range_config["interval"]
    days = int(range_config["days"])
    limit_days = _INTRADAY_INTERVAL_LIMITS.get(interval)
    if limit_days is not None and days > limit_days:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INTRADAY_RANGE_TOO_LARGE",
            message="Requested intraday range exceeds provider limits",
        )

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days)
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    cache_key = f"intraday_{exchange_code}_{symbol_key}_{interval}_{start_ts}_{end_ts}"
    cache_meta = load_cached_payload_with_meta(
        cache_key, ttl_seconds=settings.intraday_cache_ttl_seconds
    )
    cache_status = "fresh" if cache_meta else "miss"

    provider_payload: list[dict[str, Any]] | None = None
    fetch_time: datetime | None = None
    if cache_meta is None:
        try:
            provider_payload = EodhdClient(cache_ttl_seconds=0).get_intraday_series(
                symbol_key, exchange_code, start_ts, end_ts, interval
            )
            fetch_time = datetime.now(timezone.utc)
        except Exception as exc:
            raise ApiError(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                code="INTRADAY_UNAVAILABLE",
                message="Intraday data unavailable",
            ) from exc
        cache_meta = load_cached_payload_with_meta(
            cache_key, ttl_seconds=settings.intraday_cache_ttl_seconds
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

    candles = _normalize_intraday_candles(payload)
    freshness = _build_freshness(cache_meta, fetch_time, cache_status)

    return IntradayHistoryResponse(
        market_id=market_key,
        symbol=symbol_key,
        currency=str(market.get("currency", "")),
        interval=interval,
        range=range_value,
        timezone="UTC",
        start_timestamp=start_dt,
        end_timestamp=end_dt,
        candles=candles,
        freshness=freshness,
    )


def get_corporate_actions(
    market_id: str,
    symbol: str,
    start_date: Optional[date],
    end_date: Optional[date],
) -> CorporateActionsResponse:
    market_key, exchange_code, _ = _get_market_context(market_id)
    symbol_key = symbol.upper()
    start_value = start_date.isoformat() if start_date else None
    end_value = end_date.isoformat() if end_date else None

    def _load_or_fetch(
        cache_key: str,
        fetch_fn: Callable[[], list[dict[str, Any]]],
    ) -> tuple[list[dict[str, Any]], Optional[dict[str, Any]], bool, bool]:
        cache_meta = load_cached_payload_with_meta(
            cache_key, ttl_seconds=settings.historical_cache_ttl_seconds
        )
        cache_hit = cache_meta is not None
        if cache_meta is None:
            try:
                provider_payload = fetch_fn()
                fetch_time = datetime.now(timezone.utc)
            except Exception:
                return [], None, False, cache_hit
            cache_meta = load_cached_payload_with_meta(
                cache_key, ttl_seconds=settings.historical_cache_ttl_seconds
            )
            if cache_meta is None:
                cache_meta = {
                    "data": provider_payload or [],
                    "fetched_at": fetch_time,
                    "age_seconds": 0,
                }
        payload = cache_meta.get("data") if cache_meta else []
        if not isinstance(payload, list):
            payload = []
        return payload, cache_meta, True, cache_hit

    dividends_key = f"dividends_{exchange_code}_{symbol_key}_{start_value or 'na'}_{end_value or 'na'}"
    splits_key = (
        f"splits_{exchange_code}_{symbol_key}_{start_value or 'na'}_{end_value or 'na'}"
    )

    dividends_data, dividends_meta, dividends_ok, dividends_hit = _load_or_fetch(
        dividends_key,
        lambda: EodhdClient(cache_ttl_seconds=0).get_dividends(
            symbol_key, exchange_code, start_value, end_value
        ),
    )
    splits_data, splits_meta, splits_ok, splits_hit = _load_or_fetch(
        splits_key,
        lambda: EodhdClient(cache_ttl_seconds=0).get_splits(
            symbol_key, exchange_code, start_value, end_value
        ),
    )

    if not dividends_ok and not splits_ok:
        raise ApiError(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="CORP_ACTIONS_UNAVAILABLE",
            message="Corporate actions unavailable",
        )

    dividends = _normalize_dividends(dividends_data)
    splits = _normalize_splits(splits_data)

    metas = [meta for meta in (dividends_meta, splits_meta) if meta]
    fetched_at = (
        min(meta["fetched_at"] for meta in metas)
        if metas
        else datetime.now(timezone.utc)
    )
    age_seconds = max(int(meta.get("age_seconds", 0)) for meta in metas) if metas else 0
    cache_status = "fresh" if dividends_hit and splits_hit else "miss"

    freshness = HistoricalFreshness(
        as_of=fetched_at,
        age_seconds=age_seconds,
        cache_status=cache_status,
    )

    return CorporateActionsResponse(
        market_id=market_key,
        symbol=symbol_key,
        dividends=dividends,
        splits=splits,
        freshness=freshness,
    )

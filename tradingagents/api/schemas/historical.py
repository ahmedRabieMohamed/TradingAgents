"""Historical price and corporate actions response models."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class HistoricalFreshness(BaseModel):
    """Freshness metadata for historical payloads."""

    as_of: datetime
    age_seconds: int
    cache_status: str


class DailyBar(BaseModel):
    """Daily OHLCV bar with optional adjusted close."""

    date: date
    open: float
    high: float
    low: float
    close: float
    adjusted_close: Optional[float] = None
    volume: int


class DailyRangeFilterDiagnostics(BaseModel):
    """Diagnostics for dropped daily bars outside requested range."""

    dropped_count: int
    dropped_min_date: Optional[date]
    dropped_max_date: Optional[date]


class DailyHistoryResponse(BaseModel):
    """Daily historical series response."""

    market_id: str
    symbol: str
    currency: str
    start_date: date
    end_date: date
    bars: List[DailyBar]
    adjusted_close_available: bool
    freshness: HistoricalFreshness
    range_filter: Optional[DailyRangeFilterDiagnostics] = None


class IntradayCandle(BaseModel):
    """Intraday candlestick data point."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class IntradayHistoryResponse(BaseModel):
    """Intraday historical series response."""

    market_id: str
    symbol: str
    currency: str
    interval: str
    range: str
    timezone: str
    start_timestamp: datetime
    end_timestamp: datetime
    candles: List[IntradayCandle]
    freshness: HistoricalFreshness


class DividendAction(BaseModel):
    """Dividend corporate action."""

    ex_date: date
    amount: float
    declaration_date: Optional[date] = None
    record_date: Optional[date] = None
    payment_date: Optional[date] = None
    currency: Optional[str] = None


class SplitAction(BaseModel):
    """Split corporate action."""

    date: date
    ratio: Optional[str] = None
    before: Optional[float] = None
    after: Optional[float] = None


class CorporateActionsResponse(BaseModel):
    """Corporate actions response payload."""

    market_id: str
    symbol: str
    dividends: List[DividendAction]
    splits: List[SplitAction]
    freshness: HistoricalFreshness

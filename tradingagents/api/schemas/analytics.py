"""Async analytics request/response schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

DEFAULT_INDICATORS: List[str] = [
    "ma",
    "ema",
    "rsi",
    "macd",
    "atr",
    "bollinger",
]


class AnalyticsReportRequest(BaseModel):
    """Request payload for async analytics report generation."""

    market_id: str
    symbol: str
    analysis_date: date
    lookback_days: int
    online: bool
    indicators: List[str] = Field(default_factory=lambda: list(DEFAULT_INDICATORS))


class AnalyticsReportJob(BaseModel):
    """Job status record for async analytics reports."""

    report_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    idempotency_key: Optional[str] = None


class IndicatorsSummary(BaseModel):
    """Computed indicator outputs."""

    ma: Dict[str, float]
    ema: Dict[str, float]
    rsi: float
    macd: Dict[str, float]
    atr: float
    bollinger: Dict[str, float]


class TrendMomentumVolatility(BaseModel):
    """Trend, momentum, and volatility synopsis."""

    trend: str
    momentum: str
    volatility: str
    summary: Optional[str] = None


class SupportResistanceLevel(BaseModel):
    """Support/resistance level description."""

    level: float
    label: str
    note: Optional[str] = None


class LiquidityAnomaly(BaseModel):
    """Liquidity or volume anomaly indicator."""

    label: str
    severity: str
    description: Optional[str] = None


class DecisionSummary(BaseModel):
    """Decision label with confidence and rationale."""

    label: str
    confidence: float
    rationale: str


class ReportArtifacts(BaseModel):
    """Filesystem metadata for report artifacts."""

    report_dir: str
    section_files: Dict[str, str]


class AnalyticsReportResult(BaseModel):
    """Completed analytics report payload."""

    report_id: str
    final_report: str
    indicators: IndicatorsSummary
    summary: TrendMomentumVolatility
    support_resistance: List[SupportResistanceLevel]
    liquidity_anomalies: List[LiquidityAnomaly]
    risk_notes: List[str]
    decision: DecisionSummary
    artifacts: ReportArtifacts

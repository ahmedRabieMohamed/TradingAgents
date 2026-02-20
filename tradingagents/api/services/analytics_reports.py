"""Analytics report generation helpers and orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import logging
import traceback
from typing import Any, Dict, List, Optional

import pandas as pd
from stockstats import wrap

from tradingagents.api.schemas.analytics import (
    AnalyticsReportJob,
    AnalyticsReportRequest,
    AnalyticsReportResult,
    DecisionSummary,
    IndicatorsSummary,
    LiquidityAnomaly,
    ReportArtifacts,
    SupportResistanceLevel,
    TrendMomentumVolatility,
)
from tradingagents.api.services import historical as historical_service
from tradingagents.api.services import report_storage
from tradingagents.dataflows.interface import get_stock_stats_indicators_window
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.egyptian_config import EGYPTIAN_CONFIG
from tradingagents.graph.egyptian_trading_graph import EgyptianTradingAgentsGraph
from tradingagents.graph.trading_graph import TradingAgentsGraph

LOGGER = logging.getLogger(__name__)


@dataclass
class ReportBuffer:
    """Collects report sections and renders CLI-style report output."""

    market_id: str
    report_sections: Dict[str, Optional[str]]
    final_report: Optional[str] = None

    def update_section(self, section_name: str, content: Optional[str]) -> None:
        if section_name not in self.report_sections:
            return
        if content:
            self.report_sections[section_name] = content
            self.final_report = build_cli_report(self.market_id, self.report_sections)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _ensure_dataframe(
    market_id: str, symbol: str, analysis_date: date, lookback_days: int
) -> pd.DataFrame:
    start_date = analysis_date - timedelta(days=lookback_days)
    history = historical_service.get_daily_history(
        market_id=market_id,
        symbol=symbol,
        start_date=start_date,
        end_date=analysis_date,
    )
    rows = [
        {
            "Date": bar.date,
            "Open": bar.open,
            "High": bar.high,
            "Low": bar.low,
            "Close": bar.close,
            "Volume": bar.volume,
        }
        for bar in history.bars
    ]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def _safe_indicator_value(
    stock_df: pd.DataFrame,
    indicator_key: str,
    fallback_symbol: str,
    analysis_date: date,
    lookback_days: int,
    online: bool,
) -> float:
    try:
        stock_df[indicator_key]
        value = stock_df[indicator_key].iloc[-1]
        return _coerce_float(value)
    except Exception:
        try:
            fallback_text = get_stock_stats_indicators_window(
                fallback_symbol,
                indicator_key,
                analysis_date.isoformat(),
                lookback_days,
                online,
            )
            lines = [line for line in fallback_text.splitlines() if ":" in line]
            if not lines:
                return 0.0
            last_line = lines[-1]
            _, value = last_line.split(":", 1)
            return _coerce_float(value.strip())
        except Exception:
            return 0.0


def compute_indicator_summary(
    market_id: str,
    symbol: str,
    analysis_date: date,
    lookback_days: int,
    online: bool,
) -> tuple[
    IndicatorsSummary,
    TrendMomentumVolatility,
    List[SupportResistanceLevel],
    List[LiquidityAnomaly],
    List[str],
    DecisionSummary,
    pd.DataFrame,
]:
    df = _ensure_dataframe(market_id, symbol, analysis_date, lookback_days)
    if df.empty:
        indicators = IndicatorsSummary(
            ma={},
            ema={},
            rsi=0.0,
            macd={},
            atr=0.0,
            bollinger={},
        )
        summary = TrendMomentumVolatility(
            trend="insufficient data",
            momentum="insufficient data",
            volatility="insufficient data",
            summary="No historical data available for indicator computation.",
        )
        decision = DecisionSummary(
            label="HOLD",
            confidence=0.0,
            rationale="Insufficient historical data for a decision.",
        )
        return (
            indicators,
            summary,
            [],
            [],
            ["No historical data available."],
            decision,
            df,
        )

    stock_df = wrap(df.copy())
    sma_20 = _safe_indicator_value(
        stock_df,
        "close_20_sma",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    sma_50 = _safe_indicator_value(
        stock_df,
        "close_50_sma",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    sma_200 = _safe_indicator_value(
        stock_df,
        "close_200_sma",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    ema_10 = _safe_indicator_value(
        stock_df,
        "close_10_ema",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    ema_20 = _safe_indicator_value(
        stock_df,
        "close_20_ema",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    rsi = _safe_indicator_value(
        stock_df,
        "rsi_14",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    macd = _safe_indicator_value(
        stock_df,
        "macd",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    macds = _safe_indicator_value(
        stock_df,
        "macds",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    macdh = _safe_indicator_value(
        stock_df,
        "macdh",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    atr = _safe_indicator_value(
        stock_df,
        "atr",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    boll = _safe_indicator_value(
        stock_df,
        "boll",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    boll_ub = _safe_indicator_value(
        stock_df,
        "boll_ub",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )
    boll_lb = _safe_indicator_value(
        stock_df,
        "boll_lb",
        symbol,
        analysis_date,
        lookback_days,
        online,
    )

    indicators = IndicatorsSummary(
        ma={"sma_20": sma_20, "sma_50": sma_50, "sma_200": sma_200},
        ema={"ema_10": ema_10, "ema_20": ema_20},
        rsi=rsi,
        macd={"macd": macd, "signal": macds, "histogram": macdh},
        atr=atr,
        bollinger={"mid": boll, "upper": boll_ub, "lower": boll_lb},
    )

    summary = summarize_trend_momentum_volatility(indicators, df)
    support_resistance = compute_support_resistance(df)
    liquidity_anomalies = detect_liquidity_anomalies(df)
    risk_notes = generate_risk_notes(df, indicators, liquidity_anomalies)
    decision = compute_decision_label(indicators, summary, df)

    return (
        indicators,
        summary,
        support_resistance,
        liquidity_anomalies,
        risk_notes,
        decision,
        df,
    )


def summarize_trend_momentum_volatility(
    indicators: IndicatorsSummary, df: pd.DataFrame
) -> TrendMomentumVolatility:
    close = _coerce_float(df["Close"].iloc[-1])
    sma_50 = indicators.ma.get("sma_50", 0.0)
    sma_200 = indicators.ma.get("sma_200", 0.0)
    ema_20 = indicators.ema.get("ema_20", 0.0)
    macdh = indicators.macd.get("histogram", 0.0)
    rsi = indicators.rsi
    atr = indicators.atr

    trend_score = sum(
        [
            close > sma_50,
            close > sma_200,
            close > ema_20,
        ]
    )
    if trend_score >= 2:
        trend = "uptrend"
    elif trend_score == 1:
        trend = "mixed"
    else:
        trend = "downtrend"

    if rsi >= 70:
        momentum = "overbought"
    elif rsi <= 30:
        momentum = "oversold"
    elif macdh > 0:
        momentum = "positive"
    elif macdh < 0:
        momentum = "negative"
    else:
        momentum = "neutral"

    atr_ratio = atr / close if close else 0.0
    if atr_ratio >= 0.06:
        volatility = "high"
    elif atr_ratio >= 0.03:
        volatility = "moderate"
    else:
        volatility = "low"

    summary = (
        f"Price is {trend} with {momentum} momentum and {volatility} volatility. "
        f"ATR/Close ratio is {atr_ratio:.2%}."
    )

    return TrendMomentumVolatility(
        trend=trend,
        momentum=momentum,
        volatility=volatility,
        summary=summary,
    )


def compute_support_resistance(df: pd.DataFrame) -> List[SupportResistanceLevel]:
    if df.empty:
        return []
    window = min(20, len(df))
    recent = df.tail(window)
    low = _coerce_float(recent["Low"].min())
    high = _coerce_float(recent["High"].max())
    last_close = _coerce_float(df["Close"].iloc[-1])
    pivot = (high + low + last_close) / 3 if last_close else 0.0
    support = 2 * pivot - high if pivot else low
    resistance = 2 * pivot - low if pivot else high

    return [
        SupportResistanceLevel(level=low, label="support", note="20d rolling low"),
        SupportResistanceLevel(level=support, label="support", note="pivot-derived"),
        SupportResistanceLevel(level=pivot, label="pivot", note="pivot point"),
        SupportResistanceLevel(
            level=resistance, label="resistance", note="pivot-derived"
        ),
        SupportResistanceLevel(level=high, label="resistance", note="20d rolling high"),
    ]


def detect_liquidity_anomalies(df: pd.DataFrame) -> List[LiquidityAnomaly]:
    if df.empty or "Volume" not in df:
        return []
    window = min(20, len(df))
    recent = df.tail(window)
    mean_vol = _coerce_float(recent["Volume"].mean())
    std_vol = _coerce_float(recent["Volume"].std())
    current_vol = _coerce_float(df["Volume"].iloc[-1])

    if std_vol == 0:
        return []

    z_score = (current_vol - mean_vol) / std_vol
    anomalies: List[LiquidityAnomaly] = []
    if z_score >= 2:
        severity = "high" if z_score >= 3 else "moderate"
        anomalies.append(
            LiquidityAnomaly(
                label="high_volume_spike",
                severity=severity,
                description=f"Volume {current_vol:.0f} is {z_score:.1f}σ above 20d mean.",
            )
        )
    elif z_score <= -1.5:
        severity = "high" if z_score <= -2.5 else "moderate"
        anomalies.append(
            LiquidityAnomaly(
                label="low_volume_drop",
                severity=severity,
                description=f"Volume {current_vol:.0f} is {abs(z_score):.1f}σ below 20d mean.",
            )
        )
    return anomalies


def generate_risk_notes(
    df: pd.DataFrame,
    indicators: IndicatorsSummary,
    anomalies: List[LiquidityAnomaly],
) -> List[str]:
    if df.empty:
        return ["No historical data available to derive risk notes."]

    notes: List[str] = []
    close = _coerce_float(df["Close"].iloc[-1])
    prev_close = _coerce_float(df["Close"].iloc[-2]) if len(df) > 1 else close
    daily_move = (close - prev_close) / prev_close if prev_close else 0.0
    atr_ratio = indicators.atr / close if close else 0.0

    if abs(daily_move) >= 0.05:
        notes.append(
            f"Gap risk: latest daily move of {daily_move:.1%} exceeds 5% threshold."
        )
    if atr_ratio >= 0.05:
        notes.append(
            f"Volatility spike: ATR/Close at {atr_ratio:.1%} indicates elevated swings."
        )
    if anomalies:
        for anomaly in anomalies:
            if anomaly.label == "low_volume_drop":
                notes.append("Illiquidity risk: recent volume is below normal levels.")

    if not notes:
        notes.append("No major risk flags detected from recent price/volume behavior.")
    return notes


def compute_decision_label(
    indicators: IndicatorsSummary,
    summary: TrendMomentumVolatility,
    df: pd.DataFrame,
) -> DecisionSummary:
    close = _coerce_float(df["Close"].iloc[-1])
    sma_50 = indicators.ma.get("sma_50", 0.0)
    sma_200 = indicators.ma.get("sma_200", 0.0)
    macdh = indicators.macd.get("histogram", 0.0)
    rsi = indicators.rsi

    bullish = 0
    bearish = 0
    if close > sma_50:
        bullish += 1
    else:
        bearish += 1
    if close > sma_200:
        bullish += 1
    else:
        bearish += 1
    if macdh > 0:
        bullish += 1
    elif macdh < 0:
        bearish += 1
    if rsi >= 55:
        bullish += 1
    elif rsi <= 45:
        bearish += 1
    if summary.trend == "uptrend":
        bullish += 1
    elif summary.trend == "downtrend":
        bearish += 1

    score = bullish - bearish
    max_score = 5
    confidence = min(abs(score) / max_score, 1.0)

    if score >= 2:
        label = "BUY"
    elif score <= -2:
        label = "SELL"
    else:
        label = "HOLD"

    rationale = (
        f"Signals: bullish={bullish}, bearish={bearish}. "
        f"Trend is {summary.trend}, momentum {summary.momentum}, RSI {rsi:.1f}."
    )
    return DecisionSummary(label=label, confidence=confidence, rationale=rationale)


def build_cli_report(market_id: str, report_sections: Dict[str, Optional[str]]) -> str:
    report_parts: List[str] = []
    market_key = market_id.upper()

    if market_key == "EGX":
        if any(
            report_sections.get(section)
            for section in (
                "egyptian_market_report",
                "egyptian_news_report",
                "egyptian_fundamentals_report",
            )
        ):
            report_parts.append("## Egyptian Analyst Team Reports")
            if report_sections.get("egyptian_market_report"):
                report_parts.append(
                    f"### Egyptian Market Analysis\n{report_sections['egyptian_market_report']}"
                )
            if report_sections.get("egyptian_news_report"):
                report_parts.append(
                    f"### Egyptian News Analysis\n{report_sections['egyptian_news_report']}"
                )
            if report_sections.get("egyptian_fundamentals_report"):
                report_parts.append(
                    "### Egyptian Fundamentals Analysis\n"
                    f"{report_sections['egyptian_fundamentals_report']}"
                )
    else:
        if any(
            report_sections.get(section)
            for section in (
                "market_report",
                "sentiment_report",
                "news_report",
                "fundamentals_report",
            )
        ):
            report_parts.append("## Analyst Team Reports")
            if report_sections.get("market_report"):
                report_parts.append(
                    f"### Market Analysis\n{report_sections['market_report']}"
                )
            if report_sections.get("sentiment_report"):
                report_parts.append(
                    f"### Social Sentiment\n{report_sections['sentiment_report']}"
                )
            if report_sections.get("news_report"):
                report_parts.append(
                    f"### News Analysis\n{report_sections['news_report']}"
                )
            if report_sections.get("fundamentals_report"):
                report_parts.append(
                    f"### Fundamentals Analysis\n{report_sections['fundamentals_report']}"
                )

    if report_sections.get("investment_plan"):
        report_parts.append("## Research Team Decision")
        report_parts.append(report_sections["investment_plan"])

    if report_sections.get("trader_investment_plan"):
        report_parts.append("## Trading Team Plan")
        report_parts.append(report_sections["trader_investment_plan"])

    if report_sections.get("final_trade_decision"):
        report_parts.append("## Portfolio Management Decision")
        report_parts.append(report_sections["final_trade_decision"])

    return "\n\n".join(report_parts)


def _default_report_sections(market_id: str) -> Dict[str, Optional[str]]:
    if market_id.upper() == "EGX":
        return {
            "egyptian_market_report": None,
            "egyptian_news_report": None,
            "egyptian_fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }
    return {
        "market_report": None,
        "sentiment_report": None,
        "news_report": None,
        "fundamentals_report": None,
        "investment_plan": None,
        "trader_investment_plan": None,
        "final_trade_decision": None,
    }


def _render_analytics_markdown(
    indicators: IndicatorsSummary,
    summary: TrendMomentumVolatility,
    support_resistance: List[SupportResistanceLevel],
    liquidity_anomalies: List[LiquidityAnomaly],
    risk_notes: List[str],
    decision: DecisionSummary,
) -> Dict[str, str]:
    indicator_lines = [
        "## Technical Indicators",
        f"- SMA: {indicators.ma}",
        f"- EMA: {indicators.ema}",
        f"- RSI: {indicators.rsi:.2f}",
        f"- MACD: {indicators.macd}",
        f"- ATR: {indicators.atr:.2f}",
        f"- Bollinger: {indicators.bollinger}",
    ]
    summary_lines = [
        "## Trend/Momentum/Volatility Summary",
        f"- Trend: {summary.trend}",
        f"- Momentum: {summary.momentum}",
        f"- Volatility: {summary.volatility}",
    ]
    if summary.summary:
        summary_lines.append(f"- Notes: {summary.summary}")

    support_lines = ["## Support/Resistance"]
    for level in support_resistance:
        note = f" ({level.note})" if level.note else ""
        support_lines.append(f"- {level.label}: {level.level:.2f}{note}")

    liquidity_lines = ["## Liquidity Anomalies"]
    if not liquidity_anomalies:
        liquidity_lines.append("- None detected")
    else:
        for anomaly in liquidity_anomalies:
            detail = f" - {anomaly.description}" if anomaly.description else ""
            liquidity_lines.append(f"- {anomaly.label} ({anomaly.severity}){detail}")

    risk_lines = ["## Risk Notes"] + [f"- {note}" for note in risk_notes]

    decision_lines = [
        "## Decision",
        f"- Label: {decision.label}",
        f"- Confidence: {decision.confidence:.2f}",
        f"- Rationale: {decision.rationale}",
    ]

    return {
        "technical_indicators": "\n".join(indicator_lines),
        "summary": "\n".join(summary_lines),
        "support_resistance": "\n".join(support_lines),
        "liquidity_anomalies": "\n".join(liquidity_lines),
        "risk_notes": "\n".join(risk_lines),
        "decision": "\n".join(decision_lines),
    }


def build_report_result(
    report_id: str,
    final_report: str,
    indicators: IndicatorsSummary,
    summary: TrendMomentumVolatility,
    support_resistance: List[SupportResistanceLevel],
    liquidity_anomalies: List[LiquidityAnomaly],
    risk_notes: List[str],
    decision: DecisionSummary,
    artifacts: ReportArtifacts,
) -> AnalyticsReportResult:
    return AnalyticsReportResult(
        report_id=report_id,
        final_report=final_report,
        indicators=indicators,
        summary=summary,
        support_resistance=support_resistance,
        liquidity_anomalies=liquidity_anomalies,
        risk_notes=risk_notes,
        decision=decision,
        artifacts=artifacts,
    )


def _write_markdown(report_dir: Path, name: str, content: str) -> Path:
    path = report_dir / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def run_report_job(
    report_id: str, request: AnalyticsReportRequest, idempotency_key: str | None = None
) -> AnalyticsReportResult:
    job = report_storage.load_job(report_id) or {}
    created_at = job.get("created_at") or _now_utc().isoformat()
    status = "running"

    job_record = AnalyticsReportJob(
        report_id=report_id,
        status=status,
        created_at=datetime.fromisoformat(created_at)
        if isinstance(created_at, str)
        else created_at,
        updated_at=_now_utc(),
        idempotency_key=idempotency_key or job.get("idempotency_key"),
    )

    job_payload: Dict[str, Any] = {
        **job_record.model_dump(),
        "market_id": request.market_id,
        "symbol": request.symbol,
        "analysis_date": request.analysis_date,
    }
    report_storage.save_job(job_payload)

    try:
        (
            indicators,
            summary,
            support_resistance,
            liquidity_anomalies,
            risk_notes,
            decision,
            _,
        ) = compute_indicator_summary(
            request.market_id,
            request.symbol,
            request.analysis_date,
            request.lookback_days,
            request.online,
        )

        report_sections = _default_report_sections(request.market_id)
        buffer = ReportBuffer(
            market_id=request.market_id, report_sections=report_sections
        )

        if request.market_id.upper() == "EGX":
            graph = EgyptianTradingAgentsGraph(
                debug=True, config=EGYPTIAN_CONFIG.copy()
            )
        else:
            graph = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

        init_state = graph.propagator.create_initial_state(
            request.symbol, request.analysis_date.isoformat()
        )
        args = graph.propagator.get_graph_args()

        for chunk in graph.graph.stream(init_state, **args):
            for key in list(report_sections.keys()):
                if key in chunk and chunk[key]:
                    buffer.update_section(key, chunk[key])

        analytics_markdown = _render_analytics_markdown(
            indicators,
            summary,
            support_resistance,
            liquidity_anomalies,
            risk_notes,
            decision,
        )

        final_sections = [buffer.final_report] if buffer.final_report else []
        final_sections.extend(analytics_markdown.values())
        final_report = "\n\n".join([section for section in final_sections if section])

        _, report_dir = report_storage.get_report_paths(
            report_id, request.symbol, request.analysis_date
        )
        report_dir.mkdir(parents=True, exist_ok=True)

        section_files: Dict[str, str] = {}

        for name, content in buffer.report_sections.items():
            if not content:
                continue
            report_storage.save_report_section(report_dir, name, content)
            section_files[name] = str(_write_markdown(report_dir, name, content))

        for name, content in analytics_markdown.items():
            report_storage.save_report_section(report_dir, name, content)
            section_files[name] = str(_write_markdown(report_dir, name, content))

        section_files["final_report"] = str(
            _write_markdown(report_dir, "final_report", final_report)
        )

        report_storage.save_report_section(report_dir, "final_report", final_report)

        artifacts = ReportArtifacts(
            report_dir=str(report_dir),
            section_files=section_files,
        )
        result = build_report_result(
            report_id,
            final_report,
            indicators,
            summary,
            support_resistance,
            liquidity_anomalies,
            risk_notes,
            decision,
            artifacts,
        )

        completed_job = AnalyticsReportJob(
            report_id=report_id,
            status="complete",
            created_at=job_record.created_at,
            updated_at=_now_utc(),
            completed_at=_now_utc(),
            idempotency_key=job_record.idempotency_key,
        )
        job_payload = {
            **completed_job.model_dump(),
            "market_id": request.market_id,
            "symbol": request.symbol,
            "analysis_date": request.analysis_date,
            "result": result.model_dump(),
        }
        report_storage.save_job(job_payload)
        return result
    except Exception as exc:
        error_text = "\n".join(traceback.format_exc().splitlines()[-8:])
        failed_job = AnalyticsReportJob(
            report_id=report_id,
            status="failed",
            created_at=job_record.created_at,
            updated_at=_now_utc(),
            completed_at=_now_utc(),
            error=str(exc),
            idempotency_key=job_record.idempotency_key,
        )
        job_payload = {
            **failed_job.model_dump(),
            "market_id": request.market_id,
            "symbol": request.symbol,
            "analysis_date": request.analysis_date,
            "error": error_text,
        }
        report_storage.save_job(job_payload)
        LOGGER.exception("Report job %s failed", report_id)
        raise

"""Analytics report generation helpers and orchestration."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
from stockstats import wrap

from tradingagents.api.schemas.analytics import (
    DecisionSummary,
    IndicatorsSummary,
    LiquidityAnomaly,
    SupportResistanceLevel,
    TrendMomentumVolatility,
)
from tradingagents.api.services import historical as historical_service
from tradingagents.dataflows.interface import get_stock_stats_indicators_window


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

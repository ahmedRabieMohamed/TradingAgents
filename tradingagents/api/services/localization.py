"""Localization helpers for analytics report responses."""

from __future__ import annotations

import re
from enum import Enum
from typing import Iterable, List

from tradingagents.api.schemas.analytics import (
    AnalyticsReportResult,
    DecisionSummary,
    LiquidityAnomaly,
    SupportResistanceLevel,
    TrendMomentumVolatility,
)


class LanguageCode(str, Enum):
    """Supported localization languages."""

    EN = "en"
    AR = "ar"


DECISION_LABELS = {
    "BUY": "شراء",
    "SELL": "بيع",
    "HOLD": "احتفاظ",
}

TREND_VALUES = {
    "uptrend": "اتجاه صاعد",
    "downtrend": "اتجاه هابط",
    "mixed": "اتجاه مختلط",
}

MOMENTUM_VALUES = {
    "overbought": "تشبع شرائي",
    "oversold": "تشبع بيعي",
    "positive": "إيجابي",
    "negative": "سلبي",
    "neutral": "محايد",
}

VOLATILITY_VALUES = {
    "high": "مرتفعة",
    "moderate": "متوسطة",
    "low": "منخفضة",
}

SUPPORT_RESISTANCE_LABELS = {
    "support": "دعم",
    "resistance": "مقاومة",
    "pivot": "محور",
}

SUPPORT_RESISTANCE_NOTES = {
    "20d rolling low": "أدنى مستوى خلال 20 يوماً",
    "20d rolling high": "أعلى مستوى خلال 20 يوماً",
    "pivot-derived": "مستند إلى المحور",
    "pivot point": "نقطة المحور",
}

LIQUIDITY_LABELS = {
    "high_volume_spike": "ارتفاع مفاجئ في الحجم",
    "low_volume_drop": "هبوط في الحجم",
}

LIQUIDITY_SEVERITIES = {
    "high": "مرتفع",
    "moderate": "متوسط",
}

REPORT_HEADINGS = {
    "## Technical Indicators": "## المؤشرات الفنية",
    "## Trend/Momentum/Volatility Summary": "## ملخص الاتجاه/الزخم/التقلب",
    "## Support/Resistance": "## الدعم/المقاومة",
    "## Liquidity Anomalies": "## شذوذ السيولة",
    "## Risk Notes": "## ملاحظات المخاطر",
    "## Decision": "## القرار",
    "## Analyst Team Reports": "## تقارير فريق التحليل",
    "## Egyptian Analyst Team Reports": "## تقارير فريق التحليل المصري",
    "### Market Analysis": "### تحليل السوق",
    "### Social Sentiment": "### معنويات السوق",
    "### News Analysis": "### تحليل الأخبار",
    "### Fundamentals Analysis": "### التحليل الأساسي",
    "### Egyptian Market Analysis": "### تحليل السوق المصري",
    "### Egyptian News Analysis": "### تحليل الأخبار المصرية",
    "### Egyptian Fundamentals Analysis": "### التحليل الأساسي المصري",
    "## Research Team Decision": "## قرار فريق الأبحاث",
    "## Trading Team Plan": "## خطة فريق التداول",
    "## Portfolio Management Decision": "## قرار إدارة المحافظ",
}

BULLET_LABELS = {
    "- SMA:": "- المتوسط البسيط (SMA):",
    "- EMA:": "- المتوسط الأسي (EMA):",
    "- RSI:": "- مؤشر القوة النسبية (RSI):",
    "- MACD:": "- مؤشر MACD:",
    "- ATR:": "- متوسط المدى الحقيقي (ATR):",
    "- Bollinger:": "- نطاقات بولنجر:",
    "- Trend:": "- الاتجاه:",
    "- Momentum:": "- الزخم:",
    "- Volatility:": "- التقلب:",
    "- Notes:": "- ملاحظات:",
    "- Label:": "- التصنيف:",
    "- Confidence:": "- الثقة:",
    "- Rationale:": "- المبرر:",
    "- None detected": "- لا توجد شذوذات",
}


SUMMARY_PATTERN = re.compile(
    r"^Price is (?P<trend>\w+) with (?P<momentum>\w+) momentum and "
    r"(?P<volatility>\w+) volatility\. ATR/Close ratio is (?P<ratio>[\d.]+%)\."
)

DECISION_PATTERN = re.compile(
    r"^Signals: bullish=(?P<bullish>\d+), bearish=(?P<bearish>\d+)\. "
    r"Trend is (?P<trend>\w+), momentum (?P<momentum>\w+), RSI (?P<rsi>[\d.]+)\."
)

RISK_GAP_PATTERN = re.compile(
    r"^Gap risk: latest daily move of (?P<pct>[-\d.]+%) exceeds 5% threshold\."
)
RISK_VOL_PATTERN = re.compile(
    r"^Volatility spike: ATR/Close at (?P<pct>[-\d.]+%) indicates elevated swings\."
)
RISK_ILLIQ_PATTERN = re.compile(
    r"^Illiquidity risk: recent volume is below normal levels\."
)
RISK_NONE_PATTERN = re.compile(
    r"^No major risk flags detected from recent price/volume behavior\."
)
RISK_NO_HISTORY_PATTERN = re.compile(
    r"^No historical data available to derive risk notes\."
)

LIQUIDITY_ABOVE_PATTERN = re.compile(
    r"^Volume (?P<vol>[\d.]+) is (?P<sigma>[\d.]+)σ above 20d mean\."
)
LIQUIDITY_BELOW_PATTERN = re.compile(
    r"^Volume (?P<vol>[\d.]+) is (?P<sigma>[\d.]+)σ below 20d mean\."
)


def _translate_value(value: str | None, mapping: dict[str, str]) -> str | None:
    if value is None:
        return None
    return mapping.get(value, value)


def localize_summary(
    summary: TrendMomentumVolatility, lang: LanguageCode
) -> TrendMomentumVolatility:
    if lang == LanguageCode.EN:
        return summary

    localized_trend = _translate_value(summary.trend, TREND_VALUES) or summary.trend
    localized_momentum = (
        _translate_value(summary.momentum, MOMENTUM_VALUES) or summary.momentum
    )
    localized_volatility = (
        _translate_value(summary.volatility, VOLATILITY_VALUES) or summary.volatility
    )

    localized_summary_text = summary.summary
    if summary.summary:
        match = SUMMARY_PATTERN.match(summary.summary)
        if match:
            ratio = match.group("ratio")
            localized_summary_text = (
                "السعر في "
                f"{localized_trend} مع زخم {localized_momentum} "
                f"وتقلبات {localized_volatility}. "
                f"نسبة ATR/Close هي {ratio}."
            )

    return summary.model_copy(
        update={
            "trend": localized_trend,
            "momentum": localized_momentum,
            "volatility": localized_volatility,
            "summary": localized_summary_text,
        }
    )


def _localize_risk_note(note: str, lang: LanguageCode) -> str:
    if lang == LanguageCode.EN:
        return note

    match = RISK_GAP_PATTERN.match(note)
    if match:
        pct = match.group("pct")
        return f"مخاطر فجوة: الحركة اليومية الأخيرة بنسبة {pct} تتجاوز حد 5%."

    match = RISK_VOL_PATTERN.match(note)
    if match:
        pct = match.group("pct")
        return f"ارتفاع التقلب: ATR/Close عند {pct} يشير إلى تقلبات مرتفعة."

    if RISK_ILLIQ_PATTERN.match(note):
        return "مخاطر ضعف السيولة: حجم التداول الأخير أقل من المستويات الطبيعية."

    if RISK_NONE_PATTERN.match(note):
        return "لا توجد إشارات مخاطر رئيسية من سلوك السعر/الحجم الأخير."

    if RISK_NO_HISTORY_PATTERN.match(note):
        return "لا تتوفر بيانات تاريخية كافية لاستخلاص ملاحظات المخاطر."

    return note


def localize_risk_notes(notes: Iterable[str], lang: LanguageCode) -> List[str]:
    if lang == LanguageCode.EN:
        return list(notes)
    return [_localize_risk_note(note, lang) for note in notes]


def _localize_decision_rationale(rationale: str, lang: LanguageCode) -> str:
    if lang == LanguageCode.EN:
        return rationale

    match = DECISION_PATTERN.match(rationale)
    if not match:
        return rationale

    bullish = match.group("bullish")
    bearish = match.group("bearish")
    trend = _translate_value(match.group("trend"), TREND_VALUES) or match.group("trend")
    momentum = _translate_value(
        match.group("momentum"), MOMENTUM_VALUES
    ) or match.group("momentum")
    rsi = match.group("rsi")
    return (
        f"إشارات: صعودية={bullish}، هبوطية={bearish}. "
        f"الاتجاه {trend}، الزخم {momentum}، RSI {rsi}."
    )


def localize_decision(decision: DecisionSummary, lang: LanguageCode) -> DecisionSummary:
    if lang == LanguageCode.EN:
        return decision

    localized_label = (
        _translate_value(decision.label, DECISION_LABELS) or decision.label
    )
    localized_rationale = _localize_decision_rationale(decision.rationale, lang)
    return decision.model_copy(
        update={"label": localized_label, "rationale": localized_rationale}
    )


def localize_support_resistance(
    levels: Iterable[SupportResistanceLevel], lang: LanguageCode
) -> List[SupportResistanceLevel]:
    if lang == LanguageCode.EN:
        return list(levels)

    localized: List[SupportResistanceLevel] = []
    for level in levels:
        localized_label = (
            _translate_value(level.label, SUPPORT_RESISTANCE_LABELS) or level.label
        )
        localized_note = _translate_value(level.note, SUPPORT_RESISTANCE_NOTES)
        localized.append(
            level.model_copy(update={"label": localized_label, "note": localized_note})
        )
    return localized


def _localize_liquidity_description(description: str, lang: LanguageCode) -> str:
    if lang == LanguageCode.EN:
        return description

    match = LIQUIDITY_ABOVE_PATTERN.match(description)
    if match:
        vol = match.group("vol")
        sigma = match.group("sigma")
        return f"الحجم {vol} أعلى من متوسط 20 يوماً بمقدار {sigma}σ."

    match = LIQUIDITY_BELOW_PATTERN.match(description)
    if match:
        vol = match.group("vol")
        sigma = match.group("sigma")
        return f"الحجم {vol} أقل من متوسط 20 يوماً بمقدار {sigma}σ."

    return description


def localize_liquidity_anomalies(
    anomalies: Iterable[LiquidityAnomaly], lang: LanguageCode
) -> List[LiquidityAnomaly]:
    if lang == LanguageCode.EN:
        return list(anomalies)

    localized: List[LiquidityAnomaly] = []
    for anomaly in anomalies:
        localized_label = (
            _translate_value(anomaly.label, LIQUIDITY_LABELS) or anomaly.label
        )
        localized_severity = (
            _translate_value(anomaly.severity, LIQUIDITY_SEVERITIES) or anomaly.severity
        )
        localized_description = (
            _localize_liquidity_description(anomaly.description, lang)
            if anomaly.description
            else None
        )
        localized.append(
            anomaly.model_copy(
                update={
                    "label": localized_label,
                    "severity": localized_severity,
                    "description": localized_description,
                }
            )
        )
    return localized


def _localize_summary_line(text: str, lang: LanguageCode) -> str:
    if lang == LanguageCode.EN:
        return text

    match = SUMMARY_PATTERN.match(text)
    if not match:
        return text

    trend = _translate_value(match.group("trend"), TREND_VALUES) or match.group("trend")
    momentum = _translate_value(
        match.group("momentum"), MOMENTUM_VALUES
    ) or match.group("momentum")
    volatility = _translate_value(
        match.group("volatility"), VOLATILITY_VALUES
    ) or match.group("volatility")
    ratio = match.group("ratio")
    return (
        f"السعر في {trend} مع زخم {momentum} وتقلبات {volatility}. "
        f"نسبة ATR/Close هي {ratio}."
    )


def localize_final_report(text: str, lang: LanguageCode) -> str:
    if lang == LanguageCode.EN or not text:
        return text

    lines: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in REPORT_HEADINGS:
            lines.append(REPORT_HEADINGS[stripped])
            continue

        for prefix, replacement in BULLET_LABELS.items():
            if stripped.startswith(prefix):
                localized_line = stripped.replace(prefix, replacement, 1)
                line = localized_line
                break

        if line.startswith("- Trend:"):
            value = line.split(":", 1)[1].strip()
            localized_value = _translate_value(value, TREND_VALUES) or value
            line = f"- الاتجاه: {localized_value}"
        elif line.startswith("- Momentum:"):
            value = line.split(":", 1)[1].strip()
            localized_value = _translate_value(value, MOMENTUM_VALUES) or value
            line = f"- الزخم: {localized_value}"
        elif line.startswith("- Volatility:"):
            value = line.split(":", 1)[1].strip()
            localized_value = _translate_value(value, VOLATILITY_VALUES) or value
            line = f"- التقلب: {localized_value}"
        elif line.startswith("- Label:"):
            value = line.split(":", 1)[1].strip()
            localized_value = _translate_value(value, DECISION_LABELS) or value
            line = f"- التصنيف: {localized_value}"
        elif line.startswith("- Notes:"):
            value = line.split(":", 1)[1].strip()
            line = f"- ملاحظات: {_localize_summary_line(value, lang)}"
        elif line.startswith("- Rationale:"):
            value = line.split(":", 1)[1].strip()
            line = f"- المبرر: {_localize_decision_rationale(value, lang)}"

        support_match = re.match(
            r"^- (?P<label>[^:]+): (?P<level>[-\d.]+)(?: \((?P<note>[^)]+)\))?$",
            line,
        )
        if support_match:
            label = support_match.group("label")
            level = support_match.group("level")
            note = support_match.group("note")
            localized_label = (
                _translate_value(label, SUPPORT_RESISTANCE_LABELS) or label
            )
            localized_note = (
                _translate_value(note, SUPPORT_RESISTANCE_NOTES) if note else None
            )
            if localized_note:
                line = f"- {localized_label}: {level} ({localized_note})"
            else:
                line = f"- {localized_label}: {level}"

        liquidity_match = re.match(
            r"^- (?P<label>\w+) \((?P<severity>\w+)\)(?P<detail>.*)$",
            line,
        )
        if liquidity_match:
            label = liquidity_match.group("label")
            severity = liquidity_match.group("severity")
            detail = liquidity_match.group("detail")
            localized_label = _translate_value(label, LIQUIDITY_LABELS) or label
            localized_severity = (
                _translate_value(severity, LIQUIDITY_SEVERITIES) or severity
            )
            localized_detail = detail
            if detail.strip().startswith("-"):
                detail_text = detail.replace("-", "", 1).strip()
                localized_detail_text = _localize_liquidity_description(
                    detail_text, lang
                )
                localized_detail = f" - {localized_detail_text}"
            line = f"- {localized_label} ({localized_severity}){localized_detail}"

        risk_match = re.match(r"^- (?P<note>.+)$", line)
        if risk_match:
            note = risk_match.group("note")
            localized_note = _localize_risk_note(note, lang)
            line = f"- {localized_note}"

        lines.append(line)

    return "\n".join(lines)


def localize_analytics_result(
    result: AnalyticsReportResult, lang: LanguageCode
) -> AnalyticsReportResult:
    if lang == LanguageCode.EN:
        return result

    localized = result.model_copy(deep=True)
    localized.summary = localize_summary(localized.summary, lang)
    localized.risk_notes = localize_risk_notes(localized.risk_notes, lang)
    localized.decision = localize_decision(localized.decision, lang)
    localized.support_resistance = localize_support_resistance(
        localized.support_resistance, lang
    )
    localized.liquidity_anomalies = localize_liquidity_anomalies(
        localized.liquidity_anomalies, lang
    )
    localized.final_report = localize_final_report(localized.final_report, lang)
    return localized

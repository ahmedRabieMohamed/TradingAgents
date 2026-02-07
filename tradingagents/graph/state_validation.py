"""State validation helpers for multi-agent graph runs."""

from typing import Any, Dict, List, Optional


DecisionValue = Optional[str]
ValidationError = Dict[str, Any]


US_REPORT_REQUIREMENTS = {
    "market_report": ["market_report"],
    "sentiment_report": ["sentiment_report"],
    "news_report": ["news_report"],
    "fundamentals_report": ["fundamentals_report"],
}

EGX_REPORT_REQUIREMENTS = {
    "market_report": ["egyptian_market_report", "market_report"],
    "sentiment_report": ["sentiment_report"],
    "news_report": ["egyptian_news_report", "news_report"],
    "fundamentals_report": ["egyptian_fundamentals_report", "fundamentals_report"],
}

BASE_REQUIRED_FIELDS = {
    "company_of_interest",
    "trade_date",
    "investment_plan",
    "trader_investment_plan",
    "final_trade_decision",
    "investment_debate_state",
    "risk_debate_state",
}

INVESTMENT_DEBATE_REQUIRED = {
    "bull_history",
    "bear_history",
    "history",
    "current_response",
    "judge_decision",
}

RISK_DEBATE_REQUIRED = {
    "risky_history",
    "safe_history",
    "neutral_history",
    "history",
    "judge_decision",
}


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def normalize_trade_decision(decision: Any) -> DecisionValue:
    if decision is None:
        return None
    text = str(decision).strip().lower()
    if not text:
        return None

    tokens = set()
    if "buy" in text:
        tokens.add("BUY")
    if "sell" in text:
        tokens.add("SELL")
    if "hold" in text or "neutral" in text:
        tokens.add("HOLD")

    if len(tokens) == 1:
        return tokens.pop()
    return None


def _require_any(
    state: Dict[str, Any],
    logical_name: str,
    candidates: List[str],
    errors: List[ValidationError],
) -> None:
    present_candidates = [key for key in candidates if key in state]
    if not present_candidates:
        errors.append(
            {
                "type": "missing_key",
                "field": logical_name,
                "candidates": candidates,
            }
        )
        return

    non_empty_candidates = [
        key for key in present_candidates if not _is_empty(state.get(key))
    ]
    if not non_empty_candidates:
        errors.append(
            {
                "type": "empty_value",
                "field": logical_name,
                "candidates": present_candidates,
            }
        )


def validate_agent_state(
    final_state: Dict[str, Any], market: str = "us"
) -> List[ValidationError]:
    """Validate final graph state for required fields and decision integrity."""
    errors: List[ValidationError] = []

    if not isinstance(final_state, dict):
        return [
            {
                "type": "empty_value",
                "field": "final_state",
                "value": final_state,
            }
        ]

    for field in sorted(BASE_REQUIRED_FIELDS):
        if field not in final_state:
            errors.append({"type": "missing_key", "field": field})
        elif _is_empty(final_state.get(field)):
            errors.append({"type": "empty_value", "field": field})

    investment_state = final_state.get("investment_debate_state")
    if isinstance(investment_state, dict):
        for key in sorted(INVESTMENT_DEBATE_REQUIRED):
            if key not in investment_state:
                errors.append(
                    {
                        "type": "missing_key",
                        "field": f"investment_debate_state.{key}",
                    }
                )
            elif _is_empty(investment_state.get(key)):
                errors.append(
                    {
                        "type": "empty_value",
                        "field": f"investment_debate_state.{key}",
                    }
                )
    elif "investment_debate_state" in final_state:
        errors.append(
            {
                "type": "empty_value",
                "field": "investment_debate_state",
            }
        )

    risk_state = final_state.get("risk_debate_state")
    if isinstance(risk_state, dict):
        for key in sorted(RISK_DEBATE_REQUIRED):
            if key not in risk_state:
                errors.append(
                    {
                        "type": "missing_key",
                        "field": f"risk_debate_state.{key}",
                    }
                )
            elif _is_empty(risk_state.get(key)):
                errors.append(
                    {
                        "type": "empty_value",
                        "field": f"risk_debate_state.{key}",
                    }
                )
    elif "risk_debate_state" in final_state:
        errors.append(
            {
                "type": "empty_value",
                "field": "risk_debate_state",
            }
        )

    report_requirements = (
        US_REPORT_REQUIREMENTS
        if market.lower() in {"us", "usa", "default"}
        else EGX_REPORT_REQUIREMENTS
    )

    for logical_name, candidates in report_requirements.items():
        _require_any(final_state, logical_name, candidates, errors)

    normalized = normalize_trade_decision(final_state.get("final_trade_decision"))
    if normalized is None:
        errors.append(
            {
                "type": "invalid_decision",
                "field": "final_trade_decision",
                "value": final_state.get("final_trade_decision"),
                "normalized": normalized,
                "expected": ["BUY", "SELL", "HOLD"],
            }
        )

    return errors


def format_validation_errors(errors: List[ValidationError]) -> str:
    if not errors:
        return "State validation passed."

    missing = [err["field"] for err in errors if err.get("type") == "missing_key"]
    empty = [err["field"] for err in errors if err.get("type") == "empty_value"]
    invalid = [err for err in errors if err.get("type") == "invalid_decision"]

    lines = [f"State validation failed ({len(errors)} issues):"]
    if missing:
        lines.append(f"- Missing required keys: {', '.join(sorted(missing))}")
    if empty:
        lines.append(f"- Empty required values: {', '.join(sorted(empty))}")
    for err in invalid:
        lines.append(
            "- Invalid final_trade_decision: "
            f"{err.get('value')!r} (normalized: {err.get('normalized')})"
        )

    return "\n".join(lines)

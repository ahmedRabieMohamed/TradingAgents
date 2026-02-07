"""CLI runner to validate multi-agent core for US and EGX flows."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.egyptian_config import EGYPTIAN_CONFIG
from tradingagents.graph.egyptian_trading_graph import EgyptianTradingAgentsGraph
from tradingagents.graph.state_validation import (
    format_validation_errors,
    validate_agent_state,
)
from tradingagents.graph.trading_graph import TradingAgentsGraph


DEFAULT_US_SYMBOLS = ["NVDA"]
DEFAULT_EGX_SYMBOLS = ["COMI"]
DEFAULT_TRADE_DATES = ["2024-05-10"]


@dataclass
class RunResult:
    market: str
    symbol: str
    trade_date: str
    status: str
    decision: Optional[str] = None
    validation_errors: Optional[List[Dict[str, Any]]] = None
    validation_message: Optional[str] = None
    error: Optional[str] = None


def _apply_overrides(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    config = deepcopy(base)
    for key, value in overrides.items():
        if value is not None:
            config[key] = value
    return config


def _resolve_list(preferred: Optional[List[str]], fallback: List[str]) -> List[str]:
    if preferred:
        return preferred
    return fallback


def _iter_runs(
    symbols: Iterable[str], trade_dates: Iterable[str]
) -> Iterable[tuple[str, str]]:
    for symbol in symbols:
        for trade_date in trade_dates:
            yield symbol, trade_date


def _run_graph(
    graph: Any,
    market: str,
    symbol: str,
    trade_date: str,
) -> RunResult:
    result = RunResult(
        market=market,
        symbol=symbol,
        trade_date=trade_date,
        status="failed",
        validation_errors=[],
    )
    try:
        final_state, decision = graph.propagate(symbol, trade_date)
        result.decision = decision
        validation_errors = validate_agent_state(final_state, market=market)
        if validation_errors:
            result.status = "failed"
            result.validation_errors = validation_errors
            result.validation_message = format_validation_errors(validation_errors)
        else:
            result.status = "passed"
    except Exception as exc:  # noqa: BLE001 - we want all errors reported
        result.status = "failed"
        result.error = f"{type(exc).__name__}: {exc}"
        message = str(exc)
        if "State validation failed" in message:
            result.validation_message = message
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate multi-agent core for US and EGX flows.",
    )
    parser.add_argument(
        "--markets",
        nargs="+",
        choices=["us", "egx"],
        default=["us", "egx"],
        help="Markets to validate (default: us egx)",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Symbols to validate for selected markets.",
    )
    parser.add_argument(
        "--us-symbols",
        nargs="+",
        help="Override US symbols (default: NVDA).",
    )
    parser.add_argument(
        "--egx-symbols",
        nargs="+",
        help="Override EGX symbols (default: COMI).",
    )
    parser.add_argument(
        "--trade-dates",
        nargs="+",
        help="Trade dates (YYYY-MM-DD) to validate for selected markets.",
    )
    parser.add_argument(
        "--us-trade-dates",
        nargs="+",
        help="Override US trade dates (default: 2024-05-10).",
    )
    parser.add_argument(
        "--egx-trade-dates",
        nargs="+",
        help="Override EGX trade dates (default: 2024-05-10).",
    )
    parser.add_argument(
        "--output",
        default="eval_results/validation/summary.json",
        help="Path to write JSON summary (default: eval_results/validation/summary.json)",
    )

    parser.add_argument("--llm-provider", help="Override LLM provider")
    parser.add_argument("--deep-llm", help="Override deep thinking model")
    parser.add_argument("--quick-llm", help="Override quick thinking model")
    parser.add_argument("--backend-url", help="Override LLM backend URL")
    parser.add_argument("--max-debate-rounds", type=int, help="Override debate rounds")
    parser.add_argument(
        "--max-risk-rounds", type=int, help="Override risk debate rounds"
    )
    parser.add_argument("--max-recur-limit", type=int, help="Override recursion limit")

    online_group = parser.add_mutually_exclusive_group()
    online_group.add_argument(
        "--online-tools",
        dest="online_tools",
        action="store_true",
        help="Enable online tools",
    )
    online_group.add_argument(
        "--offline-tools",
        dest="online_tools",
        action="store_false",
        help="Disable online tools",
    )
    parser.set_defaults(online_tools=None)

    validation_group = parser.add_mutually_exclusive_group()
    validation_group.add_argument(
        "--validate-state",
        dest="validate_state",
        action="store_true",
        help="Enable validation before logging",
    )
    validation_group.add_argument(
        "--no-validate-state",
        dest="validate_state",
        action="store_false",
        help="Disable validation before logging",
    )
    parser.set_defaults(validate_state=None)

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    overrides = {
        "llm_provider": args.llm_provider,
        "deep_think_llm": args.deep_llm,
        "quick_think_llm": args.quick_llm,
        "backend_url": args.backend_url,
        "max_debate_rounds": args.max_debate_rounds,
        "max_risk_discuss_rounds": args.max_risk_rounds,
        "max_recur_limit": args.max_recur_limit,
        "online_tools": args.online_tools,
        "validate_state": args.validate_state,
    }

    us_symbols = _resolve_list(args.us_symbols or args.symbols, DEFAULT_US_SYMBOLS)
    egx_symbols = _resolve_list(args.egx_symbols or args.symbols, DEFAULT_EGX_SYMBOLS)
    us_trade_dates = _resolve_list(
        args.us_trade_dates or args.trade_dates, DEFAULT_TRADE_DATES
    )
    egx_trade_dates = _resolve_list(
        args.egx_trade_dates or args.trade_dates, DEFAULT_TRADE_DATES
    )

    runs: List[RunResult] = []
    started_at = datetime.utcnow().isoformat() + "Z"

    if "us" in args.markets:
        us_config = _apply_overrides(DEFAULT_CONFIG, overrides)
        us_graph = TradingAgentsGraph(config=us_config, debug=False)
        for symbol, trade_date in _iter_runs(us_symbols, us_trade_dates):
            runs.append(_run_graph(us_graph, "us", symbol, trade_date))

    if "egx" in args.markets:
        egx_config = _apply_overrides(EGYPTIAN_CONFIG, overrides)
        egx_graph = EgyptianTradingAgentsGraph(config=egx_config, debug=False)
        for symbol, trade_date in _iter_runs(egx_symbols, egx_trade_dates):
            runs.append(_run_graph(egx_graph, "egx", symbol, trade_date))

    passed = sum(1 for run in runs if run.status == "passed")
    failed = sum(1 for run in runs if run.status != "passed")
    completed_at = datetime.utcnow().isoformat() + "Z"

    summary = {
        "started_at": started_at,
        "completed_at": completed_at,
        "total_runs": len(runs),
        "passed": passed,
        "failed": failed,
        "runs": [run.__dict__ for run in runs],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))

    print("Validation summary:")
    for run in runs:
        status_marker = "PASS" if run.status == "passed" else "FAIL"
        decision = run.decision or "-"
        print(
            f"- [{status_marker}] {run.market.upper()} {run.symbol} {run.trade_date}"
            f" (decision: {decision})"
        )
        if run.validation_message:
            print(f"  Validation: {run.validation_message}")
        if run.error:
            print(f"  Error: {run.error}")

    print(
        f"\nTotals: {passed} passed, {failed} failed"
        f" (summary: {output_path.as_posix()})"
    )

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

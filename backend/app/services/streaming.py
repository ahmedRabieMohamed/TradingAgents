"""Adapter that converts LangGraph stream chunks into WebSocket event dicts."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generator


def _ts() -> str:
    """ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


# Maps state keys to (agent_name, phase) pairs for report tracking.
_REPORT_KEYS: dict[str, tuple[str, str]] = {
    "market_report": ("Market Analyst", "research"),
    "sentiment_report": ("Social Media Analyst", "research"),
    "news_report": ("News Analyst", "research"),
    "fundamentals_report": ("Fundamentals Analyst", "research"),
    "trader_investment_plan": ("Trader", "trading"),
    "final_trade_decision": ("Portfolio Manager", "risk_management"),
}


@dataclass
class StreamAdapter:
    """Stateful adapter that tracks LangGraph stream progress and yields WS events.

    Usage::

        adapter = StreamAdapter()
        for chunk in graph.graph.stream(init_state, **args):
            for event in adapter.process_chunk(chunk):
                queue.put_nowait(event)  # send to WebSocket
    """

    # --- internal tracking ---
    _seen_message_ids: set[str] = field(default_factory=set)
    _emitted_reports: set[str] = field(default_factory=set)
    _agent_status: dict[str, str] = field(default_factory=dict)
    _start_time: float = field(default_factory=time.monotonic)
    _agents_completed: int = 0
    _agents_total: int = 10  # rough count of agents in pipeline
    _reports_generated: int = 0

    # Externally injected stats (from StatsCallbackHandler)
    stats_handler: Any = None

    # ---- public API -------------------------------------------------------

    def process_chunk(self, chunk: dict[str, Any]) -> Generator[dict, None, None]:
        """Process a single LangGraph stream chunk and yield WS event dicts."""

        # 1. Messages -------------------------------------------------------
        messages = chunk.get("messages") or []
        if messages:
            last_msg = messages[-1]
            msg_id = getattr(last_msg, "id", None)
            if msg_id and msg_id not in self._seen_message_ids:
                self._seen_message_ids.add(msg_id)
                content = _extract_message_content(last_msg)
                if content and content.strip():
                    agent_name = _infer_agent_from_message(last_msg)
                    yield {
                        "type": "agent_message",
                        "timestamp": _ts(),
                        "agent_name": agent_name,
                        "content": content[:500],  # cap preview length
                        "message_type": _classify_message(last_msg),
                    }

        # 2. Analyst reports -------------------------------------------------
        for key, (agent_name, phase) in _REPORT_KEYS.items():
            value = chunk.get(key)
            if value and isinstance(value, str) and value.strip():
                if key not in self._emitted_reports:
                    self._emitted_reports.add(key)
                    self._mark_agent_completed(agent_name, phase)
                    yield {
                        "type": "agent_started",
                        "timestamp": _ts(),
                        "agent_name": agent_name,
                        "phase": phase,
                        "description": f"{agent_name} report ready",
                    }
                    yield {
                        "type": "agent_completed",
                        "timestamp": _ts(),
                        "agent_name": agent_name,
                        "phase": phase,
                        "report_preview": value[:300],
                        "report_full": value,
                    }

        # 3. Investment debate -----------------------------------------------
        invest_debate = chunk.get("investment_debate_state")
        if invest_debate:
            yield from self._process_investment_debate(invest_debate)

        # 4. Risk debate -----------------------------------------------------
        risk_debate = chunk.get("risk_debate_state")
        if risk_debate:
            yield from self._process_risk_debate(risk_debate)

        # 5. Stats update (emit on every chunk) ------------------------------
        yield self._build_stats_event()

    def build_completed_event(
        self, recommendation: str, confidence: float, summary: str
    ) -> dict:
        """Build the final analysis_completed event."""
        return {
            "type": "analysis_completed",
            "timestamp": _ts(),
            "recommendation": recommendation,
            "confidence": confidence,
            "summary": summary,
        }

    def build_failed_event(
        self, error: str, phase: str = "", agent_name: str = ""
    ) -> dict:
        """Build an analysis_failed event."""
        return {
            "type": "analysis_failed",
            "timestamp": _ts(),
            "error": str(error),
            "phase": phase,
            "agent_name": agent_name,
        }

    # ---- internals --------------------------------------------------------

    def _mark_agent_completed(self, agent_name: str, phase: str) -> None:
        if self._agent_status.get(agent_name) != "completed":
            self._agent_status[agent_name] = "completed"
            self._agents_completed += 1
            self._reports_generated += 1

    def _process_investment_debate(
        self, state: dict
    ) -> Generator[dict, None, None]:
        bull = (state.get("bull_history") or "").strip()
        bear = (state.get("bear_history") or "").strip()
        judge = (state.get("judge_decision") or "").strip()

        if bull and "invest_bull" not in self._emitted_reports:
            self._emitted_reports.add("invest_bull")
            yield {
                "type": "debate_round",
                "timestamp": _ts(),
                "debate_type": "investment",
                "round": 1,
                "total_rounds": 1,
                "role": "bull",
                "agent_name": "Bull Researcher",
                "argument": bull[:500],
                "argument_full": bull,
            }

        if bear and "invest_bear" not in self._emitted_reports:
            self._emitted_reports.add("invest_bear")
            yield {
                "type": "debate_round",
                "timestamp": _ts(),
                "debate_type": "investment",
                "round": 1,
                "total_rounds": 1,
                "role": "bear",
                "agent_name": "Bear Researcher",
                "argument": bear[:500],
                "argument_full": bear,
            }

        if judge and "invest_judge" not in self._emitted_reports:
            self._emitted_reports.add("invest_judge")
            self._mark_agent_completed("Research Manager", "investment_debate")
            yield {
                "type": "debate_round",
                "timestamp": _ts(),
                "debate_type": "investment",
                "round": 1,
                "total_rounds": 1,
                "role": "judge",
                "agent_name": "Research Manager",
                "argument": judge[:500],
                "argument_full": judge,
            }

    def _process_risk_debate(
        self, state: dict
    ) -> Generator[dict, None, None]:
        agg = (state.get("aggressive_history") or "").strip()
        con = (state.get("conservative_history") or "").strip()
        neu = (state.get("neutral_history") or "").strip()
        judge = (state.get("judge_decision") or "").strip()

        if agg and "risk_aggressive" not in self._emitted_reports:
            self._emitted_reports.add("risk_aggressive")
            yield {
                "type": "debate_round",
                "timestamp": _ts(),
                "debate_type": "risk",
                "round": 1,
                "total_rounds": 1,
                "role": "aggressive",
                "agent_name": "Aggressive Analyst",
                "argument": agg[:500],
                "argument_full": agg,
            }

        if con and "risk_conservative" not in self._emitted_reports:
            self._emitted_reports.add("risk_conservative")
            yield {
                "type": "debate_round",
                "timestamp": _ts(),
                "debate_type": "risk",
                "round": 1,
                "total_rounds": 1,
                "role": "conservative",
                "agent_name": "Conservative Analyst",
                "argument": con[:500],
                "argument_full": con,
            }

        if neu and "risk_neutral" not in self._emitted_reports:
            self._emitted_reports.add("risk_neutral")
            yield {
                "type": "debate_round",
                "timestamp": _ts(),
                "debate_type": "risk",
                "round": 1,
                "total_rounds": 1,
                "role": "neutral",
                "agent_name": "Neutral Analyst",
                "argument": neu[:500],
                "argument_full": neu,
            }

        if judge and "risk_judge" not in self._emitted_reports:
            self._emitted_reports.add("risk_judge")
            self._mark_agent_completed("Portfolio Manager", "risk_debate")
            yield {
                "type": "debate_round",
                "timestamp": _ts(),
                "debate_type": "risk",
                "round": 1,
                "total_rounds": 1,
                "role": "judge",
                "agent_name": "Portfolio Manager",
                "argument": judge[:500],
                "argument_full": judge,
            }

    def _build_stats_event(self) -> dict:
        elapsed = time.monotonic() - self._start_time
        stats: dict[str, Any] = {
            "type": "stats_update",
            "timestamp": _ts(),
            "agents_completed": self._agents_completed,
            "agents_total": self._agents_total,
            "reports_generated": self._reports_generated,
            "elapsed_seconds": round(elapsed, 1),
            "llm_calls": 0,
            "tool_calls": 0,
            "tokens_in": 0,
            "tokens_out": 0,
        }
        if self.stats_handler is not None:
            handler_stats = self.stats_handler.get_stats()
            stats["llm_calls"] = handler_stats.get("llm_calls", 0)
            stats["tool_calls"] = handler_stats.get("tool_calls", 0)
            stats["tokens_in"] = handler_stats.get("tokens_in", 0)
            stats["tokens_out"] = handler_stats.get("tokens_out", 0)
        return stats


# ---- helpers --------------------------------------------------------------


def _extract_message_content(msg: Any) -> str:
    """Safely extract text content from a LangChain message."""
    content = getattr(msg, "content", "")
    if isinstance(content, list):
        # Multimodal messages: pick text parts
        parts = [p.get("text", "") for p in content if isinstance(p, dict)]
        return " ".join(parts)
    return str(content)


def _classify_message(msg: Any) -> str:
    """Classify the message type (ai, tool, human, system)."""
    type_name = type(msg).__name__.lower()
    if "tool" in type_name:
        return "tool"
    if "human" in type_name:
        return "human"
    if "system" in type_name:
        return "system"
    return "ai"


def _infer_agent_from_message(msg: Any) -> str:
    """Best-effort agent name inference from message metadata."""
    # LangChain messages sometimes have a `name` attribute
    name = getattr(msg, "name", None)
    if name:
        return name
    return "Agent"

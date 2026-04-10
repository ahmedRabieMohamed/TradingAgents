"""Analysis service: manages running analysis sessions via TradingAgentsGraph."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.database import AgentReport, AnalysisSession
from app.models.schemas import AnalysisRequest
from app.services.streaming import StreamAdapter

logger = logging.getLogger(__name__)


@dataclass
class AnalysisSessionState:
    """In-memory state for a running analysis session."""

    session_id: str
    status: str = "pending"  # pending | running | completed | failed | cancelled
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    task: asyncio.Task | None = None
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    final_state: dict[str, Any] | None = None
    error: str | None = None


class AnalysisManager:
    """Singleton-style manager for running analysis sessions."""

    def __init__(self) -> None:
        self.sessions: dict[str, AnalysisSessionState] = {}

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def create_session(
        self, request: AnalysisRequest, db: AsyncSession
    ) -> str:
        """Persist a new AnalysisSession row and return its id."""
        session = AnalysisSession(
            ticker=request.ticker,
            market_id=request.market_id,
            analysis_date=request.analysis_date,
            status="pending",
            trade_horizon=request.trade_horizon,
            research_depth=request.research_depth,
            analysts=request.analysts,
            llm_provider=request.llm_provider,
            quick_think_model=request.quick_think_model,
            deep_think_model=request.deep_think_model,
            stock_name=request.stock_name,
            stock_price_at_analysis=request.stock_price_at_analysis,
            language=request.language,
        )
        db.add(session)
        await db.flush()  # populate session.id via default
        session_id = session.id

        # In-memory state
        self.sessions[session_id] = AnalysisSessionState(session_id=session_id)
        return session_id

    async def run_analysis(self, session_id: str, request: AnalysisRequest) -> None:
        """Launch the blocking TradingAgentsGraph.propagate in a background thread.

        Events are pushed to the session queue for the WebSocket to consume.
        """
        state = self.sessions.get(session_id)
        if state is None:
            raise ValueError(f"Unknown session {session_id}")

        state.status = "running"
        await self._update_db_status(session_id, "running")

        adapter = StreamAdapter()

        # Build config dict matching DEFAULT_CONFIG structure
        config = self._build_config(request)

        try:
            # Run the blocking propagate in a thread
            final_state, signal = await asyncio.to_thread(
                self._run_propagate_sync,
                config=config,
                request=request,
                adapter=adapter,
                queue=state.queue,
                cancel_event=state.cancel_event,
            )

            if state.cancel_event.is_set():
                state.status = "cancelled"
                await self._update_db_status(session_id, "cancelled")
                state.queue.put_nowait(
                    adapter.build_failed_event("Analysis cancelled by user")
                )
                return

            state.final_state = final_state
            state.status = "completed"

            # Parse recommendation from signal (e.g. "BUY 85%")
            recommendation, confidence = _parse_signal(signal)

            # Emit completed event
            summary = (final_state.get("final_trade_decision") or "")[:500]
            state.queue.put_nowait(
                adapter.build_completed_event(recommendation, confidence, summary)
            )

            # Persist results to DB
            await self._persist_results(
                session_id, final_state, recommendation, confidence
            )

        except Exception as exc:
            logger.exception("Analysis failed for session %s", session_id)
            state.status = "failed"
            state.error = str(exc)
            await self._update_db_status(session_id, "failed")
            state.queue.put_nowait(adapter.build_failed_event(str(exc)))

        finally:
            # Sentinel so WebSocket knows the stream is over
            state.queue.put_nowait(None)

    def get_session_state(self, session_id: str) -> AnalysisSessionState | None:
        return self.sessions.get(session_id)

    async def cancel_session(self, session_id: str) -> bool:
        state = self.sessions.get(session_id)
        if state is None:
            return False
        state.cancel_event.set()
        if state.task and not state.task.done():
            state.task.cancel()
        state.status = "cancelled"
        await self._update_db_status(session_id, "cancelled")
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_config(request: AnalysisRequest) -> dict[str, Any]:
        """Build a config dict compatible with TradingAgentsGraph."""
        from tradingagents.default_config import DEFAULT_CONFIG

        config = dict(DEFAULT_CONFIG)
        config["llm_provider"] = request.llm_provider
        config["deep_think_llm"] = request.deep_think_model
        config["quick_think_llm"] = request.quick_think_model
        config["trade_horizon"] = request.trade_horizon

        # Map market_id to market_region
        config["market_region"] = request.market_id

        # Language for agent output
        config["language"] = request.language

        # Research depth adjustments
        if request.research_depth == "quick":
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
        elif request.research_depth == "deep":
            config["max_debate_rounds"] = 3
            config["max_risk_discuss_rounds"] = 3
        else:  # medium (default)
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1

        return config

    @staticmethod
    def _run_propagate_sync(
        config: dict,
        request: AnalysisRequest,
        adapter: StreamAdapter,
        queue: asyncio.Queue,
        cancel_event: asyncio.Event,
    ) -> tuple[dict, str]:
        """Synchronous wrapper executed in a thread.

        Creates the graph, streams chunks, pushes events to the async queue.
        Returns (final_state, processed_signal).
        """
        # Import here to avoid import-time side effects
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from cli.stats_handler import StatsCallbackHandler

        stats_handler = StatsCallbackHandler()
        adapter.stats_handler = stats_handler

        graph = TradingAgentsGraph(
            selected_analysts=request.analysts,
            debug=True,  # enable streaming
            config=config,
            callbacks=[stats_handler],
        )

        # Prepare initial state and args
        init_state = graph.propagator.create_initial_state(
            request.ticker, str(request.analysis_date)
        )

        # Inject language instruction into initial state so agents respond
        # in the requested language
        language = config.get("language", "en")
        if language != "en":
            lang_names = {"ar": "Arabic", "en": "English"}
            lang_name = lang_names.get(language, language)
            lang_instruction = (
                f"\n\nIMPORTANT: You MUST write ALL your analysis, "
                f"reports, and recommendations in {lang_name}. "
                f"Keep stock ticker symbols, numbers, and financial "
                f"abbreviations in their original Latin/English form."
            )
            # Append language instruction to the human message
            if init_state.get("messages"):
                original_msg = init_state["messages"][0]
                if isinstance(original_msg, tuple):
                    init_state["messages"][0] = (
                        original_msg[0],
                        original_msg[1] + lang_instruction,
                    )

        args = graph.propagator.get_graph_args(callbacks=[stats_handler])

        trace: list[dict] = []

        for chunk in graph.graph.stream(init_state, **args):
            # Check for cancellation
            if cancel_event.is_set():
                break

            # Skip empty message chunks
            if chunk.get("messages") and len(chunk["messages"]) == 0:
                continue

            trace.append(chunk)

            # Convert chunk to WS events via adapter
            for event in adapter.process_chunk(chunk):
                # put_nowait is safe from a sync thread because Queue is thread-safe
                queue.put_nowait(event)

        if cancel_event.is_set():
            return {}, ""

        if not trace:
            raise RuntimeError("Analysis produced no output")

        final_state = trace[-1]

        # Process signal via the graph's signal processor
        decision_text = final_state.get("final_trade_decision", "")
        signal = graph.process_signal(decision_text) if decision_text else ""

        return final_state, signal

    async def _persist_results(
        self,
        session_id: str,
        final_state: dict,
        recommendation: str,
        confidence: float,
    ) -> None:
        """Save recommendation and agent reports to the DB."""
        async with async_session() as db:
            # Update session record
            result = await db.execute(
                select(AnalysisSession).where(AnalysisSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            if session is None:
                logger.error("Session %s not found in DB for persistence", session_id)
                return

            session.status = "completed"
            session.recommendation = recommendation
            session.confidence = confidence
            session.completed_at = datetime.now(timezone.utc)

            # Save individual reports
            report_mappings = [
                ("market_report", "Market Analyst", "research"),
                ("sentiment_report", "Social Media Analyst", "research"),
                ("news_report", "News Analyst", "research"),
                ("fundamentals_report", "Fundamentals Analyst", "research"),
                ("trader_investment_plan", "Trader", "trading"),
                ("final_trade_decision", "Portfolio Manager", "risk_management"),
            ]

            for seq, (key, agent_name, phase) in enumerate(report_mappings):
                content = final_state.get(key, "")
                if content and isinstance(content, str) and content.strip():
                    report = AgentReport(
                        session_id=session_id,
                        agent_name=agent_name,
                        phase=phase,
                        content=content,
                        sequence=seq,
                    )
                    db.add(report)

            # Save debate reports as well
            invest_debate = final_state.get("investment_debate_state")
            if invest_debate:
                for sub_key, agent_name in [
                    ("bull_history", "Bull Researcher"),
                    ("bear_history", "Bear Researcher"),
                    ("judge_decision", "Research Manager"),
                ]:
                    content = invest_debate.get(sub_key, "")
                    if content and isinstance(content, str) and content.strip():
                        seq += 1
                        db.add(
                            AgentReport(
                                session_id=session_id,
                                agent_name=agent_name,
                                phase="investment_debate",
                                content=content,
                                sequence=seq,
                            )
                        )

            risk_debate = final_state.get("risk_debate_state")
            if risk_debate:
                for sub_key, agent_name in [
                    ("aggressive_history", "Aggressive Analyst"),
                    ("conservative_history", "Conservative Analyst"),
                    ("neutral_history", "Neutral Analyst"),
                    ("judge_decision", "Risk Manager"),
                ]:
                    content = risk_debate.get(sub_key, "")
                    if content and isinstance(content, str) and content.strip():
                        seq += 1
                        db.add(
                            AgentReport(
                                session_id=session_id,
                                agent_name=agent_name,
                                phase="risk_debate",
                                content=content,
                                sequence=seq,
                            )
                        )

            # Save full state as JSON to disk
            reports_dir = Path(
                os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results")
            ) / session_id
            reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = reports_dir / "full_state.json"

            # Serialize state (skip non-serializable messages)
            serializable = _make_serializable(final_state)
            report_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

            session.reports_path = str(report_path)
            await db.commit()

    async def _update_db_status(self, session_id: str, status: str) -> None:
        """Update just the status column in the DB."""
        try:
            async with async_session() as db:
                result = await db.execute(
                    select(AnalysisSession).where(AnalysisSession.id == session_id)
                )
                session = result.scalar_one_or_none()
                if session:
                    session.status = status
                    if status in ("completed", "failed", "cancelled"):
                        session.completed_at = datetime.now(timezone.utc)
                    await db.commit()
        except Exception:
            logger.exception("Failed to update DB status for session %s", session_id)


# ---- module-level helpers -------------------------------------------------


def _parse_signal(signal: str) -> tuple[str, float]:
    """Parse 'BUY 85%' style signal into (recommendation, confidence).

    Returns ('HOLD', 50.0) as default if parsing fails.
    """
    if not signal:
        return "HOLD", 50.0

    signal = signal.strip().upper()
    match = re.search(r"(BUY|SELL|HOLD)\s*(\d+(?:\.\d+)?)\s*%?", signal)
    if match:
        return match.group(1), float(match.group(2))

    # Try to find just the action
    for action in ("BUY", "SELL", "HOLD"):
        if action in signal:
            return action, 50.0

    return "HOLD", 50.0


def _make_serializable(obj: Any) -> Any:
    """Recursively convert an object to JSON-serializable form."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    # For LangChain messages or other complex objects, stringify
    return str(obj)


# Singleton instance
analysis_manager = AnalysisManager()

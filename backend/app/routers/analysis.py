"""Analysis router: create, stream, query, and cancel analysis sessions."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.database import AnalysisSession
from app.models.schemas import (
    AnalysisCreateResponse,
    AnalysisListItem,
    AnalysisListResponse,
    AnalysisRequest,
    AnalysisSessionResponse,
    SimulationResultSchema,
)
from app.services.analysis import analysis_manager
from app.services.simulation import simulate_analysis as run_simulation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


# ---------------------------------------------------------------------------
# POST /analysis  --  create & start
# ---------------------------------------------------------------------------


@router.post("", response_model=AnalysisCreateResponse)
async def create_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Create a new analysis session and start processing in the background."""
    session_id = await analysis_manager.create_session(request, db)
    await db.commit()

    # Launch analysis as a background task
    background_tasks.add_task(analysis_manager.run_analysis, session_id, request)

    return AnalysisCreateResponse(
        session_id=session_id,
        status="running",
        websocket_url=f"/api/analysis/ws/{session_id}",
    )


# ---------------------------------------------------------------------------
# WS /ws/analysis/{session_id}  --  live streaming
# ---------------------------------------------------------------------------


@router.websocket("/ws/{session_id}")
async def analysis_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint that streams analysis events in real time.

    Events are JSON objects with a ``type`` field. The stream ends with a
    ``None`` sentinel (the connection is closed cleanly after that).

    The client can send a JSON message ``{"action": "cancel"}`` to request
    cancellation of the running analysis.
    """
    state = analysis_manager.get_session_state(session_id)
    if state is None:
        await websocket.close(code=4004, reason="Session not found")
        return

    await websocket.accept()

    # Task that listens for client messages (e.g. cancel)
    async def _listen_for_client():
        try:
            while True:
                raw = await websocket.receive_text()
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if msg.get("action") == "cancel":
                    await analysis_manager.cancel_session(session_id)
        except (WebSocketDisconnect, Exception):
            pass  # client disconnected — fine

    listener_task = asyncio.create_task(_listen_for_client())

    try:
        while True:
            try:
                event = await asyncio.wait_for(state.queue.get(), timeout=120)
            except asyncio.TimeoutError:
                # Send a keep-alive ping
                await websocket.send_json({"type": "ping", "timestamp": ""})
                continue

            if event is None:
                # Stream finished
                break

            await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected for session %s", session_id)
    except Exception:
        logger.exception("WebSocket error for session %s", session_id)
    finally:
        listener_task.cancel()
        try:
            await websocket.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# GET /analysis/{session_id}  --  full session detail
# ---------------------------------------------------------------------------


@router.get("/{session_id}", response_model=AnalysisSessionResponse)
async def get_analysis(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return the full analysis session with agent reports and simulation result."""
    result = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.id == session_id)
        .options(
            selectinload(AnalysisSession.agent_reports),
            selectinload(AnalysisSession.simulation_result),
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Analysis session not found")

    return AnalysisSessionResponse.model_validate(session)


# ---------------------------------------------------------------------------
# GET /analysis  --  list sessions
# ---------------------------------------------------------------------------


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    status: Optional[str] = Query(None),
    ticker: Optional[str] = Query(None),
    market_id: Optional[str] = Query(None),
    recommendation: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List analysis sessions with optional filters."""
    query = select(AnalysisSession).order_by(AnalysisSession.created_at.desc())

    if status:
        query = query.where(AnalysisSession.status == status)
    if ticker:
        query = query.where(AnalysisSession.ticker == ticker)
    if market_id:
        query = query.where(AnalysisSession.market_id == market_id)
    if recommendation:
        query = query.where(
            func.upper(AnalysisSession.recommendation) == recommendation.upper()
        )
    if from_date:
        query = query.where(AnalysisSession.analysis_date >= from_date)
    if to_date:
        query = query.where(AnalysisSession.analysis_date <= to_date)

    # Total count (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate — eagerly load simulation for list display
    query = query.options(
        selectinload(AnalysisSession.simulation_result)
    ).offset(offset).limit(limit)
    result = await db.execute(query)
    sessions = result.scalars().all()

    items = []
    for s in sessions:
        item = AnalysisListItem.model_validate(s)
        if s.simulation_result:
            item.simulation = {
                "entry_price": s.simulation_result.entry_price,
                "exit_price": s.simulation_result.exit_price,
                "return_pct": s.simulation_result.return_pct,
                "is_win": s.simulation_result.is_win,
            }
        items.append(item)

    return AnalysisListResponse(
        analyses=items,
        total=total,
    )


# ---------------------------------------------------------------------------
# GET /analysis/{session_id}/export  --  Markdown report export
# ---------------------------------------------------------------------------


@router.get("/{session_id}/export", response_class=PlainTextResponse)
async def export_analysis(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Combine all agent reports into a single Markdown document."""
    result = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.id == session_id)
        .options(selectinload(AnalysisSession.agent_reports))
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Analysis session not found")

    date_str = session.analysis_date.isoformat() if session.analysis_date else "N/A"
    parts: list[str] = [f"# Analysis Report: {session.ticker} - {date_str}\n"]

    for report in sorted(session.agent_reports, key=lambda r: r.sequence):
        parts.append(f"## {report.agent_name}\n\n{report.content}\n\n---\n")

    markdown = "\n".join(parts)
    return PlainTextResponse(content=markdown, media_type="text/markdown")


# ---------------------------------------------------------------------------
# POST /analysis/{session_id}/simulate  --  trigger simulation
# ---------------------------------------------------------------------------


@router.post("/{session_id}/simulate", response_model=SimulationResultSchema)
async def simulate_analysis(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run a simulation for a completed analysis session.

    Returns 400 if the trade horizon has not elapsed yet or the session
    is not in a valid state for simulation.
    """
    try:
        sim = await run_simulation(session_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return SimulationResultSchema.model_validate(sim)


# ---------------------------------------------------------------------------
# DELETE /analysis/{session_id}  --  cancel or delete
# ---------------------------------------------------------------------------


@router.delete("/{session_id}")
async def delete_analysis(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running session or delete a completed one."""
    # Try to cancel if still running
    in_memory = analysis_manager.get_session_state(session_id)
    if in_memory and in_memory.status == "running":
        await analysis_manager.cancel_session(session_id)
        return {"detail": "Analysis cancelled", "session_id": session_id}

    # Otherwise delete from DB
    result = await db.execute(
        select(AnalysisSession).where(AnalysisSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Analysis session not found")

    await db.delete(session)
    await db.commit()
    return {"detail": "Analysis deleted", "session_id": session_id}

"""Async analytics report endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request, status

from tradingagents.api.deps import rate_limit
from tradingagents.api.deps.auth import optional_current_account
from tradingagents.api.deps.errors import ApiError
from tradingagents.api.schemas.analytics import (
    AnalyticsReportJob,
    AnalyticsReportRequest,
    AnalyticsReportResult,
)
from tradingagents.api.services import analytics_reports
from tradingagents.api.services import report_storage
from tradingagents.api.settings import settings


router = APIRouter(prefix="/analytics", tags=["analytics"])


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _iter_report_roots() -> list[Path]:
    roots = [Path(settings.analytics_reports_dir)]
    if settings.analytics_reports_egx_dir:
        roots.append(Path(settings.analytics_reports_egx_dir))
    else:
        roots.append(Path("./egyptian_results"))
    return roots


def _load_job_payload(job_path: Path) -> Dict[str, Any] | None:
    try:
        payload = json.loads(job_path.read_text())
    except json.JSONDecodeError:
        return None
    return payload.get("data") or payload


def _find_job_by_idempotency_key(idempotency_key: str) -> Dict[str, Any] | None:
    for root in _iter_report_roots():
        if not root.exists():
            continue
        for job_path in root.rglob("job.json"):
            data = _load_job_payload(job_path)
            if not data:
                continue
            if data.get("idempotency_key") == idempotency_key:
                return data
    return None


def _build_response(job_data: Dict[str, Any]) -> Dict[str, Any]:
    job = AnalyticsReportJob.model_validate(job_data)
    result_payload = job_data.get("result")
    if result_payload:
        result = AnalyticsReportResult.model_validate(result_payload)
        return {"job": job, "result": result}
    return {"job": job}


@router.post("/report")
async def create_report(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: AnalyticsReportRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> Dict[str, Any]:
    is_authenticated = bool(getattr(request.state, "account_id", None))
    await rate_limit.enforce_rate_limits(request, is_authenticated=is_authenticated)

    request_payload = payload.model_dump()
    report_id = report_storage.build_report_id(request_payload, idempotency_key)

    existing_job = report_storage.load_job(report_id)
    if existing_job:
        return _build_response(existing_job)

    if idempotency_key:
        existing_by_key = _find_job_by_idempotency_key(idempotency_key)
        if existing_by_key:
            existing_report_id = existing_by_key.get("report_id")
            if existing_report_id != report_id:
                raise ApiError(
                    status_code=status.HTTP_409_CONFLICT,
                    code="IDEMPOTENCY_CONFLICT",
                    message="Idempotency key already used with different request",
                )
            return _build_response(existing_by_key)

    now = _now_utc()
    job_record = AnalyticsReportJob(
        report_id=report_id,
        status="queued",
        created_at=now,
        updated_at=now,
        idempotency_key=idempotency_key,
    )
    job_payload: Dict[str, Any] = {
        **job_record.model_dump(),
        **request_payload,
        "request": request_payload,
    }
    report_storage.save_job(job_payload)

    background_tasks.add_task(
        analytics_reports.run_report_job,
        report_id,
        payload,
        idempotency_key,
    )

    return _build_response(job_payload)


@router.get("/report/{report_id}")
async def get_report(
    report_id: str,
    request: Request,
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> Dict[str, Any]:
    is_authenticated = bool(getattr(request.state, "account_id", None))
    await rate_limit.enforce_rate_limits(request, is_authenticated=is_authenticated)

    job = report_storage.load_job(report_id)
    if not job:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="REPORT_NOT_FOUND",
            message="Report not found",
        )
    return _build_response(job)

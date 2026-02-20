"""Filesystem-backed analytics report storage helpers."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Tuple

from tradingagents.api.settings import settings


def resolve_reports_root(market_id: str) -> Path:
    """Resolve base reports directory for a market."""

    if market_id.upper() == "EGX":
        root = settings.analytics_reports_egx_dir or "./egyptian_results"
        return Path(root)
    return Path(settings.analytics_reports_dir)


def _stable_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def build_report_id(payload: Dict[str, Any], idempotency_key: str | None) -> str:
    """Build a deterministic report_id from payload and idempotency key."""

    payload_fingerprint = sha256(_stable_json(payload).encode("utf-8")).hexdigest()
    if idempotency_key:
        digest = sha256(f"{idempotency_key}:{payload_fingerprint}".encode("utf-8"))
        return digest.hexdigest()
    return payload_fingerprint


def get_report_paths(
    report_id: str, symbol: str, analysis_date: date
) -> Tuple[Path, Path]:
    """Return job.json and report directory paths."""

    date_str = analysis_date.isoformat()
    report_dir = (
        Path(settings.analytics_reports_dir) / symbol / date_str / "reports" / report_id
    )
    job_path = report_dir / "job.json"
    return job_path, report_dir


def _write_json_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, default=str))
    tmp_path.replace(path)


def save_job(job_dict: Dict[str, Any]) -> Path:
    """Persist job metadata with atomic write semantics."""

    symbol = job_dict.get("symbol")
    analysis_date = job_dict.get("analysis_date")
    if not symbol or not analysis_date:
        raise ValueError("job_dict must include symbol and analysis_date")

    if isinstance(analysis_date, str):
        analysis_date = date.fromisoformat(analysis_date)

    report_id = job_dict.get("report_id")
    if not report_id:
        raise ValueError("job_dict must include report_id")

    job_path, report_dir = get_report_paths(report_id, symbol, analysis_date)
    payload = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "report_dir": str(report_dir),
        "data": job_dict,
    }
    _write_json_atomic(job_path, payload)
    return job_path


def load_job(report_id: str) -> Dict[str, Any] | None:
    """Load job metadata by report_id."""

    roots = [Path(settings.analytics_reports_dir)]
    if settings.analytics_reports_egx_dir:
        roots.append(Path(settings.analytics_reports_egx_dir))
    else:
        roots.append(Path("./egyptian_results"))

    for root in roots:
        if not root.exists():
            continue
        for job_path in root.rglob(f"{report_id}/job.json"):
            try:
                payload = json.loads(job_path.read_text())
            except json.JSONDecodeError:
                continue
            return payload.get("data") or payload
    return None


def save_report_section(report_dir: Path, name: str, content: Any) -> Path:
    """Persist a report section payload under report_dir."""

    section_path = report_dir / f"{name}.json"
    payload = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "data": content,
    }
    _write_json_atomic(section_path, payload)
    return section_path


def load_report_section(report_dir: Path, name: str) -> Any | None:
    """Load a report section payload from report_dir."""

    section_path = report_dir / f"{name}.json"
    if not section_path.exists():
        return None
    try:
        payload = json.loads(section_path.read_text())
    except json.JSONDecodeError:
        return None
    return payload.get("data")

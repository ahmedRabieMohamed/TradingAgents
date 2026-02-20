# Phase 05: Async Analytics Reports - Research

**Researched:** 2026-02-20
**Domain:** FastAPI async background reporting + technical indicators
**Confidence:** MEDIUM

## Summary

This phase needs an async reporting workflow that kicks off TradingAgents analytics, writes CLI-style report artifacts to the filesystem, and returns a normalized API response that embeds the CLI report. The locked POC decisions (FastAPI `BackgroundTasks`, no external queue, filesystem storage, idempotent report IDs) align with FastAPI’s documented background-task model and the repo’s existing report generation/indicator utilities.

The codebase already provides key building blocks: FastAPI endpoints/services patterns, a `TradingAgentsGraph`/`MessageBuffer` report assembler, and indicator computations via `stockstats` with a project-specific wrapper (`get_stock_stats_indicators_window`). The standard implementation should reuse those utilities, produce a deterministic report ID from the request payload, and write both per-section markdown files and a final report string to disk.

**Primary recommendation:** Use FastAPI `BackgroundTasks` to kick off a Python-only report run that reuses `TradingAgentsGraph` + `MessageBuffer` and writes results under the CLI-style `results/{ticker}/{date}/reports` layout, returning a job record with idempotent `report_id` and embedded `final_report` when complete.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI (`BackgroundTasks`) | project dependency | Run async job after HTTP response | Official FastAPI pattern for small background work (no queue). |
| Pydantic v2 models | project dependency | Request/response schemas | Existing API uses Pydantic models in `schemas/`. |
| stockstats | project dependency | Technical indicators (MA/EMA/RSI/MACD/ATR/Boll) | Official library used in repo utilities; supports required indicators. |
| pandas | project dependency | DataFrames for indicator computation | stockstats wraps pandas DataFrame. |
| TradingAgentsGraph + MessageBuffer | project code | Produce CLI-style report + final decision | Existing CLI uses this to build the final report. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib | stdlib | File-based report storage | Use for results directory layout and atomic writes. |
| fastapi-limiter | project dependency | Optional rate limit | Align with other routers if needed. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FastAPI `BackgroundTasks` | Celery/RQ | More robust async, but violates locked POC decision (no queue). |

**Installation:**
```bash
pip install fastapi uvicorn stockstats pandas
```

## Architecture Patterns

### Recommended Project Structure
```
tradingagents/api/
├── routers/
│   └── analytics.py          # /analytics/report endpoints
├── schemas/
│   └── analytics.py          # request/response models
├── services/
│   ├── analytics_reports.py  # run + orchestration logic
│   └── report_storage.py     # filesystem persistence + idempotency
└── settings.py               # report storage configuration
```

### Pattern 1: BackgroundTasks job kickoff + file-backed job record
**What:** Accept request, generate deterministic `report_id`, return immediately while `BackgroundTasks` executes report generation and persists results to disk.
**When to use:** All async report submissions (POC uses in-process background task).
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi import BackgroundTasks, APIRouter

router = APIRouter()

def run_report(report_id: str, payload: dict) -> None:
    # generate report and write to filesystem
    ...

@router.post("/analytics/report")
async def create_report(payload: dict, background_tasks: BackgroundTasks):
    report_id = "deterministic-id"
    background_tasks.add_task(run_report, report_id, payload)
    return {"report_id": report_id, "status": "queued"}
```

### Pattern 2: CLI-style report assembly from TradingAgentsGraph
**What:** Use existing `TradingAgentsGraph` streaming + `MessageBuffer` to build the same report sections and final report text the CLI writes to files.
**When to use:** Required for “normalized API response embedding CLI report.”
**Example:**
```python
# Source: tradingagents/cli/main.py (MessageBuffer + run_analysis flow)
message_buffer = MessageBuffer(market_type=MarketType.US)
init_state = graph.propagator.create_initial_state(ticker, trade_date)
for chunk in graph.graph.stream(init_state, **graph.propagator.get_graph_args()):
    if "market_report" in chunk:
        message_buffer.update_report_section("market_report", chunk["market_report"])
    # ... other report sections ...
final_report = message_buffer.final_report
```

### Anti-Patterns to Avoid
- **Running heavy report generation inside the request handler:** background tasks must run after response; long-running tasks can block the worker.
- **Custom indicator implementations:** use `stockstats` (already integrated) instead of hand-coded MACD/RSI/etc.
- **Ad-hoc report serialization:** use Pydantic response models and consistent file layout.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Technical indicators | Custom MA/EMA/RSI/MACD/ATR/Boll code | `stockstats` | Correct formulas + many indicators are already implemented. |
| Async job execution | Threads/asyncio spawning in handlers | FastAPI `BackgroundTasks` | Standard FastAPI approach for post-response work. |
| File cache metadata | Custom “age/ttl” logic | Existing cache helpers pattern (`eodhd_cache.py`) | Consistent JSON payload + `fetched_at` fields. |

**Key insight:** This repo already has CLI report structure + indicator utilities—reuse them to avoid mismatches between CLI and API outputs.

## Common Pitfalls

### Pitfall 1: BackgroundTasks used for heavy work
**What goes wrong:** CPU-bound report generation blocks the worker, slowing other requests.
**Why it happens:** FastAPI background tasks run in the same process after response.
**How to avoid:** Keep the POC approach but control concurrency; return 202 quickly; consider queue later.
**Warning signs:** Increased request latency or timeouts during report execution.

### Pitfall 2: Missing required columns for stockstats
**What goes wrong:** Indicators return incorrect values or raise errors.
**Why it happens:** `stockstats` expects `close`, `high`, `low`, `volume`, and optional `date` columns.
**How to avoid:** Normalize DataFrame columns before wrapping with `stockstats.wrap()`.
**Warning signs:** NaN-heavy indicator outputs or KeyError on indicator access.

### Pitfall 3: Non-idempotent job creation
**What goes wrong:** Duplicate reports for the same request and inconsistent `report_id`s.
**Why it happens:** Report ID derived from non-deterministic inputs.
**How to avoid:** Hash a stable subset of request parameters (market/symbol/date/range/options). If the report file exists, return that `report_id`.
**Warning signs:** Multiple report directories for identical requests.

### Pitfall 4: Partial file writes on failures
**What goes wrong:** Polling reads incomplete reports or corrupt JSON.
**Why it happens:** Task crashes mid-write.
**How to avoid:** Write to a temp file then atomically rename; maintain status metadata.
**Warning signs:** `JSONDecodeError` or missing `final_report` content.

## Code Examples

### FastAPI BackgroundTasks kickoff
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_notification(email: str, message: str) -> None:
    with open("log.txt", "w") as handle:
        handle.write(f"notification for {email}: {message}")

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
```

### stockstats indicator access (MACD, Bollinger, RSI)
```python
# Source: https://github.com/jealous/stockstats (README)
import pandas as pd
from stockstats import wrap

df = wrap(pd.read_csv("stock.csv"))
rsi = df["rsi"]
df.get("macd")
macd_lines = df[["macd", "macds", "macdh"]]
df.get("boll")
boll_lines = df[["boll", "boll_ub", "boll_lb"]]
```

### Project indicator report utility
```python
# Source: tradingagents/dataflows/interface.py
result = get_stock_stats_indicators_window(
    symbol="AAPL",
    indicator="macd",
    curr_date="2025-01-15",
    look_back_days=30,
    online=True,
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Synchronous report generation in request | FastAPI `BackgroundTasks` for post-response execution | Current FastAPI guidance | Enables immediate 202/queued response and async polling. |
| Hand-coded indicators | `stockstats` DataFrame wrapper | Current project dependency | Reduces formula errors and aligns with existing tooling. |

**Deprecated/outdated:**
- **Custom indicator formulas**: use `stockstats` indicators (already integrated).

## Open Questions

1. **What exact fields define idempotency?**
   - What we know: Must return existing `report_id` if same request.
   - What's unclear: Which parameters are included in the hash (market, symbol, date range, indicators, online/offline, LLM config).
   - Recommendation: Document and freeze an idempotency key schema in the API spec.

2. **What is the normalized API response shape?**
   - What we know: Must embed CLI report; existing API uses Pydantic models per endpoint.
   - What's unclear: Whether to include per-section report files, raw state JSON, or just final report.
   - Recommendation: Define a response model with `status`, `report_id`, `final_report`, and `artifacts` metadata.

3. **Where should report artifacts live in API settings?**
   - What we know: CLI uses `results/{ticker}/{date}/reports` from `DEFAULT_CONFIG`.
   - What's unclear: Whether API should reuse `results_dir` or use a dedicated setting.
   - Recommendation: Add `analytics_reports_dir` in API settings, defaulting to `DEFAULT_CONFIG["results_dir"]` layout.

## Sources

### Primary (HIGH confidence)
- https://fastapi.tiangolo.com/tutorial/background-tasks/ - BackgroundTasks usage, caveats, and `add_task` API
- https://github.com/jealous/stockstats - Stockstats indicator support and access patterns

### Secondary (MEDIUM confidence)
- Repository code: `tradingagents/cli/main.py`, `tradingagents/graph/trading_graph.py`, `tradingagents/dataflows/interface.py` (CLI report assembly + indicator utility)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - FastAPI docs + stockstats README + existing dependencies
- Architecture: MEDIUM - Based on existing repo patterns and CLI flow
- Pitfalls: MEDIUM - Derived from FastAPI caveat + project code behavior

**Research date:** 2026-02-20
**Valid until:** 2026-03-22

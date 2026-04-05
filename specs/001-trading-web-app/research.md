# Research: Trading Web Application

**Feature**: 001-trading-web-app  
**Date**: 2026-04-04

## Decision 1: Web Framework (Backend)

**Decision**: FastAPI with async support

**Rationale**:
- Python 3.10+ project — FastAPI is the natural fit for async web services in the Python ecosystem
- LangGraph's `.stream()` yields intermediate state chunks that map directly to async generators
- FastAPI has native WebSocket support for real-time streaming, which is needed for live analysis updates
- The existing `TradingAgentsGraph` class and all dependencies are Python — keeping the backend in Python avoids language bridging
- FastAPI's dependency injection pairs well with the existing config pattern (`DEFAULT_CONFIG` dict)

**Alternatives Considered**:
- **Flask**: Lacks native async support; would require Celery + polling for real-time updates. More setup for less capability.
- **Django**: Too heavy for a single-purpose API layer wrapping an existing backend. ORM overhead unnecessary since persistence is file-based.
- **Direct Streamlit/Gradio**: Quick to prototype but limited UI customization and poor production scalability. Can't match the interactive design from the prototype.

## Decision 2: Real-Time Communication

**Decision**: WebSocket for analysis streaming, REST for CRUD operations

**Rationale**:
- The CLI currently iterates over `graph.stream()` in a for-loop, updating the TUI after each chunk. WebSocket replicates this pattern exactly for the browser.
- Each LangGraph stream chunk contains partial state (`messages`, `market_report`, `agent_status`, etc.) that can be serialized to JSON and pushed to the client.
- WebSocket is bidirectional — supports future features like mid-analysis cancellation.
- REST endpoints handle non-streaming operations: ticker validation, history queries, settings management.

**Alternatives Considered**:
- **Server-Sent Events (SSE)**: Simpler but one-directional. Cannot support cancellation without a separate endpoint. Adequate but less flexible.
- **Polling**: Simplest but introduces latency (at least 1-2s delay). Contradicts SC-003 (updates every 10 seconds) and wastes resources.

## Decision 3: Frontend Framework

**Decision**: React with TypeScript

**Rationale**:
- Mature WebSocket ecosystem and state management libraries (React Query, Zustand) fit the real-time update pattern.
- Component-based architecture maps well to the modular UI: market cards, config panels, pipeline stages, report sections.
- Large ecosystem for charting/data visualization needed for performance dashboard and simulation views.
- TypeScript provides type safety for the complex data structures (analysis sessions, agent reports, debate states).

**Alternatives Considered**:
- **Vue.js**: Viable but smaller ecosystem for financial/data visualization components.
- **Svelte**: Lighter but less mature WebSocket tooling and fewer pre-built charting libraries.
- **Plain HTML/JS (like prototype)**: Not maintainable for a production app with 5+ interactive screens and real-time state management.

## Decision 4: Persistence Strategy

**Decision**: SQLite for analysis history + existing file-based reports

**Rationale**:
- The spec requires analysis history, filtering, and comparison (FR-011, FR-012) — flat files are insufficient for querying.
- SQLite is zero-config, single-file, and already ships with Python. No external database server needed for a single-user app.
- Analysis sessions and metadata stored in SQLite for fast querying.
- Full report content continues to be stored as Markdown files (existing format) — SQLite stores paths and metadata only.
- Simulation results and performance stats computed from SQLite + market data.

**Alternatives Considered**:
- **PostgreSQL**: Overkill for single-user local deployment. Requires external service.
- **Redis**: Already in dependencies but better suited for caching than persistent storage. Could complement SQLite for session state during analysis.
- **Pure file-based (JSON)**: Current approach. Works for storage but poor for filtering, aggregation, and the history/performance queries in the spec.

## Decision 5: Project Structure

**Decision**: Monorepo with backend/ and frontend/ directories alongside existing code

**Rationale**:
- The web app is a new layer on top of the existing `tradingagents` package. Keeping it in the same repo ensures the backend can directly import `TradingAgentsGraph` and all existing agents/tools.
- Separate `backend/` and `frontend/` directories maintain clear separation of concerns.
- The existing `cli/`, `tradingagents/`, and `main.py` remain untouched.
- Shared Python config (`default_config.py`) used by both CLI and web backend.

**Alternatives Considered**:
- **Separate repos**: Would require packaging `tradingagents` as a pip-installable library. Adds complexity without clear benefit for a single-user tool.
- **Single src/ directory**: Would mix frontend JS/TS with Python backend, creating confusion.

## Decision 6: Testing Strategy

**Decision**: pytest (backend) + Vitest (frontend) + Playwright (E2E)

**Rationale**:
- The project currently has minimal testing. This is the opportunity to establish a testing foundation.
- pytest is the Python standard and integrates with FastAPI's `TestClient` for API testing.
- Vitest is the fastest modern JS test runner, compatible with React/TypeScript.
- Playwright handles E2E flows (market selection → analysis → results) across the full stack.

**Alternatives Considered**:
- **unittest**: More verbose than pytest with less ecosystem support.
- **Jest**: Slower than Vitest for modern React/TypeScript projects.

## Decision 7: Analysis Session Management

**Decision**: Background task with in-memory state, persisted on completion

**Rationale**:
- FastAPI's `BackgroundTasks` or a simple asyncio task can run the analysis pipeline.
- During execution, state lives in memory (just like the CLI's `MessageBuffer` pattern).
- WebSocket connection streams state to the frontend in real-time.
- On completion, the full analysis is persisted to SQLite + Markdown files.
- If the WebSocket disconnects, the analysis continues running; the user can reconnect and see results.

**Alternatives Considered**:
- **Celery + Redis**: Industrial-strength but overkill for a single-user app. Adds deployment complexity.
- **Thread pool**: The LangGraph execution already uses threads internally for tool calls. Adding another thread layer adds risk of contention.

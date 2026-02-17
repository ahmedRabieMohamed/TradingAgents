# Multi-Market Stock Analytics Platform

## What This Is

An API-first, multi-market stock analytics backend that powers a mobile app. Users choose US or EGX, pick a stock, get a sub-1s live snapshot, then receive a deeper multi-agent analytics report (async by default) with bilingual narratives.

## Core Value

Deliver fast, reliable, explainable stock analytics for US and EGX without regressions.

## Requirements

### Validated

- ✓ CLI-based US stock analysis workflow using multi-agent orchestration — existing
- ✓ Market data ingestion and indicator tooling via dataflow utilities — existing
- ✓ Report/state logging to local results directories — existing

### Active

- [ ] Market-agnostic core with market-specific adapters (US + EGX) for data, sessions, and corporate actions
- [ ] Stable, versioned API layer designed for mobile clients (FastAPI preferred)
- [ ] Sub-1s live snapshot for selected stock with freshness indicators
- [ ] Async analytics pipeline returning report_id with polling for completion
- [ ] Multi-agent outputs are consistent, traceable, and confidence-scored
- [ ] Data freshness monitoring with graceful degradation and stale-data behavior
- [ ] Bilingual narratives (Arabic/English) with language parameter support
- [ ] Decision-support label output: BUY / SELL / HOLD with rationale, confidence, and risks
- [ ] Mobile apps allow market/ticker selection, chart viewing, and analysis requests

### Out of Scope

- Guaranteed real-time data without licensing — provider-dependent
- Financial advice guarantees or outcome promises — decision support only
- Full mobile app UI build — backend/API focus for mobile consumption

## Context

- Existing system uses LangGraph + LangChain to orchestrate analyst/researcher/trader/risk agents.
- Current flow is CLI-driven and partially inconsistent; needs reliability improvements.
- EGX support must be first-class without forking or regressions in US flow.
- Mobile app experience requires low-latency snapshot and reliable async analytics.

## Constraints

- **Data licensing**: Real-time feeds may require paid providers; must support delayed fallbacks.
- **Latency**: Snapshot response target is sub-1s with caching.
- **Reliability**: No regression of existing US functionality while adding EGX.
- **Localization**: Bilingual output (Arabic/English) for narrative fields.
- **API-first**: Design stable, versioned APIs for mobile clients.
- **Platform**: Python stack; API layer preference is FastAPI.
- **Deployment**: Cloud target TBD; design should be cloud-ready and portable.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| API-first backend for mobile app | Mobile UX depends on fast, stable APIs | — Pending |
| Market-agnostic core with adapters | Avoid duplicated logic and reduce regressions | — Pending |
| Async analytics by default | Keep UI responsive while heavy compute runs | — Pending |
| Sub-1s snapshot | Mobile UX expectation | — Pending |
| Decision labels BUY/SELL/HOLD | Consistent decision-support framing | — Pending |
| Bilingual narratives | Required for target users | — Pending |
| FastAPI for API layer | Align with Python codebase | — Pending |

---
*Last updated: 2026-02-03 after initialization*

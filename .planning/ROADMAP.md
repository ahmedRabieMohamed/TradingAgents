# Roadmap: Multi-Market Stock Analytics Platform

## Overview

This roadmap delivers an API-first, multi-market analytics backend that enables users to discover markets and symbols, retrieve sub‑1s snapshots with freshness/entitlement signals, access historical data, and request async analytics reports. It culminates in localized AR/EN narratives and decision labels so mobile clients can serve both English and Arabic audiences without regressions.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Validate multi-agent core** - Verify multi-agent stability and reliability before UI/API work.
- [x] **Phase 2: Market Access & Discovery API** - Users can authenticate and discover markets/symbols via a stable API.
- [ ] **Phase 3: Snapshot Quotes & Freshness** - Users get sub‑1s snapshots with session status, freshness, and entitlement labeling.
- [ ] **Phase 4: Historical Data Access** - Users can retrieve historical prices and corporate actions for analytics and charts.
- [ ] **Phase 5: Async Analytics Reports** - Users can request and retrieve explainable analytics reports with decision labels.
- [ ] **Phase 6: Localization (AR/EN)** - Users receive bilingual narratives and localized decision labels.
- [ ] **Phase 7: Mobile Apps (iOS/Android)** - Users select market/ticker, view charts, and trigger analysis from mobile.

## Phase Details

## Current Milestone: Phase 1-6

### Phase 1: Validate multi-agent core

**Goal:** Multi-agent core runs reliably for US and EGX with validation guardrails and repeatable smoke checks.
**Depends on:** Nothing (first phase)
**Plans:** 4 plans

Plans:
- [x] 01-01-PLAN.md — Add state validation guardrails to US/EGX graphs
- [x] 01-02-PLAN.md — Provide a validation runner and documentation
- [x] 01-03-PLAN.md — Normalize final trade decision outputs
- [x] 01-04-PLAN.md — Map EGX reports to standard fields

**Details:**
Establish a shared state validation layer for both graphs and add a repeatable runner that reports pass/fail diagnostics for US and EGX flows.

### Phase 2: Market Access & Discovery API
**Goal**: Users can authenticate and discover markets/symbols via a stable API surface.
**Depends on**: Phase 1
**Requirements**: MKT-01, MKT-02, MKT-03, MKT-04, API-01, API-03
**Success Criteria** (what must be TRUE):
  1. User can authenticate with token/JWT and receives rate-limit/quota enforcement feedback when exceeded.
  2. User can select US or EGX and search symbols by ticker or company name within that market.
  3. User can filter stock lists by sector, market cap, and most active, and view top/trending lists per market.
  4. Discovery endpoints return a standard error model with explicit error codes on invalid requests.
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — API foundation (settings, error model, rate limits)
- [x] 02-02-PLAN.md — Auth tokens (access-only) + auth endpoints
- [x] 02-03-PLAN.md — Market registry + /markets endpoints
- [x] 02-04-PLAN.md — Symbol discovery + EODHD-backed lists
- [x] 02-09-PLAN.md — Optional Redis limiter init in dev
- [x] 02-10-PLAN.md — EODHD exchange details wired into market registry
- [x] 02-11-PLAN.md — EOD series fallback for symbol metrics

### Phase 3: Snapshot Quotes & Freshness
**Goal**: Users receive sub‑1s snapshot quotes with session status and freshness/entitlement signals.
**Depends on**: Phase 2
**Requirements**: SNAP-01, SNAP-02, SNAP-03, SNAP-04, API-02, API-04, API-06
**Success Criteria** (what must be TRUE):
  1. User receives a snapshot with last price, change %, session high/low, and volume for a selected stock.
  2. User receives bid/ask and spread when available, and can see when those fields are unavailable.
  3. User sees market session status (open/closed) and last update timestamp alongside freshness flags (real‑time vs delayed).
  4. Snapshot requests meet the sub‑1s latency target via cache-first responses and show delayed fallback labeling when entitlements require it.
**Plans**: 4/4 plans complete

Plans:
- [x] 03-01-PLAN.md — Define snapshot schemas and cache TTL settings
- [x] 03-02-PLAN.md — Implement cache-first snapshot service and freshness labeling
- [x] 03-03-PLAN.md — Add snapshot router and wire into API
- [x] 03-04-PLAN.md — Fix snapshot freshness timestamps and cache bypass

### Phase 4: Historical Data Access
**Goal**: Users can retrieve historical prices and corporate actions for analytics accuracy.
**Depends on**: Phase 2
**Requirements**: HIST-01, HIST-02, HIST-03, HIST-04
**Success Criteria** (what must be TRUE):
  1. User can fetch daily OHLCV history for charts and analytics.
  2. User can fetch intraday ranges (1D/1W/1M/1Y) when licensed.
  3. User can fetch corporate actions and adjusted price series for accurate analytics.
**Plans**: TBD

Plans:
- [ ] 04-01: TBD

### Phase 5: Async Analytics Reports
**Goal**: Users can request and retrieve explainable analytics reports asynchronously.
**Depends on**: Phase 4
**Requirements**: ANLT-01, ANLT-02, ANLT-03, ANLT-04, ANLT-05, ANLT-06, ANLT-07, API-05
**Success Criteria** (what must be TRUE):
  1. User can create an analytics job and poll status/result via a report_id.
  2. Reports include MA/EMA, RSI, MACD, ATR, Bollinger Bands, and a trend/momentum/volatility summary.
  3. Reports include support/resistance, liquidity/volume anomalies, and risk notes.
  4. Reports include a BUY/SELL/HOLD label with confidence and rationale, and repeated job creation with the same idempotency key returns the same report_id.
**Plans**: TBD

Plans:
- [ ] 05-01: TBD

### Phase 6: Localization (AR/EN)
**Goal**: Users receive bilingual narratives and localized decision labels in API responses.
**Depends on**: Phase 5
**Requirements**: LOC-01, LOC-02
**Success Criteria** (what must be TRUE):
  1. User can request Arabic or English via a language parameter and receives narrative fields in the chosen language.
  2. Decision labels are localized (AR/EN) in responses.
**Plans**: TBD

Plans:
- [ ] 06-01: TBD

### Phase 7: Mobile Apps (iOS/Android)

**Goal**: Users select market and ticker, view charts, and request analysis from mobile, then receive agent results.
**Depends on**: Phase 6
**Requirements**: MOB-01, MOB-02, MOB-03, MOB-04
**Success Criteria** (what must be TRUE):
  1. User can select market (US/EGX) and search/select ticker from mobile.
  2. User can view interactive price charts (range controls, latest price, volume) on mobile.
  3. User can trigger analysis from a ticker screen and receive results in-app with status and completion updates.
  4. Mobile app handles API errors and rate limits gracefully with clear messaging.
**Plans**: TBD

Plans:
- [ ] 07-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Validate multi-agent core | 4/4 | Complete | 2026-02-08 |
| 2. Market Access & Discovery API | 7/7 | Complete | 2026-02-17 |
| 3. Snapshot Quotes & Freshness | 4/4 | Complete | 2026-02-17 |
| 4. Historical Data Access | 0/TBD | Not started | - |
| 5. Async Analytics Reports | 0/TBD | Not started | - |
| 6. Localization (AR/EN) | 0/TBD | Not started | - |
| 7. Mobile Apps (iOS/Android) | 0/TBD | Not started | - |

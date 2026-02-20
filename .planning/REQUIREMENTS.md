# Requirements: Multi-Market Stock Analytics Platform

**Defined:** 2026-02-03
**Core Value:** Deliver fast, reliable, explainable stock analytics for US and EGX without regressions.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Market Discovery

- [x] **MKT-01**: User can select a market (US or EGX) for all queries
- [x] **MKT-02**: User can search symbols by ticker or company name within a market
- [x] **MKT-03**: User can filter stock lists by sector, market cap, and most active
- [x] **MKT-04**: User can view top/trending lists per market

### Snapshot & Quotes

- [x] **SNAP-01**: User receives a live snapshot with last price, change %, session high/low, and volume
- [x] **SNAP-02**: User receives bid/ask and spread when available
- [x] **SNAP-03**: User sees market session status (open/closed) and last update timestamp
- [x] **SNAP-04**: User sees freshness flags indicating real-time vs delayed data

### Historical Data

- [x] **HIST-01**: User can fetch daily OHLCV history for charts and analytics
- [x] **HIST-02**: User can fetch intraday ranges (1D/1W/1M/1Y) when licensed
- [x] **HIST-03**: User can fetch corporate actions (splits/dividends) per market
- [x] **HIST-04**: User can fetch adjusted price series for analytics accuracy

### Analytics & Reports

- [x] **ANLT-01**: User can request an async analytics report (job + status + result)
- [x] **ANLT-02**: Report includes MA/EMA, RSI, MACD, ATR, and Bollinger Bands
- [x] **ANLT-03**: Report includes trend/momentum/volatility regime summary
- [x] **ANLT-04**: Report includes support/resistance levels
- [x] **ANLT-05**: Report includes liquidity/volume anomaly signals
- [x] **ANLT-06**: Report includes risk notes (volatility, gap, illiquidity)
- [x] **ANLT-07**: Report includes BUY/SELL/HOLD label with confidence and rationale

### API & Reliability

- [x] **API-01**: API uses token/JWT auth with rate limits and quotas
- [x] **API-02**: Snapshot path is cache-first to meet sub-1s latency target
- [x] **API-03**: API returns a standard error model with explicit error codes
- [x] **API-04**: API returns data freshness metadata and stale-data behavior
- [x] **API-05**: Analytics job creation supports idempotency for safe retries
- [x] **API-06**: API enforces licensing/entitlements with delayed fallback labeling

### Localization

- [ ] **LOC-01**: Narrative fields are available in Arabic and English via a language parameter
- [ ] **LOC-02**: Decision labels are localized (AR/EN) in responses

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Comparisons & Alerts

- **COMP-01**: User can compare performance across US and EGX with normalized metrics
- **ALRT-01**: User can receive push notifications when analytics reports are ready

### Advanced EGX Insights

- **EGX-01**: User receives EGX-specific liquidity and volatility insights

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time data for all users | Licensing and cost constraints vary by provider |
| Trading execution endpoints | Regulatory + security complexity; not analytics scope |
| Black-box AI buy/sell signals | Legal risk and low explainability |
| Unlimited intraday history | Cost/performance constraints; needs tiering |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| MKT-01 | Phase 1 | Complete |
| MKT-02 | Phase 1 | Complete |
| MKT-03 | Phase 1 | Complete |
| MKT-04 | Phase 1 | Complete |
| SNAP-01 | Phase 2 | Complete |
| SNAP-02 | Phase 2 | Complete |
| SNAP-03 | Phase 2 | Complete |
| SNAP-04 | Phase 2 | Complete |
| HIST-01 | Phase 3 | Complete |
| HIST-02 | Phase 3 | Complete |
| HIST-03 | Phase 3 | Complete |
| HIST-04 | Phase 3 | Complete |
| ANLT-01 | Phase 4 | Complete |
| ANLT-02 | Phase 4 | Complete |
| ANLT-03 | Phase 4 | Complete |
| ANLT-04 | Phase 4 | Complete |
| ANLT-05 | Phase 4 | Complete |
| ANLT-06 | Phase 4 | Complete |
| ANLT-07 | Phase 4 | Complete |
| API-01 | Phase 1 | Complete |
| API-02 | Phase 2 | Complete |
| API-03 | Phase 1 | Complete |
| API-04 | Phase 2 | Complete |
| API-05 | Phase 4 | Complete |
| API-06 | Phase 2 | Complete |
| LOC-01 | Phase 5 | Pending |
| LOC-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-03*
*Last updated: 2026-02-03 after roadmap mapping*

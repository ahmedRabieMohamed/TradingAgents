# Feature Research

**Domain:** Multi-market stock analytics API (US + EGX) for mobile clients
**Researched:** 2026-02-03
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Market selection (US vs EGX) | Users need to choose the exchange context | MEDIUM | Must map symbols per market and handle differing calendars/time zones. |
| Symbol search & lookup | Users expect fast ticker discovery | MEDIUM | Include partial search, company name matching, and market-specific suffix handling. |
| Price snapshot (last/close, bid/ask, volume) | Baseline stock quote expectation | MEDIUM | Provide freshness timestamp and market delay flag (licensed real-time vs delayed). |
| OHLCV historical series (daily/intraday where licensed) | Required for charts and analytics inputs | HIGH | Provide adjusted/unadjusted where possible; handle different granularity by market. |
| Corporate actions (splits/dividends) | Needed for accurate historical performance | MEDIUM | Essential for “adjusted” analytics and chart continuity. |
| Market status & trading hours | Users need to know if market is open | LOW | Include exchange calendar, holidays, and trading session windows. |
| Error/latency transparency | API clients expect reliable behavior | MEDIUM | Return explicit data age, source, and fallback indicators (especially for delayed data). |
| Auth, rate limits, usage quotas | Standard API expectations | MEDIUM | Clear error codes and quota headers; distinct per-client limits. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Sub‑1s snapshot SLA with caching strategy | “Feels instant” on mobile | HIGH | Requires aggressive caching, prefetching, and multi-source fallback. |
| Async analytics report (job + callback/poll) | Enables heavier analytics without blocking | MEDIUM | Job status + result endpoint; aligns with “snapshot now, analytics later”. |
| Explainable analytics (inputs + method notes) | Trust and compliance | MEDIUM | Return indicator inputs, window sizes, and data recency for transparency. |
| Bilingual responses (AR/EN labels + notes) | Better UX for local market | MEDIUM | Requires translation for stock names, sectors, and analytics explanations. |
| Licensing-aware delayed fallback | Prevents outages when real-time data restricted | HIGH | Automatic fallback with explicit delay labeling and partial data warnings. |
| Cross‑market comparison view | Users compare US vs EGX performance | HIGH | Normalize currencies, sessions, and time zones; provide comparison context. |
| EGX‑specific liquidity/volatility insights | Local differentiation | HIGH | Needs tailored metrics (e.g., low‑volume adjustments) and local market norms. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| “Real‑time everything” for all markets | Users want live data | Licensing and cost constraints; regulatory restrictions | Offer delayed fallback + clear freshness labels; upgrade path if licensed. |
| Trading execution endpoints | “One‑stop” finance experience | Regulatory + security complexity; not API‑first analytics focus | Keep read‑only analytics; integrate broker links later if needed. |
| Black‑box AI “buy/sell” signals | Users want quick decisions | High legal/regulatory risk, hard to explain | Provide explainable indicators and scenarios instead. |
| Unlimited historical intraday for all users | Power‑users request it | Data cost + performance drain | Tiered access, capped window, or offline exports. |

## Feature Dependencies

```
[Market selection]
    └──requires──> [Symbol master & search]
                       └──requires──> [Market-specific metadata]

[Snapshot quote]
    └──requires──> [Market status & trading hours]
                       └──requires──> [Exchange calendar]

[Async analytics report]
    └──requires──> [OHLCV history + corporate actions]
                       └──requires──> [Adjusted price engine]

[Licensing-aware delayed fallback] ──enhances──> [Snapshot quote]

[Cross-market comparison] ──requires──> [Currency conversion + normalized time windows]
```

### Dependency Notes

- **Market selection requires Symbol master & search:** market-specific symbol sets differ (US vs EGX), so lookup must be scoped to market metadata.
- **Snapshot quote requires Market status & trading hours:** to label freshness, determine last trade, and choose delayed fallback behavior.
- **Async analytics report requires OHLCV + corporate actions:** analytics need clean, adjusted series for accurate indicators.
- **Licensing-aware delayed fallback enhances Snapshot quote:** protects API from gaps when real-time data is unavailable or restricted.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] Market selection (US/EGX) + symbol search — ensures users can find stocks per market.
- [ ] Snapshot quote with freshness + delay flag — core promise of sub‑1s data.
- [ ] Async analytics report (basic indicators) — validates “snapshot now, analytics later.”
- [ ] OHLCV daily history + corporate actions — supports baseline analytics and charts.
- [ ] API reliability + transparent error model — required for mobile integration.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Bilingual response metadata — add after initial usage confirms locale needs.
- [ ] Licensing-aware delayed fallback automation — add when real-time coverage gaps appear.
- [ ] Expanded analytics library (more indicators, sector peers) — once data quality stable.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Cross-market portfolio analytics — requires more normalization and user state.
- [ ] EGX‑specific advanced insights — needs deeper local data/market research.
- [ ] Push notifications for analytics ready — depends on mobile client adoption.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Snapshot quote with freshness/delay flag | HIGH | MEDIUM | P1 |
| Market selection + symbol search | HIGH | MEDIUM | P1 |
| OHLCV daily history + corporate actions | HIGH | HIGH | P1 |
| Async analytics report (basic indicators) | HIGH | MEDIUM | P1 |
| Market status & trading hours | MEDIUM | LOW | P2 |
| Bilingual response metadata | MEDIUM | MEDIUM | P2 |
| Licensing-aware delayed fallback | HIGH | HIGH | P2 |
| Cross‑market comparison | MEDIUM | HIGH | P3 |
| EGX‑specific liquidity insights | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Competitor A | Competitor B | Our Approach |
|---------|--------------|--------------|--------------|
| Snapshot quotes | Polygon/Massive snapshot endpoint with delayed vs real‑time plans | Alpha Vantage quote endpoint | Sub‑1s snapshot with explicit freshness + fallback policy. |
| Historical time series | Polygon daily/intraday data | Alpha Vantage time series (daily/intraday/weekly/monthly) | Focused OHLCV + adjusted series for analytics (US+EGX). |
| Technical indicators | Polygon limited; often via aggregates | Alpha Vantage broad indicators | Start with a small, explainable set; expand after validation. |
| Corporate actions | Available via fundamentals or adjusted data | Alpha Vantage dividends/splits | Required for adjusted analytics and accurate returns. |
| Market status | Available via exchange/market endpoints | Alpha Vantage market status utility | Provide per‑market trading status and next session info. |

## Sources

- https://polygon.io/docs/stocks/get_v2_snapshot_locale_us_markets_stocks_tickers (snapshot endpoint; delayed vs real‑time plans)
- https://www.alphavantage.co/documentation/ (quotes, time series, indicators, fundamentals, corporate actions)

---
*Feature research for: Multi-market stock analytics API (US + EGX)*
*Researched: 2026-02-03*

# Pitfalls Research

**Domain:** Multi-market stock analytics API (US + EGX)
**Researched:** 2026-02-03
**Confidence:** LOW (no authoritative sources located; domain-knowledge synthesis only)

## Critical Pitfalls

### Pitfall 1: Treating EGX like US markets (calendar, sessions, limits)

**What goes wrong:**
Analytics and snapshot calculations assume US market hours, holidays, volatility, and price limit rules. EGX-specific trading sessions, weekends, and price limits are ignored, producing incorrect “today” data, false gaps, or invalid analytics.

**Why it happens:**
US-first systems hardcode trading calendars and session boundaries, then “bolt on” another market without normalizing market metadata.

**How to avoid:**
Create a per-market metadata layer (calendar, session windows, price limits, lot size, currency), and make all analytics and snapshot queries explicitly market-aware. Unit-test with EGX-specific dates.

**Warning signs:**
- EGX “today” volume is zero on active days
- EOD data appears one day off
- Analytics differ between markets for identical logic

**Phase to address:**
Phase 1 — Market onboarding & licensing (define calendars/metadata) and Phase 2 — Data normalization

---

### Pitfall 2: Symbol master drift and corporate action gaps

**What goes wrong:**
Ticker mappings and historical series break when EGX symbols change, delistings occur, or corporate actions (splits, dividends) are not reconciled. Users see broken histories or incorrect analytics.

**Why it happens:**
US pipelines assume stable tickers and corporate action handling; EGX introduces additional symbol changes and incomplete vendor normalization.

**How to avoid:**
Maintain a canonical symbol master with vendor mappings, instrument IDs, and effective dates. Build a corporate action normalization pipeline and backfill logic.

**Warning signs:**
- Sudden discontinuities in historical charts
- “Unknown symbol” for previously valid EGX tickers
- Analytics drift after corporate action events

**Phase to address:**
Phase 2 — Data normalization & symbol master

---

### Pitfall 3: Licensing constraints ignored in caching and redistribution

**What goes wrong:**
Caching, derived analytics, and API responses violate market data licensing (e.g., delayed vs real-time constraints), leading to compliance risk or service takedown.

**Why it happens:**
Engineering treats “analytics output” as outside licensing scope, or uses a US vendor’s license rules for EGX data.

**How to avoid:**
Encode license rules as enforceable policies (delay windows, redistribution limits, attribution). Implement data tier labeling and enforce delayed fallback at the API boundary.

**Warning signs:**
- Unlabeled real-time data shown for EGX
- Delayed fallback not consistently applied
- Legal/licensing questions appearing late in delivery

**Phase to address:**
Phase 1 — Market onboarding & licensing (policy design), Phase 3 — API boundary enforcement

---

### Pitfall 4: US regression due to shared pipelines

**What goes wrong:**
Adding EGX changes shared code paths (cache keys, instrument schemas, analytics jobs), causing regressions for US users.

**Why it happens:**
No market isolation or feature flags; shared caches are keyed only by symbol; analytics jobs assume US-only data.

**How to avoid:**
Introduce market partitioning (cache keys, storage, queues) and contract tests that compare pre/post EGX outputs for US.

**Warning signs:**
- US API response time or accuracy changes after EGX release
- Increased cache collisions
- US incident rate spikes after EGX deployment

**Phase to address:**
Phase 3 — Analytics pipeline & caching; Phase 4 — Reliability & regression testing

---

### Pitfall 5: Timezone normalization errors

**What goes wrong:**
EOD data shows wrong date, or “latest” snapshot is from prior session due to timezone and trading session conversions.

**Why it happens:**
All timestamps assumed UTC or US Eastern; conversion happens late in the pipeline without market context.

**How to avoid:**
Normalize timestamps at ingestion with explicit market timezones and session boundaries. Store both exchange-local and UTC timestamps.

**Warning signs:**
- Daily OHLC mismatches between vendor and API
- “Today” analytics available before market open

**Phase to address:**
Phase 2 — Data normalization

---

### Pitfall 6: Analytics formulas unadjusted for market structure

**What goes wrong:**
Signals (volatility, momentum, liquidity) produce misleading results because EGX has different trading hours, liquidity profiles, and price limits.

**Why it happens:**
Analytics are implemented once for US and assumed universally valid.

**How to avoid:**
Define market-specific parameterization (window sizes, liquidity thresholds, limit-up/down rules) and document differences in explainability.

**Warning signs:**
- EGX “top movers” list dominated by limit events
- Users complain about “noisy” EGX analytics

**Phase to address:**
Phase 3 — Analytics engine & explainability

---

### Pitfall 7: Bilingual output correctness gaps (RTL, numerals, finance terms)

**What goes wrong:**
Arabic UI displays incorrect number formatting, RTL layout breaks, or financial terms are mistranslated, reducing trust.

**Why it happens:**
Translation added last, without domain glossary or numeric formatting rules.

**How to avoid:**
Create a bilingual glossary for finance terms, implement locale-aware formatting, and run bilingual review for explanations.

**Warning signs:**
- Mixed LTR/RTL strings in analytics explanations
- Wrong currency symbol placement or digits

**Phase to address:**
Phase 5 — Localization & explainability

---

### Pitfall 8: Async report pipeline not idempotent

**What goes wrong:**
Users request analytics and receive duplicate or conflicting results due to retries, job duplication, or stale cache.

**Why it happens:**
Job queue lacks dedupe keys; report generation not tied to market-aware cache keys or data version.

**How to avoid:**
Use idempotency keys per (user, market, symbol, analytics version) and store data-version stamps with reports.

**Warning signs:**
- Multiple report IDs for same request
- Reports show different results within minutes without data change

**Phase to address:**
Phase 3 — Analytics pipeline & caching

---

### Pitfall 9: Missing data quality monitoring for EGX

**What goes wrong:**
Gaps, suspensions, or vendor outages go unnoticed and analytics are generated on incomplete data.

**Why it happens:**
Existing quality checks are tailored to US vendors and do not validate EGX data coverage.

**How to avoid:**
Add market-specific data completeness checks (per symbol, per session) and publish an internal data quality status.

**Warning signs:**
- EGX snapshot shows stale price for active symbols
- Spikes in “no data” responses

**Phase to address:**
Phase 4 — Reliability & monitoring

---

### Pitfall 10: Delayed fallback not clearly labeled to users

**What goes wrong:**
Users can’t distinguish real-time vs delayed data, leading to mistrust or licensing violations.

**Why it happens:**
Fallback logic exists but UI and API metadata omit delay status.

**How to avoid:**
Expose data freshness fields (delay seconds, vendor tier) in API response and surface it in UI/explanations.

**Warning signs:**
- Support tickets questioning data freshness
- Confusion between US and EGX snapshots

**Phase to address:**
Phase 3 — API boundary & response contracts

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded market rules in analytics | Faster initial delivery | Inability to support new markets; recurring bugs | Never |
| Single shared cache key for all markets | Simple caching | Cross-market collisions; US regressions | Never |
| Skip symbol master, use vendor tickers directly | Quicker integration | Broken history; corporate action errors | MVP only if EGX pilot is short-lived |
| One global “delay” flag for all data | Simple compliance | Violates licensing per vendor/market | Never |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| EGX data vendor | Assuming same schema as US feed | Build a normalization layer + schema mapping per market |
| Corporate actions feed | Treating actions as optional | Normalize and backfill analytics using adjusted history |
| FX rates provider | Ignoring currency conversions for analytics | Explicit FX conversion step with timestamps |
| Identity/analytics jobs | Missing market context in job payloads | Include market and vendor tier in all job messages |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Per-request analytics recomputation | High latency, timeouts | Precompute/cached analytics per symbol/market | At moderate traffic (hundreds of concurrent users) |
| Unified queue for US+EGX | EGX backlog impacts US | Partition queues by market + priority | When EGX ingestion spikes |
| Missing cache invalidation on corporate actions | Old analytics served | Versioned analytics and invalidation hooks | After first major corporate action event |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing vendor data identifiers | License breach and data leakage | Mask vendor IDs and expose canonical IDs only |
| Returning raw vendor payloads | Accidental disclosure of restricted fields | Sanitize and whitelist API response fields |
| No audit trail for data tier usage | Compliance risk | Log access with market, tier, delay status |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Mixed currency display for EGX (EGP vs USD) | Misinterpretation of price | Always show currency and format per locale |
| No freshness indicator | Users distrust data | Display delay status and timestamp |
| Arabic explanations are literal translations | Confusing/incorrect | Use finance glossary + human review |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Market onboarding:** Missing per-market calendars and session rules — verify market metadata registry
- [ ] **Analytics engine:** Missing market-specific parameters — verify EGX-specific defaults
- [ ] **Licensing compliance:** Missing delay labels in responses — verify API contract fields
- [ ] **Localization:** Missing RTL number formatting — verify Arabic formatting tests

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Market rule mismatch | MEDIUM | Patch market metadata, backfill analytics, reissue reports |
| Symbol master drift | HIGH | Rebuild symbol mapping, run backfill, invalidate caches |
| Licensing violation | HIGH | Disable affected endpoints, implement policy guardrails, legal review |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Treating EGX like US markets | Phase 1–2 | Market calendar tests and EGX EOD validations |
| Symbol master drift | Phase 2 | Corporate action backfill run passes |
| Licensing constraints ignored | Phase 1 & 3 | Delay-policy tests + legal sign-off |
| US regression due to shared pipelines | Phase 3–4 | US regression test suite passes |
| Timezone normalization errors | Phase 2 | Snapshot timestamp parity with vendor |
| Unadjusted analytics formulas | Phase 3 | EGX-specific analytics benchmarks |
| Bilingual output gaps | Phase 5 | Arabic UX review + formatting tests |
| Async report non-idempotent | Phase 3 | Idempotency tests with retries |
| Missing EGX data quality monitoring | Phase 4 | Data completeness dashboard checks |
| Delayed fallback not labeled | Phase 3 | API contract tests for freshness fields |

## Sources

- No authoritative sources located in this run (no web research tools available)
- Domain-knowledge synthesis based on multi-market market-data integrations (LOW confidence)

---
*Pitfalls research for: multi-market stock analytics API (US + EGX)*
*Researched: 2026-02-03*

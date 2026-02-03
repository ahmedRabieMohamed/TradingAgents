# Architecture Research

**Domain:** Multi-market stock analytics backend (US + EGX) for mobile API
**Researched:** 2026-02-03
**Confidence:** MEDIUM (based on common backend patterns; no external sources used)

## Standard Architecture

### System Overview

```
┌────────────────────────────────────────────────────────────────────────────┐n+│                             API & Experience Layer                           │
├────────────────────────────────────────────────────────────────────────────┤n+│  ┌────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐ │
│  │ API Gateway │→ │ Market Router │→ │ Snapshot API  │→ │ Report API    │ │
│  └─────┬──────┘   └──────┬────────┘   └──────┬────────┘   └──────┬────────┘ │
│        │                 │                  │                   │          │
├────────┴─────────────────┴──────────────────┴───────────────────┴──────────┤n+│                         Domain & Orchestration Layer                        │
├────────────────────────────────────────────────────────────────────────────┤n+│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────────────┐   │
│  │ Analytics Orches │  │ Explainability   │  │ Localization (ar/en)      │   │
│  └────────┬────────┘  └────────┬──────────┘  └──────────┬────────────────┘   │
│           │                    │                         │                    │
├───────────┴────────────────────┴─────────────────────────┴──────────────────┤n+│                         Data Platform & Services                             │
├────────────────────────────────────────────────────────────────────────────┤n+│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │
│  │ Market Adapter│  │ Normalization │  │ Pricing/CA    │  │ Entitlements  │ │
│  └──────┬────────┘  └──────┬────────┘  └──────┬────────┘  └──────┬────────┘ │
│         │                  │                 │                 │           │
│  ┌──────┴────────┐  ┌──────┴────────┐  ┌──────┴────────┐  ┌─────┴─────────┐ │
│  │ Snapshot Cache│  │ Time-series DB│  │ Master Data   │  │ Object Store  │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘ │
├────────────────────────────────────────────────────────────────────────────┤n+│                         Async & Observability                                │
├────────────────────────────────────────────────────────────────────────────┤n+│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │
│  │ Job Queue     │  │ Workers       │  │ Metrics/Logs  │  │ Audit/Tracing │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| API Gateway | Auth, rate limit, request shaping | API gateway + auth service (JWT/OAuth) |
| Market Router | Route by market (US/EGX), apply entitlements | Policy + routing service |
| Snapshot API | Sub-1s quote snapshot, fallback to delayed | Read-optimized service + cache |
| Report API | Return async report status and results | Read service + object store |
| Market Adapters | Ingest per-market data feeds | Adapter per vendor/market |
| Normalization | Canonicalize symbols, corporate actions, fields | ETL/stream transform |
| Pricing/CA | Corporate actions, splits/dividends normalization | Domain service |
| Entitlements | Licensing, delay rules, user permissions | Policy engine |
| Snapshot Cache | Hot path for latest quotes | In-memory cache/kv |
| Time-series DB | Historical prices/metrics | TSDB or columnar store |
| Master Data | Symbols, exchange metadata, mappings | Relational DB |
| Object Store | Store reports/explanations | Blob/object storage |
| Job Queue + Workers | Async analytics, backfills | Queue + worker pool |
| Explainability | Store/serve model rationale | Metadata store + renderer |
| Localization | Bilingual text, formatting | i18n service/translation tables |
| Observability | SLA, latency, regression detection | Metrics + logs + tracing |

## Recommended Project Structure

```
src/
├── api/                    # HTTP handlers, request/response DTOs
│   ├── middleware/         # auth, rate limiting, locale
│   └── routes/             # snapshot, report, health
├── domain/                 # market-agnostic business logic
│   ├── markets/            # routing + market policies
│   ├── analytics/          # orchestration + explainability
│   ├── entitlements/       # licensing/delay rules
│   └── localization/       # ar/en formatting, templates
├── adapters/               # market/vendor integrations
│   ├── us/                 # US data feed adapter(s)
│   └── egx/                # EGX data feed adapter(s)
├── data/                   # storage layer & repositories
│   ├── cache/              # snapshot cache
│   ├── timeseries/         # price history
│   ├── master/             # symbols, mappings
│   └── reports/            # report storage
├── jobs/                   # async workers & queue consumers
├── observability/          # metrics, tracing, audit
└── config/                 # env, feature flags, market toggles
```

### Structure Rationale

- **domain/** isolates market-agnostic logic to reduce US regressions when adding EGX.
- **adapters/** keeps per-market ingestion isolated behind a stable interface.
- **data/** centralizes storage access so cache/DB changes don’t ripple across services.
- **jobs/** separates async analytics from the sub-1s snapshot path.

## Architectural Patterns

### Pattern 1: Market Adapter + Canonical Model

**What:** Each market feed maps into a canonical security/price schema before downstream use.
**When to use:** Any multi-market setup with different field sets and licensing rules.
**Trade-offs:** Extra mapping layer, but prevents cross-market leakage and reduces regressions.

**Example:**
```typescript
// Pseudocode: normalize feed tick into canonical format
const canonical = normalizeTick(feedTick, marketRules[market]);
snapshotCache.put(`${market}:${canonical.symbol}`, canonical);
```

### Pattern 2: Read-optimized Snapshot Path + Async Analytics

**What:** Fast read path for snapshots, heavy analytics via queue/worker.
**When to use:** Sub-1s response requirements + deeper analytics.
**Trade-offs:** Eventual consistency for reports; requires job status tracking.

**Example:**
```typescript
// Snapshot handler
return snapshotCache.get(key) ?? delayedFallback.get(key);
```

### Pattern 3: Entitlements/Delay Policy as First-Class Service

**What:** Central policy checks for licensing and delay constraints.
**When to use:** Multiple data vendors, delayed fallback requirements.
**Trade-offs:** Slight overhead on requests; clearer compliance boundaries.

## Data Flow

### Request Flow (Snapshot)

```
Mobile App → API Gateway → Market Router → Snapshot API → Entitlements Check
     ↓                                                   ↓
Response (cached real-time) ← Snapshot Cache ← Normalized Feed
     ↓ (if not allowed)
Response (delayed) ← Delayed Store/Cache
```

### Request Flow (Async Report)

```
Mobile App → API Gateway → Market Router → Report API → Enqueue Job
     ↓                                            ↓
  Job ID/status ← Report Store ← Workers ← Time-series DB + Master Data
```

### Key Data Flows

1. **Market ingestion → normalization → storage:** Feed adapters map to canonical model and update caches/TSDB.
2. **Snapshot read path:** Cache-first; policy gates real-time vs delayed fallback.
3. **Analytics job:** Worker reads history + metadata, computes metrics, stores report + explainability.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Single service + cache + queue; basic observability |
| 1k-100k users | Split ingestion/analytics workers; add cache tiering; circuit breakers |
| 100k+ users | Multi-region read replicas; sharded cache; per-market scaling |

### Scaling Priorities

1. **First bottleneck:** Snapshot latency (cache miss, entitlement checks). Fix with cache warming and fast policy path.
2. **Second bottleneck:** Analytics throughput (queue backlog). Fix with worker autoscaling + job prioritization.

## Anti-Patterns

### Anti-Pattern 1: Market-Specific Logic in Core Domain

**What people do:** Hardcode US/EGX quirks in core services.
**Why it's wrong:** Causes regressions when adding new markets.
**Do this instead:** Keep market rules in adapters/policy services with tests per market.

### Anti-Pattern 2: Heavy Analytics in Snapshot Path

**What people do:** Compute analytics on request.
**Why it's wrong:** Breaks sub-1s requirement and scales poorly.
**Do this instead:** Use async workers; return job status and cached summaries.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Market Data Vendor (US) | Streaming or polling adapter | Enforce entitlement + delay policy |
| Market Data Vendor (EGX) | Adapter with normalization | Symbol mapping and timezone rules |
| Auth/Identity | JWT/OAuth | Mobile-friendly token handling |
| Notification (optional) | Webhooks/push | For report-ready events |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| API ↔ Domain | Direct calls | DTOs only; no vendor schemas |
| Domain ↔ Adapters | Interface contract | Market adapters swap without API change |
| Domain ↔ Data | Repository interfaces | Enables cache/DB changes safely |
| Jobs ↔ Domain | Command/event | Async analytics isolated from request path |

## Suggested Build Order (Dependencies)

1. **Canonical data model + market routing policy** (blocks everything else)
2. **Market adapters + normalization** (needed for real data flow)
3. **Storage layer (cache, master data, TSDB)** (snapshot + analytics dependencies)
4. **Snapshot API + entitlement checks** (core MVP requirement)
5. **Async job pipeline + report API** (analytics UX)
6. **Explainability + localization** (compliance and bilingual support)
7. **Observability + regression guards** (protect US behavior while adding EGX)

## Sources

- No external sources used (architecture synthesized from common industry patterns). Validate against current vendor docs and licensing agreements.

---
*Architecture research for: multi-market stock analytics API (US + EGX)*
*Researched: 2026-02-03*

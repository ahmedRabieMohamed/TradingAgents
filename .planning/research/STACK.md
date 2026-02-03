# Stack Research

**Domain:** Multi-market stock analytics backend (US + EGX) with mobile-first APIs
**Researched:** 2026-02-03
**Confidence:** MEDIUM (versions verified via official sources; “standard stack” inference without websearch)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.13.11 | Runtime for analytics + API | Current stable bugfix line with broad ecosystem support; safer than jumping to newest 3.14 for production services. **Confidence: MEDIUM** |
| FastAPI | 0.128.0 | API framework | High-performance async API with OpenAPI out of the box; aligns with API-first + mobile clients. **Confidence: HIGH** |
| Uvicorn | 0.40.0 | ASGI server | Standard ASGI server for FastAPI; supports HTTP/1.1, WebSockets; widely used in production. **Confidence: HIGH** |
| Pydantic | 2.12.5 | Data validation + schema | FastAPI’s core validation layer; v2 is now the primary supported version. **Confidence: HIGH** |
| SQLAlchemy | 2.0.46 | ORM + SQL toolkit | Mature, async-capable ORM for transactional data + metadata; strong ecosystem. **Confidence: HIGH** |
| PostgreSQL | 18.1 | Primary relational database | Reliable OLTP core for users, portfolios, entitlements, audit trail, and analytics metadata. **Confidence: HIGH** |
| Redis | 8.4.0 | Cache + rate limit + task broker | Low-latency cache for sub‑1s snapshots and a durable broker for async analytics. **Confidence: HIGH** |
| Celery | 5.6.2 | Async task queue | Industry standard for background analytics pipelines and report generation. **Confidence: HIGH** |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| psycopg | 3.3.2 | PostgreSQL driver (sync/async) | Default DB driver for SQLAlchemy on Postgres (use `psycopg[binary,pool]`). **Confidence: HIGH** |
| asyncpg | 0.31.0 | High-performance async Postgres driver | Use for read-heavy, latency-sensitive paths or async-only services. **Confidence: HIGH** |
| redis-py | 7.1.0 | Redis client | Standard Redis client for caching, rate-limit, and broker operations. **Confidence: HIGH** |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Ruff | Linting + formatting | Fast and consistent; keep formatting aligned in CI. |
| Pytest | Testing | Use for unit + integration tests (DB + cache). |
| Mypy | Static typing | Helps keep schema/DTO boundaries stable. |
| Pre-commit | Hook runner | Enforce lint + format before PRs. |

## Installation

```bash
# Core (Python packages)
pip install fastapi==0.128.0 uvicorn==0.40.0 pydantic==2.12.5 sqlalchemy==2.0.46 celery==5.6.2

# Supporting (Python packages)
pip install psycopg==3.3.2 asyncpg==0.31.0 redis==7.1.0
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| FastAPI | Django REST Framework | If you need batteries‑included admin + ORM‑first web app with heavier server-rendered UI. |
| PostgreSQL | ClickHouse (columnar) | If you need multi‑TB, ad‑hoc OLAP queries and can tolerate dual‑store complexity. |
| Celery | Dramatiq / Temporal | Dramatiq for simpler task queues; Temporal for complex workflow orchestration and retries at scale. |
| Redis | Memcached | Only for simple cache-aside with no persistence or task queue needs. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Pydantic v1 | FastAPI 0.128 drops v1 support; mismatched validation behaviors. | Pydantic v2.x |
| SQLite in production | Not reliable for concurrent analytics workloads or multi‑tenant usage. | PostgreSQL 18.x |
| Redis pre‑releases (e.g., 8.6 RC) | Not production‑ready; release candidates are explicitly non‑GA. | Redis 8.4.0 GA |

## Stack Patterns by Variant

**If sub‑second snapshot is hard to maintain under load:**
- Add a Redis write‑through cache with short TTLs for snapshot endpoints.
- Because cache hits shield upstream data providers and keep latency under 1s.

**If analytics becomes heavy OLAP (large cross‑sectional scans):**
- Add a columnar store (e.g., ClickHouse) for analytics outputs.
- Because OLAP query patterns can saturate PostgreSQL.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI 0.128.0 | Pydantic >= 2.7.0 | FastAPI dropped Pydantic v1 support and expects v2. |
| Celery 5.6.x | Python >= 3.9 | Celery 5.6 drops Python 3.8. |

## Sources

- https://www.python.org/downloads/ — Python 3.13.11 / 3.14.2 listed (official releases)
- https://github.com/fastapi/fastapi/releases — FastAPI 0.128.0
- https://github.com/encode/uvicorn/releases — Uvicorn 0.40.0
- https://github.com/pydantic/pydantic/releases — Pydantic 2.12.5
- https://github.com/sqlalchemy/sqlalchemy/releases — SQLAlchemy 2.0.46
- https://www.postgresql.org/docs/current/ — PostgreSQL 18.1 documentation (current)
- https://github.com/redis/redis/releases — Redis 8.4.0 GA
- https://github.com/celery/celery/releases — Celery 5.6.2
- https://github.com/redis/redis-py/releases — redis-py 7.1.0
- https://pypi.org/pypi/psycopg/json — psycopg 3.3.2 (PyPI metadata)
- https://pypi.org/pypi/asyncpg/json — asyncpg 0.31.0 (PyPI metadata)

---
*Stack research for: multi‑market stock analytics backend*
*Researched: 2026-02-03*

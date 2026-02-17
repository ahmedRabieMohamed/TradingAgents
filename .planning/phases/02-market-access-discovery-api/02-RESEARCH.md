# Phase 01: Market Access & Discovery API - Research

**Researched:** 2026-02-03
**Domain:** Python API (FastAPI) with JWT auth, market/symbol discovery
**Confidence:** MEDIUM

## Summary

This research focused on how to implement a Phase 01 market discovery API with JWT auth, refresh tokens, and rate limiting, using standard Python API tooling. Official FastAPI security guidance covers JWT bearer tokens, password hashing helpers, and OAuth2 flows, while fastapi-limiter provides a Redis-backed rate limiter that aligns with the requirement to rate-limit by account id. Redis-py is the standard Redis client for Python and provides the connection layer for rate limiting and token/session storage.

The standard approach is: FastAPI + Pydantic for request/response modeling, JWT library for access tokens, secure password hashing for any credentialed login, and a Redis-backed rate limiter. Architecture-wise, use APIRouter modules per domain (auth, markets, symbols), dependency injection for auth + rate limit checks, and explicit response models for stable API contracts. Most API design choices in Claude's discretion (token TTLs, pagination, sorting) should be decided at plan time and reflected consistently in response schemas and docs.

**Primary recommendation:** Build the Phase 01 API as a FastAPI app with JWT bearer auth, Redis-backed rate limiting (per user id), and explicit Pydantic response models for markets/symbols; choose and document token TTLs and pagination upfront to keep the API stable.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | Latest stable | API framework with OpenAPI and dependency injection | Official docs show JWT + OAuth2 flows and security helpers | 
| PyJWT | Latest stable | JWT encode/decode for access tokens | FastAPI security tutorial installs and uses PyJWT | 
| pwdlib | Latest stable | Password hashing (Argon2 recommended) | FastAPI security tutorial recommends pwdlib for hashing | 
| fastapi-limiter | v0.1.6+ | Redis-backed rate limiting via dependencies | Official README shows RateLimiter dependency and Redis init | 
| redis-py | 6.x+ | Redis client for rate limit state | Official Redis client for Python | 

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Uvicorn | Latest stable | ASGI server for FastAPI | Local dev and production serving | 
| SQLAlchemy + Alembic | 2.x / Latest | User/account storage and refresh token persistence | When storing users/refresh tokens in a DB instead of Redis | 

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FastAPI | Django REST Framework | Heavier stack; use if the project already runs on Django | 
| fastapi-limiter | SlowAPI | Different limiter middleware; verify integration with Redis | 

**Installation:**
```bash
pip install fastapi uvicorn pyjwt "pwdlib[argon2]" fastapi-limiter redis
```

## Architecture Patterns

### Recommended Project Structure
```
tradingagents/
├── api/
│   ├── app.py            # FastAPI app setup
│   ├── routers/          # APIRouter modules per domain
│   ├── schemas/          # Pydantic request/response models
│   ├── services/         # Market discovery/business logic
│   └── deps/             # Auth, rate limit, and common dependencies
├── data/                 # Market/symbol metadata loaders
└── settings.py           # Env-driven configuration
```

### Pattern 1: JWT Bearer Auth with Dependencies
**What:** Use FastAPI dependencies to validate Bearer tokens and inject the current user into endpoints.
**When to use:** Any authenticated endpoint (non-anonymous discovery).
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload
```

### Pattern 2: Redis-Backed Rate Limiting as Dependency
**What:** Initialize fastapi-limiter with Redis and add RateLimiter to endpoints.
**When to use:** All discovery endpoints (stricter limits for anonymous access).
**Example:**
```python
# Source: https://github.com/long2ice/fastapi-limiter
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_conn = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_conn)
    yield
    await FastAPILimiter.close()

app = FastAPI(lifespan=lifespan)

@app.get("/markets", dependencies=[Depends(RateLimiter(times=60, seconds=60))])
async def list_markets():
    return []
```

### Anti-Patterns to Avoid
- **Rolling your own JWT validation:** Use PyJWT and FastAPI dependencies to avoid security mistakes.
- **Anonymous and authenticated limits mixed:** Keep separate rate limit policies and identifiers for anon vs user id.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JWT creation/verification | Custom JWT encoding/decoding | PyJWT | Avoid cryptographic pitfalls and spec errors |
| Password hashing | Manual hashing with SHA | pwdlib (Argon2) or Passlib | Secure defaults and algorithm agility |
| Rate limiting | Custom in-memory counters | fastapi-limiter + Redis | Distributed safety and retry headers |

**Key insight:** Security and rate limits are reliability boundaries; existing libs handle edge cases (clock skew, token expiry, Redis atomicity) that are easy to miss.

## Common Pitfalls

### Pitfall 1: Token TTLs chosen late
**What goes wrong:** Clients bake in assumptions, and changing TTLs breaks auth flows.
**Why it happens:** TTLs are treated as implementation detail, not contract.
**How to avoid:** Decide access/refresh TTLs in planning and document them in the auth response.
**Warning signs:** Client errors around refresh or frequent re-auth prompts.

### Pitfall 2: Rate limiting keyed only by IP
**What goes wrong:** Shared IPs cause false throttling; abuse can bypass user quotas.
**Why it happens:** Default limiter identifier uses IP.
**How to avoid:** Use user account id for authenticated requests; IP for anonymous.
**Warning signs:** Legit users throttled or attackers bypassing limits.

### Pitfall 3: Market identifiers inconsistent across endpoints
**What goes wrong:** US/EGX vs MIC vs internal ids mismatch in client apps.
**Why it happens:** Identifiers are not defined centrally.
**How to avoid:** Decide one canonical market id and optionally include MIC as metadata.
**Warning signs:** API responses include multiple ids without clear precedence.

### Pitfall 4: Trending/most-active definitions drift
**What goes wrong:** Results fluctuate or are contested by users.
**Why it happens:** Window and definition are not fixed.
**How to avoid:** Encode definition (volume, 1 week) in docs and in response metadata.
**Warning signs:** Support tickets about “wrong” top lists.

## Code Examples

Verified patterns from official sources:

### JWT Bearer Token Flow (FastAPI)
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from datetime import datetime, timedelta, timezone
import jwt

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

### Rate Limiter Dependency (fastapi-limiter)
```python
# Source: https://github.com/long2ice/fastapi-limiter
@app.get("/symbols", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search_symbols():
    return []
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom auth logic | FastAPI security helpers + PyJWT | Current FastAPI docs | Less auth boilerplate and standard OAuth2 flow | 
| In-memory rate limit counters | Redis-backed limiter | Current FastAPI limiter libs | Safe across workers and deploys | 

**Deprecated/outdated:**
- Storing passwords with plain hashing: replaced by Argon2/Bcrypt via pwdlib/Passlib.

## Open Questions

1. **Access token TTL**
   - What we know: FastAPI example uses 15 minutes.
   - What's unclear: Required TTL for product UX and security.
   - Recommendation: Start with 15 minutes and document in auth response; adjust if UX requires.

2. **Refresh token TTL and storage**
   - What we know: Refresh tokens are required and should rotate.
   - What's unclear: TTL and storage layer (DB vs Redis).
   - Recommendation: Default to 30 days with rotation; store hashed refresh tokens in DB or Redis with TTL.

3. **Pagination style**
   - What we know: Discovery endpoints can return large lists.
   - What's unclear: Cursor vs offset.
   - Recommendation: Use limit/offset for simplicity in v1; include total + next_offset in response.

4. **Search result sorting**
   - What we know: Must support prefix+contains for ticker/company.
   - What's unclear: Default sort order for mixed matches.
   - Recommendation: Sort by match quality (prefix > contains) then by volume (if available).

5. **Trending definition**
   - What we know: Default window is 1 week; “most active” by volume.
   - What's unclear: Trending definition (price movers vs volume spike).
   - Recommendation: Define trending as top % price movers over 1 week unless data quality suggests volume spike.

## Sources

### Primary (HIGH confidence)
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ - JWT bearer auth and token creation example
- https://fastapi.tiangolo.com/tutorial/security/ - FastAPI security scheme overview
- https://github.com/long2ice/fastapi-limiter - Redis-backed rate limiting for FastAPI
- https://github.com/redis/redis-py - Official Redis Python client

### Secondary (MEDIUM confidence)
- https://python-jose.readthedocs.io/en/latest/ - JOSE/JWT library documentation (alternative to PyJWT)
- https://passlib.readthedocs.io/en/stable/ - Password hashing library documentation

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - FastAPI and limiter are well sourced, but version specifics are not pinned.
- Architecture: MEDIUM - Based on FastAPI guidance and common API structuring.
- Pitfalls: MEDIUM - Derived from standard API/security experience; not all are source-verified.

**Research date:** 2026-02-03
**Valid until:** 2026-03-05

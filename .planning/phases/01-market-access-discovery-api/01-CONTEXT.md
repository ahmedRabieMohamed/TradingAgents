# Phase 1: Market Access & Discovery API - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver authenticated API endpoints that let users select US or EGX, discover markets/symbols, search, filter, and retrieve top/trending lists with a standard error model.

</domain>

<decisions>
## Implementation Decisions

### Auth model & client onboarding
- Use JWT access tokens (Bearer auth) for v1.
- Use short-lived access tokens with refresh tokens.
- Rotate refresh tokens periodically.
- Rate limits/quotas keyed to user account id.
- Allow limited anonymous access to discovery endpoints with strict rate limits.

### Market registry & metadata
- `/markets` should return a detailed payload (beyond minimal fields).
- Market status should be enum + next session timestamps.

### Symbol search behavior
- Search uses prefix + contains matching for ticker and company name.
- Return market-specific symbol plus display name.

### Filters & top/trending definitions
- “Most active” is defined by volume.
- Default window for most active/trending is 1 week.

### Claude's Discretion
- Access token TTL.
- Refresh token TTL.
- Whether to require extra headers (e.g., client app id).
- Whether `/markets` includes delay/entitlement metadata by default.
- Market identifiers to expose (US/EGX vs MIC vs both).
- Search result sorting default.
- Pagination style (cursor vs offset).
- Filter set beyond sector/market cap/most active.
- Trending definition (top movers vs volume spike).

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-market-access-discovery-api*
*Context gathered: 2026-02-03*

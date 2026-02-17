# Phase 2: Market Access & Discovery API - Context

**Gathered:** 2026-02-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver authentication and discovery endpoints so users can select US/EGX, search symbols, and access market/symbol lists with a stable error model and rate-limit feedback.

</domain>

<decisions>
## Implementation Decisions

### Discovery request behavior
- Symbol search matches ticker and company name.
- List views include all roadmap filters/lists: sector, market cap, most active, and top/trending.
- Keep market parameter and pagination style minimal; choose simplest defaults during planning.

### Auth + token behavior
- Use JWT access tokens only; no refresh flow.
- Access token lifetime is long (24h).
- Tokens are sent via `Authorization: Bearer` header.
- Keep auth issuance minimal and avoid extra flows beyond what is required to get a token.

### Claude's Discretion
- Market parameter required vs optional default.
- Pagination style (page/size vs cursor).
- Client session policy (single vs multi-device).
- Expired/invalid token response detail (beyond standard error model).
- Token revocation support.
- Exact credential type for token issuance (API key vs user login vs client credentials), keeping it minimal.

</decisions>

<specifics>
## Specific Ideas

- "Make everything simple for now — minimum to work, no over-engineering."

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-market-access-discovery-api*
*Context gathered: 2026-02-16*

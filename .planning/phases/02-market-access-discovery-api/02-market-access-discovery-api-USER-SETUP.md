# Phase 02: User Setup Required

**Generated:** 2026-02-16
**Phase:** 02-market-access-discovery-api
**Status:** Incomplete

Complete these items for the integration to function. Claude automated everything possible; these items require human access to external dashboards/accounts.

## Environment Variables

| Status | Variable | Source | Add to |
|--------|----------|--------|--------|
| [ ] | `REDIS_URL` | Redis instance connection string | `.env.local` |
| [ ] | `EODHD_API_KEY` | EODHD Dashboard → API Keys | `.env.local` |

## Verification

After completing setup, verify with:

```bash
# Confirm Redis is reachable
redis-cli -u "$REDIS_URL" ping

# Confirm EODHD-backed markets are available
python - <<'PY'
from tradingagents.api.services import market_registry
print(market_registry.list_markets())
PY
```

Expected results:
- `PONG`
- Market entries include provider metadata when EODHD API key is set

---

**Once all items complete:** Mark status as "Complete" at top of file.

# Phase 5: User Setup Required

**Generated:** 2026-02-20
**Phase:** 05-async-analytics-reports
**Status:** Incomplete

Complete these items for the analytics report integrations to function. Claude automated everything possible; these items require human access to external dashboards/accounts.

## Environment Variables

| Status | Variable | Source | Add to |
|--------|----------|--------|--------|
| [ ] | `OPENAI_API_KEY` | OpenAI dashboard → API keys | `.env` |
| [ ] | `EODHD_API_KEY` | EODHD dashboard → API keys | `.env` |

## Account Setup

- [ ] **Create OpenAI account** (if needed)
  - URL: https://platform.openai.com/
  - Skip if: Already have an OpenAI account

- [ ] **Create EODHD account** (if needed)
  - URL: https://eodhd.com/
  - Skip if: Already have an EODHD account

## Verification

After completing setup, verify with:

```bash
python -c "import os; print('OPENAI_API_KEY set:', bool(os.getenv('OPENAI_API_KEY'))); print('EODHD_API_KEY set:', bool(os.getenv('EODHD_API_KEY')))"
```

Expected results:
- Both keys report `True`.

---

**Once all items complete:** Mark status as "Complete" at top of file.

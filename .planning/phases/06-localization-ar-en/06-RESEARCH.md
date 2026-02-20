# Phase 6: Localization (AR/EN) - Research

**Researched:** 2026-02-20
**Domain:** FastAPI response localization for analytics narratives and decision labels
**Confidence:** MEDIUM

## Summary

The current API is FastAPI-based, with analytics responses assembled in `tradingagents/api/services/analytics_reports.py` and response models defined in `tradingagents/api/schemas/analytics.py`. Narrative strings and labels are generated in English (e.g., `summary.summary`, `risk_notes`, `decision.rationale`, `decision.label`, and markdown section headings inside `final_report`). Phase 6 needs a language parameter on responses to return Arabic or English narratives, and localized decision labels. The cleanest approach for a POC is to keep English as the canonical payload internally and apply a localization pass at response time based on a `lang` query parameter.

FastAPI supports query parameters with defaults and type validation out of the box, so a `lang: str = Query("en")` or an Enum-backed query param can be used on endpoints that return narratives (notably `/analytics/report` POST + GET). A small translation dictionary for the deterministic strings is sufficient for this phase; agent-generated narrative sections may need translation only if required (open question). Localization should be centralized in a helper module and applied consistently to nested fields so labels, summaries, and markdown headings stay aligned.

**Primary recommendation:** Add a `lang` query parameter (default `en`) to analytics endpoints and localize narrative fields and decision labels via a centralized translation map applied at response time.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | >=0.110.0 | HTTP API framework | Existing API framework and built-in query parameter parsing | 
| Pydantic (v2) | via pydantic-settings | Response/request validation | Existing schemas and serialization in codebase |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (Built-in) dict/Enum | n/a | Language code validation and translation mapping | POC-friendly localization without extra deps |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Simple translation dict | gettext/Babel | More robust i18n but adds complexity and dependencies (not needed for POC) |

**Installation:**
```bash
pip install fastapi pydantic-settings
```

## Architecture Patterns

### Recommended Project Structure
```
tradingagents/api/
├── deps/                 # shared dependencies
├── routers/              # endpoints (add lang param here)
├── schemas/              # response models
├── services/
│   ├── analytics_reports.py  # generates narratives and labels
│   └── localization.py        # NEW: localization helpers
```

### Pattern 1: Response-time localization pass
**What:** Keep canonical English payloads and apply a translation pass right before returning JSON to the client, based on `lang` query param.
**When to use:** When storing results (jobs) in a single canonical language and supporting on-the-fly localization for responses.
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/query-params/
@router.get("/report/{report_id}")
async def get_report(report_id: str, lang: str = "en"):
    ...
```

### Pattern 2: Centralized translation map
**What:** Store all AR/EN strings in one module and expose helper functions like `localize_decision_label(label, lang)` and `localize_report_result(result, lang)`.
**When to use:** To avoid scattered string replacements and ensure consistent labels/phrases.

### Anti-Patterns to Avoid
- **Scattering translations in multiple files:** Causes inconsistent strings and missed fields.
- **Persisting localized results only:** Prevents future language additions and complicates caching; keep canonical English and localize at response time.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Query parameter parsing/validation | Custom parsing of `lang` | FastAPI query parameters / Enum validation | FastAPI already handles parsing, defaults, and validation |

**Key insight:** The app already uses FastAPI and Pydantic schemas; leverage their validation and keep localization as a thin layer at the response boundary.

## Common Pitfalls

### Pitfall 1: Partial localization
**What goes wrong:** Only `decision.label` is translated, but other narrative strings remain in English (e.g., `summary.summary`, `risk_notes`, markdown headings).
**Why it happens:** Localization logic is applied to a subset of fields.
**How to avoid:** Define a clear list of narrative fields and localize all of them in one helper.
**Warning signs:** Mixed-language output in the same response.

### Pitfall 2: Missing `lang` parameter on both POST and GET
**What goes wrong:** Report creation returns localized data, but fetching the same report later ignores the language.
**Why it happens:** Only one endpoint is updated.
**How to avoid:** Add `lang` to both `/analytics/report` POST and `/analytics/report/{report_id}` GET and apply the same localization.
**Warning signs:** Language changes between POST response and subsequent GET.

### Pitfall 3: Localizing stored job payloads
**What goes wrong:** Stored results become language-specific and no longer reusable for another language.
**Why it happens:** Localization occurs before persisting results in job storage.
**How to avoid:** Store canonical English data and translate at response time.
**Warning signs:** Job JSON differs by language or must be regenerated per locale.

## Code Examples

Verified patterns from official sources:

### Query parameter with default
```python
# Source: https://fastapi.tiangolo.com/tutorial/query-params/
@router.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-language responses (EN only) | Language parameter with response-time localization | Phase 6 | Supports AR/EN without duplicating stored results |

**Deprecated/outdated:**
- Hard-coding English-only narrative templates without localization hooks.

## Open Questions

1. **Should agent-generated report sections be translated?**
   - What we know: `final_report` includes LLM-produced sections and deterministic analytics markdown.
   - What's unclear: Whether Phase 6 must translate LLM output or only deterministic narratives.
   - Recommendation: Clarify scope; if required, add a translation step or constrain LLM output language.

## Sources

### Primary (HIGH confidence)
- https://fastapi.tiangolo.com/tutorial/query-params/ - Query parameter defaults and validation

### Secondary (MEDIUM confidence)
- Codebase review: `tradingagents/api/services/analytics_reports.py` and `tradingagents/api/schemas/analytics.py` for narrative fields and labels

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - FastAPI/Pydantic versions verified in `setup.py`/requirements
- Architecture: MEDIUM - Based on codebase patterns and FastAPI docs
- Pitfalls: MEDIUM - Derived from existing response composition and storage flow

**Research date:** 2026-02-20
**Valid until:** 2026-03-22

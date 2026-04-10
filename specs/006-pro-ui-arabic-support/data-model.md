# Data Model: 006 — Professional UI Redesign & Arabic/English Bilingual Support

**Date**: 2026-04-10

## Entity Changes

### Modified: AnalysisSession

Add `language` field to track the language used for each analysis.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `language` | string | `"en"` | Language code for the analysis reports (`"en"` or `"ar"`) |

**Constraints**:
- Must be one of: `"en"`, `"ar"`
- Immutable after analysis starts (language is locked when the analysis begins)
- Default `"en"` ensures backward compatibility with existing sessions

**Migration**: Add column with default `"en"` — all existing sessions remain English.

### New: Language Preference (Client-side only)

| Field | Type | Default | Storage |
|-------|------|---------|---------|
| `locale` | string | `"en"` | Browser localStorage |

**Constraints**:
- Must be one of: `"en"`, `"ar"`
- Persists across browser sessions
- Drives UI language + RTL direction + Ant Design locale + analysis request language

### New: Translation Catalog (Static files)

| Namespace | Scope | Estimated Keys |
|-----------|-------|----------------|
| `common` | Shared UI: nav labels, buttons, statuses, errors | ~60 |
| `analysis` | NewAnalysis page: wizard steps, agent names, config labels | ~40 |
| `dashboard` | Dashboard: card titles, metrics, empty states | ~25 |
| `history` | History: filters, table headers, compare modal | ~30 |
| `portfolio` | Portfolio: positions, trades, simulation labels | ~35 |
| `watchlist` | Watchlist: table headers, actions, empty state | ~15 |
| `performance` | Performance: cards, comparisons, metrics | ~20 |
| `settings` | Settings: labels, descriptions, toggles | ~15 |

**Total estimated translatable strings**: ~240

## Relationships

```
AnalysisSession
  └── language: str  ← set from user's locale at analysis start time
                        determines agent output language
                        preserved for historical viewing

User Locale (localStorage)
  ├── drives → UI language (i18n translations)
  ├── drives → layout direction (RTL/LTR)
  ├── drives → Ant Design locale (ar_EG / en_US)
  └── drives → analysis request language field
```

## State Transitions

```
Language Switch Flow:
  User clicks language toggle
  → localStorage updated
  → Zustand locale store updated
  → document.dir set to "rtl" or "ltr"
  → Ant Design ConfigProvider re-renders with new direction + locale
  → i18next language changed → all translated strings update
  → No page reload required

Analysis Language Flow:
  User starts analysis
  → Current locale read from store
  → language field included in POST /api/analysis request
  → Backend stores language on AnalysisSession
  → Agent system prompts include language instruction
  → Reports generated in specified language
  → Stored permanently with session
```

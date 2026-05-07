# Contract — Engine Reference (Frontend i18n)

**Feature**: Smart Picks Overhaul (`012-smart-picks-overhaul`)
**Audience**: Frontend developers and translators.
**Stability**: Public-internal — adding a new engine requires adding new keys; renaming or removing a key is a breaking change.

This contract defines the **only** location where engine education content lives. The backend never returns this text. Components that need to display "what is this engine" content read it via `react-i18next`.

---

## Storage

```text
frontend/src/locales/
├── en/engines.json
└── ar/engines.json
```

Both files are loaded by the existing i18n bootstrap in `frontend/src/i18n.ts`. They register under the namespace `engines` so consumers call `t('engines.rsi.label')`, etc.

---

## Per-engine key shape

For every engine name `<name>` (where `<name>` is the same string used as the key in the API's `engines` dict — `rsi`, `macd`, `volatility_regime`, `momentum`, …), both files MUST contain:

| Key | Type | Required | Length guideline | Example (English, RSI) |
|-----|------|----------|------------------|------------------------|
| `engines.<name>.label` | string | Yes | ≤ 24 chars | `"RSI"` |
| `engines.<name>.category` | string | Yes | ≤ 16 chars | `"Oscillator"` |
| `engines.<name>.measures` | string | Yes | 1 sentence | `"Whether the recent price moves leave the stock oversold or overbought."` |
| `engines.<name>.scoreRange` | string | Yes | 1–2 sentences | `"0–30: bullish (oversold). 70–100: bearish (overbought). 40–60: neutral."` |
| `engines.<name>.whyMatters` | string | Yes | 1–2 sentences | `"Identifies stretched moves that often snap back. Best paired with a trend signal."` |

### Plain-language rule

Per FR-014, all four text fields MUST be readable by a trader who is not a quantitative analyst. Concretely:

- No formulas, Greek letters, or bracket-and-subscript notation.
- No backend code identifiers (no `np.diff`, no `roc_5d`).
- No untranslated abbreviations except universally known ones (RSI, MACD, S/R, BB are okay as labels but should be expanded inside `measures` / `whyMatters` content).

---

## Locale parity (SC-010)

A CI / lint check (or, until that lands, a `quickstart.md` verification step) MUST verify:

```text
keys(en/engines.json.engines.<*>) == keys(ar/engines.json.engines.<*>)
```

i.e., **every engine that has an English entry has an Arabic entry, with the same five sub-keys**. Mismatch is a build-blocking error.

---

## Consumer rules

1. **Components MUST NOT hard-code engine descriptions.** Always go through `t('engines.<name>.<field>')`.
2. **Components MUST NOT call backend metadata endpoints for this content.** The backend does not expose any. (Decision recorded in `research.md` R6.)
3. **The popover trigger MUST handle missing keys gracefully** — if a future engine appears in API output without an i18n entry, the UI shows the engine's name with a "no description available" fallback, not a `engines.foo.measures`-style raw key.

---

## Adding a new engine

Steps required (enforced via the per-engine task list during `/speckit-tasks`):

1. Add the engine module to `backend/app/services/engines/<name>.py` and wire it into `__init__.py`.
2. Add `engines.<name>` block (5 keys) to `frontend/src/locales/en/engines.json`.
3. Add the same block, translated, to `frontend/src/locales/ar/engines.json`.
4. Confirm `t('engines.<name>.label')` resolves in both locales.

Skipping any of those steps is treated as an incomplete engine landing.

---

## Anti-rules (what this contract intentionally does NOT cover)

- It does not standardize **screenshots** or **example calculations**. Those belong in long-form docs (out of scope for v1).
- It does not standardize **theme-specific** content. The same string serves dark and light themes; theming happens in CSS, not in the i18n catalog.
- It does not enforce a maximum word count beyond the soft guidelines above. Brevity is encouraged, not policed mechanically.

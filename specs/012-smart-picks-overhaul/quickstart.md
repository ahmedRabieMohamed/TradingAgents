# Quickstart — Smart Picks Overhaul

**Feature**: Smart Picks Overhaul (`012-smart-picks-overhaul`)
**Date**: 2026-05-01

This document is the smallest path from "fresh checkout" to "I have walked through every acceptance scenario in `spec.md`". Use it during code review and after the branch lands.

---

## 1. Pull, install, run

```bash
git checkout 012-smart-picks-overhaul
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# Frontend (separate terminal)
cd ../frontend
npm install
npm run dev
```

Open http://localhost:5173/smart-picks.

---

## 2. Walk the acceptance scenarios

### Story 1 — Redesigned Smart Picks page (P1)

1. **Viewport fit (LTR)**: resize the browser to 1280×800. Confirm the rank, ticker, signal, and combined-score columns are visible without page-level horizontal scroll. The sidebar must still be visible. *(AC-1 / SC-001)*
2. **Viewport fit (RTL)**: switch language to Arabic in Settings. Repeat the 1280×800 check. Sidebar mirrors to the right; no horizontal page scroll. *(AC-2 / SC-001)*
3. **Feature parity**: open the expand-row on each pick and click any pick to open the detail drawer. Confirm every metric that was visible on the pre-redesign page is reachable somewhere — table column, expand-row, or drawer. *(AC-3 / SC-002)*

### Story 2 — Per-engine education inline (P1)

1. Hover any engine score chip in an expand-row. A popover appears within 200 ms with: what it measures, score-range meaning, and why it matters. *(AC-1)*
2. Click "Learn more" inside the popover. The detail drawer opens at the engine's section. *(AC-2)*
3. Switch to Arabic and repeat steps 1–2. Popover content is in Arabic. *(AC-3 / SC-010)*
4. **10-second test**: ask someone unfamiliar with the engines "what does Engine X do and why does it matter?". They answer correctly within 10 seconds without leaving the page. *(SC-003)*

### Story 3 — New engines appear (P2)

1. Open any pick's detail drawer. The engines list MUST include `RSI`, `MACD`, and `Volatility Regime` in addition to the existing 7. *(AC-1 / SC-004)*
2. Find a ticker with RSI in the 0–30 band (e.g., search history for an "oversold" tagged stock). Confirm the RSI engine score is high (≥ 70) with an "oversold" rationale. *(AC-2)*
3. Find a ticker with a recent bullish moving-average crossover. Confirm the MACD engine score is bullish (≥ 60) with a "bullish crossover" rationale. *(AC-3)*
4. Pick a ticker with elevated recent vol (any large-cap during a known turbulent week). Confirm `volatility_regime_tag` is `elevated` or `extreme`, visible as a top-of-row badge. *(AC-4)*

### Story 4 — Integration into combined score (P2)

1. Pick a ticker; record `combined_score`, `combined_score_raw`, and `volatility_regime_tag` from the detail drawer.
2. If `regime_tag` is `calm` or `normal`, `combined_score == combined_score_raw`. Confirm. *(AC-1)*
3. If `regime_tag` is `extreme`, `combined_score` is **closer to 50** than `combined_score_raw` is. Confirm `sign(combined_score - 50) == sign(combined_score_raw - 50)` — the dampener never inverts. *(AC-2 / FR-008)*
4. Expand the engine list in the detail drawer. Each engine displays a `weight %` summing to 100% across the engines that contributed. Engines marked "insufficient data" show 0%. *(AC-3 / FR-010)*

### Story 5 — Drill-down transparency (P3)

1. Click a pick row → drawer opens. Every engine listed with score, weight, signal, and one-line rationale. *(AC-1)*
2. Close the drawer. Page returns to the previous filter/sort state. *(AC-2)*

---

## 3. Edge-case sweep

- **Insufficient history**: pick a recently-IPO'd stock (< 26 bars). RSI/MACD show "insufficient data" badges; combined score still computes from the engines that did fire. Pick is NOT dropped.
- **No-invert proof**: open backend tests and run `pytest backend/tests/services/engines/test_combined_score.py::test_dampening_never_inverts -v`. Test asserts: for `raw_score ∈ {10, 20, 30, 40, 60, 70, 80, 90}` and every regime tag, `sign(adjusted - 50) == sign(raw - 50)`.
- **Determinism (FR-013 / SC-009)**:
  ```bash
  curl -s "http://localhost:8000/api/engines/score/COMI?market=egypt" > /tmp/run1.json
  curl -s "http://localhost:8000/api/engines/score/COMI?market=egypt" > /tmp/run2.json
  diff /tmp/run1.json /tmp/run2.json   # must be empty
  ```
- **Locale parity (SC-010)**:
  ```bash
  python3 - <<'PY'
  import json, sys
  en = json.load(open('frontend/src/locales/en/engines.json'))['engines']
  ar = json.load(open('frontend/src/locales/ar/engines.json'))['engines']
  missing = set(en) ^ set(ar)
  if missing:
      sys.exit(f"i18n parity violation: {missing}")
  for name in en:
      if set(en[name]) != set(ar[name]):
          sys.exit(f"sub-key parity violation in {name}: {set(en[name]) ^ set(ar[name])}")
  print("OK")
  PY
  ```
- **Engine outage (FR-009 / SC-007)**: temporarily raise an exception inside `services/engines/momentum.py:compute`. Refresh Smart Picks. Picks still render; momentum cell shows an error indicator; combined score recomputes from remaining engines.
- **Long lists**: refresh with `limit=100`. Page first-meaningful-render no slower than baseline. *(SC-008)*
- **Conflicting engines**: find a ticker where one engine reads STRONG BUY and another reads STRONG SELL. Combined score lands closer to NEUTRAL than either, and the detail drawer makes the disagreement visible.

---

## 4. Performance budgets

| Budget | Source | How to verify |
|--------|--------|----------------|
| Smart Picks first-meaningful-render ≤ baseline | SC-008 | DevTools Performance, A/B against `main` branch |
| Engine pipeline ≤ baseline + 10% | Plan Performance Goals | Backend log timestamps for `_compute_smart_picks` |
| Determinism: 0 differences across runs | SC-009 | The diff script in §3 |
| Locale parity: 0 missing keys | SC-010 | The Python script in §3 |
| Score reweight calibration: 90%+ tickers within ±10 of pre-branch score | SC-005 | Run pipeline on `main`, save scores; run on this branch, diff per-ticker; tabulate |

If any budget fails, file a P1 issue against this branch — do not merge until resolved.

---

## 5. Pre-merge checklist

- [ ] Lint clean (`cd backend && ruff check .` exits 0; `cd frontend && npx eslint src/pages/SmartPicks.tsx src/components/smart-picks/` exits 0)
- [ ] Frontend typechecks (`cd frontend && npx tsc --noEmit` exits 0)
- [ ] Frontend builds (`cd frontend && npm run build` succeeds)
- [ ] Backend engine tests pass (`pytest backend/tests/services/engines/`)
- [ ] Manual walkthrough of stories 1–5 passes
- [ ] No regression on the rest of the app (Dashboard, Portfolio, History, Watchlist, Performance still render correctly)
- [ ] CHANGELOG entry under the next minor version

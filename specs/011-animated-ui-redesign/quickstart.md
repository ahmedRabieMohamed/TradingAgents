# Quickstart — Animated UI Redesign

**Feature**: Animated & Motion-Driven Frontend UI (`011-animated-ui-redesign`)
**Date**: 2026-04-30

This document is the smallest path from "fresh checkout" to "I have walked through every acceptance scenario". Use it during code review and after the redesign lands.

---

## 1. Pull the branch and install

```bash
git checkout 011-animated-ui-redesign
cd frontend
npm install        # picks up the new `motion` dependency
```

## 2. Run backend + frontend

In two terminals:

```bash
# Terminal A — backend (unchanged for this feature)
cd backend
uvicorn app.main:app --reload --port 8000
```

```bash
# Terminal B — frontend
cd frontend
npm run dev
```

Open http://localhost:5173.

## 3. Walk the acceptance scenarios

### Story 1 — Animated first impression (P1)

1. **Dashboard load** → primary panels animate into place within ~600 ms; finishes fully usable. *(AC-1)*
2. **Navigate**: Dashboard → New Analysis → Portfolio → Watchlist → Smart Picks → Performance → History → Settings. Each transition plays a continuous fade/slide; no flash. *(AC-2)*
3. **Feature parity**: at each page, confirm every existing control, table, chart, and data point is present and unchanged. *(AC-3 / SC-001)*

### Story 2 — Motion as feedback (P2)

1. Click any primary button → press response within 100 ms. *(AC-1)*
2. Add a stock to the watchlist → row animates in. Remove it → row animates out. *(AC-2)*
3. Start an analysis → animated progress / shimmer indicator appears for the duration of the run. *(AC-3)*
4. Trigger a price update on a position you hold → value flashes (and counts up if reduced motion is off). *(AC-4)*

### Story 3 — Animated charts (P2)

1. Open the candlestick view (New Analysis) → container fades and scales subtly into view. *(AC-1)*
2. Open Performance / Equity Curve → Recharts series draw in over the chart-enter duration. *(AC-1)*
3. Trigger a data refresh (e.g., re-run analysis) → charts ease between states rather than jumping. *(AC-2)*

### Story 4 — Accessibility & performance (P1)

1. **Reduced motion ON**: macOS → System Settings → Accessibility → Display → Reduce motion. Reload the app.
   - Decorative entrances are suppressed (≤ 150 ms fades). *(AC-1 / SC-006)*
   - Value updates still flash by color; count-up is suppressed.
   - Skeleton loaders render but no shimmer.
2. While any animation is mid-flight, click a button or type → input is accepted immediately. *(AC-2)*
3. Open DevTools → Performance and record a Dashboard load + a navigation. Frame rate stays ≥ 55 fps. *(AC-3 / SC-005)*

### Story 5 — RTL / Arabic (P3)

1. Switch language to Arabic in Settings.
2. Repeat the Story 1 walkthrough.
3. Confirm directional slides mirror — entrances come from the start of the line in RTL, not from the LTR-side. *(SC-009)*

## 4. Edge-case spot checks

- **Rapid navigation**: click sidebar entries faster than 400 ms apart — no orphan half-faded panels remain.
- **Long lists**: scroll a watchlist with 100+ items — only newly added/removed items animate; scroll feels native.
- **Modal stack**: open a modal that itself opens a second modal (e.g., compare from history) — page underneath does not re-animate.
- **Theme switch**: toggle dark/light from Settings — pages do not replay their entrance animations.

## 5. Regression check

```bash
cd frontend
npm run lint
npm run build      # tsc --noEmit + vite build, must succeed with no new errors
```

Manual: page-by-page parity against `main`. Any feature that worked on `main` MUST work here (FR-001 / SC-001).

## 6. Performance budgets reference

| Budget | Source | How to verify |
|--------|--------|----------------|
| Dashboard FMP ≤ 1.5 s | SC-002 | DevTools → Performance / Lighthouse |
| Page transition ≤ 400 ms | SC-003 | DevTools → Performance, measure transition span |
| Entrance ≤ 800 ms | SC-003 | DevTools timeline |
| Press feedback within 100 ms | SC-004 | Visual inspection |
| Sustained ≥ 55 fps | SC-005 | DevTools Performance, FPS meter |
| Reduced-motion ≤ 150 ms | SC-006 | Enable OS reduce-motion, record DevTools timeline |

If any budget is violated, file a P1 issue against this branch — do not merge until resolved.

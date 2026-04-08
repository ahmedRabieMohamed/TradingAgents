# Implementation Plan: Markdown Rendering & Premium UI Polish

**Branch**: `005-ui-polish-markdown` | **Date**: 2026-04-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-ui-polish-markdown/spec.md`

## Summary

Fix raw markdown display in analysis reports by adding react-markdown
rendering, and polish the entire UI to premium quality with consistent
shadows, hover states, typography, skeleton loading, and refined spacing.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend only)
**Primary Dependencies**: React 18, react-markdown (new), remark-gfm (new)
**Storage**: N/A — no backend changes
**Testing**: Manual verification per quickstart.md
**Target Platform**: Web browser (desktop)
**Project Type**: Frontend SPA polish
**Constraints**: Must use existing dark theme color palette and inline
style patterns. No CSS framework (Tailwind, etc.).

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | PASS | react-markdown is one dependency solving a real problem (raw markdown). UI polish modifies existing styles, no new abstractions. |
| II. Correctness Over Speed | PASS | Markdown must render correctly for all report content. |
| III. Separation of Concerns | PASS | Frontend-only changes. Markdown styles in globals.css, not inline. |
| IV. Incremental Delivery | PASS | US1 (markdown) works independently of US2 (polish). |
| V. Data Integrity | PASS | No data changes. |

## Project Structure

### Source Code Changes

```text
frontend/
├── src/
│   ├── styles/
│   │   └── globals.css              # MODIFY: add markdown styles, shadows,
│   │                                #   hover utilities, skeleton class
│   ├── components/
│   │   └── analysis/
│   │       └── ReportSection.tsx     # MODIFY: use react-markdown instead
│   │                                #   of raw <pre> tag
│   ├── pages/
│   │   ├── Dashboard.tsx            # MODIFY: polish cards, hover states,
│   │   │                            #   skeleton loading
│   │   ├── History.tsx              # MODIFY: hover states on rows
│   │   ├── Portfolio.tsx            # MODIFY: card polish
│   │   ├── Watchlist.tsx            # MODIFY: hover states
│   │   ├── NewAnalysis.tsx          # MODIFY: step indicator polish
│   │   └── Performance.tsx          # MODIFY: card polish
│   └── components/
│       ├── layout/
│       │   ├── Sidebar.tsx          # MODIFY: hover polish
│       │   └── Topbar.tsx           # MODIFY: subtle refinements
│       ├── portfolio/
│       │   └── TradeModal.tsx       # MODIFY: modal shadow
│       └── history/
│           └── CompareModal.tsx     # MODIFY: modal shadow
```

## Complexity Tracking

No constitution violations to justify. react-markdown + remark-gfm are
the only new dependencies — both solve a real, current problem.

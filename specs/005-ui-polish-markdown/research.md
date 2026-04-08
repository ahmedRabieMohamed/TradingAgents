# Research: Markdown Rendering & Premium UI Polish

**Feature**: 005-ui-polish-markdown
**Date**: 2026-04-08

## R1: Markdown Rendering Library

**Decision**: Use `react-markdown` with `remark-gfm` plugin.

**Rationale**: react-markdown is the standard React markdown renderer —
renders markdown as React components (not innerHTML), supports GFM
tables/strikethrough, and allows custom component overrides for styling.
~30KB gzipped. remark-gfm adds GitHub-flavored markdown support (tables,
task lists, strikethrough) which the analysis reports use heavily.

**Alternatives considered**:
- `marked` + `dangerouslySetInnerHTML`: Rejected — XSS risk, not React-
  idiomatic, harder to style individual elements.
- `mdx`: Rejected — overkill, designed for JSX-in-markdown authoring.
- Custom regex parsing: Rejected — fragile, can't handle nested markdown.

---

## R2: Markdown Styling Approach

**Decision**: Add a `.markdown-body` CSS class in globals.css with dark
theme styles for all markdown elements (h1-h6, strong, em, ul/ol, table,
code, blockquote, hr). Override react-markdown components for tables to
add proper borders and padding.

**Rationale**: A single CSS class keeps styles centralized and consistent.
react-markdown's `components` prop allows overriding specific elements
(e.g., table → styled table component) without global CSS pollution.

---

## R3: Card Depth & Shadow System

**Decision**: Add a `--shadow-sm` and `--shadow-md` CSS variable to the
design system. Apply `--shadow-sm` to cards and panels, `--shadow-md` to
modals and elevated elements.

**Values**:
- `--shadow-sm`: `0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)`
- `--shadow-md`: `0 4px 12px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)`

**Rationale**: Subtle shadows on dark backgrounds need higher opacity
than light themes. Two levels cover all use cases without over-complicating.

---

## R4: Hover & Interaction States

**Decision**: Add global CSS hover rules for table rows and cards.
Use `transition: all 0.15s ease` as the standard timing.

**Patterns**:
- Table rows: `background: rgba(59,130,246,0.04)` on hover
- Buttons: slight brightness increase on hover, scale(0.98) on active
- Cards with actions: border color shifts to accent on hover

---

## R5: Skeleton Loading

**Decision**: Extend the existing `@keyframes pulse` pattern with a
`.skeleton` utility class. Replace spinners with skeleton blocks on
Dashboard, History, Portfolio, and Watchlist pages where table data loads.

**Rationale**: Skeleton loading feels faster and more polished than
a centered spinner. The pulse animation already exists in globals.css.

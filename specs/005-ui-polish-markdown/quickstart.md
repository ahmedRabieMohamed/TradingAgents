# Quickstart: Markdown Rendering & Premium UI Polish

## Prerequisites

- Frontend running: `cd frontend && npm run dev`
- react-markdown installed: `cd frontend && npm install react-markdown remark-gfm`

## Verify Markdown Rendering (User Story 1)

1. Open the app, run an analysis on any ticker (or load a past one from History)
2. On the results page, expand any agent report (Market Analysis, News, etc.)
3. **Expected**: Headings are larger and bold, `**bold**` text is bold,
   bullet lists have proper bullets, tables have borders and aligned columns
4. **NOT expected**: Raw `###`, `**`, `|---|`, or other markdown syntax visible
5. Check a report with a data table — columns should be aligned with borders
6. Check a report with nested lists — indentation should be visible

## Verify UI Polish (User Story 2)

### Cards & Depth
1. Go to Dashboard — stat cards should have subtle shadow/depth
2. Go to Portfolio — position cards and summary should feel elevated

### Hover States
1. On Dashboard, hover over a recent analysis row — should highlight
2. On History page, hover over any analysis row — should highlight
3. On Watchlist, hover over a ticker row — should highlight
4. Hover over any button — should show slight visual feedback

### Typography & Spacing
1. Navigate through all pages — page titles should be consistent size
2. Section headers should be smaller than page titles but larger than body
3. Secondary text (dates, labels) should be visually muted
4. Spacing between sections should be uniform

### Loading States
1. Refresh the Dashboard — should see skeleton blocks, not just a spinner
2. Navigate to History — table should have skeleton rows while loading

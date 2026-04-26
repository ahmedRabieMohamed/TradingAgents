# Feature Specification: Markdown Rendering & Premium UI Polish

**Feature Branch**: `005-ui-polish-markdown`
**Created**: 2026-04-08
**Status**: Draft
**Input**: User description: "Analysis reports show raw markdown (###, **, etc.) instead of formatted text. The overall UI/UX is not polished enough for a paid product — needs premium quality look and feel."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Properly Rendered Analysis Reports (Priority: P1)

As a trader, I want the AI-generated analysis reports to display with proper formatting (headings, bold text, bullet lists, tables, etc.) so I can easily read and understand the detailed analysis without seeing raw markdown syntax.

**Why this priority**: This is the most visible broken experience. The reports are the core value of the product — they must be readable. Currently, users see raw `###`, `**`, `---` symbols throughout, making reports hard to parse visually.

**Independent Test**: Run an analysis on any ticker, open a report section, and verify all markdown elements render as formatted text — headings are larger, bold text is bold, lists have bullets, tables have grid lines.

**Acceptance Scenarios**:

1. **Given** an analysis is complete with detailed reports, **When** I expand any agent report (Market Analysis, News, etc.), **Then** I see properly formatted text: headings are visually distinct, bold/italic text is styled, bullet lists have proper indentation, and tables render with borders and alignment.
2. **Given** a report contains nested markdown (headers, sub-headers, lists within lists), **When** I view it, **Then** all nesting levels are visually clear and correctly rendered.
3. **Given** a report contains a data table (e.g., price data, indicator values), **When** I view it, **Then** the table renders with proper columns, rows, borders, and alignment — not as pipe-separated raw text.
4. **Given** I view a report on a mobile-width screen, **When** the content has tables or long lines, **Then** the content wraps or scrolls horizontally without breaking the layout.

---

### User Story 2 - Premium UI Polish (Priority: P1)

As a user evaluating this product, I want the interface to feel professional and polished — with consistent spacing, visual hierarchy, smooth interactions, and attention to detail — so it feels worth paying for.

**Why this priority**: First impressions determine willingness to pay. The current UI is functional but feels like a prototype: inconsistent spacing, flat cards, minimal visual hierarchy, and no micro-interactions.

**Independent Test**: Navigate through all pages (Dashboard, Analysis, History, Watchlist, Portfolio, Settings) and verify each page has consistent card styling, clear visual hierarchy, hover states on interactive elements, and professional typography.

**Acceptance Scenarios**:

1. **Given** I land on the Dashboard, **When** I scan the page, **Then** the stats cards have subtle shadows or depth, the layout feels balanced, and the visual hierarchy guides my eye (most important data is most prominent).
2. **Given** I hover over any clickable row in a table (recent analyses, positions, watchlist), **When** my cursor enters the row, **Then** I see a subtle highlight indicating it is interactive.
3. **Given** I navigate between pages, **When** content loads, **Then** transitions feel smooth — loading states have skeleton placeholders rather than just a spinner, and content appears without layout jumps.
4. **Given** I view any page, **When** I look at the overall layout, **Then** spacing is consistent (same padding, margins, gaps), typography has clear hierarchy (page title > section title > body > secondary text), and colors are used consistently (green = positive, red = negative, accent = actions).
5. **Given** I use the analysis wizard, **When** I progress through steps, **Then** the step indicator, buttons, and cards feel premium — not flat and basic.

---

### Edge Cases

- Reports containing code blocks or inline code should render with a monospace font on a slightly different background.
- Reports with very long content should not cause performance issues during rendering.
- Markdown rendering should handle malformed or partial markdown gracefully (no crash, best-effort rendering).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render markdown content in analysis reports as formatted HTML — headings, bold, italic, lists, tables, code blocks, and horizontal rules MUST all display correctly.
- **FR-002**: Rendered markdown MUST inherit the application's dark theme — text colors, background, and link colors MUST be consistent with the existing design system.
- **FR-003**: Tables in rendered markdown MUST have visible borders, header styling, and proper cell padding.
- **FR-004**: All interactive elements (table rows, buttons, cards) MUST have hover states that indicate interactivity.
- **FR-005**: Cards and panels MUST have subtle visual depth (shadow, border treatment, or gradient) to create visual hierarchy.
- **FR-006**: Spacing MUST be consistent across all pages — same padding scale, margin scale, and gap values.
- **FR-007**: Typography MUST follow a clear hierarchy — page titles, section headings, body text, and secondary text MUST each have distinct and consistent sizing and weight.
- **FR-008**: Loading states MUST use skeleton placeholders where possible, not just spinners.
- **FR-009**: Color usage MUST be consistent — green for positive/gains, red for negative/losses, accent blue for primary actions, muted for secondary elements.

### Key Entities

- **Rendered Report**: Markdown content converted to styled HTML, displayed within collapsible report sections.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of markdown elements in reports (headings, bold, italic, lists, tables, code) render as formatted HTML — zero raw markdown syntax visible.
- **SC-002**: All interactive elements across all pages have visible hover states.
- **SC-003**: Users can read a full analysis report (including tables and nested lists) without encountering raw markdown characters.
- **SC-004**: Visual consistency audit: spacing, typography, and color usage is uniform across all pages.
- **SC-005**: A new user landing on the Dashboard perceives the product as professional and premium within 5 seconds of viewing.

## Assumptions

- A lightweight markdown-to-HTML rendering approach is preferred — no need for full GitHub-flavored markdown (e.g., no need for task checkboxes, emoji shortcodes, or footnotes). Basic markdown (headings, bold, italic, lists, tables, code, links, horizontal rules) is sufficient.
- The dark theme is the only theme — no light mode support needed.
- UI polish focuses on the existing pages and components, not adding new pages or features.
- Performance of markdown rendering should be acceptable for reports up to 50KB of content per section.
- No changes to the backend are needed — this is purely a frontend rendering and styling effort.

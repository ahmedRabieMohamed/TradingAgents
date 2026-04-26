# Feature Specification: Professional UI Redesign & Arabic/English Bilingual Support

**Feature Branch**: `006-pro-ui-arabic-support`  
**Created**: 2026-04-10  
**Status**: Draft  
**Input**: User description: "Current UI is very basic, I want to use Ant Design for UI/UX that makes this look professional as a trading agent. Support Arabic — agents we use should support either Arabic or English, and the web interface as well."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Professional Trading Interface (Priority: P1)

A trader opens the application and sees a polished, professional trading interface that inspires confidence. The layout uses a professional design system with consistent spacing, typography, icons, and color palette. Navigation is clear, data is well-organized in tables and cards, and interactive elements (buttons, inputs, dropdowns, modals) follow a unified design language. The overall look matches the quality of professional trading platforms like Bloomberg Terminal or TradingView.

**Why this priority**: The current custom CSS approach produces an inconsistent, basic-looking interface. Adopting a mature design system is the highest-impact change — it transforms every page at once and establishes the foundation for all other UI work.

**Independent Test**: Can be fully tested by navigating through all 7 pages (Dashboard, Analysis, History, Performance, Watchlist, Portfolio, Settings) and verifying each uses consistent, professional-grade components (tables, cards, buttons, forms, modals, charts).

**Acceptance Scenarios**:

1. **Given** a user opens the app, **When** they view any page, **Then** all UI elements use a consistent design system with uniform typography, spacing, colors, and component styles.
2. **Given** a user navigates between pages, **When** they interact with tables, forms, buttons, and modals, **Then** every interactive element follows the same design language with proper hover/focus/active states.
3. **Given** a user views the sidebar and top bar, **When** the app loads, **Then** the navigation looks polished with proper icons, active-state indicators, and smooth transitions.
4. **Given** a user is on the Dashboard, **When** data cards, charts, and summary sections render, **Then** they display in well-structured layouts with proper visual hierarchy (headings, subtext, dividers, shadows).

---

### User Story 2 - Arabic Language Web Interface (Priority: P1)

An Arabic-speaking trader switches the application language to Arabic. All static UI text — navigation labels, button text, page titles, form labels, placeholders, status messages, and tooltips — displays in Arabic. The entire layout flips to right-to-left (RTL) orientation: the sidebar moves to the right, text aligns right, and directional icons mirror. The trader can switch back to English at any time, and the layout returns to left-to-right (LTR).

**Why this priority**: Equal to P1 because the target user base includes Arabic speakers on the Egyptian Exchange (EGX). Without Arabic support, a significant portion of users cannot effectively use the product.

**Independent Test**: Can be tested by switching language to Arabic and verifying all navigation items, buttons, labels, and page content display in Arabic with correct RTL layout. Then switch back to English and verify LTR layout restores.

**Acceptance Scenarios**:

1. **Given** a user is on any page in English, **When** they select Arabic from the language switcher, **Then** all UI text changes to Arabic and the layout switches to RTL.
2. **Given** the app is in Arabic mode, **When** the user views the sidebar, **Then** it appears on the right side of the screen with Arabic labels and right-aligned text.
3. **Given** the app is in Arabic mode, **When** the user interacts with forms (ticker input, configuration panels), **Then** all labels, placeholders, and validation messages display in Arabic.
4. **Given** the app is in Arabic mode, **When** the user switches back to English, **Then** all text reverts to English and layout returns to LTR immediately without page reload.
5. **Given** a user selects a language, **When** they close and reopen the app, **Then** their language preference is persisted.

---

### User Story 3 - Arabic AI Agent Reports (Priority: P2)

A trader runs an analysis and the AI agents produce their reports. If the trader's language is set to Arabic, the AI agents generate their analysis reports, recommendations, and summaries in Arabic. If set to English, reports are in English. The report content — including financial terminology, stock symbols, and numerical data — renders correctly in the selected language with appropriate text direction.

**Why this priority**: While the UI translation (P1) is a frontend-only effort, making AI agents respond in Arabic requires backend coordination. It's critical for the full Arabic experience but can follow after the UI is localized.

**Independent Test**: Can be tested by setting language to Arabic, running a stock analysis, and verifying the returned agent reports (market analyst, fundamentals, sentiment, risk, recommendation) are in Arabic with correct RTL rendering. Stock tickers and numbers should remain in their standard format.

**Acceptance Scenarios**:

1. **Given** the app is set to Arabic, **When** a user starts a new analysis, **Then** the AI agents produce reports in Arabic.
2. **Given** an Arabic report is displayed, **When** the user views it, **Then** financial terms, headings, and body text are in Arabic while stock tickers (e.g., "JUFO") and numbers remain in standard Latin format.
3. **Given** the app is set to English, **When** a user starts a new analysis, **Then** agents produce reports in English as they do today.
4. **Given** a past analysis was run in Arabic, **When** the user views it from History in English mode, **Then** the report displays in the original Arabic it was generated in.

---

### User Story 4 - Responsive Professional Layout (Priority: P2)

A trader accesses the app from different screen sizes (desktop wide monitor, laptop, tablet). The professional layout adapts gracefully — the sidebar collapses on smaller screens, tables become scrollable, cards stack vertically, and the interface remains usable down to tablet size (768px width).

**Why this priority**: A professional trading app must handle various screen sizes. While not mobile-first (traders primarily use desktops), laptop and tablet support rounds out the professional feel.

**Independent Test**: Can be tested by resizing the browser window from 1920px to 768px and verifying the layout adapts at each breakpoint without broken elements or horizontal overflow.

**Acceptance Scenarios**:

1. **Given** a user on a wide screen (1920px+), **When** they view any page, **Then** the layout uses full width with sidebar expanded and multi-column layouts.
2. **Given** a user on a laptop (1024px-1440px), **When** they view the app, **Then** content adjusts proportionally and remains fully usable.
3. **Given** a user on a tablet-sized screen (768px-1024px), **When** they view the app, **Then** the sidebar collapses to icons or a hamburger menu, and content uses single-column layout where needed.

---

### Edge Cases

- What happens when Arabic text is mixed with English content (e.g., stock ticker names inside Arabic sentences)? The system must handle bidirectional text correctly without breaking layout.
- What happens when an AI agent report contains markdown tables with Arabic text? Tables must render with correct RTL alignment while keeping numeric columns readable.
- What happens when the user switches language mid-analysis (while agents are streaming)? The current analysis continues in the original language; the language switch applies to the UI immediately but only affects new analyses.
- What happens when stored historical analyses are viewed in a different language than they were created in? Reports display in their original language; only the surrounding UI (labels, buttons) changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST replace the current custom CSS with a professional design system across all 7 pages and all shared components (sidebar, topbar, modals, tables, forms, cards, buttons).
- **FR-002**: System MUST provide a language switcher accessible from every page (e.g., in the topbar or settings) that allows toggling between English and Arabic.
- **FR-003**: System MUST support full right-to-left (RTL) layout when Arabic is selected, including mirrored sidebar position, text alignment, icon direction, and component layout.
- **FR-004**: System MUST translate all static UI text (navigation labels, button text, page titles, form labels, placeholders, status messages, empty states, error messages) into Arabic.
- **FR-005**: System MUST persist the user's language preference locally so it survives browser refresh and app reopening.
- **FR-006**: System MUST pass the user's selected language to the AI analysis pipeline so agents generate reports in the chosen language.
- **FR-007**: System MUST render Arabic markdown reports correctly with RTL text direction, including mixed-direction content (Arabic text with English stock tickers and numbers).
- **FR-008**: System MUST maintain all existing functionality — analysis workflow, history, portfolio, watchlist, dashboard, performance — without regression after the UI redesign.
- **FR-009**: System MUST handle bidirectional text (BiDi) correctly when Arabic and English content appear together (e.g., "تحليل سهم JUFO").
- **FR-010**: System MUST apply the professional design system consistently in both LTR (English) and RTL (Arabic) modes.

### Key Entities

- **Language Preference**: The user's chosen display language (English or Arabic), stored locally and sent with analysis requests.
- **Translation Catalog**: A mapping of all UI text strings to their Arabic translations, organized by page/component.
- **Agent Language Directive**: The language instruction passed to AI agents when initiating an analysis, determining the output language of reports.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of pages and shared components use the professional design system with zero instances of unstyled or inconsistent elements.
- **SC-002**: Users can switch between English and Arabic in under 2 seconds with the layout fully adapting (RTL/LTR) without page reload.
- **SC-003**: 100% of static UI text strings have Arabic translations — no English text leaks through when Arabic is selected.
- **SC-004**: AI agent reports render in Arabic when the user's language is set to Arabic, with correct RTL text rendering for at least 95% of report content.
- **SC-005**: All existing features (analysis, history, portfolio, watchlist, dashboard, performance, settings) pass manual smoke testing after the redesign with zero functional regressions.
- **SC-006**: The application layout adapts gracefully to screen widths from 768px to 2560px without horizontal overflow or broken elements.
- **SC-007**: Language preference persists across browser sessions — selecting Arabic, closing, and reopening the app still shows Arabic.

## Assumptions

- The primary users are traders on the Egyptian Exchange (EGX) who are bilingual (Arabic/English), so both languages are equally important.
- Mobile phone support (below 768px) is out of scope for this iteration; tablet is the minimum target.
- The AI agents (powered by LLMs) can generate reports in Arabic when instructed — no additional translation service is needed.
- Stock tickers, numerical values, and chart labels remain in English/Latin characters regardless of language selection, as this is standard practice in Arabic financial applications.
- The existing dark theme color palette will be preserved and adapted to work with the new design system.
- The current 7-page structure and routing remain unchanged; this is a visual and localization overhaul, not a feature restructure.
- Historical analyses stored in English will not be retroactively translated; they display in the language they were generated in.

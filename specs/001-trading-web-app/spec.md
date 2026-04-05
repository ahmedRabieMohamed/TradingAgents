# Feature Specification: Trading Web Application

**Feature Branch**: `001-trading-web-app`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: "I want to have an app that deals like helping me to be better in trade, also mirror what we have in the CLI flow, have a way to choose between markets (EGX, US) and stocks for every one of them, simulate the result of analysing tracker...etc"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Market & Stock Selection (Priority: P1)

As a trader, I want to select a market (US or Egypt/EGX) and then pick a stock from that market so I can begin analysis on the specific investment I'm interested in.

**Why this priority**: This is the foundational interaction — without market and stock selection, no other feature can function. It mirrors the first two steps of the existing CLI flow and gates all downstream analysis.

**Independent Test**: Can be fully tested by opening the app, selecting a market, entering a ticker symbol, and confirming the app recognizes it. Delivers value by showing the user that their chosen market context is active and the stock is valid.

**Acceptance Scenarios**:

1. **Given** I open the app for the first time, **When** I am presented with the market selection screen, **Then** I see options for US Market (NYSE/NASDAQ) and Egypt Market (EGX) with clear labels and descriptions.
2. **Given** I have selected the Egypt Market, **When** I enter a ticker symbol (e.g., COMI), **Then** the app validates the ticker and displays the stock name and basic info.
3. **Given** I have selected the US Market, **When** I enter a ticker symbol (e.g., AAPL), **Then** the app validates the ticker and displays the stock name and basic info.
4. **Given** I enter an invalid ticker, **When** the app attempts to validate it, **Then** I see a clear error message suggesting I check the symbol and try again.

---

### User Story 2 - Configure & Run Analysis (Priority: P1)

As a trader, I want to configure my analysis parameters (trade horizon, analyst team, research depth, and LLM provider) and launch a full stock analysis so I can receive an AI-driven trading recommendation.

**Why this priority**: This is the core value proposition — running the multi-agent analysis pipeline through a visual interface rather than the CLI. Without this, the app has no analytical function.

**Independent Test**: Can be tested by selecting a stock, configuring analysis options, running the analysis, and receiving a final trading recommendation (BUY/SELL/HOLD with confidence). Delivers value as a complete end-to-end analysis workflow.

**Acceptance Scenarios**:

1. **Given** I have selected a valid stock, **When** I access the analysis configuration screen, **Then** I see options for trade horizon (intraday, short-term, medium-term, long-term), analyst team selection (Market, Social Media, News, Fundamentals), research depth (Shallow, Medium, Deep), and LLM provider/model selection.
2. **Given** I have configured all analysis parameters, **When** I start the analysis, **Then** the app displays a real-time progress view showing which agents are currently working, their status, and elapsed time.
3. **Given** the analysis is running, **When** each agent completes its phase (analysts, researchers, trader, risk team, portfolio manager), **Then** I see live updates reflecting the current stage of the pipeline.
4. **Given** the analysis completes successfully, **When** I view the results, **Then** I see the final recommendation (BUY/SELL/HOLD) with a confidence percentage, along with summaries from each analysis phase.

---

### User Story 3 - View Detailed Analysis Reports (Priority: P2)

As a trader, I want to drill down into the individual reports from each analysis phase so I can understand the reasoning behind the recommendation and make a more informed decision.

**Why this priority**: Transparency in the recommendation builds user trust and helps traders learn. However, the summary recommendation (P1) already delivers standalone value.

**Independent Test**: Can be tested by completing an analysis and navigating to each section's detailed report (market analysis, news analysis, fundamentals, bull/bear debate, risk assessment). Delivers value by providing educational insight into the AI reasoning.

**Acceptance Scenarios**:

1. **Given** an analysis has completed, **When** I navigate to the detailed reports section, **Then** I see individual reports organized by analysis phase: Market Analysis, Social Media Sentiment, News Analysis, Fundamentals Analysis, Bull/Bear Research Debate, Trader Recommendation, Risk Assessment, and Portfolio Decision.
2. **Given** I am viewing the Bull/Bear Research Debate, **When** I expand the section, **Then** I see each round of debate with the bullish and bearish arguments clearly labeled and the research manager's synthesis.
3. **Given** I am viewing the Risk Assessment, **When** I expand the section, **Then** I see the aggressive, neutral, and conservative perspectives and the risk manager's final assessment.

---

### User Story 4 - Analysis History & Comparison (Priority: P2)

As a trader, I want to view my past analyses and compare recommendations over time so I can track patterns and improve my trading decisions.

**Why this priority**: History and comparison are key to the "helping me be better at trading" goal. They enable learning from past decisions, but the core analysis flow must work first.

**Independent Test**: Can be tested by running multiple analyses and then viewing the history list, filtering by market or stock, and comparing two analyses side by side. Delivers value by revealing trends in recommendations.

**Acceptance Scenarios**:

1. **Given** I have completed at least two analyses, **When** I navigate to the history screen, **Then** I see a chronological list of all past analyses with stock ticker, date, market, recommendation, and confidence level.
2. **Given** I am on the history screen, **When** I filter by market (US or EGX), **Then** the list shows only analyses for that market.
3. **Given** I select two past analyses, **When** I choose to compare them, **Then** I see a side-by-side view highlighting differences in analyst reports, recommendations, and confidence levels.

---

### User Story 5 - Result Simulation & Performance Tracking (Priority: P3)

As a trader, I want the app to simulate and track the outcome of past recommendations against actual market performance so I can evaluate the accuracy of the AI analysis over time.

**Why this priority**: This closes the feedback loop — critical for long-term user value and the "helping me be better at trade" goal. Depends on history (P2) and analysis (P1) being functional first.

**Independent Test**: Can be tested by viewing a past analysis and seeing the simulated outcome (what would have happened if the recommendation was followed), including actual price movement and profit/loss calculation. Delivers value by quantifying AI accuracy.

**Acceptance Scenarios**:

1. **Given** a past analysis recommended BUY for a stock at a specific date, **When** I view the simulation for that analysis, **Then** the app shows the actual price movement from the analysis date to the end of the trade horizon period, and calculates the simulated profit/loss.
2. **Given** I have multiple tracked analyses, **When** I view the overall performance dashboard, **Then** I see aggregate statistics: total analyses, win rate, average return, and performance by market.
3. **Given** a simulation shows a loss, **When** I view the details, **Then** the app highlights which analyst signals were correct versus incorrect to help me understand what went wrong.

---

### Edge Cases

- What happens when the user's internet connection drops during an analysis run? The app should save partial progress and allow resumption or show a clear error with the option to retry.
- How does the system handle a stock that was delisted between the analysis date and current date? The app should display a notice that the stock is no longer traded and show last available data.
- What happens when the selected LLM provider's API key is missing or invalid? The app should detect this before starting analysis and prompt the user to configure their API key.
- How does the app handle tickers that exist in both markets? The market context (US or EGX) selected by the user determines which exchange is queried.
- What happens when market data is unavailable for the selected analysis date (e.g., weekends, holidays)? The app should inform the user and suggest the nearest valid trading day.
- How does the system handle very long-running analyses (deep research with many debate rounds)? The app should show estimated remaining time and allow the user to cancel gracefully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to select between US Market (NYSE/NASDAQ) and Egypt Market (EGX) as their analysis context.
- **FR-002**: System MUST allow users to enter and validate stock ticker symbols appropriate to the selected market.
- **FR-003**: System MUST display relevant stock information (name, current price, market) after ticker validation.
- **FR-004**: System MUST allow users to configure trade horizon: intraday, short-term, medium-term, or long-term.
- **FR-005**: System MUST allow users to select which analysts to include in the analysis (Market, Social Media, News, Fundamentals) with at least one required.
- **FR-006**: System MUST allow users to choose research depth (Shallow: 1 round, Medium: 3 rounds, Deep: 5 rounds).
- **FR-007**: System MUST allow users to select an LLM provider and corresponding models for both quick-thinking and deep-thinking tasks.
- **FR-008**: System MUST execute the full multi-agent analysis pipeline (Analysts, Researchers, Trader, Risk Team, Portfolio Manager) and display real-time progress.
- **FR-009**: System MUST display the final trading recommendation with a confidence percentage (e.g., "BUY 85%").
- **FR-010**: System MUST display detailed reports from each analysis phase, organized by stage.
- **FR-011**: System MUST persist analysis results so users can review past analyses.
- **FR-012**: System MUST allow users to filter analysis history by market, stock, or date range.
- **FR-013**: System MUST simulate the outcome of past recommendations by comparing the recommendation against actual subsequent market performance.
- **FR-014**: System MUST display aggregate performance statistics (win rate, average return, total analyses).
- **FR-015**: System MUST handle Egypt-specific market conventions (Sunday-Thursday trading week, .CA ticker suffix, EGP currency display).
- **FR-016**: System MUST provide clear error messages when API keys are missing, tickers are invalid, or market data is unavailable.
- **FR-017**: System MUST allow users to save or export analysis reports.
- **FR-018**: System MUST mirror all configuration options available in the existing CLI flow (market, ticker, horizon, analysts, depth, LLM provider, model selection).

### Key Entities

- **Market**: A supported exchange (US or EGX), including its trading days, currency, ticker conventions, and available news sources.
- **Stock**: A tradeable security identified by ticker symbol within a specific market, with associated price data and fundamentals.
- **Analysis Session**: A single execution of the multi-agent pipeline for a specific stock, date, and configuration. Contains all agent reports and the final recommendation.
- **Analysis Configuration**: The set of parameters chosen by the user: market, ticker, trade horizon, analyst team, research depth, LLM provider/models.
- **Agent Report**: An individual output from one stage of the analysis pipeline (e.g., Market Analysis report, Bull Researcher argument, Risk Manager assessment).
- **Recommendation**: The final trading decision (BUY/SELL/HOLD) with a confidence percentage, produced by the portfolio manager.
- **Simulation Result**: The comparison of a past recommendation against actual market performance, including price movement and calculated returns over the trade horizon.
- **Performance Tracker**: Aggregate view of all simulation results, showing overall accuracy and returns across multiple analyses.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can go from opening the app to launching an analysis in under 2 minutes (market selection through configuration).
- **SC-002**: 90% of users can complete their first analysis without external documentation or help.
- **SC-003**: Analysis progress updates appear in real-time, with status refreshing at least once every 10 seconds during an active run.
- **SC-004**: Users can access any past analysis report within 3 clicks from the main screen.
- **SC-005**: The app supports at least 2 markets (US and EGX) with market-appropriate stock validation and conventions.
- **SC-006**: Result simulation shows actual vs. predicted outcomes with market data no more than 1 day stale.
- **SC-007**: The app mirrors 100% of the CLI flow's configuration options (market, ticker, horizon, analysts, depth, LLM provider/model).
- **SC-008**: Users report improved confidence in trading decisions after using the app for 2+ weeks (measured via optional feedback).
- **SC-009**: All analysis phases (analyst reports, debate summaries, risk assessment) are viewable within the app without needing to export.

## Assumptions

- Users have existing API keys for their chosen LLM provider (the app does not manage provider subscriptions).
- The existing analysis backend (multi-agent pipeline) will be reused as the analysis engine — the web app is a frontend layer over the existing system.
- Market data is available through the existing data vendors already integrated in the project.
- Users have a stable internet connection for LLM calls and market data retrieval.
- The app targets desktop/laptop browsers as the primary platform; mobile-responsive design is a secondary concern for the initial version.
- Users are individual traders, not teams — no multi-user collaboration or shared accounts are needed for the initial version.
- Authentication is not required for the initial version (single-user local or personal deployment).
- The Egypt market news sources already configured in the project will be reused.
- The existing LLM provider integrations (OpenAI, Anthropic, Google, xAI, OpenRouter, Ollama) will be reused without modification.

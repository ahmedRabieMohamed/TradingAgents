# Feature Specification: Paper Trading & Portfolio Simulation

**Feature Branch**: `003-paper-trading-simulation`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: User description: "I want to work on the simulation part — also I want to see if I did an action based on analysis"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute Virtual Trade from Analysis (Priority: P1)

As a trader, after receiving an AI analysis recommendation (BUY/SELL/HOLD), I want to "execute" that trade with virtual money so I can track whether following the AI's advice would have been profitable.

**Why this priority**: This is the core ask — connecting analysis recommendations to actionable virtual trades. Without this, the analysis results are informational only with no way to measure their real-world value.

**Independent Test**: Complete an analysis → see BUY recommendation → click "Execute Trade" → confirm position size → see the trade recorded with entry price. Delivers value as a single trade-tracking action.

**Acceptance Scenarios**:

1. **Given** an analysis has completed with a BUY recommendation, **When** I click "Execute Trade" on the results screen, **Then** I see a trade execution form with the recommended action (BUY), current price as entry price, and a field to specify position size (shares or amount).
2. **Given** I am executing a virtual trade, **When** I confirm the trade, **Then** the system records the trade with: ticker, market, direction (BUY/SELL), entry price, quantity, entry date, and links it to the originating analysis session.
3. **Given** the analysis recommends HOLD, **When** I view the results, **Then** the "Execute Trade" option is dimmed/disabled with a note "No action recommended."
4. **Given** I already have an open position in the same stock, **When** I execute a new BUY on it, **Then** the system asks whether to add to the existing position or open a new one.

---

### User Story 2 - Portfolio Dashboard (Priority: P1)

As a trader, I want a portfolio dashboard showing all my virtual positions, their current P&L, and my overall portfolio value so I can see at a glance how well I'm doing following the AI's recommendations.

**Why this priority**: Without a portfolio view, individual trades have no context. The dashboard is the primary place users will check to evaluate their AI-guided trading performance.

**Independent Test**: Execute 2-3 virtual trades → navigate to Portfolio → see all positions with live P&L, total portfolio value, and cash balance.

**Acceptance Scenarios**:

1. **Given** I have executed virtual trades, **When** I navigate to the Portfolio page, **Then** I see a summary bar showing: starting balance, current portfolio value, total P&L (amount and percentage), cash remaining, and number of open positions.
2. **Given** I have open positions, **When** I view the positions table, **Then** each row shows: ticker, market, direction, quantity, entry price, current price, unrealized P&L (amount and %), days held, and the linked analysis recommendation.
3. **Given** a position is profitable, **When** I view it, **Then** the P&L is displayed in green. If losing, it's displayed in red.
4. **Given** I have no positions yet, **When** I visit the Portfolio page, **Then** I see an empty state with my starting balance and a prompt to run an analysis and execute a trade.

---

### User Story 3 - Close Position & Realize P&L (Priority: P1)

As a trader, I want to close a virtual position to lock in the profit or loss, so I can track my realized returns over time.

**Why this priority**: Opening positions without closing them makes the simulation incomplete. Closing positions is essential for tracking actual performance.

**Independent Test**: Have an open position → click "Close Position" → confirm at current price → see realized P&L added to history and cash balance updated.

**Acceptance Scenarios**:

1. **Given** I have an open position, **When** I click "Close Position" on that row, **Then** I see a confirmation showing the exit price (current market price), realized P&L, and return percentage.
2. **Given** I confirm closing a position, **When** the close is executed, **Then** the position moves from "Open" to "Closed," the realized P&L is added to my trade history, and my cash balance is updated accordingly.
3. **Given** I have closed positions, **When** I view the trade history section of the portfolio, **Then** I see a chronological list of all closed trades with: ticker, direction, entry/exit prices, realized P&L, return %, hold duration, and the AI recommendation that triggered it.

---

### User Story 4 - Portfolio Performance Analytics (Priority: P2)

As a trader, I want to see performance analytics for my paper trading — win rate, average return, best/worst trades, and performance over time — so I can evaluate how well the AI recommendations work for my trading style.

**Why this priority**: Analytics turn raw trade data into actionable insights. They are the "helping me be better at trade" goal. But they require trade history (P1 stories) to exist first.

**Independent Test**: Have 5+ closed trades → view Performance Analytics → see win rate, avg return, equity curve, best/worst trade, performance by market.

**Acceptance Scenarios**:

1. **Given** I have at least 5 closed trades, **When** I view the performance analytics section, **Then** I see: total trades, win rate, average return per trade, total realized P&L, and Sharpe-like ratio (return consistency).
2. **Given** I have trades across both US and EGX markets, **When** I view the analytics, **Then** I see a breakdown by market showing which market my AI-guided trading performs better in.
3. **Given** I have trades over multiple weeks, **When** I view the equity curve, **Then** I see a chart showing my portfolio value over time from the starting balance.
4. **Given** I want to know my best and worst trades, **When** I view the analytics, **Then** I see the top 3 winners and top 3 losers with their details.

---

### User Story 5 - "What If I Followed the AI" Backtest View (Priority: P3)

As a trader, I want to see a comparison of "what happened when I followed the AI" vs "what happened when I didn't" so I can understand the value of the AI recommendations.

**Why this priority**: This is the highest-level insight — quantifying the AI's value. It depends on having a substantial trade history and is more of an advanced analytics feature.

**Independent Test**: Have some analyses where you executed the trade and some where you didn't → view the comparison → see the difference in outcomes.

**Acceptance Scenarios**:

1. **Given** I have analyses where I executed the recommended trade AND analyses where I did not, **When** I view the backtest comparison, **Then** I see two columns: "Followed AI" (trades I executed) vs "Ignored AI" (analyses I didn't act on, with simulated outcomes).
2. **Given** the comparison is displayed, **When** I look at the metrics, **Then** I see: average return for followed recommendations, average return for ignored recommendations, and the difference.
3. **Given** I view a specific ignored analysis, **When** I see its simulated outcome, **Then** I see what would have happened if I had followed the recommendation (entry at analysis price, exit at horizon end).

---

### Edge Cases

- What happens when the user tries to execute a trade but has insufficient virtual cash? Show an error with current balance and suggest reducing position size.
- How does the system handle a stock that gets delisted while the user has an open position? Mark the position as "Frozen" with last known price and prompt the user to close it manually.
- What happens when the user has open positions in both markets? Each position tracks its own currency (USD or EGP) — the portfolio summary converts to a single display currency based on the user's default market setting.
- How does the system handle partial closes (selling half a position)? For simplicity in v1, only full position closes are supported.
- What is the starting virtual balance? Default to $100,000 USD or 1,000,000 EGP, configurable in settings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to execute a virtual trade (BUY or SELL) directly from an analysis results screen, linked to the originating analysis session.
- **FR-002**: System MUST record each virtual trade with: ticker, market, direction, quantity, entry price, entry date, linked analysis session ID, and status (open/closed).
- **FR-003**: System MUST display a portfolio dashboard showing: starting balance, current value, total P&L, cash remaining, and all open positions with live unrealized P&L.
- **FR-004**: System MUST allow users to close an open position at current market price, recording the exit price, exit date, and realized P&L.
- **FR-005**: System MUST maintain a virtual cash balance that decreases when buying and increases when selling/closing.
- **FR-006**: System MUST display a trade history of all closed positions with entry/exit details, P&L, hold duration, and linked analysis recommendation.
- **FR-007**: System MUST display portfolio performance analytics: total trades, win rate, average return, total realized P&L, and breakdown by market.
- **FR-008**: System MUST display an equity curve showing portfolio value over time.
- **FR-009**: System MUST show a "Followed AI vs Ignored AI" comparison for analyses where the user acted vs didn't act.
- **FR-010**: System MUST prevent trades that exceed available virtual cash balance.
- **FR-011**: System MUST link each trade to its originating AI analysis, allowing users to see the recommendation context for any position.
- **FR-012**: System MUST handle both USD (US market) and EGP (Egypt market) positions within the same portfolio.
- **FR-013**: System MUST allow users to configure their starting virtual balance in settings.
- **FR-014**: System MUST allow users to reset their portfolio (clear all positions and trade history, restart with fresh balance).

### Key Entities

- **Portfolio**: The user's virtual trading account with a cash balance and starting balance. Single portfolio per user.
- **Position**: An open virtual trade — ticker, market, direction (long/short), quantity, entry price, entry date, linked analysis session. Becomes a closed trade when exited.
- **Trade**: A completed round-trip trade (position opened then closed) — includes entry and exit details, realized P&L, hold duration, and the AI recommendation that triggered it.
- **Trade Execution**: The act of opening or closing a position — captures the price, timestamp, and action taken.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can execute a virtual trade from an analysis result in under 30 seconds (2 clicks: Execute → Confirm).
- **SC-002**: Portfolio dashboard shows current P&L updated with market prices no more than 15 minutes stale.
- **SC-003**: Users can close any position in 2 clicks and see realized P&L immediately.
- **SC-004**: 90% of users can understand their portfolio performance within 30 seconds of viewing the analytics.
- **SC-005**: The "Followed AI vs Ignored AI" comparison clearly shows the difference in outcomes with a single metric.
- **SC-006**: Portfolio balance accurately reflects all trades — no discrepancies between cash + positions and total value.
- **SC-007**: All trades link back to their originating analysis, viewable in 1 click.

## Assumptions

- This is paper trading only — no real money, no broker integration, no actual market orders.
- Starting balance defaults to $100,000 (configurable). EGP positions are tracked in EGP but converted to USD for the portfolio total using a fixed or daily exchange rate.
- Position sizing is in shares (whole numbers), not fractional shares.
- Only full position closes are supported in v1 (no partial sells).
- Market prices for P&L calculation use the same yfinance data already available in the app (15-minute delay acceptable).
- The portfolio is single-user — no shared or team portfolios.
- Short selling (SELL without owning) is supported for when the AI recommends SELL — the position profits when the price drops.
- This feature depends on the existing analysis system (001-trading-web-app) being fully functional.

# Research: 010 — 7 Trading Engines + Smart Picks + Danger Alerts

**Date**: 2026-04-25

## R1: Engine Implementation Approach

**Decision**: Pure functions with numpy — no engine framework or class hierarchy.

**Rationale**: Each engine is a simple function: `compute_X(prices: np.ndarray, volumes: np.ndarray) -> EngineResult`. No shared state, no inheritance, no plugins. The constitution demands simplicity — 7 small functions are simpler than 1 abstract Engine class with 7 subclasses.

**Alternatives considered**:
- Abstract base class `Engine` with `.compute()` method — rejected (unnecessary abstraction for 7 functions that share nothing)
- Strategy pattern — rejected (overengineering for static function set)

## R2: Monte Carlo Model

**Decision**: Geometric Brownian Motion (GBM) with historical drift and volatility.

**Rationale**: GBM is the standard model used in quantitative finance for simulating stock price paths. It's mathematically sound, well-understood, and requires only two parameters (μ, σ) estimated from historical returns. 10,000 simulations with 7-day horizon takes <1 second with numpy vectorization.

**Implementation**:
```python
returns = np.diff(prices) / prices[:-1]
mu, sigma = returns.mean(), returns.std()
random_returns = np.random.normal(mu, sigma, (10000, days))
price_paths = current_price * np.cumprod(1 + random_returns, axis=1)
final_prices = price_paths[:, -1]
prob_up = (final_prices > current_price).mean()
```

**Alternatives considered**:
- GARCH model (time-varying volatility) — more accurate but complex to implement, marginal improvement for 7-day horizon
- Bootstrap resampling (resample actual historical returns instead of assuming normal) — good alternative, could add later as option

## R3: News Sentiment Scoring

**Decision**: Use existing LLM (OpenAI/Claude) to score news articles on a -100 to +100 scale via a simple prompt.

**Rationale**: No need for a separate NLP model. The existing LLM infrastructure can score sentiment with a single API call: "Rate the sentiment of this news headline for stock X on a scale of -100 (very bearish) to +100 (very bullish). Return only the number."

**Cost**: ~$0.001 per article (using quick_think_model). 10 articles = $0.01. Negligible.

**Alternative**: Rule-based keyword scoring (positive/negative word lists) — faster but much less accurate for financial context, especially Arabic.

## R4: Stock Discovery (News-Driven vs Full Scan)

**Decision**: News mentions + EGX top movers. No full 228-stock scan.

**Rationale**: As discussed with user — scanning 228 stocks is expensive and slow. Instead:
1. Fetch news → extract ticker mentions → 5-15 stocks
2. Fetch EGX top movers (gainers/losers/volume) → 10-20 stocks
3. Union + dedup → ~15-25 unique candidates
4. Run 7 engines only on these → fast and cheap

**Data sources for top movers**: yfinance can batch-download last-day data for all EGX30 tickers quickly. Or scrape EGX website top movers page.

## R5: Score Persistence

**Decision**: Store engine scores as a JSON column on AnalysisSession.

**Rationale**: Engine scores are computed alongside analysis and should be viewable when revisiting past analyses. A JSON column (`engine_scores`) on the existing AnalysisSession table is the simplest approach — no new table, backward-compatible (NULL for old sessions).

**Alternative**: Separate EngineScore table with foreign key to AnalysisSession — more normalized but adds complexity for read/write. JSON column is sufficient since we never query by individual engine scores.

## R6: Frontend Charting for Engines

**Decision**: Reuse Recharts (already installed) for histograms and bar charts. CSS gauges for score bars.

**Rationale**: Recharts handles bar charts (volume, MC histogram) well. Score gauge bars are simple CSS divs with percentage widths — no library needed. Support/Resistance chart is a simple SVG. No new charting dependency needed.

## R7: Combined Score Formula

**Decision**: Fixed weights — MC 40% + News 30% + Technical Average 30%.

**Rationale**: Monte Carlo gets the highest weight because it's the most statistically grounded. News gets 30% because catalysts drive short-term moves. The remaining 6 technical engines share 30% (5% each, averaged). This is a reasonable starting point that can be tuned later based on backtest results.

When an engine returns N/A, its weight is redistributed proportionally among available engines.

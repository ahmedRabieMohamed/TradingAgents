"""Monte Carlo simulation engine — GBM model with 10K paths."""

import numpy as np


def compute(prices: np.ndarray, days: int = 7, simulations: int = 10000) -> dict:
    """Run Monte Carlo simulation using Geometric Brownian Motion.

    Args:
        prices: Array of historical closing prices (oldest first).
        days: Simulation horizon in trading days.
        simulations: Number of simulation paths.

    Returns:
        Dict with score (0-100), verdict, prob_up, expected_change,
        best_case (95th pct), worst_case (5th pct).
    """
    if len(prices) < 30:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Insufficient data (<30 days)"}

    # Calculate daily log returns
    returns = np.diff(prices) / prices[:-1]
    mu = returns.mean()
    sigma = returns.std()

    if sigma == 0:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Zero volatility"}

    current_price = prices[-1]

    # Simulate paths using vectorized GBM
    random_returns = np.random.normal(mu, sigma, (simulations, days))
    price_paths = current_price * np.cumprod(1 + random_returns, axis=1)
    final_prices = price_paths[:, -1]

    # Statistics
    prob_up = float((final_prices > current_price).mean() * 100)
    expected_change = float(((final_prices.mean() / current_price) - 1) * 100)
    best_case = float(((np.percentile(final_prices, 95) / current_price) - 1) * 100)
    worst_case = float(((np.percentile(final_prices, 5) / current_price) - 1) * 100)

    # Score: map prob_up (0-100%) to score (0-100)
    score = max(0, min(100, int(prob_up)))

    # Verdict
    if prob_up >= 60:
        verdict = "BULLISH"
    elif prob_up <= 40:
        verdict = "BEARISH"
    else:
        verdict = "NEUTRAL"

    return {
        "score": score,
        "verdict": verdict,
        "prob_up": round(prob_up, 1),
        "expected_change": round(expected_change, 2),
        "best_case": round(best_case, 2),
        "worst_case": round(worst_case, 2),
    }

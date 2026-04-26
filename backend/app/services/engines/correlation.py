"""Correlation engine — sector peer confirmation."""

import numpy as np


# Sector groupings from EGX ticker database (top tickers per sector)
SECTOR_PEERS: dict[str, list[str]] = {
    "Banking": ["COMI", "HDBK", "ADIB", "CIEB", "QNBE", "FAIT", "SAUD", "EGBE", "SAIB", "EXPA"],
    "Real Estate": ["TMGH", "PHDC", "EMFD", "OCDI", "ORHD", "MASR", "HELI", "MNHD"],
    "Chemicals": ["ABUK", "MFPC", "SKPC", "EGCH", "FERC", "MICH", "KZPC"],
    "Financial Services": ["HRHO", "EFIH", "BTFH", "CCAP", "BINV", "CICH", "CNFN", "EFIC"],
    "Consumer": ["EAST", "JUFO", "ORWE", "EFID", "DOMT", "SUGR", "POUL", "OLFI"],
    "Telecom": ["ETEL", "EGSA", "RAYA"],
    "Industrials": ["SWDY", "EGAL", "IRON", "ELEC", "LCSW", "ALUM"],
    "Pharma": ["ISPH", "PHAR", "MIPH", "CPCI", "OCPH", "RMDA", "NIPH"],
    "Energy": ["AMOC", "MOIL", "EGAS"],
    "Construction": ["ORAS", "ARCC", "NCCW"],
    "Healthcare": ["CLHO", "CCAP", "AMES", "SPMD"],
    "Fintech": ["FWRY", "EFIH", "VALU"],
    "Cement": ["MCQE", "MBSC", "SCEM", "SVCE"],
    "Steel": ["IRON", "ESRS", "ATQA"],
    "Tourism": ["MHOT", "SPHT", "ROTO", "SDTI"],
    "Education": ["CIRA", "TALM", "MOED"],
}


def _find_sector(ticker: str) -> tuple[str, list[str]]:
    """Find the sector and peer list for a ticker."""
    clean = ticker.upper().replace(".CA", "")
    for sector, tickers in SECTOR_PEERS.items():
        if clean in tickers:
            peers = [t for t in tickers if t != clean]
            return sector, peers
    return "Unknown", []


def compute(prices: np.ndarray, ticker: str, peer_changes: dict[str, float] | None = None) -> dict:
    """Check if sector peers confirm the stock's movement.

    Args:
        prices: Array of historical closing prices for the target ticker.
        ticker: The ticker symbol.
        peer_changes: Optional dict of {peer_ticker: 5d_change_pct}.
                      If not provided, returns sector info only.

    Returns:
        Dict with score (0-100), verdict, sector, peers_bullish, peers_total.
    """
    sector, peers = _find_sector(ticker)

    if not peers:
        return {"score": 50, "verdict": "NEUTRAL", "sector": sector, "error": "No sector peers found"}

    if len(prices) < 6:
        return {"score": 50, "verdict": "NEUTRAL", "sector": sector, "error": "Insufficient data"}

    # Target stock's 5-day change
    target_change = ((prices[-1] / prices[-6]) - 1) * 100 if len(prices) >= 6 else 0
    target_bullish = target_change > 0

    if peer_changes is None:
        # No peer data provided — can only return sector info
        return {
            "score": 50,
            "verdict": "NEUTRAL",
            "sector": sector,
            "peers": peers[:5],
            "target_change_5d": round(float(target_change), 2),
            "error": "No peer data available",
        }

    # Count how many peers are moving in the same direction
    peers_bullish = 0
    peers_total = 0

    for peer in peers:
        if peer in peer_changes:
            peers_total += 1
            if peer_changes[peer] > 0:
                peers_bullish += 1

    if peers_total == 0:
        return {"score": 50, "verdict": "NEUTRAL", "sector": sector, "error": "No peer data"}

    # Sector agreement ratio
    bullish_ratio = peers_bullish / peers_total

    # Score based on agreement with target direction
    if target_bullish:
        # We're bullish — high peer agreement = confirmation
        score = int(30 + bullish_ratio * 70)
    else:
        # We're bearish — low peer bullish = confirmation of bearishness
        score = int(30 + (1 - bullish_ratio) * 70)

    score = max(0, min(100, score))

    if bullish_ratio > 0.6:
        verdict = "BULLISH"
    elif bullish_ratio < 0.4:
        verdict = "BEARISH"
    else:
        verdict = "NEUTRAL"

    return {
        "score": score,
        "verdict": verdict,
        "sector": sector,
        "peers_bullish": peers_bullish,
        "peers_total": peers_total,
        "bullish_ratio": round(bullish_ratio, 2),
        "target_change_5d": round(float(target_change), 2),
    }

from copy import deepcopy
from typing import Dict, Optional

import tradingagents.default_config as default_config

# Use default config but allow it to be overridden
_config: Optional[Dict] = None


def initialize_config():
    """Initialize the configuration with default values."""
    global _config
    if _config is None:
        _config = deepcopy(default_config.DEFAULT_CONFIG)


def set_config(config: Dict):
    """Update the configuration with custom values.

    Dict-valued keys (e.g. ``data_vendors``) are merged one level deep so a
    partial update like ``{"data_vendors": {"core_stock_apis": "alpha_vantage"}}``
    keeps the other nested keys from the default; scalar keys are replaced.
    """
    global _config
    initialize_config()
    incoming = deepcopy(config)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(_config.get(key), dict):
            _config[key].update(value)
        else:
            _config[key] = value


def get_config() -> Dict:
    """Get the current configuration."""
    if _config is None:
        initialize_config()
    return deepcopy(_config)


def get_market_region() -> Dict:
    """Get the market region configuration for the current region."""
    config = get_config()
    region_name = config.get("market_region", "us")
    regions = default_config.MARKET_REGIONS
    if region_name not in regions:
        raise ValueError(
            f"Unknown market region '{region_name}'. "
            f"Available regions: {list(regions.keys())}"
        )
    return regions[region_name]


def get_trade_horizon() -> Dict:
    """Get the trade horizon configuration for the current horizon."""
    config = get_config()
    horizon_name = config.get("trade_horizon", "short-term")
    horizons = default_config.TRADE_HORIZONS
    if horizon_name not in horizons:
        raise ValueError(
            f"Unknown trade horizon '{horizon_name}'. "
            f"Available horizons: {list(horizons.keys())}"
        )
    return horizons[horizon_name]


def get_ticker_with_suffix(symbol: str) -> str:
    """Apply the market region's ticker suffix if needed."""
    region = get_market_region()
    suffix = region.get("ticker_suffix", "")
    if suffix and not symbol.upper().endswith(suffix):
        return symbol.upper() + suffix
    return symbol.upper()


# Initialize with default config
initialize_config()

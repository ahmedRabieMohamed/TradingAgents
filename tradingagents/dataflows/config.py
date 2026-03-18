import tradingagents.default_config as default_config
from typing import Dict, Optional

# Use default config but allow it to be overridden
_config: Optional[Dict] = None


def initialize_config():
    """Initialize the configuration with default values."""
    global _config
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()


def set_config(config: Dict):
    """Update the configuration with custom values."""
    global _config
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    _config.update(config)


def get_config() -> Dict:
    """Get the current configuration."""
    if _config is None:
        initialize_config()
    return _config.copy()


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


def get_ticker_with_suffix(symbol: str) -> str:
    """Apply the market region's ticker suffix if needed."""
    region = get_market_region()
    suffix = region.get("ticker_suffix", "")
    if suffix and not symbol.upper().endswith(suffix):
        return symbol.upper() + suffix
    return symbol.upper()


# Initialize with default config
initialize_config()

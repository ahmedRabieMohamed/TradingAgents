from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# DEFAULT_CONFIG already applies TRADINGAGENTS_* env-var overrides
# (llm_provider, deep_think_llm, quick_think_llm, backend_url, etc.),
# so users can switch models or endpoints purely via .env without
# editing this script. Override individual keys here only when you
# want a hard-coded value that should ignore the environment.
config = DEFAULT_CONFIG.copy()

# Market region: "us" (default) or "egypt"
# For Egypt: tickers like COMI, HRHO, TMGH, EFIH, SWDY
# The .CA suffix for yfinance is applied automatically
config["market_region"] = "us"

# Trade horizon: "intraday", "short-term", "medium-term", "long-term"
# "intraday" = 1-4 hours, focuses on momentum and catalysts
# Output now includes confidence: e.g., "BUY 85%"
config["trade_horizon"] = "short-term"

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate (US market example)
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Egypt market example:
# config["market_region"] = "egypt"
# ta_egypt = TradingAgentsGraph(debug=True, config=config)
# _, decision = ta_egypt.propagate("COMI", "2024-05-10")  # Commercial International Bank
# print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns

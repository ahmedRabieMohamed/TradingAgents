from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-5-mini"  # Use a different model
config["quick_think_llm"] = "gpt-5-mini"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance, no extra API keys needed)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: alpha_vantage, yfinance
    "technical_indicators": "yfinance",      # Options: alpha_vantage, yfinance
    "fundamental_data": "yfinance",          # Options: alpha_vantage, yfinance
    "news_data": "yfinance",                 # Options: alpha_vantage, yfinance
}

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

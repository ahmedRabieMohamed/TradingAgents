"""
Egyptian Stock Market Interface Functions
Additional functions for Egyptian Exchange (EGX) stock analysis
"""

from typing import Annotated
from datetime import datetime
import yfinance as yf
from openai import OpenAI

from .config import get_config
from .googlenews_utils import getNewsData
from .egyptian_utils import EgyptianStockUtils, EgyptianStockStatsUtils
from ..egyptian_config import EGYPTIAN_CONFIG, get_egyptian_stock_info


def get_egyptian_stock_data(
    symbol: Annotated[str, "Egyptian stock symbol (e.g., COMI, ORAS, EFID)"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve Egyptian stock price data from EGX (Egyptian Exchange)
    
    Args:
        symbol (str): Egyptian stock symbol (e.g., COMI, ORAS, EFID)
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    
    Returns:
        str: Formatted Egyptian stock data
    """
    try:
        # Validate Egyptian symbol
        stock_info = get_egyptian_stock_info(symbol)
        if not stock_info:
            return f"Error: Unknown Egyptian stock symbol '{symbol}'. Available symbols: {list(EGYPTIAN_CONFIG['major_stocks'].keys())}"
        
        # Initialize Egyptian stock utils
        egyptian_utils = EgyptianStockUtils()
        
        # Get stock data
        data = egyptian_utils.get_stock_data(symbol, start_date, end_date)
        
        if data.empty:
            return f"No data found for Egyptian stock {symbol} ({stock_info['name']}) from {start_date} to {end_date}"
        
        # Format the data
        data = data.reset_index()
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
        
        # Add Egyptian market context
        header = f"## Egyptian Stock Data for {symbol} ({stock_info['name']})\n"
        header += f"**Market**: {EGYPTIAN_CONFIG['market_name']} (EGX)\n"
        header += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n"
        header += f"**Sector**: {stock_info['sector']}\n"
        header += f"**Period**: {start_date} to {end_date}\n\n"
        
        return header + data.to_string()
        
    except Exception as e:
        return f"Error fetching Egyptian stock data for {symbol}: {str(e)}"


def get_egyptian_stock_data_online(
    symbol: Annotated[str, "Egyptian stock symbol"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve Egyptian stock data online (real-time)
    
    Args:
        symbol (str): Egyptian stock symbol
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    
    Returns:
        str: Formatted Egyptian stock data
    """
    try:
        stock_info = get_egyptian_stock_info(symbol)
        if not stock_info:
            return f"Error: Unknown Egyptian stock symbol '{symbol}'"
        
        # Use Yahoo Finance with .CA suffix
        ticker_symbol = stock_info["yahoo_symbol"]
        ticker = yf.Ticker(ticker_symbol)
        
        # Fetch data
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            return f"No online data found for Egyptian stock {symbol} ({stock_info['name']})"
        
        # Format data
        data = data.reset_index()
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
        
        # Add metadata
        header = f"# Egyptian Stock Data for {symbol} ({stock_info['name']})\n"
        header += f"# Market: {EGYPTIAN_CONFIG['market_name']} (EGX)\n"
        header += f"# Currency: {EGYPTIAN_CONFIG['currency']}\n"
        header += f"# Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Total records: {len(data)}\n\n"
        
        return header + data.to_csv()
        
    except Exception as e:
        return f"Error fetching online Egyptian stock data for {symbol}: {str(e)}"


def get_egyptian_stock_indicators_report(
    symbol: Annotated[str, "Egyptian stock symbol"],
    curr_date: Annotated[str, "Current trading date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"],
    online: Annotated[bool, "Use online data"] = True,
) -> str:
    """
    Get technical indicators report for Egyptian stocks
    
    Args:
        symbol (str): Egyptian stock symbol
        curr_date (str): Current trading date
        look_back_days (int): Number of days to look back
        online (bool): Use online data
    
    Returns:
        str: Technical indicators report
    """
    try:
        stock_info = get_egyptian_stock_info(symbol)
        if not stock_info:
            return f"Error: Unknown Egyptian stock symbol '{symbol}'"
        
        # Initialize Egyptian stock stats utils
        egyptian_stats = EgyptianStockStatsUtils()
        
        # Get indicators from config
        indicators = EGYPTIAN_CONFIG["analysis_settings"]["technical_indicators"]
        
        report = f"## Egyptian Stock Technical Analysis Report for {symbol} ({stock_info['name']})\n\n"
        report += f"**Market**: {EGYPTIAN_CONFIG['market_name']} (EGX)\n"
        report += f"**Sector**: {stock_info['sector']}\n"
        report += f"**Analysis Date**: {curr_date}\n"
        report += f"**Lookback Period**: {look_back_days} days\n\n"
        
        # Calculate each indicator
        for indicator in indicators:
            try:
                value = egyptian_stats.get_egyptian_stock_stats(
                    symbol, indicator, curr_date, 
                    EGYPTIAN_CONFIG["data_cache_dir"], online
                )
                report += f"**{indicator}**: {value}\n"
            except Exception as e:
                report += f"**{indicator}**: Error - {str(e)}\n"
        
        return report
        
    except Exception as e:
        return f"Error generating Egyptian stock indicators report for {symbol}: {str(e)}"


def get_egyptian_stock_indicators_report_online(
    symbol: Annotated[str, "Egyptian stock symbol"],
    curr_date: Annotated[str, "Current trading date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"],
) -> str:
    """
    Get technical indicators report for Egyptian stocks using online data
    """
    return get_egyptian_stock_indicators_report(symbol, curr_date, look_back_days, online=True)


def get_egyptian_news(
    symbol: Annotated[str, "Egyptian stock symbol"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"],
) -> str:
    """
    Get Egyptian stock news and market sentiment
    
    Args:
        symbol (str): Egyptian stock symbol
        curr_date (str): Current date
        look_back_days (int): Number of days to look back
    
    Returns:
        str: Egyptian stock news report
    """
    try:
        stock_info = get_egyptian_stock_info(symbol)
        if not stock_info:
            return f"Error: Unknown Egyptian stock symbol '{symbol}'"
        
        # Create search queries for Egyptian context
        queries = [
            f"{symbol} Egypt stock market",
            f"{stock_info['name']} Egypt",
            f"EGX {symbol}",
            f"Egyptian Exchange {symbol}"
        ]
        
        combined_news = ""
        
        for query in queries:
            try:
                from .interface import get_google_news
                news_result = get_google_news(query, curr_date, look_back_days)
                if news_result:
                    combined_news += news_result + "\n\n"
            except Exception as e:
                print(f"Error fetching news for query '{query}': {e}")
        
        if not combined_news:
            return f"No news found for Egyptian stock {symbol} ({stock_info['name']}) in the past {look_back_days} days"
        
        # Add Egyptian market context
        header = f"## Egyptian Stock News Report for {symbol} ({stock_info['name']})\n\n"
        header += f"**Market**: {EGYPTIAN_CONFIG['market_name']} (EGX)\n"
        header += f"**Sector**: {stock_info['sector']}\n"
        header += f"**Period**: {look_back_days} days ending {curr_date}\n\n"
        
        return header + combined_news
        
    except Exception as e:
        return f"Error fetching Egyptian stock news for {symbol}: {str(e)}"


def get_egyptian_market_news(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"],
) -> str:
    """
    Get Egyptian market news and macroeconomic updates
    
    Args:
        curr_date (str): Current date
        look_back_days (int): Number of days to look back
    
    Returns:
        str: Egyptian market news report
    """
    try:
        # Egyptian market news queries
        queries = [
            "Egypt stock market EGX",
            "Egyptian Exchange news",
            "Egypt economy",
            "Cairo stock exchange",
            "Egyptian pound EGP",
            "Egypt central bank",
            "Egypt inflation",
            "Egypt interest rates"
        ]
        
        combined_news = ""
        
        for query in queries:
            try:
                from .interface import get_google_news
                news_result = get_google_news(query, curr_date, look_back_days)
                if news_result:
                    combined_news += news_result + "\n\n"
            except Exception as e:
                print(f"Error fetching Egyptian market news for query '{query}': {e}")
        
        if not combined_news:
            return f"No Egyptian market news found in the past {look_back_days} days"
        
        # Add Egyptian market context
        header = f"## Egyptian Market News Report\n\n"
        header += f"**Market**: {EGYPTIAN_CONFIG['market_name']} (EGX)\n"
        header += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n"
        header += f"**Period**: {look_back_days} days ending {curr_date}\n"
        header += f"**Trading Hours**: {EGYPTIAN_CONFIG['trading_hours']['start']} - {EGYPTIAN_CONFIG['trading_hours']['end']} (Sunday-Thursday)\n\n"
        
        return header + combined_news
        
    except Exception as e:
        return f"Error fetching Egyptian market news: {str(e)}"


def get_egyptian_fundamentals_openai(
    symbol: Annotated[str, "Egyptian stock symbol"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
) -> str:
    """
    Get Egyptian stock fundamentals using OpenAI
    
    Args:
        symbol (str): Egyptian stock symbol
        curr_date (str): Current date
    
    Returns:
        str: Egyptian stock fundamentals report
    """
    try:
        stock_info = get_egyptian_stock_info(symbol)
        if not stock_info:
            return f"Error: Unknown Egyptian stock symbol '{symbol}'"
        
        config = get_config()
        client = OpenAI(base_url=config["backend_url"])
        
        prompt = f"""
        Can you search for fundamental analysis and financial discussions on {symbol} ({stock_info['name']}) 
        from the Egyptian Exchange (EGX) during the month before {curr_date} to the month of {curr_date}. 
        
        Focus on:
        - Financial statements (P&L, Balance Sheet, Cash Flow)
        - Key ratios (P/E, P/B, ROE, ROA, Debt-to-Equity)
        - Revenue and profit trends
        - Market cap and valuation
        - Dividend information
        - Analyst ratings and price targets
        - Egyptian market context and economic factors
        
        Present the information in a structured table format with the following columns:
        Metric | Value | Period | Source | Notes
        
        Make sure you only get data posted during the specified period.
        """
        
        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                }
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[
                {
                    "type": "web_search_preview",
                    "user_location": {"type": "approximate"},
                    "search_context_size": "medium",
                }
            ],
            temperature=0.7,
            max_output_tokens=4096,
            top_p=1,
            store=True,
        )
        
        result = response.output[1].content[0].text
        
        # Add Egyptian market context
        header = f"## Egyptian Stock Fundamentals Report for {symbol} ({stock_info['name']})\n\n"
        header += f"**Market**: {EGYPTIAN_CONFIG['market_name']} (EGX)\n"
        header += f"**Sector**: {stock_info['sector']}\n"
        header += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n"
        header += f"**Analysis Date**: {curr_date}\n\n"
        
        return header + result
        
    except Exception as e:
        return f"Error fetching Egyptian stock fundamentals for {symbol}: {str(e)}"


def get_egyptian_stock_info_summary(
    symbol: Annotated[str, "Egyptian stock symbol"],
) -> str:
    """
    Get comprehensive information about an Egyptian stock
    
    Args:
        symbol (str): Egyptian stock symbol
    
    Returns:
        str: Egyptian stock information summary
    """
    try:
        stock_info = get_egyptian_stock_info(symbol)
        if not stock_info:
            return f"Error: Unknown Egyptian stock symbol '{symbol}'"
        
        # Initialize Egyptian stock utils
        egyptian_utils = EgyptianStockUtils()
        
        # Get stock info
        stock_data = egyptian_utils.get_stock_info(symbol)
        
        # Format summary
        summary = f"## Egyptian Stock Information: {symbol} ({stock_info['name']})\n\n"
        summary += f"**Market**: {EGYPTIAN_CONFIG['market_name']} (EGX)\n"
        summary += f"**Sector**: {stock_info['sector']}\n"
        summary += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n"
        summary += f"**Yahoo Symbol**: {stock_info['yahoo_symbol']}\n"
        summary += f"**Trading Hours**: {EGYPTIAN_CONFIG['trading_hours']['start']} - {EGYPTIAN_CONFIG['trading_hours']['end']} (Sunday-Thursday)\n\n"
        
        if stock_data:
            summary += "### Financial Information\n"
            summary += f"**Market Cap**: {stock_data.get('marketCap', 'N/A')}\n"
            summary += f"**P/E Ratio**: {stock_data.get('trailingPE', 'N/A')}\n"
            summary += f"**P/B Ratio**: {stock_data.get('priceToBook', 'N/A')}\n"
            summary += f"**52-Week High**: {stock_data.get('fiftyTwoWeekHigh', 'N/A')}\n"
            summary += f"**52-Week Low**: {stock_data.get('fiftyTwoWeekLow', 'N/A')}\n"
            summary += f"**Volume**: {stock_data.get('volume', 'N/A')}\n"
            summary += f"**Average Volume**: {stock_data.get('averageVolume', 'N/A')}\n\n"
        
        summary += "### Egyptian Market Context\n"
        summary += f"**Trading Days**: Sunday to Thursday\n"
        summary += f"**Market Cap Categories**:\n"
        summary += f"- Large Cap: >{EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['large_cap']:,} EGP\n"
        summary += f"- Mid Cap: {EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['mid_cap']:,} - {EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['large_cap']:,} EGP\n"
        summary += f"- Small Cap: <{EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['mid_cap']:,} EGP\n"
        
        return summary
        
    except Exception as e:
        return f"Error fetching Egyptian stock information for {symbol}: {str(e)}"


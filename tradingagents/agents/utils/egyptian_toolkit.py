"""
Egyptian Toolkit
Specialized toolkit for Egyptian Exchange (EGX) stock analysis
"""

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List, Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI

import tradingagents.dataflows.egyptian_interface as egyptian_interface
from tradingagents.egyptian_config import EGYPTIAN_CONFIG


def create_egyptian_msg_delete():
    """Create message deletion function for Egyptian toolkit"""
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        
        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue Egyptian analysis")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages


class EgyptianToolkit:
    """Toolkit specialized for Egyptian Exchange (EGX) stock analysis"""
    
    _config = EGYPTIAN_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """Update the class-level configuration."""
        cls._config.update(config)

    @property
    def config(self):
        """Access the configuration."""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
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
            str: Formatted Egyptian stock data with market context
        """
        return egyptian_interface.get_egyptian_stock_data(symbol, start_date, end_date)

    @staticmethod
    @tool
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
            str: Real-time Egyptian stock data
        """
        return egyptian_interface.get_egyptian_stock_data_online(symbol, start_date, end_date)

    @staticmethod
    @tool
    def get_egyptian_stock_indicators_report(
        symbol: Annotated[str, "Egyptian stock symbol"],
        curr_date: Annotated[str, "Current trading date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "Number of days to look back"],
    ) -> str:
        """
        Get technical indicators report for Egyptian stocks
        
        Args:
            symbol (str): Egyptian stock symbol
            curr_date (str): Current trading date
            look_back_days (int): Number of days to look back
        
        Returns:
            str: Technical indicators report for Egyptian stock
        """
        return egyptian_interface.get_egyptian_stock_indicators_report(
            symbol, curr_date, look_back_days, online=False
        )

    @staticmethod
    @tool
    def get_egyptian_stock_indicators_report_online(
        symbol: Annotated[str, "Egyptian stock symbol"],
        curr_date: Annotated[str, "Current trading date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "Number of days to look back"],
    ) -> str:
        """
        Get technical indicators report for Egyptian stocks using online data
        
        Args:
            symbol (str): Egyptian stock symbol
            curr_date (str): Current trading date
            look_back_days (int): Number of days to look back
        
        Returns:
            str: Online technical indicators report for Egyptian stock
        """
        return egyptian_interface.get_egyptian_stock_indicators_report_online(
            symbol, curr_date, look_back_days
        )

    @staticmethod
    @tool
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
        return egyptian_interface.get_egyptian_news(symbol, curr_date, look_back_days)

    @staticmethod
    @tool
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
        return egyptian_interface.get_egyptian_market_news(curr_date, look_back_days)

    @staticmethod
    @tool
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
        return egyptian_interface.get_egyptian_fundamentals_openai(symbol, curr_date)

    @staticmethod
    @tool
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
        return egyptian_interface.get_egyptian_stock_info_summary(symbol)

    @staticmethod
    @tool
    def get_egyptian_market_summary() -> str:
        """
        Get Egyptian market summary information
        
        Returns:
            str: Egyptian market summary
        """
        summary = f"## Egyptian Exchange (EGX) Market Summary\n\n"
        summary += f"**Market Name**: {EGYPTIAN_CONFIG['market_name']}\n"
        summary += f"**Market Code**: {EGYPTIAN_CONFIG['market_code']}\n"
        summary += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n"
        summary += f"**Country**: {EGYPTIAN_CONFIG['country']}\n"
        summary += f"**Timezone**: {EGYPTIAN_CONFIG['timezone']}\n\n"
        
        summary += f"**Trading Hours**:\n"
        summary += f"- Days: {', '.join(EGYPTIAN_CONFIG['trading_hours']['days'])}\n"
        summary += f"- Time: {EGYPTIAN_CONFIG['trading_hours']['start']} - {EGYPTIAN_CONFIG['trading_hours']['end']}\n"
        summary += f"- Timezone: {EGYPTIAN_CONFIG['trading_hours']['timezone']}\n\n"
        
        summary += f"**Major Stocks**:\n"
        for symbol, info in EGYPTIAN_CONFIG['major_stocks'].items():
            summary += f"- {symbol}: {info['name']} ({info['sector']})\n"
        
        summary += f"\n**Market Statistics**:\n"
        summary += f"- Total Stocks: {len(EGYPTIAN_CONFIG['major_stocks'])}\n"
        summary += f"- Trading Days per Week: {EGYPTIAN_CONFIG['market_specific']['trading_days_per_week']}\n"
        summary += f"- Volatility Threshold: {EGYPTIAN_CONFIG['market_specific']['volatility_threshold']*100:.1f}%\n"
        summary += f"- Liquidity Threshold: {EGYPTIAN_CONFIG['market_specific']['liquidity_threshold']:,} EGP\n"
        
        return summary

    @staticmethod
    @tool
    def get_egyptian_trading_calendar(
        year: Annotated[int, "Year for trading calendar"] = 2025
    ) -> str:
        """
        Get Egyptian trading calendar for a specific year
        
        Args:
            year (int): Year for trading calendar
        
        Returns:
            str: Egyptian trading calendar
        """
        from tradingagents.dataflows.egyptian_utils import EgyptianStockUtils
        
        egyptian_utils = EgyptianStockUtils()
        calendar_df = egyptian_utils.get_trading_calendar(year)
        
        header = f"## Egyptian Exchange (EGX) Trading Calendar {year}\n\n"
        header += f"**Market**: {EGYPTIAN_CONFIG['market_name']}\n"
        header += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n"
        header += f"**Trading Days**: Sunday to Thursday\n\n"
        
        return header + calendar_df.to_string()

    @staticmethod
    @tool
    def get_egyptian_stocks_by_sector(
        sector: Annotated[str, "Sector name (Banking, Construction, Technology, etc.)"]
    ) -> str:
        """
        Get Egyptian stocks filtered by sector
        
        Args:
            sector (str): Sector name
        
        Returns:
            str: List of Egyptian stocks in the specified sector
        """
        from tradingagents.dataflows.egyptian_utils import EgyptianStockUtils
        
        egyptian_utils = EgyptianStockUtils()
        stocks = egyptian_utils.get_egyptian_stocks_by_sector(sector)
        
        if not stocks:
            return f"No Egyptian stocks found in the {sector} sector. Available sectors: Banking, Construction, Technology, Industrial, Investment, Tourism, Chemicals"
        
        header = f"## Egyptian Stocks in {sector} Sector\n\n"
        header += f"**Market**: {EGYPTIAN_CONFIG['market_name']}\n"
        header += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n\n"
        
        stock_list = ""
        for symbol, name in stocks.items():
            stock_list += f"- **{symbol}**: {name}\n"
        
        return header + stock_list

    @staticmethod
    @tool
    def validate_egyptian_symbol(
        symbol: Annotated[str, "Egyptian stock symbol to validate"]
    ) -> str:
        """
        Validate if a symbol is a known Egyptian stock
        
        Args:
            symbol (str): Egyptian stock symbol to validate
        
        Returns:
            str: Validation result and stock information
        """
        from tradingagents.dataflows.egyptian_utils import EgyptianStockUtils
        from tradingagents.egyptian_config import get_egyptian_stock_info
        
        egyptian_utils = EgyptianStockUtils()
        is_valid = egyptian_utils.validate_egyptian_symbol(symbol)
        
        if is_valid:
            stock_info = get_egyptian_stock_info(symbol)
            result = f"✅ **{symbol}** is a valid Egyptian stock symbol\n\n"
            result += f"**Company**: {stock_info['name']}\n"
            result += f"**Sector**: {stock_info['sector']}\n"
            result += f"**Yahoo Symbol**: {stock_info['yahoo_symbol']}\n"
            result += f"**Market**: {EGYPTIAN_CONFIG['market_name']}\n"
            result += f"**Currency**: {EGYPTIAN_CONFIG['currency']}\n"
        else:
            result = f"❌ **{symbol}** is not a valid Egyptian stock symbol\n\n"
            result += f"**Available Egyptian Stock Symbols**:\n"
            for symbol, info in EGYPTIAN_CONFIG['major_stocks'].items():
                result += f"- {symbol}: {info['name']}\n"
        
        return result


"""
Egyptian Stock Market Data Utilities
Handles data retrieval and processing for Egyptian Exchange (EGX) stocks
"""

import pandas as pd
import yfinance as yf
import requests
import os
from typing import Annotated, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from functools import wraps

from .config import get_config
from ..egyptian_config import EGYPTIAN_CONFIG, get_egyptian_stock_info, is_egyptian_trading_day


def init_egyptian_ticker(func):
    """Decorator to initialize Egyptian ticker and pass it to the function."""
    @wraps(func)
    def wrapper(symbol: Annotated[str, "Egyptian stock symbol"], *args, **kwargs):
        # Get Egyptian stock info
        stock_info = get_egyptian_stock_info(symbol)
        if not stock_info:
            raise ValueError(f"Unknown Egyptian stock symbol: {symbol}")
        
        # Create ticker with .CA suffix for Yahoo Finance
        ticker_symbol = stock_info["yahoo_symbol"]
        ticker = yf.Ticker(ticker_symbol)
        return func(ticker, symbol, *args, **kwargs)
    
    return wrapper


class EgyptianStockUtils:
    """Utilities for Egyptian stock market data retrieval and processing"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or EGYPTIAN_CONFIG["data_sources"]["eodhd_api_key"]
        self.base_url = "https://eodhd.com/api"
    
    @init_egyptian_ticker
    def get_stock_data(
        self, 
        ticker, 
        symbol: Annotated[str, "Egyptian stock symbol"],
        start_date: Annotated[str, "Start date in YYYY-mm-dd format"],
        end_date: Annotated[str, "End date in YYYY-mm-dd format"],
        save_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Retrieve Egyptian stock price data"""
        try:
            # Add one day to end_date for inclusive range
            end_date_dt = pd.to_datetime(end_date) + pd.DateOffset(days=1)
            end_date_str = end_date_dt.strftime("%Y-%m-%d")
            
            stock_data = ticker.history(start=start_date, end=end_date_str)
            
            if stock_data.empty:
                raise Exception(f"No data found for Egyptian stock {symbol}")
            
            # Add Egyptian market metadata
            stock_data['Market'] = 'EGX'
            stock_data['Currency'] = 'EGP'
            stock_data['Symbol'] = symbol
            
            if save_path:
                stock_data.to_csv(save_path)
                print(f"Egyptian stock data for {symbol} saved to {save_path}")
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching Egyptian stock data for {symbol}: {e}")
            # Try backup data source if available
            if self.api_key:
                return self._get_eodhd_data(symbol, start_date, end_date)
            else:
                raise e
    
    def _get_eodhd_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get data from EODHD API as backup"""
        try:
            url = f"{self.base_url}/eod/{symbol}.EGX"
            params = {
                'api_token': self.api_key,
                'from': start_date,
                'to': end_date,
                'fmt': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = pd.DataFrame(response.json())
                if not data.empty:
                    data['Date'] = pd.to_datetime(data['date'])
                    data['Market'] = 'EGX'
                    data['Currency'] = 'EGP'
                    data['Symbol'] = symbol
                    return data
                else:
                    raise Exception("No data returned from EODHD API")
            else:
                raise Exception(f"EODHD API Error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"EODHD backup failed: {e}")
    
    @init_egyptian_ticker
    def get_stock_info(
        self, 
        ticker, 
        symbol: Annotated[str, "Egyptian stock symbol"]
    ) -> Dict[str, Any]:
        """Fetch Egyptian stock information"""
        try:
            stock_info = ticker.info
            
            # Add Egyptian market specific info
            egyptian_info = get_egyptian_stock_info(symbol)
            if egyptian_info:
                stock_info.update({
                    'egyptian_name': egyptian_info['name'],
                    'egyptian_sector': egyptian_info['sector'],
                    'market': 'EGX',
                    'currency': 'EGP',
                    'country': 'Egypt'
                })
            
            return stock_info
            
        except Exception as e:
            print(f"Error fetching Egyptian stock info for {symbol}: {e}")
            return {}
    
    @init_egyptian_ticker
    def get_company_info(
        self, 
        ticker, 
        symbol: Annotated[str, "Egyptian stock symbol"],
        save_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch Egyptian company information"""
        try:
            info = ticker.info
            egyptian_info = get_egyptian_stock_info(symbol)
            
            company_info = {
                "Company Name": egyptian_info['name'] if egyptian_info else info.get("shortName", "N/A"),
                "Egyptian Symbol": symbol,
                "Yahoo Symbol": egyptian_info['yahoo_symbol'] if egyptian_info else f"{symbol}.CA",
                "Industry": info.get("industry", "N/A"),
                "Sector": egyptian_info['sector'] if egyptian_info else info.get("sector", "N/A"),
                "Country": "Egypt",
                "Market": "EGX",
                "Currency": "EGP",
                "Website": info.get("website", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "Employees": info.get("fullTimeEmployees", "N/A")
            }
            
            company_info_df = pd.DataFrame([company_info])
            
            if save_path:
                company_info_df.to_csv(save_path)
                print(f"Egyptian company info for {symbol} saved to {save_path}")
            
            return company_info_df
            
        except Exception as e:
            print(f"Error fetching Egyptian company info for {symbol}: {e}")
            return pd.DataFrame()
    
    @init_egyptian_ticker
    def get_stock_dividends(
        self, 
        ticker, 
        symbol: Annotated[str, "Egyptian stock symbol"],
        save_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch Egyptian stock dividends"""
        try:
            dividends = ticker.dividends
            
            if save_path:
                dividends.to_csv(save_path)
                print(f"Egyptian stock dividends for {symbol} saved to {save_path}")
            
            return dividends
            
        except Exception as e:
            print(f"Error fetching Egyptian stock dividends for {symbol}: {e}")
            return pd.DataFrame()
    
    @init_egyptian_ticker
    def get_financial_statements(
        self, 
        ticker, 
        symbol: Annotated[str, "Egyptian stock symbol"],
        statement_type: str = "income"
    ) -> pd.DataFrame:
        """Fetch Egyptian company financial statements"""
        try:
            if statement_type == "income":
                statements = ticker.financials
            elif statement_type == "balance":
                statements = ticker.balance_sheet
            elif statement_type == "cashflow":
                statements = ticker.cashflow
            else:
                raise ValueError("statement_type must be 'income', 'balance', or 'cashflow'")
            
            return statements
            
        except Exception as e:
            print(f"Error fetching Egyptian {statement_type} statement for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_egyptian_market_summary(self) -> Dict[str, Any]:
        """Get Egyptian market summary information"""
        return {
            "market_name": EGYPTIAN_CONFIG["market_name"],
            "market_code": EGYPTIAN_CONFIG["market_code"],
            "currency": EGYPTIAN_CONFIG["currency"],
            "trading_hours": EGYPTIAN_CONFIG["trading_hours"],
            "total_stocks": len(EGYPTIAN_CONFIG["major_stocks"]),
            "trading_days_per_week": EGYPTIAN_CONFIG["market_specific"]["trading_days_per_week"],
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def validate_egyptian_symbol(self, symbol: str) -> bool:
        """Validate if symbol is a known Egyptian stock"""
        return symbol.upper() in EGYPTIAN_CONFIG["major_stocks"]
    
    def get_egyptian_stocks_by_sector(self, sector: str) -> Dict[str, str]:
        """Get Egyptian stocks filtered by sector"""
        stocks = {}
        for symbol, info in EGYPTIAN_CONFIG["major_stocks"].items():
            if info["sector"].lower() == sector.lower():
                stocks[symbol] = info["name"]
        return stocks
    
    def format_egyptian_price(self, price: float) -> str:
        """Format price in Egyptian Pounds"""
        return f"{price:.2f} EGP"
    
    def get_trading_calendar(self, year: int = 2025) -> pd.DataFrame:
        """Get Egyptian trading calendar for a year"""
        calendar_data = []
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            is_trading = is_egyptian_trading_day(date_str)
            
            calendar_data.append({
                "Date": date_str,
                "Day": current_date.strftime("%A"),
                "Is_Trading_Day": is_trading,
                "Market": "EGX" if is_trading else "Closed"
            })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(calendar_data)


class EgyptianStockStatsUtils:
    """Utilities for Egyptian stock technical analysis"""
    
    def __init__(self):
        self.config = get_config()
    
    def get_egyptian_stock_stats(
        self,
        symbol: Annotated[str, "Egyptian stock symbol"],
        indicator: Annotated[str, "Technical indicator"],
        curr_date: Annotated[str, "Current date in YYYY-mm-dd format"],
        data_dir: Annotated[str, "Data directory"],
        online: Annotated[bool, "Use online data"] = False
    ) -> str:
        """Get technical indicators for Egyptian stocks"""
        
        if not online:
            # Try to read from cached data
            try:
                data_file = os.path.join(
                    data_dir,
                    f"{symbol}-EGX-data-2015-01-01-2025-03-25.csv"
                )
                
                if os.path.exists(data_file):
                    data = pd.read_csv(data_file)
                    data["Date"] = pd.to_datetime(data["Date"], utc=True)
                    
                    # Calculate indicator using stockstats
                    from stockstats import wrap
                    df = wrap(data)
                    df[indicator]  # trigger calculation
                    
                    # Find matching date
                    matching_rows = df[df["Date"].str.startswith(curr_date)]
                    
                    if not matching_rows.empty:
                        indicator_value = matching_rows[indicator].values[0]
                        return str(indicator_value)
                    else:
                        return "N/A: Not a trading day"
                else:
                    raise FileNotFoundError("Cached data not found")
                    
            except Exception as e:
                print(f"Error with cached data: {e}")
                # Fallback to online
                online = True
        
        if online:
            # Use online data
            try:
                stock_info = get_egyptian_stock_info(symbol)
                if not stock_info:
                    raise ValueError(f"Unknown Egyptian stock: {symbol}")
                
                ticker_symbol = stock_info["yahoo_symbol"]
                ticker = yf.Ticker(ticker_symbol)
                
                # Get data for the last 2 years to calculate indicators
                end_date = pd.Timestamp.today()
                start_date = end_date - pd.DateOffset(years=2)
                
                data = ticker.history(start=start_date, end=end_date)
                
                if data.empty:
                    return "N/A: No data available"
                
                # Calculate indicator
                from stockstats import wrap
                df = wrap(data.reset_index())
                df[indicator]  # trigger calculation
                
                # Find matching date
                df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
                matching_rows = df[df["Date"].str.startswith(curr_date)]
                
                if not matching_rows.empty:
                    indicator_value = matching_rows[indicator].values[0]
                    return str(indicator_value)
                else:
                    return "N/A: Not a trading day"
                    
            except Exception as e:
                print(f"Error with online data: {e}")
                return f"Error: {str(e)}"
        
        return "N/A: Unable to fetch data"


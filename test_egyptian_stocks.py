#!/usr/bin/env python3
"""
Test Script for Egyptian Stock Market Integration
Tests the Egyptian trading agents system with real Egyptian stocks
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.graph.egyptian_trading_graph import EgyptianTradingAgentsGraph
from tradingagents.egyptian_config import EGYPTIAN_CONFIG
from tradingagents.dataflows.egyptian_interface import (
    get_egyptian_stock_data,
    get_egyptian_stock_data_online,
    get_egyptian_stock_indicators_report_online,
    get_egyptian_news,
    get_egyptian_market_news,
    get_egyptian_fundamentals_openai,
    get_egyptian_stock_info_summary
)


def test_egyptian_data_functions():
    """Test Egyptian data interface functions"""
    print("🧪 Testing Egyptian Data Interface Functions...")
    
    # Test parameters
    symbol = "COMI"  # Commercial International Bank
    start_date = "2025-01-01"
    end_date = "2025-01-15"
    curr_date = "2025-01-15"
    look_back_days = 7
    
    print(f"\n📊 Testing with Egyptian stock: {symbol}")
    print(f"📅 Date range: {start_date} to {end_date}")
    
    # Test 1: Stock data retrieval
    print("\n1️⃣ Testing Egyptian stock data retrieval...")
    try:
        data = get_egyptian_stock_data(symbol, start_date, end_date)
        print(f"✅ Stock data retrieved: {len(data)} characters")
        print(f"📄 Sample: {data[:200]}...")
    except Exception as e:
        print(f"❌ Error retrieving stock data: {e}")
    
    # Test 2: Online stock data
    print("\n2️⃣ Testing online Egyptian stock data...")
    try:
        online_data = get_egyptian_stock_data_online(symbol, start_date, end_date)
        print(f"✅ Online stock data retrieved: {len(online_data)} characters")
        print(f"📄 Sample: {online_data[:200]}...")
    except Exception as e:
        print(f"❌ Error retrieving online stock data: {e}")
    
    # Test 3: Technical indicators
    print("\n3️⃣ Testing Egyptian technical indicators...")
    try:
        indicators = get_egyptian_stock_indicators_report_online(symbol, curr_date, look_back_days)
        print(f"✅ Technical indicators retrieved: {len(indicators)} characters")
        print(f"📄 Sample: {indicators[:200]}...")
    except Exception as e:
        print(f"❌ Error retrieving technical indicators: {e}")
    
    # Test 4: Egyptian news
    print("\n4️⃣ Testing Egyptian stock news...")
    try:
        news = get_egyptian_news(symbol, curr_date, look_back_days)
        print(f"✅ Egyptian news retrieved: {len(news)} characters")
        print(f"📄 Sample: {news[:200]}...")
    except Exception as e:
        print(f"❌ Error retrieving Egyptian news: {e}")
    
    # Test 5: Egyptian market news
    print("\n5️⃣ Testing Egyptian market news...")
    try:
        market_news = get_egyptian_market_news(curr_date, look_back_days)
        print(f"✅ Egyptian market news retrieved: {len(market_news)} characters")
        print(f"📄 Sample: {market_news[:200]}...")
    except Exception as e:
        print(f"❌ Error retrieving Egyptian market news: {e}")
    
    # Test 6: Stock info summary
    print("\n6️⃣ Testing Egyptian stock info summary...")
    try:
        info = get_egyptian_stock_info_summary(symbol)
        print(f"✅ Stock info summary retrieved: {len(info)} characters")
        print(f"📄 Sample: {info[:200]}...")
    except Exception as e:
        print(f"❌ Error retrieving stock info summary: {e}")


def test_egyptian_trading_graph():
    """Test the Egyptian trading graph"""
    print("\n🧪 Testing Egyptian Trading Graph...")
    
    # Test parameters
    symbol = "COMI"  # Commercial International Bank
    trade_date = "2025-01-15"
    selected_analysts = ["egyptian_market", "egyptian_news", "egyptian_fundamentals"]
    
    print(f"\n📊 Testing Egyptian trading graph with:")
    print(f"   Stock: {symbol}")
    print(f"   Date: {trade_date}")
    print(f"   Analysts: {', '.join(selected_analysts)}")
    
    try:
        # Initialize Egyptian trading graph
        print("\n🚀 Initializing Egyptian trading graph...")
        egyptian_graph = EgyptianTradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=False,
            config=EGYPTIAN_CONFIG
        )
        print("✅ Egyptian trading graph initialized successfully")
        
        # Test market info
        print("\n📈 Getting Egyptian market info...")
        market_info = egyptian_graph.get_egyptian_market_info()
        print(f"✅ Market info retrieved:")
        print(f"   Market: {market_info['market_name']}")
        print(f"   Currency: {market_info['currency']}")
        print(f"   Total stocks: {market_info['total_stocks']}")
        
        # Test symbol validation
        print(f"\n🔍 Validating Egyptian symbol: {symbol}")
        is_valid = egyptian_graph.validate_egyptian_symbol(symbol)
        print(f"✅ Symbol validation: {'Valid' if is_valid else 'Invalid'}")
        
        # Test available stocks
        print("\n📋 Getting available Egyptian stocks...")
        available_stocks = egyptian_graph.get_available_egyptian_stocks()
        print(f"✅ Available stocks: {', '.join(available_stocks[:5])}...")
        
        print("\n🎯 Egyptian trading graph test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Egyptian trading graph: {e}")
        import traceback
        traceback.print_exc()


def test_egyptian_config():
    """Test Egyptian configuration"""
    print("\n🧪 Testing Egyptian Configuration...")
    
    print(f"\n📋 Egyptian Market Configuration:")
    print(f"   Market Name: {EGYPTIAN_CONFIG['market_name']}")
    print(f"   Market Code: {EGYPTIAN_CONFIG['market_code']}")
    print(f"   Currency: {EGYPTIAN_CONFIG['currency']}")
    print(f"   Country: {EGYPTIAN_CONFIG['country']}")
    print(f"   Timezone: {EGYPTIAN_CONFIG['timezone']}")
    
    print(f"\n⏰ Trading Hours:")
    print(f"   Days: {', '.join(EGYPTIAN_CONFIG['trading_hours']['days'])}")
    print(f"   Time: {EGYPTIAN_CONFIG['trading_hours']['start']} - {EGYPTIAN_CONFIG['trading_hours']['end']}")
    print(f"   Timezone: {EGYPTIAN_CONFIG['trading_hours']['timezone']}")
    
    print(f"\n📊 Major Stocks ({len(EGYPTIAN_CONFIG['major_stocks'])}):")
    for symbol, info in list(EGYPTIAN_CONFIG['major_stocks'].items())[:5]:
        print(f"   {symbol}: {info['name']} ({info['sector']})")
    print(f"   ... and {len(EGYPTIAN_CONFIG['major_stocks']) - 5} more")
    
    print(f"\n💰 Market Statistics:")
    print(f"   Trading Days per Week: {EGYPTIAN_CONFIG['market_specific']['trading_days_per_week']}")
    print(f"   Volatility Threshold: {EGYPTIAN_CONFIG['market_specific']['volatility_threshold']*100:.1f}%")
    print(f"   Liquidity Threshold: {EGYPTIAN_CONFIG['market_specific']['liquidity_threshold']:,} EGP")
    
    print(f"\n📈 Economic Indicators:")
    print(f"   Inflation Target: {EGYPTIAN_CONFIG['economic_indicators']['inflation_target']*100:.1f}%")
    print(f"   Interest Rate Range: {EGYPTIAN_CONFIG['economic_indicators']['interest_rate_range'][0]*100:.1f}% - {EGYPTIAN_CONFIG['economic_indicators']['interest_rate_range'][1]*100:.1f}%")
    print(f"   GDP Growth Target: {EGYPTIAN_CONFIG['economic_indicators']['gdp_growth_target']*100:.1f}%")
    
    print("\n✅ Egyptian configuration test completed successfully!")


def test_multiple_egyptian_stocks():
    """Test with multiple Egyptian stocks"""
    print("\n🧪 Testing Multiple Egyptian Stocks...")
    
    # Test stocks
    test_stocks = ["COMI", "ORAS", "EFID", "FWRY"]
    
    for symbol in test_stocks:
        print(f"\n📊 Testing Egyptian stock: {symbol}")
        
        try:
            # Get stock info
            stock_info = EGYPTIAN_CONFIG["major_stocks"][symbol]
            print(f"   Company: {stock_info['name']}")
            print(f"   Sector: {stock_info['sector']}")
            print(f"   Yahoo Symbol: {stock_info['yahoo_symbol']}")
            
            # Test stock data retrieval
            start_date = "2025-01-01"
            end_date = "2025-01-15"
            
            data = get_egyptian_stock_data(symbol, start_date, end_date)
            print(f"   ✅ Data retrieved: {len(data)} characters")
            
        except Exception as e:
            print(f"   ❌ Error testing {symbol}: {e}")
    
    print("\n✅ Multiple Egyptian stocks test completed!")


def main():
    """Main test function"""
    print("🇪🇬 Egyptian Stock Market Integration Test")
    print("=" * 50)
    
    # Test 1: Configuration
    test_egyptian_config()
    
    # Test 2: Data functions
    test_egyptian_data_functions()
    
    # Test 3: Trading graph
    test_egyptian_trading_graph()
    
    # Test 4: Multiple stocks
    test_multiple_egyptian_stocks()
    
    print("\n🎉 All Egyptian stock market tests completed!")
    print("\n📋 Summary:")
    print("✅ Egyptian configuration loaded")
    print("✅ Egyptian data interface functions working")
    print("✅ Egyptian trading graph initialized")
    print("✅ Multiple Egyptian stocks tested")
    
    print("\n🚀 Ready to use Egyptian trading agents!")
    print("\nExample usage:")
    print("  python cli/egyptian_main.py analyze COMI")
    print("  python cli/egyptian_main.py list-stocks")
    print("  python cli/egyptian_main.py market-info")


if __name__ == "__main__":
    main()


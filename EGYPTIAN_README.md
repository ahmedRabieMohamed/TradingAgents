# 🇪🇬 Egyptian Trading Agents

Complete integration of the Trading Agents framework for Egyptian Exchange (EGX) stocks.

## 🏛️ Egyptian Market Overview

- **Market**: Egyptian Exchange (EGX)
- **Currency**: Egyptian Pound (EGP)
- **Trading Hours**: Sunday-Thursday, 10:00-14:30 (Cairo time)
- **Trading Days**: 5 days per week (no Friday/Saturday trading)
- **Major Sectors**: Banking, Construction, Technology, Industrial, Tourism

## 📊 Supported Egyptian Stocks

| Symbol | Company Name | Sector | Yahoo Symbol |
|--------|--------------|--------|--------------|
| COMI | Commercial International Bank | Banking | COMI.CA |
| ORAS | Orascom Construction | Construction | ORAS.CA |
| EFID | EFG Hermes | Financial Services | EFID.CA |
| EGBE | Egyptian Bank | Banking | EGBE.CA |
| SWDY | El Sewedy Electric | Industrial | SWDY.CA |
| OCIC | Orascom Investment | Investment | OCIC.CA |
| FWRY | Fawry | Technology | FWRY.CA |
| RAPH | Raya Holding | Technology | RAPH.CA |
| ABUK | Abu Qir Fertilizers | Chemicals | ABUK.CA |
| EGTS | Egyptian Tourism | Tourism | EGTS.CA |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Egyptian Integration

```bash
python test_egyptian_stocks.py
```

### 3. Analyze Egyptian Stocks

```bash
# Analyze Commercial International Bank (COMI)
python cli/egyptian_main.py analyze COMI

# Analyze with specific date
python cli/egyptian_main.py analyze ORAS --date 2025-01-15

# Analyze with specific analysts
python cli/egyptian_main.py analyze EFID --analysts egyptian_market,egyptian_fundamentals

# Show live updates
python cli/egyptian_main.py analyze FWRY --live
```

## 📋 Available Commands

### Analyze Egyptian Stock
```bash
python cli/egyptian_main.py analyze <SYMBOL> [OPTIONS]

Options:
  --date, -d TEXT        Analysis date (YYYY-MM-DD)
  --analysts, -a TEXT    Comma-separated list of analysts
  --debug                Enable debug mode
  --live/--no-live       Show live updates
```

### List Egyptian Stocks
```bash
python cli/egyptian_main.py list-stocks
```

### Market Information
```bash
python cli/egyptian_main.py market-info
```

### List by Sector
```bash
python cli/egyptian_main.py sectors
```

### Validate Symbol
```bash
python cli/egyptian_main.py validate <SYMBOL>
```

## 🧠 Egyptian-Specific Analysts

### 1. Egyptian Market Analyst
- **Purpose**: Technical analysis for Egyptian stocks
- **Focus**: EGX-specific indicators, EGP currency impact, Egyptian market volatility
- **Tools**: Egyptian stock data, technical indicators

### 2. Egyptian News Analyst
- **Purpose**: Egyptian market news and macroeconomic analysis
- **Focus**: CBE policy, inflation, interest rates, regional factors
- **Tools**: Egyptian news, market news, economic indicators

### 3. Egyptian Fundamentals Analyst
- **Purpose**: Fundamental analysis for Egyptian companies
- **Focus**: Financial statements in EGP, Egyptian accounting standards, sector analysis
- **Tools**: Fundamentals data, company information

## 🔧 Configuration

### Egyptian Market Settings
```python
EGYPTIAN_CONFIG = {
    "market_name": "Egyptian Exchange (EGX)",
    "currency": "EGP",
    "trading_hours": {
        "start": "10:00",
        "end": "14:30",
        "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    },
    "major_stocks": {
        "COMI": {
            "name": "Commercial International Bank",
            "sector": "Banking",
            "yahoo_symbol": "COMI.CA"
        },
        # ... more stocks
    }
}
```

### Economic Indicators
- **Inflation Target**: 7%
- **Interest Rate Range**: 18-25%
- **GDP Growth Target**: 5%

## 📈 Technical Analysis

### Supported Indicators
- **Moving Averages**: 50 SMA, 200 SMA, 10 EMA
- **MACD**: MACD, Signal, Histogram
- **Momentum**: RSI
- **Volatility**: Bollinger Bands, ATR
- **Volume**: VWMA

### Egyptian Market Considerations
- Currency impact (EGP fluctuations)
- Egyptian economic factors
- Regional events (MENA)
- Market hours (Sunday-Thursday)
- Liquidity patterns
- Volatility characteristics

## 📰 News Sources

### Arabic Sources
- الأهرام (Al Ahram)
- الوفد (Al Wafd)
- المصري اليوم (Al Masry Al Youm)
- اليوم السابع (Youm7)
- الوطن (Al Watan)

### English Sources
- Egypt Today
- Ahram Online
- Daily News Egypt
- Egypt Independent

### Financial Sources
- Al Mal News
- Al Borsa News
- Mubasher Info

## 🏗️ Architecture

### Core Components

1. **Egyptian Configuration** (`egyptian_config.py`)
   - Market settings, trading hours, stock information
   - Economic indicators, holidays, news sources

2. **Egyptian Data Utils** (`egyptian_utils.py`)
   - Stock data retrieval from Yahoo Finance
   - Technical indicators calculation
   - Market summary and validation

3. **Egyptian Interface** (`egyptian_interface.py`)
   - Data interface functions for Egyptian stocks
   - News retrieval, fundamentals analysis
   - Market-specific data formatting

4. **Egyptian Analysts** (`egyptian_*_analyst.py`)
   - Market analyst for technical analysis
   - News analyst for market news
   - Fundamentals analyst for financial analysis

5. **Egyptian Toolkit** (`egyptian_toolkit.py`)
   - Tool definitions for Egyptian market
   - Data validation and market information

6. **Egyptian Trading Graph** (`egyptian_trading_graph.py`)
   - Main orchestration for Egyptian analysis
   - Graph setup and execution

7. **Egyptian CLI** (`egyptian_main.py`)
   - Command-line interface for Egyptian stocks
   - Live updates and analysis results

## 🧪 Testing

### Run Tests
```bash
python test_egyptian_stocks.py
```

### Test Coverage
- ✅ Egyptian configuration loading
- ✅ Data interface functions
- ✅ Trading graph initialization
- ✅ Multiple stock testing
- ✅ Symbol validation
- ✅ Market information retrieval

## 📊 Example Analysis

### Commercial International Bank (COMI)
```bash
python cli/egyptian_main.py analyze COMI --live
```

**Output includes:**
- Egyptian market technical analysis
- Banking sector news and trends
- CBE policy impact
- EGP currency considerations
- Regional economic factors
- Final trading decision (BUY/HOLD/SELL)

## 🔍 Troubleshooting

### Common Issues

1. **Symbol Not Found**
   ```bash
   python cli/egyptian_main.py validate <SYMBOL>
   ```

2. **No Data Available**
   - Check if market is open (Sunday-Thursday, 10:00-14:30 Cairo time)
   - Verify symbol is in supported list
   - Check internet connection for online data

3. **Analysis Errors**
   - Enable debug mode: `--debug`
   - Check date format (YYYY-MM-DD)
   - Verify analyst selection

### Debug Mode
```bash
python cli/egyptian_main.py analyze COMI --debug
```

## 📚 Additional Resources

### Egyptian Market Information
- [Egyptian Exchange Official Website](https://www.egx.com.eg)
- [Central Bank of Egypt](https://www.cbe.org.eg)
- [Egyptian Financial Supervisory Authority](https://www.fra.gov.eg)

### Trading Hours
- **Sunday-Thursday**: 10:00 - 14:30 (Cairo time)
- **Friday-Saturday**: Closed
- **Holidays**: Check `egyptian_config.py` for holiday list

### Currency Information
- **Base Currency**: Egyptian Pound (EGP)
- **Exchange Rate**: Consider EGP/USD fluctuations
- **Inflation Impact**: Monitor CBE inflation targets

## 🤝 Contributing

### Adding New Egyptian Stocks
1. Update `EGYPTIAN_CONFIG["major_stocks"]` in `egyptian_config.py`
2. Add stock information (name, sector, Yahoo symbol)
3. Test with `python test_egyptian_stocks.py`

### Adding New Analysts
1. Create analyst file in `agents/analysts/`
2. Add to `egyptian_trading_graph.py`
3. Update CLI commands
4. Test integration

## 📄 License

This Egyptian market integration follows the same license as the main Trading Agents project.

---

**🇪🇬 Ready to analyze Egyptian stocks with AI-powered trading agents!**


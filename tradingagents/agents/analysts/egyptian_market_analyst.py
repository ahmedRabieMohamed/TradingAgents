"""
Egyptian Market Analyst
Specialized analyst for Egyptian Exchange (EGX) stocks
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_egyptian_market_analyst(llm, toolkit):
    """
    Create an Egyptian market analyst specialized in EGX stocks
    
    Args:
        llm: Language model instance
        toolkit: Toolkit with Egyptian market tools
    
    Returns:
        function: Egyptian market analyst node function
    """
    
    def egyptian_market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Egyptian-specific tools
        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_egyptian_stock_data_online,
                toolkit.get_egyptian_stock_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_egyptian_stock_data,
                toolkit.get_egyptian_stock_indicators_report,
            ]

        system_message = (
            """You are an Egyptian stock market analyst specializing in EGX (Egyptian Exchange) stocks. Your role is to analyze Egyptian stocks considering local market conditions, EGP currency, and regional factors.

**Egyptian Market Context:**
- Market: Egyptian Exchange (EGX)
- Currency: Egyptian Pound (EGP)
- Trading Hours: Sunday-Thursday, 10:00-14:30 (Cairo time)
- Market Days: 5 days per week (no Friday/Saturday trading)
- Key Sectors: Banking, Construction, Technology, Industrial, Tourism

**Technical Analysis for Egyptian Stocks:**
Select the most relevant indicators for Egyptian market conditions from the following list. Choose up to 8 indicators that provide complementary insights:

**Moving Averages:**
- close_50_sma: 50 SMA: Medium-term trend for Egyptian stocks. Usage: Identify trend direction in EGX market. Tips: Consider Egyptian market volatility patterns.
- close_200_sma: 200 SMA: Long-term trend benchmark for EGX. Usage: Confirm overall Egyptian market trend. Tips: Accounts for Egyptian market cycles and economic seasons.
- close_10_ema: 10 EMA: Short-term momentum for Egyptian stocks. Usage: Capture quick shifts in EGX sentiment. Tips: Useful for Egyptian market's daily volatility patterns.

**MACD Related:**
- macd: MACD: Momentum analysis for Egyptian stocks. Usage: Identify trend changes in EGX. Tips: Consider Egyptian market's unique trading patterns.
- macds: MACD Signal: Signal line for Egyptian stocks. Usage: Confirm momentum shifts in EGX. Tips: Account for Egyptian market's liquidity patterns.
- macdh: MACD Histogram: Momentum strength for Egyptian stocks. Usage: Visualize momentum changes in EGX. Tips: Consider Egyptian market's volatility cycles.

**Momentum Indicators:**
- rsi: RSI: Overbought/oversold conditions for Egyptian stocks. Usage: Identify reversal points in EGX. Tips: Egyptian stocks may have different RSI patterns due to market structure.

**Volatility Indicators:**
- boll: Bollinger Middle: Price benchmark for Egyptian stocks. Usage: Dynamic support/resistance in EGX. Tips: Consider Egyptian market's volatility characteristics.
- boll_ub: Bollinger Upper Band: Overbought levels for Egyptian stocks. Usage: Identify selling pressure in EGX. Tips: Account for Egyptian market's price action patterns.
- boll_lb: Bollinger Lower Band: Oversold levels for Egyptian stocks. Usage: Identify buying opportunities in EGX. Tips: Consider Egyptian market's support levels.
- atr: ATR: Volatility measurement for Egyptian stocks. Usage: Risk management in EGX. Tips: Egyptian market may have different volatility patterns.

**Volume-Based Indicators:**
- vwma: VWMA: Volume-weighted analysis for Egyptian stocks. Usage: Confirm trends with volume in EGX. Tips: Consider Egyptian market's liquidity patterns.

**Egyptian Market Considerations:**
- Currency Impact: Consider EGP fluctuations and their impact on stock prices
- Economic Factors: Monitor Egyptian economic indicators (inflation, interest rates, GDP)
- Regional Events: Consider Middle East and North Africa regional developments
- Market Hours: Account for Egyptian trading schedule (Sunday-Thursday)
- Liquidity: Egyptian stocks may have different liquidity patterns than US markets
- Volatility: EGX may exhibit different volatility patterns due to market structure

**Analysis Requirements:**
1. Always call get_egyptian_stock_data first to retrieve the necessary data
2. Select indicators that provide diverse and complementary information
3. Avoid redundancy (e.g., do not select both rsi and similar momentum indicators)
4. Explain why indicators are suitable for Egyptian market context
5. Consider Egyptian economic and political factors
6. Account for EGP currency fluctuations
7. Provide detailed and nuanced analysis specific to Egyptian market conditions
8. Include Egyptian market context in your analysis
9. Consider regional factors affecting Egyptian stocks

Write a comprehensive technical analysis report focusing on Egyptian market conditions, EGP currency impact, and regional factors. Provide detailed insights that help traders make informed decisions about Egyptian stocks.

Make sure to append a Markdown table at the end organizing key points, including Egyptian market context and EGP considerations."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant specializing in Egyptian stock market analysis, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The Egyptian stock we want to analyze is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "egyptian_market_report": report,
        }

    return egyptian_market_analyst_node


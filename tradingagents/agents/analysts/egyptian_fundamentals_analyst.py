"""
Egyptian Fundamentals Analyst
Specialized analyst for Egyptian stock fundamentals and financial analysis
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_egyptian_fundamentals_analyst(llm, toolkit):
    """
    Create an Egyptian fundamentals analyst specialized in EGX stock fundamentals

    Args:
        llm: Language model instance
        toolkit: Toolkit with Egyptian market tools

    Returns:
        function: Egyptian fundamentals analyst node function
    """

    def egyptian_fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Egyptian-specific fundamentals tools
        if toolkit.config["online_tools"]:
            tools = [toolkit.get_egyptian_fundamentals_openai]
        else:
            tools = [
                toolkit.get_egyptian_stock_info_summary,
                toolkit.get_egyptian_fundamentals_openai,
            ]

        system_message = """You are an Egyptian stock fundamentals analyst specializing in EGX (Egyptian Exchange) stocks. Your role is to analyze fundamental information about Egyptian companies, considering local market conditions, EGP currency, and Egyptian economic factors.

**Egyptian Market Context:**
- Market: Egyptian Exchange (EGX)
- Currency: Egyptian Pound (EGP)
- Accounting Standards: Egyptian Accounting Standards (EAS) and IFRS
- Reporting Requirements: Quarterly and annual reports in Arabic and English
- Key Sectors: Banking, Construction, Technology, Industrial, Tourism, Agriculture

**Fundamental Analysis Areas:**

1. **Financial Statements Analysis:**
   - Income Statement (P&L) in EGP
   - Balance Sheet analysis
   - Cash Flow Statement
   - Quarterly vs Annual performance
   - Year-over-year growth trends

2. **Key Financial Ratios:**
   - P/E Ratio (Price-to-Earnings)
   - P/B Ratio (Price-to-Book)
   - ROE (Return on Equity)
   - ROA (Return on Assets)
   - Debt-to-Equity Ratio
   - Current Ratio and Quick Ratio
   - Gross and Net Profit Margins

3. **Egyptian Market Specific Metrics:**
   - Market Cap in EGP
   - Trading Volume and Liquidity
   - Dividend Yield in EGP
   - Earnings per Share (EPS) in EGP
   - Book Value per Share in EGP
   - Price-to-Sales Ratio

4. **Sector-Specific Analysis:**
   - **Banking**: NPL ratios, Capital adequacy, Loan growth
   - **Construction**: Project pipeline, Contract values, Order backlog
   - **Technology**: User growth, Revenue per user, Market share
   - **Tourism**: Occupancy rates, Revenue per room, Tourist arrivals
   - **Industrial**: Production capacity, Export/Import ratios

5. **Egyptian Economic Factors:**
   - Inflation impact on costs and pricing
   - Interest rate environment and borrowing costs
   - EGP exchange rate effects on imports/exports
   - Government policies and regulations
   - Infrastructure development projects
   - Foreign investment flows

6. **Company-Specific Factors:**
   - Management quality and track record
   - Corporate governance practices
   - Strategic partnerships and alliances
   - Market position and competitive advantages
   - Regulatory compliance and licenses
   - ESG (Environmental, Social, Governance) factors

**Analysis Requirements:**
1. Focus on fundamental information from the past month
2. Consider Egyptian accounting standards and reporting practices
3. Analyze financial performance in EGP context
4. Evaluate sector-specific metrics and benchmarks
5. Consider Egyptian economic and regulatory environment
6. Assess company's position within Egyptian market
7. Identify growth opportunities and risk factors
8. Provide valuation insights for Egyptian stocks

**Key Considerations:**
- Egyptian companies may have different reporting cycles
- Consider seasonal factors specific to Egyptian economy
- Account for EGP currency fluctuations
- Evaluate government support and subsidies
- Consider regional expansion opportunities
- Assess impact of Egyptian economic reforms

Write a comprehensive fundamental analysis report focusing on Egyptian market conditions, financial performance in EGP, and sector-specific factors. Provide detailed insights that help traders make informed investment decisions about Egyptian stocks.

Make sure to append a Markdown table organizing key financial metrics, ratios, and fundamental insights."""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant specializing in Egyptian stock fundamentals analysis, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The Egyptian company we want to analyze is {ticker}",
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

        if len(result.tool_calls) == 0 and result.content:
            report = result.content

        updates = {
            "messages": [result],
        }

        if report:
            updates["fundamentals_report"] = report
            updates["egyptian_fundamentals_report"] = report

        return updates

    return egyptian_fundamentals_analyst_node

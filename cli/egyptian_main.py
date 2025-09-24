"""
Egyptian Trading Agents CLI
Command-line interface for Egyptian Exchange (EGX) stock analysis
"""

from typing import Optional
import datetime
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.egyptian_trading_graph import EgyptianTradingAgentsGraph
from tradingagents.egyptian_config import EGYPTIAN_CONFIG
from cli.models import AnalystType
from cli.utils import *

console = Console()

app = typer.Typer(
    name="EgyptianTradingAgents",
    help="Egyptian TradingAgents CLI: Multi-Agents LLM Financial Trading Framework for Egyptian Exchange (EGX)",
    add_completion=True,  # Enable shell completion
)


# Create a deque to store recent messages with a maximum length
class EgyptianMessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # Store the complete final report
        self.agent_status = {
            # Egyptian Analyst Team
            "Egyptian Market Analyst": "pending",
            "Egyptian News Analyst": "pending",
            "Egyptian Fundamentals Analyst": "pending",
            # Research Team
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # Trading Team
            "Trader": "pending",
            # Risk Management Team
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            # Portfolio Management Team
            "Portfolio Manager": "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "egyptian_market_report": None,
            "egyptian_news_report": None,
            "egyptian_fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # For the panel display, only show the most recently updated section
        latest_section = None
        latest_content = None

        # Find the most recently updated section
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content

        if latest_section and latest_content:
            self.current_report = f"**{latest_section.replace('_', ' ').title()}**\n\n{latest_content[:500]}..."
            if len(latest_content) > 500:
                self.current_report += "\n\n... (truncated)"

    def get_status_table(self):
        table = Table(title="Egyptian Trading Agents Status", box=box.ROUNDED)
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")

        for agent, status in self.agent_status.items():
            status_style = "green" if status == "completed" else "yellow" if status == "running" else "red"
            table.add_row(agent, f"[{status_style}]{status}[/{status_style}]")

        return table

    def get_tool_calls_table(self):
        if not self.tool_calls:
            return Table(title="No Tool Calls Yet", box=box.ROUNDED)

        table = Table(title="Recent Egyptian Tool Calls", box=box.ROUNDED)
        table.add_column("Time", style="cyan", no_wrap=True)
        table.add_column("Tool", style="green")
        table.add_column("Args", style="yellow")

        for timestamp, tool_name, args in list(self.tool_calls)[-10:]:  # Show last 10
            args_str = str(args)[:50] + "..." if len(str(args)) > 50 else str(args)
            table.add_row(timestamp, tool_name, args_str)

        return table


# Global message buffer
message_buffer = EgyptianMessageBuffer()


def create_egyptian_layout():
    """Create the Egyptian CLI layout"""
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )

    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1),
    )

    layout["left"].split_column(
        Layout(name="status", size=10),
        Layout(name="reports", ratio=1),
    )

    layout["right"].split_column(
        Layout(name="tools", size=10),
        Layout(name="messages", ratio=1),
    )

    return layout


def update_egyptian_layout(layout):
    """Update the Egyptian layout with current data"""
    # Header
    header_text = Text("🇪🇬 Egyptian Trading Agents - EGX Analysis", style="bold blue")
    layout["header"].update(Panel(Align.center(header_text), style="blue"))

    # Status
    layout["status"].update(Panel(message_buffer.get_status_table(), title="Agent Status"))

    # Reports
    if message_buffer.current_report:
        layout["reports"].update(Panel(Markdown(message_buffer.current_report), title="Latest Report"))
    else:
        layout["reports"].update(Panel("No reports yet...", title="Reports"))

    # Tools
    layout["tools"].update(Panel(message_buffer.get_tool_calls_table(), title="Tool Calls"))

    # Messages
    if message_buffer.messages:
        messages_text = "\n".join([f"[{timestamp}] {msg_type}: {content[:100]}..." 
                                 for timestamp, msg_type, content in list(message_buffer.messages)[-10:]])
        layout["messages"].update(Panel(messages_text, title="Recent Messages"))
    else:
        layout["messages"].update(Panel("No messages yet...", title="Messages"))

    # Footer
    footer_text = Text("Egyptian Exchange (EGX) | Currency: EGP | Trading: Sun-Thu 10:00-14:30", style="dim")
    layout["footer"].update(Panel(Align.center(footer_text), style="dim"))


@app.command()
def analyze(
    symbol: str = typer.Argument(..., help="Egyptian stock symbol (e.g., COMI, ORAS, EFID)"),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Analysis date (YYYY-MM-DD)"),
    analysts: Optional[str] = typer.Option("egyptian_market,egyptian_news,egyptian_fundamentals", 
                                          "--analysts", "-a", help="Comma-separated list of analysts"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    live: bool = typer.Option(True, "--live/--no-live", help="Show live updates"),
):
    """
    Analyze an Egyptian stock using the trading agents framework.
    
    Examples:
    - egyptian-trading-agents analyze COMI
    - egyptian-trading-agents analyze ORAS --date 2025-01-15
    - egyptian-trading-agents analyze EFID --analysts egyptian_market,egyptian_fundamentals
    """
    
    # Validate Egyptian symbol
    if symbol.upper() not in EGYPTIAN_CONFIG["major_stocks"]:
        console.print(f"[red]Error: '{symbol}' is not a valid Egyptian stock symbol.[/red]")
        console.print(f"[yellow]Available Egyptian stocks: {', '.join(EGYPTIAN_CONFIG['major_stocks'].keys())}[/yellow]")
        raise typer.Exit(1)
    
    # Set analysis date
    if date:
        try:
            analysis_date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            console.print("[red]Error: Invalid date format. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)
    else:
        analysis_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Parse analysts
    analyst_list = [a.strip() for a in analysts.split(",")]
    valid_analysts = ["egyptian_market", "egyptian_news", "egyptian_fundamentals"]
    for analyst in analyst_list:
        if analyst not in valid_analysts:
            console.print(f"[red]Error: '{analyst}' is not a valid Egyptian analyst.[/red]")
            console.print(f"[yellow]Available analysts: {', '.join(valid_analysts)}[/yellow]")
            raise typer.Exit(1)
    
    # Display analysis info
    stock_info = EGYPTIAN_CONFIG["major_stocks"][symbol.upper()]
    console.print(f"\n[bold blue]🇪🇬 Egyptian Stock Analysis[/bold blue]")
    console.print(f"[cyan]Stock:[/cyan] {symbol} - {stock_info['name']}")
    console.print(f"[cyan]Sector:[/cyan] {stock_info['sector']}")
    console.print(f"[cyan]Market:[/cyan] {EGYPTIAN_CONFIG['market_name']} (EGX)")
    console.print(f"[cyan]Currency:[/cyan] {EGYPTIAN_CONFIG['currency']}")
    console.print(f"[cyan]Analysis Date:[/cyan] {analysis_date}")
    console.print(f"[cyan]Analysts:[/cyan] {', '.join(analyst_list)}")
    console.print(f"[cyan]Trading Hours:[/cyan] {EGYPTIAN_CONFIG['trading_hours']['start']}-{EGYPTIAN_CONFIG['trading_hours']['end']} (Sun-Thu)")
    
    if live:
        console.print("\n[yellow]Starting Egyptian analysis with live updates...[/yellow]")
        
        # Create layout
        layout = create_egyptian_layout()
        
        # Initialize Egyptian trading graph
        try:
            egyptian_graph = EgyptianTradingAgentsGraph(
                selected_analysts=analyst_list,
                debug=debug,
                config=EGYPTIAN_CONFIG
            )
            
            # Update initial status
            for analyst in analyst_list:
                message_buffer.update_agent_status(f"Egyptian {analyst.replace('egyptian_', '').title()} Analyst", "running")
            
            # Run analysis with live updates
            with Live(layout, refresh_per_second=2, screen=True):
                try:
                    final_state, signal = egyptian_graph.propagate(symbol.upper(), analysis_date)
                    
                    # Update final status
                    for analyst in analyst_list:
                        message_buffer.update_agent_status(f"Egyptian {analyst.replace('egyptian_', '').title()} Analyst", "completed")
                    
                    message_buffer.update_agent_status("Bull Researcher", "completed")
                    message_buffer.update_agent_status("Bear Researcher", "completed")
                    message_buffer.update_agent_status("Trader", "completed")
                    message_buffer.update_agent_status("Portfolio Manager", "completed")
                    
                    # Update report sections
                    if "egyptian_market_report" in final_state:
                        message_buffer.update_report_section("egyptian_market_report", final_state["egyptian_market_report"])
                    if "egyptian_news_report" in final_state:
                        message_buffer.update_report_section("egyptian_news_report", final_state["egyptian_news_report"])
                    if "egyptian_fundamentals_report" in final_state:
                        message_buffer.update_report_section("egyptian_fundamentals_report", final_state["egyptian_fundamentals_report"])
                    if "final_trade_decision" in final_state:
                        message_buffer.update_report_section("final_trade_decision", final_state["final_trade_decision"])
                    
                    # Store final report
                    message_buffer.final_report = final_state
                    
                except Exception as e:
                    console.print(f"[red]Error during analysis: {str(e)}[/red]")
                    raise typer.Exit(1)
        
        except Exception as e:
            console.print(f"[red]Error initializing Egyptian trading graph: {str(e)}[/red]")
            raise typer.Exit(1)
    
    else:
        # Run without live updates
        console.print("\n[yellow]Starting Egyptian analysis...[/yellow]")
        
        try:
            egyptian_graph = EgyptianTradingAgentsGraph(
                selected_analysts=analyst_list,
                debug=debug,
                config=EGYPTIAN_CONFIG
            )
            
            with Spinner("Analyzing Egyptian stock..."):
                final_state, signal = egyptian_graph.propagate(symbol.upper(), analysis_date)
            
            # Display results
            console.print("\n[bold green]✅ Egyptian Analysis Complete![/bold green]")
            console.print(f"[cyan]Final Decision:[/cyan] {signal}")
            
            # Display reports
            if "egyptian_market_report" in final_state and final_state["egyptian_market_report"]:
                console.print("\n[bold blue]📊 Egyptian Market Analysis[/bold blue]")
                console.print(Panel(Markdown(final_state["egyptian_market_report"]), title="Market Report"))
            
            if "egyptian_news_report" in final_state and final_state["egyptian_news_report"]:
                console.print("\n[bold blue]📰 Egyptian News Analysis[/bold blue]")
                console.print(Panel(Markdown(final_state["egyptian_news_report"]), title="News Report"))
            
            if "egyptian_fundamentals_report" in final_state and final_state["egyptian_fundamentals_report"]:
                console.print("\n[bold blue]📈 Egyptian Fundamentals Analysis[/bold blue]")
                console.print(Panel(Markdown(final_state["egyptian_fundamentals_report"]), title="Fundamentals Report"))
            
            if "final_trade_decision" in final_state and final_state["final_trade_decision"]:
                console.print("\n[bold green]🎯 Final Trading Decision[/bold green]")
                console.print(Panel(Markdown(final_state["final_trade_decision"]), title="Trade Decision"))
        
        except Exception as e:
            console.print(f"[red]Error during analysis: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def list_stocks():
    """List all available Egyptian stocks."""
    console.print(f"\n[bold blue]🇪🇬 Available Egyptian Stocks ({EGYPTIAN_CONFIG['market_name']})[/bold blue]")
    
    table = Table(title="Egyptian Exchange (EGX) Stocks", box=box.ROUNDED)
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Company Name", style="green")
    table.add_column("Sector", style="yellow")
    table.add_column("Yahoo Symbol", style="magenta")
    
    for symbol, info in EGYPTIAN_CONFIG["major_stocks"].items():
        table.add_row(symbol, info["name"], info["sector"], info["yahoo_symbol"])
    
    console.print(table)
    
    console.print(f"\n[cyan]Market Info:[/cyan]")
    console.print(f"- Market: {EGYPTIAN_CONFIG['market_name']} (EGX)")
    console.print(f"- Currency: {EGYPTIAN_CONFIG['currency']}")
    console.print(f"- Trading Hours: {EGYPTIAN_CONFIG['trading_hours']['start']}-{EGYPTIAN_CONFIG['trading_hours']['end']} (Sunday-Thursday)")
    console.print(f"- Timezone: {EGYPTIAN_CONFIG['trading_hours']['timezone']}")


@app.command()
def market_info():
    """Display Egyptian market information."""
    console.print(f"\n[bold blue]🇪🇬 Egyptian Exchange (EGX) Market Information[/bold blue]")
    
    # Market overview
    console.print(f"\n[bold cyan]Market Overview[/bold cyan]")
    console.print(f"- Market Name: {EGYPTIAN_CONFIG['market_name']}")
    console.print(f"- Market Code: {EGYPTIAN_CONFIG['market_code']}")
    console.print(f"- Currency: {EGYPTIAN_CONFIG['currency']}")
    console.print(f"- Country: {EGYPTIAN_CONFIG['country']}")
    console.print(f"- Timezone: {EGYPTIAN_CONFIG['timezone']}")
    
    # Trading hours
    console.print(f"\n[bold cyan]Trading Hours[/bold cyan]")
    console.print(f"- Days: {', '.join(EGYPTIAN_CONFIG['trading_hours']['days'])}")
    console.print(f"- Time: {EGYPTIAN_CONFIG['trading_hours']['start']} - {EGYPTIAN_CONFIG['trading_hours']['end']}")
    console.print(f"- Timezone: {EGYPTIAN_CONFIG['trading_hours']['timezone']}")
    
    # Market statistics
    console.print(f"\n[bold cyan]Market Statistics[/bold cyan]")
    console.print(f"- Total Stocks: {len(EGYPTIAN_CONFIG['major_stocks'])}")
    console.print(f"- Trading Days per Week: {EGYPTIAN_CONFIG['market_specific']['trading_days_per_week']}")
    console.print(f"- Volatility Threshold: {EGYPTIAN_CONFIG['market_specific']['volatility_threshold']*100:.1f}%")
    console.print(f"- Liquidity Threshold: {EGYPTIAN_CONFIG['market_specific']['liquidity_threshold']:,} EGP")
    
    # Market cap categories
    console.print(f"\n[bold cyan]Market Cap Categories[/bold cyan]")
    console.print(f"- Large Cap: >{EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['large_cap']:,} EGP")
    console.print(f"- Mid Cap: {EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['mid_cap']:,} - {EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['large_cap']:,} EGP")
    console.print(f"- Small Cap: <{EGYPTIAN_CONFIG['market_specific']['market_cap_categories']['mid_cap']:,} EGP")
    
    # Economic indicators
    console.print(f"\n[bold cyan]Economic Indicators[/bold cyan]")
    console.print(f"- Inflation Target: {EGYPTIAN_CONFIG['economic_indicators']['inflation_target']*100:.1f}%")
    console.print(f"- Interest Rate Range: {EGYPTIAN_CONFIG['economic_indicators']['interest_rate_range'][0]*100:.1f}% - {EGYPTIAN_CONFIG['economic_indicators']['interest_rate_range'][1]*100:.1f}%")
    console.print(f"- GDP Growth Target: {EGYPTIAN_CONFIG['economic_indicators']['gdp_growth_target']*100:.1f}%")


@app.command()
def sectors():
    """List Egyptian stocks by sector."""
    console.print(f"\n[bold blue]🇪🇬 Egyptian Stocks by Sector[/bold blue]")
    
    # Group stocks by sector
    sectors = {}
    for symbol, info in EGYPTIAN_CONFIG["major_stocks"].items():
        sector = info["sector"]
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append((symbol, info["name"]))
    
    # Display each sector
    for sector, stocks in sectors.items():
        console.print(f"\n[bold cyan]{sector}[/bold cyan]")
        table = Table(box=box.SIMPLE)
        table.add_column("Symbol", style="cyan")
        table.add_column("Company Name", style="green")
        
        for symbol, name in stocks:
            table.add_row(symbol, name)
        
        console.print(table)


@app.command()
def validate(
    symbol: str = typer.Argument(..., help="Egyptian stock symbol to validate"),
):
    """Validate if a symbol is a valid Egyptian stock."""
    if symbol.upper() in EGYPTIAN_CONFIG["major_stocks"]:
        stock_info = EGYPTIAN_CONFIG["major_stocks"][symbol.upper()]
        console.print(f"[green]✅ '{symbol}' is a valid Egyptian stock symbol[/green]")
        console.print(f"[cyan]Company:[/cyan] {stock_info['name']}")
        console.print(f"[cyan]Sector:[/cyan] {stock_info['sector']}")
        console.print(f"[cyan]Yahoo Symbol:[/cyan] {stock_info['yahoo_symbol']}")
    else:
        console.print(f"[red]❌ '{symbol}' is not a valid Egyptian stock symbol[/red]")
        console.print(f"[yellow]Available symbols: {', '.join(EGYPTIAN_CONFIG['major_stocks'].keys())}[/yellow]")


if __name__ == "__main__":
    app()


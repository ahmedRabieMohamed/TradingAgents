"""
Egyptian Trading Agents Graph
Specialized trading graph for Egyptian Exchange (EGX) stocks - matches US structure exactly
"""

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import RemoveMessage, HumanMessage

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.egyptian_config import EGYPTIAN_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.dataflows.interface import set_config
from tradingagents.agents.utils.egyptian_toolkit import EgyptianToolkit

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class EgyptianTradingAgentsGraph:
    """Main class that orchestrates the Egyptian trading agents framework."""

    def __init__(
        self,
        selected_analysts=["egyptian_market", "egyptian_news", "egyptian_fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Initialize the Egyptian trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default Egyptian config
        """
        self.debug = debug
        self.config = config or EGYPTIAN_CONFIG.copy()

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs
        if self.config["llm_provider"].lower() == "openai" or self.config["llm_provider"] == "ollama" or self.config["llm_provider"] == "openrouter":
            self.deep_thinking_llm = ChatOpenAI(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatOpenAI(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatAnthropic(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config["deep_think_llm"])
            self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config["quick_think_llm"])
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
        
        self.toolkit = EgyptianToolkit(config=self.config)

        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components (reuse US components)
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = EgyptianGraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources for the Egyptian market."""
        return {
            "egyptian_market": ToolNode(
                [
                    self.toolkit.get_egyptian_stock_data,
                    self.toolkit.get_egyptian_stock_data_online,
                    self.toolkit.get_egyptian_stock_indicators_report,
                    self.toolkit.get_egyptian_stock_indicators_report_online,
                ]
            ),
            "egyptian_news": ToolNode(
                [
                    self.toolkit.get_egyptian_news,
                    self.toolkit.get_egyptian_market_summary,
                ]
            ),
            "egyptian_fundamentals": ToolNode(
                [
                    self.toolkit.get_egyptian_fundamentals_openai,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """Run the Egyptian trading agents graph for a company on a specific date."""

        self.ticker = company_name

        # Initialize state
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # Standard mode without tracing
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file for Egyptian market."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "egyptian_market_report": final_state.get("egyptian_market_report"),
            "egyptian_news_report": final_state.get("egyptian_news_report"),
            "egyptian_fundamentals_report": final_state.get("egyptian_fundamentals_report"),
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
            "market_type": "Egyptian Exchange (EGX)",
            "currency": "EGP",
        }

        # Save to Egyptian results directory
        directory = Path(f"egyptian_results/{self.ticker}/EgyptianTradingAgents_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"egyptian_results/{self.ticker}/EgyptianTradingAgents_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on Egyptian decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal)

    def get_egyptian_market_info(self):
        """Get Egyptian market information."""
        return {
            "market_name": EGYPTIAN_CONFIG["market_name"],
            "market_code": EGYPTIAN_CONFIG["market_code"],
            "currency": EGYPTIAN_CONFIG["currency"],
            "trading_hours": EGYPTIAN_CONFIG["trading_hours"],
            "major_stocks_count": len(EGYPTIAN_CONFIG["major_stocks"]),
        }


class EgyptianGraphSetup:
    """Egyptian graph setup class that mimics the US GraphSetup exactly."""
    
    def __init__(
        self,
        quick_thinking_llm,
        deep_thinking_llm,
        toolkit,
        tool_nodes,
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic,
    ):
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.toolkit = toolkit
        self.tool_nodes = tool_nodes
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic

    def setup_graph(self, selected_analysts=["egyptian_market", "egyptian_news", "egyptian_fundamentals"]):
        """Set up and compile the Egyptian agent workflow graph - exactly like US structure."""
        if len(selected_analysts) == 0:
            raise ValueError("Egyptian Trading Agents Graph Setup Error: no analysts selected!")

        # Import Egyptian analysts
        from tradingagents.agents.analysts.egyptian_market_analyst import create_egyptian_market_analyst
        from tradingagents.agents.analysts.egyptian_news_analyst import create_egyptian_news_analyst
        from tradingagents.agents.analysts.egyptian_fundamentals_analyst import create_egyptian_fundamentals_analyst

        # Create analyst nodes
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}

        if "egyptian_market" in selected_analysts:
            analyst_nodes["market"] = create_egyptian_market_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["market"] = create_msg_delete()
            tool_nodes["market"] = self.tool_nodes["egyptian_market"]

        if "egyptian_news" in selected_analysts:
            analyst_nodes["news"] = create_egyptian_news_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["news"] = create_msg_delete()
            tool_nodes["news"] = self.tool_nodes["egyptian_news"]

        if "egyptian_fundamentals" in selected_analysts:
            analyst_nodes["fundamentals"] = create_egyptian_fundamentals_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["fundamentals"] = create_msg_delete()
            tool_nodes["fundamentals"] = self.tool_nodes["egyptian_fundamentals"]


        # Create researcher and manager nodes (same as US)
        bull_researcher_node = create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        bear_researcher_node = create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        research_manager_node = create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        trader_node = create_trader(self.quick_thinking_llm, self.trader_memory)

        # Create risk analysis nodes (same as US)
        risky_analyst = create_risky_debator(self.quick_thinking_llm)
        neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
        safe_analyst = create_safe_debator(self.quick_thinking_llm)
        risk_manager_node = create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # Create workflow
        from langgraph.graph import StateGraph, END, START
        workflow = StateGraph(AgentState)

        # Add state mapping node first
        workflow.add_node("state_mapper", create_egyptian_state_mapper())

        # Map Egyptian analysts to standard names for compatibility
        analyst_mapping = {
            "egyptian_market": "market",
            "egyptian_news": "news", 
            "egyptian_fundamentals": "fundamentals"
        }

        # Convert selected_analysts to standard names
        standard_analysts = [analyst_mapping.get(analyst, analyst) for analyst in selected_analysts]

        # Add analyst nodes to the graph (using standard names)
        for analyst_type in standard_analysts:
            if analyst_type in analyst_nodes:
                workflow.add_node(f"{analyst_type.capitalize()} Analyst", analyst_nodes[analyst_type])
                workflow.add_node(f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type])
                workflow.add_node(f"tools_{analyst_type}", tool_nodes.get(analyst_type, self._create_empty_tool_node()))

        # Add other nodes (same as US)
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Risky Analyst", risky_analyst)
        workflow.add_node("Neutral Analyst", neutral_analyst)
        workflow.add_node("Safe Analyst", safe_analyst)
        workflow.add_node("Risk Judge", risk_manager_node)

        # Define edges (same structure as US)
        # Start with state mapping
        workflow.add_edge(START, "state_mapper")
        
        # From state mapper to first analyst
        first_analyst = standard_analysts[0]
        workflow.add_edge("state_mapper", f"{first_analyst.capitalize()} Analyst")

        # Connect analysts in sequence (same as US)
        for i, analyst_type in enumerate(standard_analysts):
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # Add conditional edges for current analyst
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)

            # Connect to next analyst or to Bull Researcher if this is the last analyst
            if i < len(standard_analysts) - 1:
                next_analyst = f"{standard_analysts[i+1].capitalize()} Analyst"
                workflow.add_edge(current_clear, next_analyst)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        # Add remaining edges (exactly like US)
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")
        workflow.add_conditional_edges(
            "Risky Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Safe Analyst": "Safe Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Safe Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Risky Analyst": "Risky Analyst",
                "Risk Judge": "Risk Judge",
            },
        )

        workflow.add_edge("Risk Judge", END)

        # Compile and return
        return workflow.compile()


    def _create_empty_tool_node(self):
        """Create an empty tool node."""
        from langgraph.prebuilt import ToolNode
        return ToolNode([])


def create_egyptian_state_mapper():
    """Create state mapping function to convert Egyptian reports to standard format"""
    def map_state(state):
        """Map Egyptian reports to standard state structure for compatibility with existing agents"""
        # Map Egyptian reports to standard format
        mapped_state = state.copy()
        
        # Map Egyptian market report to standard market report
        if "egyptian_market_report" in state and state["egyptian_market_report"]:
            mapped_state["market_report"] = state["egyptian_market_report"]
        
        # Map Egyptian news report to standard news report
        if "egyptian_news_report" in state and state["egyptian_news_report"]:
            mapped_state["news_report"] = state["egyptian_news_report"]
        
        # Map Egyptian fundamentals report to standard fundamentals report
        if "egyptian_fundamentals_report" in state and state["egyptian_fundamentals_report"]:
            mapped_state["fundamentals_report"] = state["egyptian_fundamentals_report"]
        
        # Set empty sentiment report for Egyptian market (no social media analysis)
        mapped_state["sentiment_report"] = "No social media analysis available for Egyptian market."
        
        return mapped_state
    
    return map_state

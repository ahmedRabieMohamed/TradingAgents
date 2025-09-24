"""
Egyptian Trading Agents Graph
Specialized trading graph for Egyptian Exchange (EGX) stocks
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
            selected_analysts: List of Egyptian analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses Egyptian config
        """
        self.debug = debug
        self.config = config or EGYPTIAN_CONFIG

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "egyptian_data_cache"),
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
        self.bull_memory = FinancialSituationMemory("egyptian_bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("egyptian_bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("egyptian_trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("egyptian_invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("egyptian_risk_manager_memory", self.config)

        # Create Egyptian tool nodes
        self.tool_nodes = self._create_egyptian_tool_nodes()

        # Initialize components
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

        # Set up the Egyptian graph
        self.graph = self.graph_setup.setup_egyptian_graph(selected_analysts)

    def _create_egyptian_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create Egyptian tool nodes for different data sources."""
        return {
            "egyptian_market": ToolNode(
                [
                    # Egyptian market tools
                    self.toolkit.get_egyptian_stock_data_online,
                    self.toolkit.get_egyptian_stock_indicators_report_online,
                    self.toolkit.get_egyptian_stock_data,
                    self.toolkit.get_egyptian_stock_indicators_report,
                ]
            ),
            "egyptian_news": ToolNode(
                [
                     self.toolkit.get_egyptian_news,
                     self.toolkit.get_egyptian_market_news,
                     self.toolkit.get_egyptian_market_summary,
                ]
            ),
            "egyptian_fundamentals": ToolNode(
                [
                    # Egyptian fundamentals tools
                    self.toolkit.get_egyptian_fundamentals_openai,
                    self.toolkit.get_egyptian_stock_info_summary,
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
        self._log_egyptian_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_egyptian_state(self, trade_date, final_state):
        """Log the final Egyptian state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "egyptian_market_report": final_state.get("egyptian_market_report", ""),
            "egyptian_news_report": final_state.get("egyptian_news_report", ""),
            "egyptian_fundamentals_report": final_state.get("egyptian_fundamentals_report", ""),
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
            "major_stocks": EGYPTIAN_CONFIG["major_stocks"],
            "total_stocks": len(EGYPTIAN_CONFIG["major_stocks"]),
        }

    def validate_egyptian_symbol(self, symbol):
        """Validate if symbol is a known Egyptian stock."""
        return symbol.upper() in EGYPTIAN_CONFIG["major_stocks"]

    def get_available_egyptian_stocks(self):
        """Get list of available Egyptian stocks."""
        return list(EGYPTIAN_CONFIG["major_stocks"].keys())


class EgyptianGraphSetup:
    """Handles the setup and configuration of the Egyptian agent graph."""

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        toolkit: EgyptianToolkit,
        tool_nodes: Dict[str, ToolNode],
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
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

    def setup_egyptian_graph(
        self, selected_analysts=["egyptian_market", "egyptian_news", "egyptian_fundamentals"]
    ):
        """Set up and compile the Egyptian agent workflow graph.

        Args:
            selected_analysts (list): List of Egyptian analyst types to include. Options are:
                - "egyptian_market": Egyptian market analyst
                - "egyptian_news": Egyptian news analyst
                - "egyptian_fundamentals": Egyptian fundamentals analyst
        """
        if len(selected_analysts) == 0:
            raise ValueError("Egyptian Trading Agents Graph Setup Error: no analysts selected!")

        # Import Egyptian analysts
        from tradingagents.agents.analysts.egyptian_market_analyst import create_egyptian_market_analyst
        from tradingagents.agents.analysts.egyptian_news_analyst import create_egyptian_news_analyst
        from tradingagents.agents.analysts.egyptian_fundamentals_analyst import create_egyptian_fundamentals_analyst

        # Create Egyptian analyst nodes
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}

        if "egyptian_market" in selected_analysts:
            analyst_nodes["egyptian_market"] = create_egyptian_market_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["egyptian_market"] = create_egyptian_msg_delete()
            tool_nodes["egyptian_market"] = self.tool_nodes["egyptian_market"]

        if "egyptian_news" in selected_analysts:
            analyst_nodes["egyptian_news"] = create_egyptian_news_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["egyptian_news"] = create_egyptian_msg_delete()
            tool_nodes["egyptian_news"] = self.tool_nodes["egyptian_news"]

        if "egyptian_fundamentals" in selected_analysts:
            analyst_nodes["egyptian_fundamentals"] = create_egyptian_fundamentals_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["egyptian_fundamentals"] = create_egyptian_msg_delete()
            tool_nodes["egyptian_fundamentals"] = self.tool_nodes["egyptian_fundamentals"]

        # Create researcher and manager nodes (reuse existing ones)
        bull_researcher_node = create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        bear_researcher_node = create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        trader_node = create_trader(self.deep_thinking_llm, self.trader_memory)
        invest_judge_node = create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        risk_manager_node = create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # Create the Egyptian graph
        from langgraph.graph import StateGraph, END

        workflow = StateGraph(AgentState)

        # Add Egyptian analyst nodes
        for analyst_name in selected_analysts:
            workflow.add_node(analyst_name, analyst_nodes[analyst_name])
            workflow.add_node(f"{analyst_name}_tools", tool_nodes[analyst_name])
            workflow.add_node(f"{analyst_name}_delete", delete_nodes[analyst_name])

        # Add state mapping node to convert Egyptian reports to standard format
        workflow.add_node("state_mapper", create_egyptian_state_mapper())
        
        # Add researcher and manager nodes
        workflow.add_node("bull_researcher", bull_researcher_node)
        workflow.add_node("bear_researcher", bear_researcher_node)
        workflow.add_node("trader", trader_node)
        workflow.add_node("invest_judge", invest_judge_node)
        workflow.add_node("risk_manager", risk_manager_node)

        # Add edges for Egyptian analysts
        for analyst_name in selected_analysts:
            workflow.add_edge(analyst_name, f"{analyst_name}_tools")
            workflow.add_edge(f"{analyst_name}_tools", f"{analyst_name}_delete")
            workflow.add_edge(f"{analyst_name}_delete", "state_mapper")
        
        # Add edge from state mapper to bull researcher
        workflow.add_edge("state_mapper", "bull_researcher")

        # Add edges for researchers and managers
        workflow.add_edge("bull_researcher", "bear_researcher")
        workflow.add_edge("bear_researcher", "invest_judge")
        workflow.add_edge("invest_judge", "trader")
        workflow.add_edge("trader", "risk_manager")
        workflow.add_edge("risk_manager", END)

        # Set entry point
        workflow.set_entry_point(selected_analysts[0])

        # Compile the graph
        return workflow.compile()


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


"""Pydantic v2 schemas for the REST API."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Markets ---


class MarketSchema(BaseModel):
    id: str
    name: str
    exchange: str
    currency: str
    trading_days: list[str]
    ticker_suffix: str
    example_tickers: list[str] = []


class MarketsResponse(BaseModel):
    markets: list[MarketSchema]


# --- Stocks ---


class StockValidationResponse(BaseModel):
    valid: bool
    ticker: str
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None


class StockValidationError(BaseModel):
    valid: bool = False
    ticker: str
    error: str


# --- Analysis ---


class AnalysisRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    market_id: str
    analysis_date: date
    trade_horizon: str
    research_depth: str = "medium"
    analysts: list[str] = Field(..., min_length=1)
    llm_provider: str
    quick_think_model: str
    deep_think_model: str
    stock_name: str = ""
    stock_price_at_analysis: Optional[float] = None


class AnalysisCreateResponse(BaseModel):
    session_id: str
    status: str
    websocket_url: str


class AnalysisSessionResponse(BaseModel):
    id: str
    ticker: str
    market_id: str
    analysis_date: date
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    trade_horizon: str
    research_depth: str
    analysts: list[str]
    llm_provider: str
    quick_think_model: str
    deep_think_model: str
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    reports_path: str
    stock_name: str
    stock_price_at_analysis: Optional[float] = None
    reports: list["AgentReportSchema"] = Field(default=[], validation_alias="agent_reports")
    simulation: Optional["SimulationResultSchema"] = Field(default=None, validation_alias="simulation_result")

    model_config = {"from_attributes": True, "populate_by_name": True}


class SimulationSummary(BaseModel):
    entry_price: float
    exit_price: float
    return_pct: float
    is_win: bool


class AnalysisListItem(BaseModel):
    id: str
    ticker: str
    market_id: str
    analysis_date: date
    created_at: datetime
    status: str
    trade_horizon: str
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    stock_name: str
    stock_price_at_analysis: Optional[float] = None
    simulation: Optional[SimulationSummary] = None

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    analyses: list[AnalysisListItem]
    total: int


# --- Agent Reports ---


class AgentReportSchema(BaseModel):
    id: str
    session_id: str
    agent_name: str
    phase: str
    content: str
    created_at: datetime
    sequence: int

    model_config = {"from_attributes": True}


# --- Simulation ---


class SimulationResultSchema(BaseModel):
    id: str
    session_id: str
    entry_price: float
    exit_price: float
    horizon_end_date: date
    return_pct: float
    is_win: bool
    simulated_at: datetime

    model_config = {"from_attributes": True}


class SimulationTriggerResponse(BaseModel):
    id: str
    session_id: str
    status: str
    message: str


# --- Performance ---


class PerformanceResponse(BaseModel):
    total_analyses: int = 0
    total_simulations: int = 0
    win_rate: Optional[float] = None
    avg_return_pct: Optional[float] = None
    by_market: dict[str, dict] = {}
    by_horizon: dict[str, dict] = {}


# --- Settings ---


class UserSettingsResponse(BaseModel):
    default_market: str = "us"
    default_horizon: str = "short-term"
    default_depth: str = "medium"
    default_llm_provider: str = "openai"
    api_keys: dict[str, bool] = {}


class SettingsUpdateRequest(BaseModel):
    default_market: Optional[str] = None
    default_horizon: Optional[str] = None
    default_depth: Optional[str] = None
    default_llm_provider: Optional[str] = None
    api_keys: Optional[dict[str, str]] = None


# --- LLM Providers ---


class LLMProviderSchema(BaseModel):
    id: str
    name: str
    models: list[str]
    requires_api_key: bool
    is_configured: bool = False


class LLMProvidersResponse(BaseModel):
    providers: list[LLMProviderSchema]


# --- Market Overview ---


class StockSnapshot(BaseModel):
    ticker: str
    name: str
    name_ar: Optional[str] = None
    sector: str
    price: float
    currency: str
    change: float
    change_pct: float


class IndexData(BaseModel):
    name: str
    symbol: str
    value: float
    change: float
    change_pct: float


class MarketSummary(BaseModel):
    total_stocks: int
    gainers_count: int
    losers_count: int
    unchanged_count: int
    breadth_pct: float


class MarketOverviewResponse(BaseModel):
    market_id: str
    market_status: str
    last_updated: str
    indices: list[IndexData]
    summary: MarketSummary
    stocks: list[StockSnapshot]
    gainers: list[StockSnapshot]
    losers: list[StockSnapshot]


class NewsArticle(BaseModel):
    title: str
    snippet: str = ""
    source: str = "Unknown"
    url: str = ""
    published_at: Optional[str] = None
    is_hot: bool = False


class MarketNewsResponse(BaseModel):
    market_id: str
    ticker: Optional[str] = None
    articles: list[NewsArticle]


# --- Paper Trading & Portfolio ---


class PositionResponse(BaseModel):
    id: str
    portfolio_id: str
    analysis_session_id: Optional[str] = None
    ticker: str
    market_id: str
    direction: str
    quantity: int
    entry_price: float
    entry_date: datetime
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    status: str
    realized_pnl: Optional[float] = None
    realized_pnl_pct: Optional[float] = None
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    days_held: int = 0
    recommendation: Optional[str] = None
    confidence: Optional[float] = None

    model_config = {"from_attributes": True}


class PortfolioResponse(BaseModel):
    id: str
    starting_balance: float
    cash_balance: float
    currency: str
    total_value: float
    total_pnl: float
    total_pnl_pct: float
    open_positions_count: int
    open_positions: list[PositionResponse] = []


class TradeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    market_id: str
    direction: str = Field(..., pattern="^(long|short)$")
    quantity: int = Field(..., gt=0)
    analysis_session_id: Optional[str] = None


class TradeExecutionResponse(BaseModel):
    position_id: str
    ticker: str
    direction: str
    quantity: int
    entry_price: float
    total_cost: float
    remaining_cash: float


class ClosePositionResponse(BaseModel):
    position_id: str
    ticker: str
    direction: str
    entry_price: float
    exit_price: float
    quantity: int
    realized_pnl: float
    realized_pnl_pct: float
    hold_days: int
    cash_balance: float


class TradeHistoryItem(BaseModel):
    id: str
    ticker: str
    market_id: str
    direction: str
    quantity: int
    entry_price: float
    exit_price: Optional[float] = None
    entry_date: datetime
    exit_date: Optional[datetime] = None
    realized_pnl: Optional[float] = None
    realized_pnl_pct: Optional[float] = None
    hold_days: int = 0
    recommendation: Optional[str] = None
    confidence: Optional[float] = None

    model_config = {"from_attributes": True}


class TradeHistoryResponse(BaseModel):
    total: int
    trades: list[TradeHistoryItem]


class EquityPointSchema(BaseModel):
    date: str
    value: float


class MarketBreakdown(BaseModel):
    count: int
    win_rate: float
    avg_return_pct: float


class TradeSummary(BaseModel):
    ticker: str
    pnl: float
    pnl_pct: float


class PortfolioAnalyticsResponse(BaseModel):
    total_trades: int
    win_rate: float
    avg_return_pct: float
    total_realized_pnl: float
    best_trade: Optional[TradeSummary] = None
    worst_trade: Optional[TradeSummary] = None
    by_market: dict[str, MarketBreakdown] = {}
    equity_curve: list[EquityPointSchema] = []


class AIComparisonSide(BaseModel):
    count: int
    avg_return_pct: float
    win_rate: float
    total_pnl: float


class AIComparisonResponse(BaseModel):
    followed: AIComparisonSide
    ignored: AIComparisonSide
    difference: dict

// === Market ===

export interface Market {
  id: string;
  name: string;
  exchange: string;
  currency: string;
  trading_days: string[];
  example_tickers: string[];
}

export interface MarketsResponse {
  markets: Market[];
}

// === Stock ===

export interface StockValidation {
  valid: boolean;
  ticker: string;
  name: string;
  price: number;
  currency: string;
  change_pct: number;
  market_id: string;
}

export interface StockValidationError {
  valid: false;
  error: string;
}

// === Analysis Session ===

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type TradeHorizon = 'intraday' | 'short-term' | 'medium-term' | 'long-term';
export type ResearchDepth = 'shallow' | 'medium' | 'deep';
export type Recommendation = 'BUY' | 'SELL' | 'HOLD';
export type AnalystType = 'market' | 'social' | 'news' | 'fundamentals';

export interface AnalysisRequest {
  ticker: string;
  market_id: string;
  analysis_date: string;
  trade_horizon: TradeHorizon;
  analysts: AnalystType[];
  research_depth: ResearchDepth;
  llm_provider: string;
  quick_think_model: string;
  deep_think_model: string;
  language?: string;
}

export interface AnalysisCreateResponse {
  session_id: string;
  status: AnalysisStatus;
  websocket_url: string;
}

export interface AgentReport {
  agent_name: string;
  phase: string;
  content: string;
  sequence: number;
}

export interface SimulationSummary {
  entry_price: number;
  exit_price: number;
  return_pct: number;
  is_win: boolean;
}

export interface AnalysisSession {
  id: string;
  ticker: string;
  market_id: string;
  stock_name: string;
  analysis_date: string;
  created_at: string;
  completed_at: string | null;
  status: AnalysisStatus;
  trade_horizon: TradeHorizon;
  research_depth: ResearchDepth;
  analysts: AnalystType[];
  llm_provider: string;
  recommendation: Recommendation | null;
  confidence: number | null;
  language?: string;
  reports: AgentReport[];
  simulation: SimulationResult | null;
}

export interface AnalysisListItem {
  id: string;
  ticker: string;
  market_id: string;
  stock_name: string;
  analysis_date: string;
  status: AnalysisStatus;
  trade_horizon: TradeHorizon;
  recommendation: Recommendation | null;
  confidence: number | null;
  simulation: SimulationSummary | null;
}

export interface AnalysisListResponse {
  total: number;
  items: AnalysisListItem[];
}

// === Simulation ===

export interface SimulationResult {
  session_id: string;
  entry_price: number;
  exit_price: number;
  horizon_end_date: string;
  return_pct: number;
  is_win: boolean;
  simulated_at: string;
}

// === Performance ===

export interface MarketPerformance {
  count: number;
  win_rate: number;
  avg_return_pct: number;
}

export interface HorizonPerformance {
  count: number;
  win_rate: number;
}

export interface PerformanceStats {
  total_analyses: number;
  total_simulations: number;
  simulated_count?: number;
  win_rate: number | null;
  avg_return_pct: number | null;
  by_market: Record<string, MarketPerformance>;
  by_horizon: Record<string, HorizonPerformance>;
}

// === Settings ===

export interface UserSettings {
  default_market: string;
  default_horizon: TradeHorizon;
  default_depth: ResearchDepth;
  default_llm_provider: string;
  api_keys: Record<string, boolean>;
}

export interface SettingsUpdate {
  default_market?: string;
  default_horizon?: TradeHorizon;
  default_depth?: ResearchDepth;
  default_llm_provider?: string;
  api_keys?: Record<string, string>;
  starting_balance?: number;
}

// === LLM Providers ===

export interface LLMProvider {
  id: string;
  name: string;
  configured: boolean;
  quick_models: string[];
  deep_models: string[];
}

export interface LLMProvidersResponse {
  providers: LLMProvider[];
}

// === WebSocket Events ===

export interface WSAgentStarted {
  type: 'agent_started';
  timestamp: string;
  agent_name: string;
  phase: string;
  description: string;
}

export interface WSAgentMessage {
  type: 'agent_message';
  timestamp: string;
  agent_name: string;
  content: string;
  message_type: 'info' | 'tool_call' | 'tool_result' | 'thinking';
}

export interface WSAgentCompleted {
  type: 'agent_completed';
  timestamp: string;
  agent_name: string;
  phase: string;
  report_preview: string;
  report_full: string;
}

export interface WSDebateRound {
  type: 'debate_round';
  timestamp: string;
  debate_type: 'investment' | 'risk';
  round: number;
  total_rounds: number;
  bull_argument?: string;
  bear_argument?: string;
  aggressive?: string;
  neutral?: string;
  conservative?: string;
}

export interface WSStatsUpdate {
  type: 'stats_update';
  timestamp: string;
  agents_completed: number;
  agents_total: number;
  llm_calls: number;
  tool_calls: number;
  tokens_in: number;
  tokens_out: number;
  reports_generated: number;
  elapsed_seconds: number;
}

export interface WSAnalysisCompleted {
  type: 'analysis_completed';
  timestamp: string;
  recommendation: Recommendation;
  confidence: number;
  summary: string;
}

export interface WSAnalysisFailed {
  type: 'analysis_failed';
  timestamp: string;
  error: string;
  phase: string;
  agent_name: string;
}

export interface WSAnalysisCancelled {
  type: 'analysis_cancelled';
  timestamp: string;
}

export type WSEvent =
  | WSAgentStarted
  | WSAgentMessage
  | WSAgentCompleted
  | WSDebateRound
  | WSStatsUpdate
  | WSAnalysisCompleted
  | WSAnalysisFailed
  | WSAnalysisCancelled;

// === Watchlist ===

export interface WatchlistItem {
  id: string;
  ticker: string;
  market_id: string;
  name: string;
  added_at: string;
  notes: string;
  price: number | null;
  change_pct: number | null;
  currency: string | null;
}

export interface WatchlistResponse {
  items: WatchlistItem[];
}

// === Price History (OHLC) ===

export interface OHLCBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PriceHistoryResponse {
  ticker: string;
  market_id: string;
  currency: string;
  period: string;
  interval: string;
  bars: OHLCBar[];
}

// === Market Overview ===

export interface StockSnapshot {
  ticker: string;
  name: string;
  name_ar: string | null;
  sector: string;
  price: number;
  currency: string;
  change: number;
  change_pct: number;
}

export interface IndexData {
  name: string;
  symbol: string;
  value: number;
  change: number;
  change_pct: number;
}

export interface MarketSummaryData {
  total_stocks: number;
  gainers_count: number;
  losers_count: number;
  unchanged_count: number;
  breadth_pct: number;
}

export interface MarketOverviewResponse {
  market_id: string;
  market_status: 'open' | 'closed';
  last_updated: string;
  indices: IndexData[];
  summary: MarketSummaryData;
  stocks: StockSnapshot[];
  gainers: StockSnapshot[];
  losers: StockSnapshot[];
}

export interface NewsArticle {
  title: string;
  snippet: string;
  source: string;
  url: string;
  published_at: string;
  is_hot: boolean;
}

export interface MarketNewsResponse {
  market_id: string;
  ticker: string | null;
  articles: NewsArticle[];
}

// === Portfolio & Paper Trading ===

export interface PositionResponse {
  id: string;
  ticker: string;
  market_id: string;
  direction: 'long' | 'short';
  quantity: number;
  entry_price: number;
  entry_date: string;
  exit_price: number | null;
  exit_date: string | null;
  status: 'open' | 'closed';
  realized_pnl: number | null;
  realized_pnl_pct: number | null;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  days_held: number;
  analysis_session_id: string | null;
  recommendation: string | null;
  confidence: number | null;
}

export interface PortfolioResponse {
  id: string;
  starting_balance: number;
  cash_balance: number;
  currency: string;
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions_count: number;
  open_positions: PositionResponse[];
}

export interface TradeRequest {
  ticker: string;
  market_id: string;
  direction: 'long' | 'short';
  quantity: number;
  analysis_session_id?: string;
}

export interface TradeExecutionResponse {
  position_id: string;
  ticker: string;
  direction: string;
  quantity: number;
  entry_price: number;
  total_cost: number;
  remaining_cash: number;
}

export interface ClosePositionResponse {
  position_id: string;
  ticker: string;
  direction: string;
  entry_price: number;
  exit_price: number;
  quantity: number;
  realized_pnl: number;
  realized_pnl_pct: number;
  hold_days: number;
  cash_balance: number;
}

export interface TradeHistoryItem {
  id: string;
  ticker: string;
  market_id: string;
  direction: string;
  quantity: number;
  entry_price: number;
  exit_price: number;
  entry_date: string;
  exit_date: string;
  realized_pnl: number;
  realized_pnl_pct: number;
  hold_days: number;
  recommendation: string | null;
  confidence: number | null;
}

export interface TradeHistoryResponse {
  total: number;
  trades: TradeHistoryItem[];
}

export interface EquityPoint {
  date: string;
  value: number;
}

export interface TradeSummary {
  ticker: string;
  pnl: number;
  pnl_pct: number;
}

export interface MarketBreakdown {
  count: number;
  win_rate: number;
  avg_return_pct: number;
}

export interface PortfolioAnalyticsResponse {
  total_trades: number;
  win_rate: number;
  avg_return_pct: number;
  total_realized_pnl: number;
  best_trade: TradeSummary | null;
  worst_trade: TradeSummary | null;
  by_market: Record<string, MarketBreakdown>;
  equity_curve: EquityPoint[];
}

export interface AIComparisonSide {
  count: number;
  avg_return_pct: number;
  win_rate: number;
  total_pnl: number;
}

export interface AIComparisonResponse {
  followed: AIComparisonSide;
  ignored: AIComparisonSide;
  difference: {
    return_advantage_pct: number;
    win_rate_advantage: number;
    message: string;
  };
}

// --- Smart Picks / Engines ---

export type EngineSignal = 'STRONG BUY' | 'BUY' | 'HOLD' | 'NEUTRAL' | 'SELL' | 'STRONG SELL';
export type VolatilityRegimeTag = 'calm' | 'normal' | 'elevated' | 'extreme';

export interface EngineResult {
  score?: number;
  signal?: EngineSignal;
  reason?: string;
  data_sufficient: boolean;
  weight: number;
  // Engine-specific extras (any subset may be present):
  rsi_value?: number;
  macd_line?: number;
  signal_line?: number;
  histogram?: number;
  crossover_age_bars?: number;
  realized_vol_annualized?: number;
  regime_tag?: VolatilityRegimeTag;
  pull_alpha?: number;
  // Existing engines also report ad-hoc extras (probability, expected, etc.) — keep open-ended:
  [extra: string]: unknown;
}

export interface SmartPick {
  ticker: string;
  company_name: string;
  company_name_ar?: string;
  sector: string;
  market_id: string;
  reason: string;
  combined_score: number;
  combined_score_raw: number;
  signal: EngineSignal;
  bullish_engines: number;
  total_engines: number;
  engines: Record<string, EngineResult>;
  news_sentiment?: { score: number | null; headline_count?: number };
  volatility_regime_tag: VolatilityRegimeTag;
  // Convenience display fields kept for backwards compatibility with the current UI:
  mc_probability?: number;
  mc_expected?: number;
  mc_best_case?: number;
  mc_worst_case?: number;
  momentum_score?: number;
  momentum_roc_5d?: number;
  momentum_roc_20d?: number;
  [extra: string]: unknown;
}

export interface SmartPicksResponse {
  market_id: string;
  computed_at: string;
  total_scored: number;
  total_failed: number;
  picks: SmartPick[];
}

export interface EngineScoreResponse {
  ticker: string;
  market_id: string;
  combined_score: number;
  combined_score_raw: number;
  combined_signal: EngineSignal;
  volatility_regime_tag: VolatilityRegimeTag;
  engines: Record<string, EngineResult>;
  news_sentiment?: { score: number | null };
}

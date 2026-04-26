import type {
  MarketsResponse,
  StockValidation,
  WatchlistResponse,
  WatchlistItem,
  AnalysisRequest,
  AnalysisCreateResponse,
  AnalysisSession,
  AnalysisListResponse,
  SimulationResult,
  PerformanceStats,
  UserSettings,
  SettingsUpdate,
  LLMProvidersResponse,
  MarketOverviewResponse,
  MarketNewsResponse,
  PriceHistoryResponse,
  PortfolioResponse,
  TradeRequest,
  TradeExecutionResponse,
  ClosePositionResponse,
  TradeHistoryResponse,
  PortfolioAnalyticsResponse,
  AIComparisonResponse,
} from '../types';

const API_BASE = 'http://localhost:8000/api';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, text);
  }

  const contentType = res.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    return res.json() as Promise<T>;
  }
  return res.text() as unknown as T;
}

async function get<T>(path: string): Promise<T> {
  return request<T>('GET', path);
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>('POST', path, body);
}

async function patch<T>(path: string, body?: unknown): Promise<T> {
  return request<T>('PATCH', path, body);
}

async function del(path: string): Promise<void> {
  await request<void>('DELETE', path);
}

// --- Markets ---

export function fetchMarkets(): Promise<MarketsResponse> {
  return get<MarketsResponse>('/markets');
}

export function validateStock(ticker: string, market: string): Promise<StockValidation> {
  return get<StockValidation>(`/stocks/validate?ticker=${encodeURIComponent(ticker)}&market=${encodeURIComponent(market)}`);
}

// --- CSV Export ---

export function downloadCsv(filename: string, headers: string[], rows: string[][]) {
  const csvContent = [
    headers.join(','),
    ...rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')),
  ].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// --- Watchlist ---

export function getWatchlist(): Promise<WatchlistResponse> {
  return get<WatchlistResponse>('/watchlist');
}

export function addToWatchlist(ticker: string, marketId: string, name: string): Promise<WatchlistItem> {
  return post<WatchlistItem>('/watchlist', { ticker, market_id: marketId, name });
}

export function removeFromWatchlist(itemId: string): Promise<void> {
  return del(`/watchlist/${itemId}`);
}

// --- Price History ---

export function getPriceHistory(ticker: string, marketId: string, period: string = '3mo'): Promise<PriceHistoryResponse> {
  return get<PriceHistoryResponse>(
    `/stocks/price-history?ticker=${encodeURIComponent(ticker)}&market_id=${encodeURIComponent(marketId)}&period=${encodeURIComponent(period)}`
  );
}

// --- Engines ---

export function getEngineScore(ticker: string, marketId: string, days = 7): Promise<any> {
  return get<any>(`/engines/score/${encodeURIComponent(ticker)}?market_id=${encodeURIComponent(marketId)}&days=${days}`);
}

export function getSmartPicks(marketId = 'egypt', limit = 10): Promise<any> {
  return get<any>(`/engines/smart-picks?market_id=${encodeURIComponent(marketId)}&limit=${limit}`);
}

export function getDangerAlerts(): Promise<any> {
  return get<any>('/engines/danger-alerts');
}

// --- Analysis ---

export function createAnalysis(req: AnalysisRequest): Promise<AnalysisCreateResponse> {
  return post<AnalysisCreateResponse>('/analysis', req);
}

export function getAnalysis(sessionId: string): Promise<AnalysisSession> {
  return get<AnalysisSession>(`/analysis/${sessionId}`);
}

export function listAnalyses(params?: Record<string, string>): Promise<AnalysisListResponse> {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return get<AnalysisListResponse>(`/analysis${query}`);
}

export function deleteAnalysis(sessionId: string): Promise<void> {
  return del(`/analysis/${sessionId}`);
}

export function updateAnalysisNotes(sessionId: string, notes?: string, tags?: string[]): Promise<{ notes: string; tags: string[] }> {
  return patch<{ notes: string; tags: string[] }>(`/analysis/${sessionId}/notes`, { notes, tags });
}

export function exportAnalysis(sessionId: string): Promise<string> {
  return get<string>(`/analysis/${sessionId}/export`);
}

export function simulateAnalysis(sessionId: string): Promise<SimulationResult> {
  return post<SimulationResult>(`/analysis/${sessionId}/simulate`);
}

// --- Performance ---

export function getPerformance(market?: string): Promise<PerformanceStats> {
  const query = market ? `?market=${encodeURIComponent(market)}` : '';
  return get<PerformanceStats>(`/performance${query}`);
}

// --- Settings ---

export function getSettings(): Promise<UserSettings> {
  return get<UserSettings>('/settings');
}

export function updateSettings(data: SettingsUpdate): Promise<UserSettings> {
  return patch<UserSettings>('/settings', data);
}

// --- LLM Providers ---

export function getLLMProviders(): Promise<LLMProvidersResponse> {
  return get<LLMProvidersResponse>('/llm-providers');
}

// --- Market Overview ---

export function fetchMarketOverview(marketId: string): Promise<MarketOverviewResponse> {
  return get<MarketOverviewResponse>(`/market-overview/${encodeURIComponent(marketId)}`);
}

export function fetchMarketNews(marketId: string, ticker?: string, limit?: number): Promise<MarketNewsResponse> {
  const params = new URLSearchParams();
  if (ticker) params.set('ticker', ticker);
  if (limit) params.set('limit', String(limit));
  const query = params.toString() ? `?${params.toString()}` : '';
  return get<MarketNewsResponse>(`/market-overview/${encodeURIComponent(marketId)}/news${query}`);
}

// --- Portfolio & Paper Trading ---

export function getPortfolio(): Promise<PortfolioResponse> {
  return get<PortfolioResponse>('/portfolio');
}

export function executeTrade(req: TradeRequest): Promise<TradeExecutionResponse> {
  return post<TradeExecutionResponse>('/portfolio/trade', req);
}

export function closePosition(positionId: string): Promise<ClosePositionResponse> {
  return post<ClosePositionResponse>(`/portfolio/positions/${positionId}/close`);
}

export function getTradeHistory(params?: Record<string, string>): Promise<TradeHistoryResponse> {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return get<TradeHistoryResponse>(`/portfolio/trades${query}`);
}

export function getPortfolioAnalytics(): Promise<PortfolioAnalyticsResponse> {
  return get<PortfolioAnalyticsResponse>('/portfolio/analytics');
}

export function getAIComparison(): Promise<AIComparisonResponse> {
  return get<AIComparisonResponse>('/portfolio/ai-comparison');
}

export function resetPortfolio(): Promise<{ message: string }> {
  return post<{ message: string }>('/portfolio/reset');
}

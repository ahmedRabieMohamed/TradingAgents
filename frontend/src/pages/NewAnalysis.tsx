import { useState, useCallback, useEffect, CSSProperties } from 'react';
import { useSearchParams } from 'react-router-dom';
import Topbar from '../components/layout/Topbar';
import MarketSelector from '../components/analysis/MarketSelector';
import TickerInput from '../components/analysis/TickerInput';
import ConfigPanel from '../components/analysis/ConfigPanel';
import AnalysisProgress from '../components/analysis/AnalysisProgress';
import ResultHero from '../components/analysis/ResultHero';
import ReportSection from '../components/analysis/ReportSection';
import MarketOverview from '../components/market-overview/MarketOverview';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAnalysisStore } from '../stores/analysisStore';
import { createAnalysis, getAnalysis } from '../services/api';
import type { StockValidation, AnalysisRequest, TradeHorizon, WSEvent } from '../types';

const STEPS = ['Market', 'Overview', 'Configure', 'Analyze', 'Results'] as const;

const AGENT_DISPLAY: Record<string, { icon: string; label: string }> = {
  market_analyst:        { icon: '\ud83d\udcca', label: 'Market Analysis' },
  'Market Analyst':      { icon: '\ud83d\udcca', label: 'Market Analysis' },
  news_analyst:          { icon: '\ud83d\udcf0', label: 'News Analysis' },
  'News Analyst':        { icon: '\ud83d\udcf0', label: 'News Analysis' },
  social_media_analyst:  { icon: '\ud83d\udcac', label: 'Social Sentiment' },
  'Social Media Analyst':{ icon: '\ud83d\udcac', label: 'Social Sentiment' },
  fundamentals_analyst:  { icon: '\ud83d\udcd1', label: 'Fundamentals' },
  'Fundamentals Analyst':{ icon: '\ud83d\udcd1', label: 'Fundamentals' },
  bull_researcher:       { icon: '\ud83d\udc02', label: 'Bull vs Bear Debate' },
  bear_researcher:       { icon: '\ud83d\udc02', label: 'Bull vs Bear Debate' },
  'Bull vs Bear Debate': { icon: '\ud83d\udc02', label: 'Bull vs Bear Debate' },
  trader:                { icon: '\ud83d\udcb9', label: 'Trader Recommendation' },
  Trader:                { icon: '\ud83d\udcb9', label: 'Trader Recommendation' },
  risk_manager:          { icon: '\ud83d\udee1\ufe0f', label: 'Risk Assessment' },
  'Risk Assessment':     { icon: '\ud83d\udee1\ufe0f', label: 'Risk Assessment' },
  portfolio_manager:     { icon: '\ud83d\udcbc', label: 'Portfolio Decision' },
  'Portfolio Manager':   { icon: '\ud83d\udcbc', label: 'Portfolio Decision' },
};

const pageStyle: CSSProperties = {
  padding: 24,
  maxWidth: 800,
};

// --- Step Indicator ---

const indicatorBar: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 0,
  marginBottom: 32,
};

function stepCircleStyle(state: 'done' | 'active' | 'pending'): CSSProperties {
  const bg =
    state === 'done'
      ? 'var(--green)'
      : state === 'active'
        ? 'var(--accent)'
        : 'var(--surface2)';
  const color =
    state === 'pending' ? 'var(--text3)' : '#fff';
  return {
    width: 28,
    height: 28,
    borderRadius: '50%',
    background: bg,
    color,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 12,
    fontWeight: 700,
    flexShrink: 0,
  };
}

function stepLabelStyle(state: 'done' | 'active' | 'pending'): CSSProperties {
  return {
    fontSize: 12,
    fontWeight: state === 'active' ? 600 : 400,
    color:
      state === 'done'
        ? 'var(--green)'
        : state === 'active'
          ? 'var(--accent)'
          : 'var(--text3)',
    marginLeft: 6,
    whiteSpace: 'nowrap',
  };
}

const connectorStyle = (done: boolean): CSSProperties => ({
  flex: 1,
  height: 2,
  background: done ? 'var(--green)' : 'var(--border)',
  margin: '0 8px',
  minWidth: 20,
});

// --- Section heading & back button ---

const sectionHeading: CSSProperties = {
  fontSize: 18,
  fontWeight: 600,
  color: 'var(--text)',
  marginBottom: 6,
};

const sectionSub: CSSProperties = {
  fontSize: 13,
  color: 'var(--text3)',
  marginBottom: 20,
};

const backBtn: CSSProperties = {
  padding: '6px 14px',
  background: 'transparent',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text2)',
  fontSize: 12,
  cursor: 'pointer',
  marginBottom: 20,
};

const saveBtnStyle: CSSProperties = {
  padding: '10px 24px',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--accent)',
  color: '#fff',
  fontSize: 14,
  fontWeight: 600,
  cursor: 'pointer',
  marginTop: 16,
};

const newAnalysisBtnStyle: CSSProperties = {
  padding: '10px 24px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--text2)',
  fontSize: 14,
  fontWeight: 600,
  cursor: 'pointer',
  marginTop: 16,
};

const reportListStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 12,
  marginTop: 24,
};

const btnRowStyle: CSSProperties = {
  display: 'flex',
  gap: 12,
  marginTop: 20,
};

const errorBox: CSSProperties = {
  padding: 12,
  background: 'rgba(239, 68, 68, 0.1)',
  border: '1px solid rgba(239, 68, 68, 0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#ef4444',
  fontSize: 13,
  marginBottom: 16,
};

export default function NewAnalysis() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [step, setStep] = useState(0);
  const [selectedMarket, setSelectedMarket] = useState<string | null>(null);
  const [selectedStock, setSelectedStock] = useState<StockValidation | null>(null);
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  const [tradeHorizon, setTradeHorizon] = useState<TradeHorizon>('short-term');
  const [analysisDate, setAnalysisDate] = useState('');
  const [startError, setStartError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [loadingSession, setLoadingSession] = useState(false);
  const [showCustomTicker, setShowCustomTicker] = useState(false);

  const analysisStore = useAnalysisStore();

  // Load past analysis when ?session= is in the URL
  useEffect(() => {
    const sessionId = searchParams.get('session');
    if (!sessionId) return;

    setLoadingSession(true);
    getAnalysis(sessionId)
      .then((session) => {
        analysisStore.reset();
        analysisStore.setSession(session.id);

        // Populate store with the completed session data
        if (session.recommendation) {
          analysisStore.handleEvent({
            type: 'analysis_completed',
            timestamp: session.completed_at || new Date().toISOString(),
            recommendation: session.recommendation,
            confidence: session.confidence ?? 0,
            summary: '',
          });
        }

        // Load reports into the store
        for (const report of session.reports || []) {
          analysisStore.handleEvent({
            type: 'agent_completed',
            timestamp: session.completed_at || new Date().toISOString(),
            agent_name: report.agent_name,
            phase: report.phase,
            report_preview: report.content.slice(0, 200),
            report_full: report.content,
          });
        }

        setSelectedMarket(session.market_id);
        setSelectedStock({
          valid: true,
          ticker: session.ticker,
          name: session.stock_name,
          price: 0,
          currency: session.market_id === 'egypt' ? 'EGP' : 'USD',
          change_pct: 0,
          market_id: session.market_id,
        });
        setTradeHorizon(session.trade_horizon);
        setAnalysisDate(session.analysis_date);
        setStep(4); // Go to results step
        setSearchParams({}, { replace: true }); // Clear query param
      })
      .catch((err) => {
        console.error('Failed to load session:', err);
      })
      .finally(() => {
        setLoadingSession(false);
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleEvent = useCallback(
    (event: WSEvent) => {
      analysisStore.handleEvent(event);

      if (event.type === 'analysis_completed') {
        setStep(4);
      }
    },
    // handleEvent is stable from zustand, safe to depend on
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const { connected } = useWebSocket(wsUrl, handleEvent);

  function getStepState(index: number): 'done' | 'active' | 'pending' {
    if (index < step) return 'done';
    if (index === step) return 'active';
    return 'pending';
  }

  function handleMarketSelect(marketId: string) {
    setSelectedMarket(marketId);
    setSelectedStock(null);
    setShowCustomTicker(false);
    setStep(1);
  }

  function handleStockValidated(stock: StockValidation) {
    setSelectedStock(stock);
    setStep(2);
  }

  function handleOverviewStockSelect(ticker: string, name: string) {
    if (!selectedMarket) return;
    // Create a StockValidation-compatible object from the overview selection
    const stock: StockValidation = {
      valid: true,
      ticker,
      name,
      price: 0,
      currency: selectedMarket === 'egypt' ? 'EGP' : 'USD',
      change_pct: 0,
      market_id: selectedMarket,
    };
    setSelectedStock(stock);
    setShowCustomTicker(false);
    setStep(2);
  }

  async function handleStartAnalysis(config: Partial<AnalysisRequest>) {
    setStartError(null);
    setStarting(true);

    try {
      const fullConfig: AnalysisRequest = {
        ticker: config.ticker || selectedStock?.ticker || '',
        market_id: config.market_id || selectedMarket || '',
        analysis_date: config.analysis_date || new Date().toISOString().slice(0, 10),
        trade_horizon: config.trade_horizon || 'short-term',
        analysts: config.analysts || ['market', 'news', 'social', 'fundamentals'],
        research_depth: config.research_depth || 'medium',
        llm_provider: config.llm_provider || 'openai',
        quick_think_model: config.quick_think_model || 'gpt-4o-mini',
        deep_think_model: config.deep_think_model || 'o1',
      };

      setTradeHorizon(fullConfig.trade_horizon);
      setAnalysisDate(fullConfig.analysis_date);

      const response = await createAnalysis(fullConfig);

      // Initialize store
      analysisStore.reset();
      analysisStore.setSession(response.session_id);

      // Connect WebSocket
      const wsBase = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = 'localhost:8000';
      setWsUrl(`${wsBase}//${wsHost}/api/analysis/ws/${response.session_id}`);

      setStep(3);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to start analysis';
      setStartError(message);
    } finally {
      setStarting(false);
    }
  }

  function goBack() {
    if (step === 3 || step === 4) {
      // Don't allow going back during or after analysis
      return;
    }
    if (step === 1) {
      setShowCustomTicker(false);
    }
    if (step > 0) {
      setStep(step - 1);
    }
  }

  if (loadingSession) {
    return (
      <>
        <Topbar title="Loading Analysis..." />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: 12, color: 'var(--text3)' }}>
          <span className="spinner" />
          <span>Loading analysis...</span>
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title="New Analysis" />
      <div style={pageStyle}>
        {/* Step indicator */}
        <div style={indicatorBar}>
          {STEPS.map((label, i) => {
            const state = getStepState(i);
            return (
              <div key={label} style={{ display: 'flex', alignItems: 'center', flex: i < STEPS.length - 1 ? 1 : undefined }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={stepCircleStyle(state)}>
                    {state === 'done' ? '\u2713' : i + 1}
                  </div>
                  <span style={stepLabelStyle(state)}>{label}</span>
                </div>
                {i < STEPS.length - 1 && <div style={connectorStyle(i < step)} />}
              </div>
            );
          })}
        </div>

        {/* Back button (steps 1-2 only) */}
        {step > 0 && step < 3 && (
          <button style={backBtn} onClick={goBack}>
            &larr; Back
          </button>
        )}

        {/* Step 1: Market */}
        {step === 0 && (
          <>
            <h2 style={sectionHeading}>Select Market</h2>
            <p style={sectionSub}>Choose the market you want to analyze a stock from.</p>
            <MarketSelector onSelect={handleMarketSelect} />
          </>
        )}

        {/* Step 2: Market Overview */}
        {step === 1 && selectedMarket && (
          <>
            <h2 style={sectionHeading}>Market Overview</h2>
            <p style={sectionSub}>Browse stocks or select one to analyze.</p>

            {showCustomTicker ? (
              <>
                <button
                  style={{
                    padding: '6px 14px',
                    background: 'transparent',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text2)',
                    fontSize: 12,
                    cursor: 'pointer',
                    marginBottom: 16,
                  }}
                  onClick={() => setShowCustomTicker(false)}
                >
                  &larr; Back to overview
                </button>
                <TickerInput marketId={selectedMarket} onValidated={handleStockValidated} />
              </>
            ) : (
              <>
                <MarketOverview
                  marketId={selectedMarket}
                  onSelectStock={handleOverviewStockSelect}
                />
                <button
                  style={{
                    padding: '8px 0',
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--accent)',
                    fontSize: 13,
                    cursor: 'pointer',
                    marginTop: 16,
                    textDecoration: 'underline',
                  }}
                  onClick={() => setShowCustomTicker(true)}
                >
                  Enter custom ticker
                </button>
              </>
            )}
          </>
        )}

        {/* Step 3: Configure */}
        {step === 2 && selectedMarket && selectedStock && (
          <>
            <h2 style={sectionHeading}>Configure Analysis</h2>
            <p style={sectionSub}>
              Set parameters for analyzing {selectedStock.name} ({selectedStock.ticker}).
            </p>
            {startError && <div style={errorBox}>{startError}</div>}
            <ConfigPanel
              ticker={selectedStock.ticker}
              marketId={selectedMarket}
              onStart={handleStartAnalysis}
            />
            {starting && (
              <p style={{ fontSize: 13, color: 'var(--text3)', marginTop: 12 }}>
                Starting analysis...
              </p>
            )}
          </>
        )}

        {/* Step 4: Analyze */}
        {step === 3 && (
          <>
            <h2 style={sectionHeading}>Analyzing {selectedStock?.name}</h2>
            <p style={sectionSub}>
              {connected
                ? 'Connected - receiving live updates from agents.'
                : 'Connecting to analysis stream...'}
            </p>
            <AnalysisProgress />
          </>
        )}

        {/* Step 5: Results */}
        {step === 4 && analysisStore.recommendation && analysisStore.confidence !== null && (
          <>
            <h2 style={sectionHeading}>Analysis Complete</h2>
            <p style={sectionSub}>
              {analysisStore.summary || 'Your analysis has been completed successfully.'}
            </p>
            <ResultHero
              recommendation={analysisStore.recommendation}
              confidence={analysisStore.confidence}
              ticker={selectedStock?.ticker || ''}
              market={selectedMarket || ''}
              horizon={tradeHorizon}
              date={analysisDate}
            />

            {/* Detailed Agent Reports */}
            {Object.keys(analysisStore.reports).length > 0 && (
              <div style={reportListStyle}>
                <h3 style={{ ...sectionHeading, fontSize: 16, marginTop: 8 }}>Detailed Reports</h3>
                {Object.entries(analysisStore.reports).map(([agentName, content], idx) => {
                  const display = AGENT_DISPLAY[agentName] || { icon: '\ud83d\udccb', label: agentName };
                  return (
                    <ReportSection
                      key={agentName}
                      icon={display.icon}
                      title={display.label}
                      content={content}
                      defaultOpen={idx === 0}
                    />
                  );
                })}
              </div>
            )}

            {/* Action buttons */}
            <div style={btnRowStyle}>
              <button
                style={saveBtnStyle}
                onClick={async () => {
                  if (!analysisStore.sessionId) return;
                  try {
                    const res = await fetch(
                      `http://localhost:8000/api/analysis/${analysisStore.sessionId}/export`
                    );
                    const markdown = await res.text();
                    const blob = new Blob([markdown], { type: 'text/markdown' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `analysis-${selectedStock?.ticker || 'report'}-${analysisDate || 'report'}.md`;
                    a.click();
                    URL.revokeObjectURL(url);
                  } catch {
                    // Silently fail - could add error toast later
                  }
                }}
              >
                Save Report
              </button>
              <button
                style={newAnalysisBtnStyle}
                onClick={() => {
                  analysisStore.reset();
                  setSelectedMarket(null);
                  setSelectedStock(null);
                  setWsUrl(null);
                  setStartError(null);
                  setShowCustomTicker(false);
                  setStep(0);
                }}
              >
                New Analysis
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
}

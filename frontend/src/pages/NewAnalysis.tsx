import { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Steps, Button, Typography, Space, Spin, Alert, Empty } from 'antd';
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  ReloadOutlined,
  DollarOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import Topbar from '../components/layout/Topbar';
import MarketSelector from '../components/analysis/MarketSelector';
import TickerInput from '../components/analysis/TickerInput';
import ConfigPanel from '../components/analysis/ConfigPanel';
import AnalysisProgress from '../components/analysis/AnalysisProgress';
import ResultHero from '../components/analysis/ResultHero';
import ReportSection from '../components/analysis/ReportSection';
import MarketOverview from '../components/market-overview/MarketOverview';
import CandlestickChart from '../components/analysis/CandlestickChart';
import TradeModal from '../components/portfolio/TradeModal';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAnalysisStore } from '../stores/analysisStore';
import { useWizardStore } from '../stores/wizardStore';
import { useLocaleStore } from '../stores/localeStore';
import { createAnalysis, getAnalysis } from '../services/api';
import type { StockValidation, AnalysisRequest, WSEvent } from '../types';

const { Title, Text, Paragraph } = Typography;

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

export default function NewAnalysis() {
  const { t } = useTranslation(['analysis', 'common']);
  const locale = useLocaleStore((s) => s.locale);
  const [searchParams, setSearchParams] = useSearchParams();

  // Persisted wizard state (survives navigation)
  const wizard = useWizardStore();
  const step = wizard.step;
  const selectedMarket = wizard.selectedMarket;
  const selectedStock = wizard.selectedStock;
  const wsUrl = wizard.wsUrl;
  const tradeHorizon = wizard.tradeHorizon;
  const analysisDate = wizard.analysisDate;
  const showCustomTicker = wizard.showCustomTicker;

  // Transient UI state (OK to lose on navigation)
  const [startError, setStartError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [loadingSession, setLoadingSession] = useState(false);
  const [tradeModalOpen, setTradeModalOpen] = useState(false);

  const analysisStore = useAnalysisStore();

  // On remount: if analysis completed while away, jump to results
  useEffect(() => {
    if (step === 3 && analysisStore.status === 'completed') {
      wizard.setStep(4);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load past analysis when ?session= is in the URL
  const sessionParam = searchParams.get('session');
  useEffect(() => {
    if (!sessionParam) return;

    setLoadingSession(true);
    getAnalysis(sessionParam)
      .then((session) => {
        analysisStore.reset();
        analysisStore.setSession(session.id);

        if (session.recommendation) {
          analysisStore.handleEvent({
            type: 'analysis_completed',
            timestamp: session.completed_at || new Date().toISOString(),
            recommendation: session.recommendation,
            confidence: session.confidence ?? 0,
            summary: '',
          });
        }

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

        wizard.setSelectedMarket(session.market_id);
        wizard.setSelectedStock({
          valid: true,
          ticker: session.ticker,
          name: session.stock_name,
          price: (session as any).stock_price_at_analysis ?? 0,
          currency: session.market_id === 'egypt' ? 'EGP' : 'USD',
          change_pct: 0,
          market_id: session.market_id,
        });
        wizard.setTradeHorizon(session.trade_horizon);
        wizard.setAnalysisDate(session.analysis_date);
        wizard.setStep(4);
        setSearchParams({}, { replace: true });
      })
      .catch((err) => {
        console.error('Failed to load session:', err);
        wizard.reset();
      })
      .finally(() => {
        setLoadingSession(false);
      });
  }, [sessionParam]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleEvent = useCallback(
    (event: WSEvent) => {
      analysisStore.handleEvent(event);
      if (event.type === 'analysis_completed') {
        wizard.setStep(4);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const { connected } = useWebSocket(wsUrl, handleEvent);

  function handleMarketSelect(marketId: string) {
    wizard.setSelectedMarket(marketId);
    wizard.setSelectedStock(null);
    wizard.setShowCustomTicker(false);
    wizard.setStep(1);
  }

  function handleStockValidated(stock: StockValidation) {
    wizard.setSelectedStock(stock);
    wizard.setStep(2);
  }

  function handleOverviewStockSelect(ticker: string, name: string) {
    if (!selectedMarket) return;
    const stock: StockValidation = {
      valid: true,
      ticker,
      name,
      price: 0,
      currency: selectedMarket === 'egypt' ? 'EGP' : 'USD',
      change_pct: 0,
      market_id: selectedMarket,
    };
    wizard.setSelectedStock(stock);
    wizard.setShowCustomTicker(false);
    wizard.setStep(2);
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
        language: locale,
      };

      wizard.setTradeHorizon(fullConfig.trade_horizon);
      wizard.setAnalysisDate(fullConfig.analysis_date);

      const response = await createAnalysis(fullConfig);

      analysisStore.reset();
      analysisStore.setSession(response.session_id);

      const wsBase = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = 'localhost:8000';
      wizard.setWsUrl(`${wsBase}//${wsHost}/api/analysis/ws/${response.session_id}`);

      wizard.setStep(3);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to start analysis';
      setStartError(message);
    } finally {
      setStarting(false);
    }
  }

  function goBack() {
    if (step === 3 || step === 4) return;
    if (step === 1) wizard.setShowCustomTicker(false);
    if (step > 0) wizard.setStep(step - 1);
  }

  if (loadingSession) {
    return (
      <>
        <Topbar title={t('common:status.loading')} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
          <Spin size="large" tip={t('common:status.loading')} />
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 800 }}>
        {/* Step indicator */}
        <Steps
          current={step}
          size="small"
          style={{ marginBottom: 32 }}
          items={[
            { title: t('steps.market') },
            { title: t('steps.stock') },
            { title: t('steps.configure') },
            { title: t('steps.analyze') },
            { title: t('steps.results') },
          ]}
        />

        {/* Back button (steps 1-2 only) */}
        {step > 0 && step < 3 && (
          <Button
            icon={<ArrowLeftOutlined />}
            size="small"
            onClick={goBack}
            style={{ marginBottom: 20 }}
          >
            {t('common:actions.back')}
          </Button>
        )}

        {/* Step 1: Market */}
        {step === 0 && (
          <>
            <Title level={4}>{t('market.selectMarket')}</Title>
            <Paragraph type="secondary">Choose the market you want to analyze a stock from.</Paragraph>
            <MarketSelector onSelect={handleMarketSelect} />
          </>
        )}

        {/* Step 2: Market Overview */}
        {step === 1 && selectedMarket && (
          <>
            <Title level={4}>Market Overview</Title>
            <Paragraph type="secondary">Browse stocks or select one to analyze.</Paragraph>

            {showCustomTicker ? (
              <>
                <Button
                  icon={<ArrowLeftOutlined />}
                  size="small"
                  onClick={() => wizard.setShowCustomTicker(false)}
                  style={{ marginBottom: 16 }}
                >
                  {t('common:actions.back')}
                </Button>
                <TickerInput marketId={selectedMarket} onValidated={handleStockValidated} />
              </>
            ) : (
              <>
                <MarketOverview
                  marketId={selectedMarket}
                  onSelectStock={handleOverviewStockSelect}
                />
                <Button
                  type="link"
                  onClick={() => wizard.setShowCustomTicker(true)}
                  style={{ marginTop: 16, padding: 0 }}
                >
                  Enter custom ticker
                </Button>
              </>
            )}
          </>
        )}

        {/* Step 3: Configure */}
        {step === 2 && selectedMarket && selectedStock && (
          <>
            <Title level={4}>Configure Analysis</Title>
            <Paragraph type="secondary">
              Set parameters for analyzing {selectedStock.name} ({selectedStock.ticker}).
            </Paragraph>
            <CandlestickChart
              ticker={selectedStock.ticker}
              marketId={selectedMarket}
              currency={selectedStock.currency}
            />
            {startError && (
              <Alert
                type="error"
                message={startError}
                showIcon
                closable
                onClose={() => setStartError(null)}
                style={{ marginBottom: 16 }}
              />
            )}
            <ConfigPanel
              ticker={selectedStock.ticker}
              marketId={selectedMarket}
              onStart={handleStartAnalysis}
            />
            {starting && (
              <Text type="secondary" style={{ display: 'block', marginTop: 12 }}>
                <Spin size="small" style={{ marginInlineEnd: 8 }} />
                {t('common:status.loading')}
              </Text>
            )}
          </>
        )}

        {/* Step 4: Analyze */}
        {step === 3 && (
          <>
            <Title level={4}>Analyzing {selectedStock?.name}</Title>
            <Paragraph type="secondary">
              {connected
                ? 'Connected - receiving live updates from agents.'
                : 'Connecting to analysis stream...'}
            </Paragraph>
            <AnalysisProgress />
          </>
        )}

        {/* Step 5: Results */}
        {step === 4 && analysisStore.recommendation && analysisStore.confidence !== null && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Title level={4} style={{ marginBottom: 4 }}>{t('results.recommendation')}</Title>
                <Text type="secondary">
                  {analysisStore.summary || 'Your analysis has been completed successfully.'}
                </Text>
              </div>
              <Button
                icon={<PlusOutlined />}
                onClick={() => {
                  analysisStore.reset();
                  wizard.reset();
                  setStartError(null);
                }}
              >
                {t('title')}
              </Button>
            </div>

            <ResultHero
              recommendation={analysisStore.recommendation}
              confidence={analysisStore.confidence}
              ticker={selectedStock?.ticker || ''}
              market={selectedMarket || ''}
              horizon={tradeHorizon}
              date={analysisDate}
            />

            {/* Action buttons */}
            <Space style={{ marginTop: 20 }}>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
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
                    // Silently fail
                  }
                }}
              >
                {t('common:actions.save')}
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  analysisStore.reset();
                  wizard.setWsUrl(null);
                  wizard.setStep(2);
                }}
              >
                {t('common:actions.reAnalyze')}
              </Button>
              <Button
                type="primary"
                icon={<DollarOutlined />}
                style={
                  analysisStore.recommendation?.toUpperCase() !== 'HOLD'
                    ? { background: '#22c55e', borderColor: '#22c55e' }
                    : undefined
                }
                disabled={analysisStore.recommendation?.toUpperCase() === 'HOLD'}
                onClick={() => setTradeModalOpen(true)}
              >
                Execute Trade
              </Button>
            </Space>

            {/* Detailed Agent Reports */}
            {Object.keys(analysisStore.reports).length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 24 }}>
                <Title level={5}>{t('results.reports')}</Title>
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

            {/* Trade Modal */}
            <TradeModal
              isOpen={tradeModalOpen}
              onClose={() => setTradeModalOpen(false)}
              ticker={selectedStock?.ticker || ''}
              marketId={selectedMarket || ''}
              direction={analysisStore.recommendation?.toUpperCase() === 'BUY' ? 'long' : 'short'}
              recommendation={analysisStore.recommendation || ''}
              confidence={analysisStore.confidence}
              currentPrice={selectedStock?.price || 0}
              analysisSessionId={analysisStore.sessionId}
              onSuccess={() => {}}
            />
          </>
        )}

        {/* Step 5 fallback: session loaded but no recommendation */}
        {step === 4 && !analysisStore.recommendation && !loadingSession && (
          <Empty
            description={t('results.noRecommendation')}
            style={{ padding: 40 }}
          >
            <Button
              onClick={() => {
                analysisStore.reset();
                wizard.reset();
              }}
            >
              {t('common:actions.startNewAnalysis')}
            </Button>
          </Empty>
        )}
      </div>
    </>
  );
}

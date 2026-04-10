import { useState } from 'react';
import type { CSSProperties } from 'react';
import { useMarketOverview } from '../../hooks/useMarketOverview';
import IndexBar from './IndexBar';
import MarketSummaryBar from './MarketSummaryBar';
import StockTable from './StockTable';
import MoverGrid from './MoverGrid';
import NewsSection from './NewsSection';
import TickerNews from './TickerNews';

interface MarketOverviewProps {
  marketId: string;
  onSelectStock: (ticker: string, name: string) => void;
}

type Tab = 'stocks' | 'movers' | 'news';

const headerRowStyle: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 16,
};

const refreshBtnStyle: CSSProperties = {
  padding: '6px 14px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--text2)',
  fontSize: 12,
  cursor: 'pointer',
};

const tabBarStyle: CSSProperties = {
  display: 'flex',
  gap: 0,
  marginBottom: 20,
  borderBottom: '2px solid var(--border)',
};

function tabStyle(active: boolean): CSSProperties {
  return {
    padding: '10px 20px',
    fontSize: 13,
    fontWeight: active ? 700 : 500,
    color: active ? 'var(--accent)' : 'var(--text3)',
    background: 'transparent',
    border: 'none',
    borderBottom: active ? '2px solid var(--accent)' : '2px solid transparent',
    marginBottom: -2,
    cursor: 'pointer',
    transition: 'color 0.15s',
  };
}

const errorBoxStyle: CSSProperties = {
  padding: 24,
  background: 'rgba(239, 68, 68, 0.1)',
  border: '1px solid rgba(239, 68, 68, 0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#ef4444',
  fontSize: 14,
  textAlign: 'center',
};

const retryBtnStyle: CSSProperties = {
  padding: '8px 18px',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--accent)',
  color: '#fff',
  fontSize: 13,
  fontWeight: 600,
  cursor: 'pointer',
  marginTop: 12,
};

const marketClosedBannerStyle: CSSProperties = {
  padding: '10px 16px',
  background: 'rgba(245, 158, 11, 0.08)',
  border: '1px solid rgba(245, 158, 11, 0.2)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--yellow)',
  fontSize: 13,
  fontWeight: 500,
  marginBottom: 16,
  textAlign: 'center',
};

/* Loading skeleton styles */
const skeletonContainerStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 16,
  padding: '8px 0',
};

const skeletonBarStyle = (width: string, height: number): CSSProperties => ({
  width,
  height,
  borderRadius: 'var(--radius-sm)',
  background: 'var(--surface2)',
  animation: 'pulse 1.5s ease-in-out infinite',
});

const skeletonRowStyle: CSSProperties = {
  display: 'flex',
  gap: 12,
};

const TABS: { key: Tab; label: string }[] = [
  { key: 'stocks', label: 'All Stocks' },
  { key: 'movers', label: 'Top Movers' },
  { key: 'news', label: 'Hot News' },
];

function LoadingSkeleton() {
  return (
    <div style={skeletonContainerStyle}>
      {/* Index bar skeleton */}
      <div style={skeletonRowStyle}>
        <div style={skeletonBarStyle('33%', 80)} />
        <div style={skeletonBarStyle('33%', 80)} />
        <div style={skeletonBarStyle('33%', 80)} />
      </div>
      {/* Summary bar skeleton */}
      <div style={skeletonRowStyle}>
        <div style={skeletonBarStyle('80px', 28)} />
        <div style={skeletonBarStyle('90px', 28)} />
        <div style={skeletonBarStyle('80px', 28)} />
        <div style={skeletonBarStyle('100px', 28)} />
      </div>
      {/* Tab bar skeleton */}
      <div style={skeletonBarStyle('100%', 40)} />
      {/* Table rows skeleton */}
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} style={skeletonBarStyle('100%', 44)} />
      ))}
    </div>
  );
}

export default function MarketOverview({ marketId, onSelectStock }: MarketOverviewProps) {
  const { data, loading, error, refresh } = useMarketOverview(marketId);
  const [activeTab, setActiveTab] = useState<Tab>('stocks');
  const [newsTicker, setNewsTicker] = useState<string | null>(null);

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div style={errorBoxStyle}>
        <div>{error}</div>
        <button style={retryBtnStyle} onClick={refresh}>
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div>
      {/* Market closed banner */}
      {data.market_status === 'closed' && (
        <div style={marketClosedBannerStyle}>
          🕐 Market Closed — Showing last close data
        </div>
      )}

      {/* Index bar */}
      <IndexBar indices={data.indices} />

      {/* Summary bar */}
      <MarketSummaryBar summary={data.summary} />

      {/* Header with refresh */}
      <div style={headerRowStyle}>
        <div style={{ fontSize: 13, color: 'var(--text3)' }}>
          Last updated: {new Date(data.last_updated).toLocaleTimeString()}
        </div>
        <button style={refreshBtnStyle} onClick={refresh}>
          Refresh
        </button>
      </div>

      {/* Tab bar */}
      <div style={tabBarStyle}>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            style={tabStyle(activeTab === tab.key)}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'stocks' && (
        <StockTable
          stocks={data.stocks}
          onSelectStock={onSelectStock}
          onViewNews={(ticker) => setNewsTicker(ticker)}
        />
      )}

      {activeTab === 'movers' && (
        <MoverGrid
          gainers={data.gainers}
          losers={data.losers}
          onSelectStock={onSelectStock}
        />
      )}

      {activeTab === 'news' && <NewsSection marketId={marketId} />}

      {/* Ticker news overlay */}
      {newsTicker && (
        <TickerNews
          ticker={newsTicker}
          marketId={marketId}
          onClose={() => setNewsTicker(null)}
        />
      )}
    </div>
  );
}

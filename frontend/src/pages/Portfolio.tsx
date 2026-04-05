import { useState, CSSProperties } from 'react';
import Topbar from '../components/layout/Topbar';
import PortfolioSummary from '../components/portfolio/PortfolioSummary';
import PositionsTable from '../components/portfolio/PositionsTable';
import TradeHistory from '../components/portfolio/TradeHistory';
import PortfolioAnalytics from '../components/portfolio/PortfolioAnalytics';
import AIComparison from '../components/portfolio/AIComparison';
import { usePortfolio } from '../hooks/usePortfolio';
import { resetPortfolio } from '../services/api';

type Tab = 'positions' | 'history' | 'analytics';

const pageStyle: CSSProperties = {
  padding: 24,
  maxWidth: 1100,
};

const headerRow: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 24,
};

const titleStyle: CSSProperties = {
  fontSize: 20,
  fontWeight: 700,
  color: 'var(--text)',
};

const resetBtnStyle: CSSProperties = {
  padding: '8px 16px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid rgba(239,68,68,0.3)',
  background: 'rgba(239,68,68,0.08)',
  color: '#ef4444',
  fontSize: 12,
  fontWeight: 600,
  cursor: 'pointer',
};

const tabBarStyle: CSSProperties = {
  display: 'flex',
  gap: 0,
  borderBottom: '1px solid var(--border)',
  marginBottom: 20,
};

const tabStyle = (active: boolean): CSSProperties => ({
  padding: '10px 20px',
  fontSize: 13,
  fontWeight: active ? 600 : 400,
  color: active ? 'var(--accent)' : 'var(--text3)',
  background: 'transparent',
  border: 'none',
  borderBottom: active ? '2px solid var(--accent)' : '2px solid transparent',
  cursor: 'pointer',
  transition: 'color 0.15s, border-color 0.15s',
});

const loadingContainer: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '60vh',
  gap: 12,
  color: 'var(--text3)',
  fontSize: 14,
};

const errorContainer: CSSProperties = {
  textAlign: 'center',
  padding: 48,
  color: '#ef4444',
  fontSize: 14,
};

const emptyContainer: CSSProperties = {
  textAlign: 'center',
  padding: 64,
  color: 'var(--text3)',
};

const confirmOverlay: CSSProperties = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0, 0, 0, 0.6)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
};

const confirmCard: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 28,
  maxWidth: 380,
  textAlign: 'center',
  display: 'flex',
  flexDirection: 'column',
  gap: 16,
};

export default function Portfolio() {
  const { portfolio, loading, error, refresh } = usePortfolio();
  const [activeTab, setActiveTab] = useState<Tab>('positions');
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [resetting, setResetting] = useState(false);

  async function handleReset() {
    setResetting(true);
    try {
      await resetPortfolio();
      setShowResetConfirm(false);
      refresh();
    } catch {
      // keep dialog open on error
    } finally {
      setResetting(false);
    }
  }

  return (
    <>
      <Topbar title="Portfolio" />
      <div style={pageStyle}>
        {loading && !portfolio && (
          <div style={loadingContainer}>
            <span className="spinner" />
            Loading portfolio...
          </div>
        )}

        {error && !portfolio && (
          <div style={errorContainer}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>⚠️</div>
            <div>{error}</div>
            <button
              style={{ ...resetBtnStyle, marginTop: 16, color: 'var(--accent)', borderColor: 'var(--accent)' }}
              onClick={refresh}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && !portfolio && (
          <div style={emptyContainer}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>💰</div>
            <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 8 }}>
              No Portfolio Yet
            </div>
            <div style={{ fontSize: 13 }}>
              Execute your first trade from an analysis to get started.
            </div>
          </div>
        )}

        {portfolio && (
          <>
            <div style={headerRow}>
              <div style={titleStyle}>Paper Trading Portfolio</div>
              <button style={resetBtnStyle} onClick={() => setShowResetConfirm(true)}>
                Reset Portfolio
              </button>
            </div>

            <PortfolioSummary portfolio={portfolio} />

            <div style={tabBarStyle}>
              <button style={tabStyle(activeTab === 'positions')} onClick={() => setActiveTab('positions')}>
                Open Positions
              </button>
              <button style={tabStyle(activeTab === 'history')} onClick={() => setActiveTab('history')}>
                Trade History
              </button>
              <button style={tabStyle(activeTab === 'analytics')} onClick={() => setActiveTab('analytics')}>
                Analytics
              </button>
            </div>

            {activeTab === 'positions' && (
              <PositionsTable positions={portfolio.open_positions} onRefresh={refresh} />
            )}

            {activeTab === 'history' && <TradeHistory />}

            {activeTab === 'analytics' && (
              <>
                <PortfolioAnalytics />
                <AIComparison />
              </>
            )}
          </>
        )}

        {/* Reset confirmation dialog */}
        {showResetConfirm && (
          <div style={confirmOverlay} onClick={() => setShowResetConfirm(false)}>
            <div style={confirmCard} onClick={(e) => e.stopPropagation()}>
              <div style={{ fontSize: 32 }}>⚠️</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text)' }}>
                Reset Portfolio?
              </div>
              <div style={{ fontSize: 13, color: 'var(--text3)' }}>
                This will close all positions and reset your balance. This action cannot be undone.
              </div>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                <button
                  style={{
                    padding: '10px 20px',
                    borderRadius: 'var(--radius-sm)',
                    border: 'none',
                    background: '#ef4444',
                    color: '#fff',
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: 'pointer',
                    opacity: resetting ? 0.6 : 1,
                  }}
                  onClick={handleReset}
                  disabled={resetting}
                >
                  {resetting ? 'Resetting...' : 'Yes, Reset'}
                </button>
                <button
                  style={{
                    padding: '10px 20px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border)',
                    background: 'transparent',
                    color: 'var(--text2)',
                    fontSize: 13,
                    cursor: 'pointer',
                  }}
                  onClick={() => setShowResetConfirm(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

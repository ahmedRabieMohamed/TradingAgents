import { useEffect, useState, CSSProperties } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/layout/Topbar';
import { listAnalyses, getPortfolio, getPerformance } from '../services/api';
import type {
  AnalysisListItem,
  PortfolioResponse,
  PerformanceStats,
  Recommendation,
} from '../types';

const pageStyle: CSSProperties = { padding: 24, maxWidth: 1000 };

const gridStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: 16,
  marginBottom: 28,
};

const cardStyle: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-md)',
  padding: 20,
};

const cardLabel: CSSProperties = {
  fontSize: 11,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: 'var(--text3)',
  marginBottom: 8,
};

const cardValue: CSSProperties = {
  fontSize: 24,
  fontWeight: 700,
  color: 'var(--text)',
};

const cardSub: CSSProperties = {
  fontSize: 12,
  color: 'var(--text3)',
  marginTop: 4,
};

const sectionTitle: CSSProperties = {
  fontSize: 15,
  fontWeight: 600,
  color: 'var(--text)',
  marginBottom: 12,
};

const tableStyle: CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: 13,
};

const thStyle: CSSProperties = {
  textAlign: 'left',
  padding: '8px 12px',
  borderBottom: '1px solid var(--border)',
  color: 'var(--text3)',
  fontSize: 11,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
};

const tdStyle: CSSProperties = {
  padding: '10px 12px',
  borderBottom: '1px solid var(--border)',
  color: 'var(--text)',
};

const recBadge = (rec: Recommendation | null): CSSProperties => ({
  display: 'inline-block',
  padding: '2px 8px',
  borderRadius: 4,
  fontSize: 11,
  fontWeight: 700,
  background:
    rec === 'BUY'
      ? 'rgba(16,185,129,0.15)'
      : rec === 'SELL'
        ? 'rgba(239,68,68,0.15)'
        : 'rgba(245,158,11,0.15)',
  color:
    rec === 'BUY'
      ? 'var(--green)'
      : rec === 'SELL'
        ? 'var(--red)'
        : 'var(--yellow)',
});

const quickActionBtn: CSSProperties = {
  padding: '10px 20px',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--accent)',
  color: '#fff',
  fontSize: 13,
  fontWeight: 600,
  cursor: 'pointer',
};

const secondaryBtn: CSSProperties = {
  ...quickActionBtn,
  background: 'var(--surface2)',
  color: 'var(--text2)',
};

const pnlColor = (v: number) => (v >= 0 ? 'var(--green)' : 'var(--red)');

export default function Dashboard() {
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [perf, setPerf] = useState<PerformanceStats | null>(null);
  const [recent, setRecent] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      getPortfolio().catch(() => null),
      getPerformance().catch(() => null),
      listAnalyses({ limit: '5' }).catch(() => null),
    ]).then(([p, pf, an]) => {
      if (cancelled) return;
      if (p) setPortfolio(p);
      if (pf) setPerf(pf);
      if (an && an.items) setRecent(an.items.slice(0, 5));
    }).catch(() => {}).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <>
        <Topbar title="Dashboard" />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: 8, color: 'var(--text3)' }}>
          <span className="spinner" />
          Loading dashboard...
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title="Dashboard" />
      <div style={pageStyle}>
        {/* Quick Actions */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
          <button style={quickActionBtn} onClick={() => navigate('/analysis')}>
            + New Analysis
          </button>
          <button style={secondaryBtn} onClick={() => navigate('/history')}>
            View History
          </button>
          <button style={secondaryBtn} onClick={() => navigate('/portfolio')}>
            Portfolio
          </button>
        </div>

        {/* Stats Cards */}
        <div style={gridStyle}>
          <div style={cardStyle}>
            <div style={cardLabel}>Portfolio Value</div>
            <div style={cardValue}>
              ${portfolio ? portfolio.total_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '—'}
            </div>
            {portfolio && (
              <div style={{ ...cardSub, color: pnlColor(portfolio.total_pnl) }}>
                {portfolio.total_pnl >= 0 ? '+' : ''}
                ${portfolio.total_pnl.toFixed(2)} ({portfolio.total_pnl_pct >= 0 ? '+' : ''}{portfolio.total_pnl_pct.toFixed(2)}%)
              </div>
            )}
          </div>

          <div style={cardStyle}>
            <div style={cardLabel}>Open Positions</div>
            <div style={cardValue}>{portfolio?.open_positions_count ?? 0}</div>
            <div style={cardSub}>
              Cash: ${portfolio ? portfolio.cash_balance.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '—'}
            </div>
          </div>

          <div style={cardStyle}>
            <div style={cardLabel}>Total Analyses</div>
            <div style={cardValue}>{perf?.total_analyses ?? 0}</div>
            <div style={cardSub}>
              {perf?.total_simulations ?? 0} simulated
            </div>
          </div>

          <div style={cardStyle}>
            <div style={cardLabel}>Win Rate</div>
            <div style={{ ...cardValue, color: perf?.win_rate != null && perf.win_rate >= 50 ? 'var(--green)' : perf?.win_rate != null ? 'var(--red)' : 'var(--text)' }}>
              {perf?.win_rate != null ? `${perf.win_rate.toFixed(1)}%` : '—'}
            </div>
            <div style={cardSub}>
              Avg return: {perf?.avg_return_pct != null ? `${perf.avg_return_pct >= 0 ? '+' : ''}${perf.avg_return_pct.toFixed(2)}%` : '—'}
            </div>
          </div>
        </div>

        {/* Open Positions */}
        {portfolio && portfolio.open_positions.length > 0 && (
          <div style={{ marginBottom: 28 }}>
            <div style={sectionTitle}>Open Positions</div>
            <div style={{ ...cardStyle, padding: 0, overflow: 'hidden' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Ticker</th>
                    <th style={thStyle}>Direction</th>
                    <th style={thStyle}>Qty</th>
                    <th style={thStyle}>Entry</th>
                    <th style={thStyle}>Current</th>
                    <th style={thStyle}>P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.open_positions.map((pos) => (
                    <tr key={pos.id}>
                      <td style={{ ...tdStyle, fontWeight: 600 }}>{pos.ticker}</td>
                      <td style={tdStyle}>
                        <span style={{ color: pos.direction === 'long' ? 'var(--green)' : 'var(--red)' }}>
                          {pos.direction.toUpperCase()}
                        </span>
                      </td>
                      <td style={tdStyle}>{pos.quantity}</td>
                      <td style={tdStyle}>${pos.entry_price.toFixed(2)}</td>
                      <td style={tdStyle}>${pos.current_price.toFixed(2)}</td>
                      <td style={{ ...tdStyle, color: pnlColor(pos.unrealized_pnl), fontWeight: 600 }}>
                        {pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)}
                        <span style={{ fontSize: 11, opacity: 0.7 }}> ({pos.unrealized_pnl_pct >= 0 ? '+' : ''}{pos.unrealized_pnl_pct.toFixed(1)}%)</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Recent Analyses */}
        {recent.length > 0 && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div style={sectionTitle}>Recent Analyses</div>
              <button
                style={{ background: 'none', border: 'none', color: 'var(--accent)', fontSize: 12, cursor: 'pointer' }}
                onClick={() => navigate('/history')}
              >
                View all →
              </button>
            </div>
            <div style={{ ...cardStyle, padding: 0, overflow: 'hidden' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Ticker</th>
                    <th style={thStyle}>Market</th>
                    <th style={thStyle}>Date</th>
                    <th style={thStyle}>Horizon</th>
                    <th style={thStyle}>Result</th>
                    <th style={thStyle}>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {recent.map((a) => (
                    <tr
                      key={a.id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/analysis?session=${a.id}`)}
                    >
                      <td style={{ ...tdStyle, fontWeight: 600 }}>{a.ticker}</td>
                      <td style={tdStyle}>{a.market_id === 'egypt' ? 'EGX' : 'US'}</td>
                      <td style={tdStyle}>{a.analysis_date}</td>
                      <td style={tdStyle}>{a.trade_horizon}</td>
                      <td style={tdStyle}>
                        {a.recommendation ? (
                          <span style={recBadge(a.recommendation)}>{a.recommendation}</span>
                        ) : (
                          <span style={{ color: 'var(--text3)' }}>{a.status}</span>
                        )}
                      </td>
                      <td style={tdStyle}>
                        {a.confidence != null ? `${(a.confidence * 100).toFixed(0)}%` : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty state */}
        {recent.length === 0 && (!portfolio || portfolio.open_positions.length === 0) && (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--text3)' }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>📊</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text2)', marginBottom: 8 }}>
              Welcome to TradingAgents
            </div>
            <div style={{ fontSize: 13, marginBottom: 20 }}>
              Start by running your first stock analysis.
            </div>
            <button style={quickActionBtn} onClick={() => navigate('/analysis')}>
              + New Analysis
            </button>
          </div>
        )}
      </div>
    </>
  );
}

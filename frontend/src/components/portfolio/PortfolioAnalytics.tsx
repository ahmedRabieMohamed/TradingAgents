import { useState, useEffect, CSSProperties } from 'react';
import { getPortfolioAnalytics } from '../../services/api';
import type { PortfolioAnalyticsResponse } from '../../types';
import EquityCurve from './EquityCurve';

const gridStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: 12,
  marginBottom: 20,
};

const statCard: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: '18px 16px',
  display: 'flex',
  flexDirection: 'column',
  gap: 4,
};

const statLabel: CSSProperties = {
  fontSize: 11,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
  color: 'var(--text3)',
};

const statValue: CSSProperties = {
  fontSize: 22,
  fontWeight: 700,
  color: 'var(--text)',
};

const tradeCardsRow: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 12,
  marginBottom: 20,
};

function tradeCard(isGood: boolean): CSSProperties {
  const clr = isGood ? '#22c55e' : '#ef4444';
  return {
    background: `linear-gradient(135deg, ${clr}11 0%, ${clr}04 100%)`,
    border: `1px solid ${clr}33`,
    borderRadius: 'var(--radius-lg)',
    padding: '16px 18px',
  };
}

const sectionTitle: CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text)',
  marginBottom: 12,
};

const breakdownRow: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  marginBottom: 10,
};

const breakdownLabel: CSSProperties = {
  fontSize: 13,
  color: 'var(--text2)',
  minWidth: 60,
  fontWeight: 500,
};

const barContainer: CSSProperties = {
  flex: 1,
  height: 8,
  background: 'var(--surface2)',
  borderRadius: 4,
  overflow: 'hidden',
};

const breakdownStats: CSSProperties = {
  fontSize: 12,
  color: 'var(--text3)',
  minWidth: 130,
  textAlign: 'right',
};

const loadingStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 48,
  gap: 10,
  color: 'var(--text3)',
  fontSize: 13,
};

const emptyStyle: CSSProperties = {
  textAlign: 'center',
  padding: 48,
  color: 'var(--text3)',
  fontSize: 13,
};

function formatMoney(v: number): string {
  const sign = v >= 0 ? '+' : '';
  return sign + '$' + Math.abs(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function pnlColor(v: number): string {
  if (v > 0) return '#22c55e';
  if (v < 0) return '#ef4444';
  return 'var(--text2)';
}

export default function PortfolioAnalytics() {
  const [data, setData] = useState<PortfolioAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPortfolioAnalytics()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load analytics'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={loadingStyle}>
        <span className="spinner" />
        Loading analytics...
      </div>
    );
  }

  if (error) {
    return <div style={{ ...emptyStyle, color: '#ef4444' }}>{error}</div>;
  }

  if (!data || data.total_trades < 3) {
    return (
      <div style={emptyStyle}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>📊</div>
        <div style={{ fontWeight: 600, color: 'var(--text)', marginBottom: 4 }}>
          Not Enough Data
        </div>
        <div>Close at least 3 trades to see analytics.</div>
      </div>
    );
  }

  const marketEntries = Object.entries(data.by_market);
  const maxCount = Math.max(...marketEntries.map(([, v]) => v.count), 1);

  return (
    <div className="fade-in">
      {/* Stat cards */}
      <div style={gridStyle}>
        <div style={statCard}>
          <div style={statLabel}>Total Trades</div>
          <div style={statValue}>{data.total_trades}</div>
        </div>
        <div style={statCard}>
          <div style={statLabel}>Win Rate</div>
          <div style={{ ...statValue, color: data.win_rate >= 50 ? '#22c55e' : '#ef4444' }}>
            {data.win_rate.toFixed(1)}%
          </div>
        </div>
        <div style={statCard}>
          <div style={statLabel}>Avg Return</div>
          <div style={{ ...statValue, color: pnlColor(data.avg_return_pct) }}>
            {data.avg_return_pct >= 0 ? '+' : ''}{data.avg_return_pct.toFixed(2)}%
          </div>
        </div>
        <div style={statCard}>
          <div style={statLabel}>Total Realized P&L</div>
          <div style={{ ...statValue, color: pnlColor(data.total_realized_pnl) }}>
            {formatMoney(data.total_realized_pnl)}
          </div>
        </div>
      </div>

      {/* Best / Worst trade */}
      {(data.best_trade || data.worst_trade) && (
        <div style={tradeCardsRow}>
          {data.best_trade ? (
            <div style={tradeCard(true)}>
              <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: '#22c55e', marginBottom: 6, letterSpacing: '0.06em' }}>
                Best Trade
              </div>
              <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text)' }}>
                {data.best_trade.ticker}
              </div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#22c55e', marginTop: 4 }}>
                +{data.best_trade.pnl_pct.toFixed(2)}% ({formatMoney(data.best_trade.pnl)})
              </div>
            </div>
          ) : (
            <div />
          )}
          {data.worst_trade ? (
            <div style={tradeCard(false)}>
              <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: '#ef4444', marginBottom: 6, letterSpacing: '0.06em' }}>
                Worst Trade
              </div>
              <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text)' }}>
                {data.worst_trade.ticker}
              </div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#ef4444', marginTop: 4 }}>
                {data.worst_trade.pnl_pct.toFixed(2)}% ({formatMoney(data.worst_trade.pnl)})
              </div>
            </div>
          ) : (
            <div />
          )}
        </div>
      )}

      {/* By-market breakdown */}
      {marketEntries.length > 0 && (
        <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '18px 20px', marginBottom: 20 }}>
          <div style={sectionTitle}>By Market</div>
          {marketEntries.map(([market, stats]) => (
            <div key={market} style={breakdownRow}>
              <div style={breakdownLabel}>{market.toUpperCase()}</div>
              <div style={barContainer}>
                <div
                  style={{
                    width: `${(stats.count / maxCount) * 100}%`,
                    height: '100%',
                    background: stats.win_rate >= 50 ? '#22c55e' : '#ef4444',
                    borderRadius: 4,
                    transition: 'width 0.4s ease',
                  }}
                />
              </div>
              <div style={breakdownStats}>
                {stats.count} trades &middot; {stats.win_rate.toFixed(0)}% WR &middot; {stats.avg_return_pct >= 0 ? '+' : ''}{stats.avg_return_pct.toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Equity curve */}
      <EquityCurve data={data.equity_curve} />
    </div>
  );
}

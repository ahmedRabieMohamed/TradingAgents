import { CSSProperties, useEffect, useState } from 'react';
import Topbar from '../components/layout/Topbar';
import PerfCard from '../components/performance/PerfCard';
import MarketPerf from '../components/performance/MarketPerf';
import SimulationTable from '../components/performance/SimulationTable';
import type { SimulationRow } from '../components/performance/SimulationTable';
import { getPerformance, listAnalyses } from '../services/api';
import type { PerformanceStats } from '../types';

const pageStyle: CSSProperties = {
  padding: 24,
  display: 'flex',
  flexDirection: 'column',
  gap: 20,
  animation: 'fadeIn 0.3s ease',
};

const gridStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(4, 1fr)',
  gap: 16,
};

const loadingStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: 'calc(100vh - var(--topbar-height))',
  gap: 12,
  color: 'var(--text3)',
  fontSize: 14,
};

const emptyStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: 'calc(100vh - var(--topbar-height))',
  gap: 12,
  padding: 40,
};

const emptyCardStyle: CSSProperties = {
  textAlign: 'center',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: 12,
  padding: 40,
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
};

export default function Performance() {
  const [stats, setStats] = useState<PerformanceStats | null>(null);
  const [simRows, setSimRows] = useState<SimulationRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);

        const [perfData, analysesData] = await Promise.all([
          getPerformance(),
          listAnalyses({ status: 'completed', limit: '100' }),
        ]);

        setStats(perfData);

        // Build simulation rows from analyses that have simulation data
        const rows: SimulationRow[] = [];
        const analyses = analysesData.analyses ?? analysesData.items ?? [];
        for (const a of analyses) {
          const sim = (a as any).simulation;
          if (sim && sim.return_pct !== undefined) {
            rows.push({
              id: a.id,
              ticker: a.ticker,
              stock_name: a.stock_name,
              market_id: a.market_id,
              recommendation: a.recommendation,
              entry_price: sim.entry_price ?? 0,
              exit_price: sim.exit_price ?? 0,
              return_pct: sim.return_pct,
              is_win: sim.is_win,
            });
          }
        }
        setSimRows(rows);
      } catch (err: any) {
        setError(err.message || 'Failed to load performance data');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <>
        <Topbar title="Performance" />
        <div style={loadingStyle}>
          <span className="spinner" />
          <span>Loading performance data...</span>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Topbar title="Performance" />
        <div style={loadingStyle}>
          <span style={{ color: 'var(--red)' }}>{error}</span>
        </div>
      </>
    );
  }

  if (!stats || stats.total_simulations === 0) {
    return (
      <>
        <Topbar title="Performance" />
        <div style={emptyStyle}>
          <div style={emptyCardStyle}>
            <span style={{ fontSize: 40 }}>&#128202;</span>
            <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)' }}>No Simulations Yet</h2>
            <p style={{ fontSize: 13, color: 'var(--text3)', maxWidth: 360 }}>
              Once your completed analyses pass their trade horizon, you can run
              simulations to see how predictions performed against actual market data.
            </p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title="Performance" />
      <div style={pageStyle}>
        {/* Summary cards */}
        <div style={gridStyle}>
          <PerfCard
            value={String(stats.total_analyses)}
            label="Total Analyses"
          />
          <PerfCard
            value={stats.win_rate != null ? `${stats.win_rate}%` : '-'}
            label="Win Rate"
            color={
              stats.win_rate != null
                ? stats.win_rate >= 50
                  ? 'var(--green)'
                  : 'var(--red)'
                : undefined
            }
          />
          <PerfCard
            value={stats.avg_return_pct != null ? `${stats.avg_return_pct > 0 ? '+' : ''}${stats.avg_return_pct}%` : '-'}
            label="Avg Return"
            color={
              stats.avg_return_pct != null
                ? stats.avg_return_pct >= 0
                  ? 'var(--green)'
                  : 'var(--red)'
                : undefined
            }
          />
          <PerfCard
            value={String(stats.total_simulations ?? stats.simulated_count ?? 0)}
            label="Simulated"
          />
        </div>

        {/* Breakdown by market and horizon */}
        <MarketPerf
          byMarket={stats.by_market}
          byHorizon={stats.by_horizon}
        />

        {/* Simulation results table */}
        <SimulationTable rows={simRows} />
      </div>
    </>
  );
}

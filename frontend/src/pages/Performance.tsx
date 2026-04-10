import { useEffect, useState } from 'react';
import { Alert, Col, Empty, Row, Spin, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import Topbar from '../components/layout/Topbar';
import PerfCard from '../components/performance/PerfCard';
import MarketPerf from '../components/performance/MarketPerf';
import SimulationTable from '../components/performance/SimulationTable';
import type { SimulationRow } from '../components/performance/SimulationTable';
import { getPerformance, listAnalyses } from '../services/api';
import type { PerformanceStats } from '../types';

const { Title, Text } = Typography;

export default function Performance() {
  const { t } = useTranslation(['performance', 'common']);

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
        const analyses = (analysesData as any).analyses ?? (analysesData as any).items ?? [];
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
        <Topbar title={t('title')} />
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 'calc(100vh - var(--topbar-height))',
            gap: 12,
          }}
        >
          <Spin size="large" tip={t('common:status.loading')} />
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Topbar title={t('title')} />
        <div style={{ padding: 24 }}>
          <Alert type="error" message={error} showIcon />
        </div>
      </>
    );
  }

  if (!stats || stats.total_simulations === 0) {
    return (
      <>
        <Topbar title={t('title')} />
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 'calc(100vh - var(--topbar-height))',
            padding: 40,
          }}
        >
          <Empty
            image={<span style={{ fontSize: 40 }}>&#128202;</span>}
            description={
              <>
                <Title level={5} style={{ marginBottom: 4 }}>
                  {t('empty')}
                </Title>
                <Text type="secondary" style={{ fontSize: 13, maxWidth: 360, display: 'block' }}>
                  Once your completed analyses pass their trade horizon, you can run simulations to
                  see how predictions performed against actual market data.
                </Text>
              </>
            }
          />
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title={t('title')} />
      <div
        style={{
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          gap: 20,
          animation: 'fadeIn 0.3s ease',
        }}
      >
        {/* Summary cards */}
        <Row gutter={16}>
          <Col span={6}>
            <PerfCard value={String(stats.total_analyses)} label="Total Analyses" />
          </Col>
          <Col span={6}>
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
          </Col>
          <Col span={6}>
            <PerfCard
              value={
                stats.avg_return_pct != null
                  ? `${stats.avg_return_pct > 0 ? '+' : ''}${stats.avg_return_pct}%`
                  : '-'
              }
              label="Avg Return"
              color={
                stats.avg_return_pct != null
                  ? stats.avg_return_pct >= 0
                    ? 'var(--green)'
                    : 'var(--red)'
                  : undefined
              }
            />
          </Col>
          <Col span={6}>
            <PerfCard
              value={String(stats.total_simulations ?? stats.simulated_count ?? 0)}
              label="Simulated"
            />
          </Col>
        </Row>

        {/* Breakdown by market and horizon */}
        <MarketPerf byMarket={stats.by_market} byHorizon={stats.by_horizon} />

        {/* Simulation results table */}
        <SimulationTable rows={simRows} />
      </div>
    </>
  );
}

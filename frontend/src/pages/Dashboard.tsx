import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Row,
  Col,
  Card,
  Statistic,
  Table,
  Button,
  Tag,
  Space,
  Empty,
  Spin,
  Typography,
} from 'antd';
import { useTranslation } from 'react-i18next';
import Topbar from '../components/layout/Topbar';
import { listAnalyses, getPortfolio, getPerformance } from '../services/api';
import type {
  AnalysisListItem,
  PortfolioResponse,
  PerformanceStats,
  Recommendation,
  PositionResponse,
} from '../types';

const { Title, Text } = Typography;

const recTagColor = (rec: Recommendation | null): string => {
  if (rec === 'BUY') return 'success';
  if (rec === 'SELL') return 'error';
  return 'warning';
};

const pnlColor = (v: number) => (v >= 0 ? '#10b981' : '#ef4444');

export default function Dashboard() {
  const navigate = useNavigate();
  const { t } = useTranslation(['dashboard', 'common']);
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
        <Topbar title={t('title')} />
        <div style={{ padding: 24, maxWidth: 1000, display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
          <Spin size="large" />
        </div>
      </>
    );
  }

  const positionsColumns = [
    {
      title: 'Ticker',
      dataIndex: 'ticker',
      key: 'ticker',
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: 'Direction',
      dataIndex: 'direction',
      key: 'direction',
      render: (v: string) => (
        <Text style={{ color: v === 'long' ? '#10b981' : '#ef4444' }}>
          {v.toUpperCase()}
        </Text>
      ),
    },
    {
      title: 'Qty',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Entry',
      dataIndex: 'entry_price',
      key: 'entry_price',
      render: (v: number) => `$${v.toFixed(2)}`,
    },
    {
      title: 'Current',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (v: number) => `$${v.toFixed(2)}`,
    },
    {
      title: 'P&L',
      key: 'pnl',
      render: (_: unknown, record: PositionResponse) => (
        <Text strong style={{ color: pnlColor(record.unrealized_pnl) }}>
          {record.unrealized_pnl >= 0 ? '+' : ''}${record.unrealized_pnl.toFixed(2)}
          <Text style={{ fontSize: 11, opacity: 0.7 }}>
            {' '}({record.unrealized_pnl_pct >= 0 ? '+' : ''}{record.unrealized_pnl_pct.toFixed(1)}%)
          </Text>
        </Text>
      ),
    },
  ];

  const analysesColumns = [
    {
      title: 'Ticker',
      dataIndex: 'ticker',
      key: 'ticker',
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: 'Market',
      dataIndex: 'market_id',
      key: 'market_id',
      render: (v: string) => (v === 'egypt' ? 'EGX' : 'US'),
    },
    {
      title: 'Date',
      dataIndex: 'analysis_date',
      key: 'analysis_date',
    },
    {
      title: 'Horizon',
      dataIndex: 'trade_horizon',
      key: 'trade_horizon',
    },
    {
      title: 'Result',
      key: 'result',
      render: (_: unknown, record: AnalysisListItem) =>
        record.recommendation ? (
          <Tag color={recTagColor(record.recommendation)}>{record.recommendation}</Tag>
        ) : (
          <Text type="secondary">{record.status}</Text>
        ),
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (v: number | null) => (v != null ? `${(v * 100).toFixed(0)}%` : '—'),
    },
  ];

  const isEmpty = recent.length === 0 && (!portfolio || portfolio.open_positions.length === 0);

  return (
    <>
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 1000 }}>
        {/* Quick Actions */}
        <Space style={{ marginBottom: 24 }}>
          <Button type="primary" onClick={() => navigate('/analysis')}>
            {t('common:actions.startNewAnalysis')}
          </Button>
          <Button onClick={() => navigate('/history')}>
            {t('common:nav.history')}
          </Button>
          <Button onClick={() => navigate('/portfolio')}>
            {t('common:nav.portfolio')}
          </Button>
        </Space>

        {/* Stats Cards */}
        <Row gutter={[16, 16]} style={{ marginBottom: 28 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title="Portfolio Value"
                value={
                  portfolio
                    ? portfolio.total_value.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })
                    : '—'
                }
                prefix={portfolio ? '$' : undefined}
                suffix={
                  portfolio ? (
                    <Text style={{ fontSize: 12, color: pnlColor(portfolio.total_pnl) }}>
                      {' '}
                      {portfolio.total_pnl >= 0 ? '+' : ''}${portfolio.total_pnl.toFixed(2)} (
                      {portfolio.total_pnl_pct >= 0 ? '+' : ''}
                      {portfolio.total_pnl_pct.toFixed(2)}%)
                    </Text>
                  ) : undefined
                }
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title="Open Positions"
                value={portfolio?.open_positions_count ?? 0}
                suffix={
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {' '}Cash: $
                    {portfolio
                      ? portfolio.cash_balance.toLocaleString(undefined, { maximumFractionDigits: 2 })
                      : '—'}
                  </Text>
                }
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title={t('totalAnalyses')}
                value={perf?.total_analyses ?? 0}
                suffix={
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {' '}{perf?.total_simulations ?? 0} simulated
                  </Text>
                }
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title="Win Rate"
                value={perf?.win_rate != null ? `${perf.win_rate.toFixed(1)}%` : '—'}
                valueStyle={
                  perf?.win_rate != null
                    ? { color: perf.win_rate >= 50 ? '#10b981' : '#ef4444' }
                    : undefined
                }
                suffix={
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {' '}Avg:{' '}
                    {perf?.avg_return_pct != null
                      ? `${perf.avg_return_pct >= 0 ? '+' : ''}${perf.avg_return_pct.toFixed(2)}%`
                      : '—'}
                  </Text>
                }
              />
            </Card>
          </Col>
        </Row>

        {/* Open Positions */}
        {portfolio && portfolio.open_positions.length > 0 && (
          <div style={{ marginBottom: 28 }}>
            <Title level={5} style={{ marginBottom: 12 }}>Open Positions</Title>
            <Table<PositionResponse>
              columns={positionsColumns}
              dataSource={portfolio.open_positions}
              rowKey="id"
              size="small"
              pagination={false}
              scroll={{ x: true }}
            />
          </div>
        )}

        {/* Recent Analyses */}
        {recent.length > 0 && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <Title level={5} style={{ margin: 0 }}>{t('recentAnalyses')}</Title>
              <Button
                type="link"
                size="small"
                onClick={() => navigate('/history')}
              >
                {t('viewAll')} →
              </Button>
            </div>
            <Table<AnalysisListItem>
              columns={analysesColumns}
              dataSource={recent}
              rowKey="id"
              size="small"
              pagination={false}
              scroll={{ x: true }}
              onRow={(record) => ({
                onClick: () => navigate(`/analysis?session=${record.id}`),
                style: { cursor: 'pointer' },
              })}
            />
          </div>
        )}

        {/* Empty state */}
        {isEmpty && (
          <Empty
            description={
              <Space direction="vertical" size="small">
                <Text strong style={{ fontSize: 16 }}>{t('common:app.title')}</Text>
                <Text type="secondary">{t('noAnalyses')}</Text>
              </Space>
            }
          >
            <Button type="primary" onClick={() => navigate('/analysis')}>
              {t('common:actions.startNewAnalysis')}
            </Button>
          </Empty>
        )}
      </div>
    </>
  );
}

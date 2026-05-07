import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table, Button, Tag, Typography, Space, Spin, Alert, Card,
  Progress, Input, Select, Statistic, Row, Col, Empty,
} from 'antd';
import {
  ReloadOutlined,
  SearchOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import Topbar from '../components/layout/Topbar';
import PickRowExpanded from '../components/smart-picks/PickRowExpanded';
import PickDetailDrawer from '../components/smart-picks/PickDetailDrawer';
import VolatilityBadge from '../components/smart-picks/VolatilityBadge';
import EngineCell from '../components/smart-picks/EngineCell';
import { getSmartPicks, getDangerAlerts, getEngineScore } from '../services/api';
import type { SmartPick, EngineScoreResponse } from '../types';

const { Title, Text } = Typography;

const ENGINE_KEYS = [
  { key: 'monte_carlo', tKey: 'monteCarlo', icon: '🎲' },
  { key: 'momentum', tKey: 'momentum', icon: '🚀' },
  { key: 'volume', tKey: 'volume', icon: '📊' },
  { key: 'support_resistance', tKey: 'supportResistance', icon: '🎯' },
  { key: 'mean_reversion', tKey: 'meanReversion', icon: '🔄' },
  { key: 'bollinger', tKey: 'bollinger', icon: '💥' },
  { key: 'correlation', tKey: 'correlation', icon: '🔗' },
  { key: 'rsi', tKey: 'rsi', icon: '⚖️' },
  { key: 'macd', tKey: 'macd', icon: '📈' },
] as const;

function scoreColor(score: number): string {
  if (score >= 65) return '#00d4aa';
  if (score >= 45) return '#ffd43b';
  return '#ff4757';
}

function signalTag(signal: string) {
  const color = signal.includes('BUY') ? 'success' : signal.includes('SELL') ? 'error' : 'warning';
  return <Tag color={color}>{signal}</Tag>;
}

function alertLevelColor(level: string) {
  if (level === 'red') return '#ff4757';
  if (level === 'yellow') return '#ffd43b';
  return '#00d4aa';
}

function alertIcon(level: string) {
  if (level === 'red') return <WarningOutlined style={{ color: '#ff4757', fontSize: 18 }} />;
  if (level === 'yellow') return <ExclamationCircleOutlined style={{ color: '#ffd43b', fontSize: 18 }} />;
  return <CheckCircleOutlined style={{ color: '#00d4aa', fontSize: 18 }} />;
}

interface DangerAlert {
  position_id: string;
  ticker: string;
  direction?: string;
  primary_reason: string;
  alert_level: 'red' | 'yellow' | 'green';
  combined_score: number;
  engines?: Record<string, { score: number; verdict?: string }>;
}

export default function SmartPicks() {
  const { t } = useTranslation(['engines', 'common']);
  const navigate = useNavigate();

  const [picks, setPicks] = useState<SmartPick[]>([]);
  const [totalScored, setTotalScored] = useState(0);
  const [alerts, setAlerts] = useState<DangerAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [computedAt, setComputedAt] = useState<string | null>(null);

  // Detail drawer
  const [drawerPick, setDrawerPick] = useState<SmartPick | null>(null);

  // Manual score
  const [manualTicker, setManualTicker] = useState('');
  const [manualMarket, setManualMarket] = useState('egypt');
  const [manualResult, setManualResult] = useState<EngineScoreResponse | { error: string } | null>(null);
  const [manualLoading, setManualLoading] = useState(false);

  async function fetchPicks() {
    setLoading(true);
    setError(null);
    try {
      const data = await getSmartPicks('egypt', 50);
      setPicks(data.picks || []);
      setTotalScored(data.total_scored || 0);
      setComputedAt(data.computed_at || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load smart picks');
    } finally {
      setLoading(false);
    }
  }

  async function fetchAlerts() {
    setAlertsLoading(true);
    try {
      const data = await getDangerAlerts();
      setAlerts(((data as { alerts?: DangerAlert[] }).alerts) || []);
    } catch {
      /* silent */
    } finally {
      setAlertsLoading(false);
    }
  }

  async function handleManualScore() {
    if (!manualTicker.trim()) return;
    setManualLoading(true);
    setManualResult(null);
    try {
      const data = await getEngineScore(manualTicker.trim(), manualMarket);
      setManualResult(data);
    } catch (err) {
      setManualResult({ error: err instanceof Error ? err.message : 'Failed to score' });
    } finally {
      setManualLoading(false);
    }
  }

  useEffect(() => {
    fetchPicks();
    fetchAlerts();
  }, []);

  // PRIMARY columns only — secondary metrics live in the expanded row.
  // Sized to fit ~1020px (1280 viewport minus 260px sidebar).
  const columns = [
    {
      title: '#',
      dataIndex: 'rank',
      key: 'rank',
      width: 45,
      render: (_: unknown, _r: SmartPick, idx: number) => (
        <Text strong style={{ color: '#ff6b00' }}>#{idx + 1}</Text>
      ),
    },
    {
      title: t('ticker'),
      dataIndex: 'ticker',
      key: 'ticker',
      width: 80,
      render: (v: string, record: SmartPick) => (
        <Button
          type="link"
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            setDrawerPick(record);
          }}
          style={{ padding: 0, color: '#ff6b00', fontWeight: 600 }}
        >
          {v}
        </Button>
      ),
    },
    {
      title: t('company'),
      dataIndex: 'company_name',
      key: 'company_name',
      ellipsis: true,
      render: (v: string, r: SmartPick) => (
        <div>
          <Text ellipsis style={{ fontSize: 12 }}>{v}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 10 }}>{r.sector}</Text>
        </div>
      ),
    },
    {
      title: t('signal'),
      dataIndex: 'signal',
      key: 'signal',
      width: 110,
      filters: [
        { text: 'Strong Buy', value: 'STRONG BUY' },
        { text: 'Buy', value: 'BUY' },
        { text: 'Hold', value: 'HOLD' },
        { text: 'Neutral', value: 'NEUTRAL' },
        { text: 'Sell', value: 'SELL' },
      ],
      onFilter: (value: boolean | React.Key, record: SmartPick) => record.signal === value,
      render: (v: string) => signalTag(v),
    },
    {
      title: t('score'),
      dataIndex: 'combined_score',
      key: 'combined_score',
      width: 75,
      sorter: (a: SmartPick, b: SmartPick) => a.combined_score - b.combined_score,
      defaultSortOrder: 'descend' as const,
      render: (v: number, r: SmartPick) => (
        <div>
          <Text strong style={{ color: scoreColor(v), fontSize: 16 }}>{v}</Text>
          {r.combined_score_raw !== v && (
            <div>
              <Text type="secondary" style={{ fontSize: 9 }}>raw {r.combined_score_raw}</Text>
            </div>
          )}
        </div>
      ),
    },
    {
      title: t('regimeLabel', { defaultValue: 'Regime' }),
      dataIndex: 'volatility_regime_tag',
      key: 'volatility_regime_tag',
      width: 90,
      render: (v: SmartPick['volatility_regime_tag']) => <VolatilityBadge tag={v} />,
    },
    {
      title: t('enginesLabel', { defaultValue: 'Engines' }),
      key: 'engines_agree',
      width: 80,
      render: (_: unknown, r: SmartPick) => (
        <Text style={{ color: r.bullish_engines >= 5 ? '#00d4aa' : r.bullish_engines >= 3 ? '#ffd43b' : '#ff4757' }}>
          {r.bullish_engines}/{r.total_engines}
        </Text>
      ),
    },
    {
      title: '',
      key: 'action',
      width: 90,
      render: (_: unknown, record: SmartPick) => (
        <Button
          size="small"
          type="primary"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/analysis?ticker=${record.ticker}&market=${record.market_id}`);
          }}
        >
          {t('analyze')} →
        </Button>
      ),
    },
  ];

  return (
    <>
      <Topbar title={t('title')} />
      <div style={{ padding: 24 }}>
        {/* Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: 16,
            gap: 12,
          }}
        >
          <div style={{ minWidth: 0 }}>
            <Title level={4} style={{ margin: 0 }}>
              <ThunderboltOutlined style={{ color: '#ff6b00', marginInlineEnd: 8 }} />
              {t('title')}
            </Title>
            <Text type="secondary" style={{ fontSize: 12 }}>{t('subtitle')}</Text>
            {computedAt && (
              <Text type="secondary" style={{ fontSize: 10, display: 'block', marginTop: 2 }}>
                Last updated: {new Date(computedAt).toLocaleString()} · {totalScored} stocks scored
              </Text>
            )}
          </div>
          <Button icon={<ReloadOutlined />} onClick={fetchPicks} loading={loading} type="primary">
            {t('refresh')}
          </Button>
        </div>

        {/* Error */}
        {error && <Alert type="error" message={error} showIcon closable style={{ marginBottom: 16 }} />}

        {/* Smart Picks Table */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 80 }}>
            <Spin size="large" />
            <div style={{ marginTop: 12, color: 'var(--text3)' }}>{t('loading')}</div>
          </div>
        ) : picks.length === 0 ? (
          <Empty description={t('noData')} style={{ padding: 60 }} />
        ) : (
          <Table<SmartPick>
            dataSource={picks}
            columns={columns}
            rowKey="ticker"
            size="small"
            pagination={{ pageSize: 25, showTotal: (total) => `${total} stocks` }}
            expandable={{ expandedRowRender: (record) => <PickRowExpanded record={record} /> }}
          />
        )}

        {/* Score Any Stock */}
        <Card size="small" style={{ marginTop: 24 }}>
          <Space style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text strong><SearchOutlined /> {t('scoreAny')}</Text>
          </Space>
          <Space style={{ marginTop: 10, width: '100%' }} wrap>
            <Select
              value={manualMarket}
              onChange={setManualMarket}
              style={{ width: 120 }}
              options={[{ value: 'egypt', label: 'EGX' }, { value: 'us', label: 'US' }]}
            />
            <Input
              placeholder="ETEL, COMI, AAPL..."
              value={manualTicker}
              onChange={(e) => setManualTicker(e.target.value.toUpperCase())}
              onPressEnter={handleManualScore}
              style={{ width: 200 }}
              prefix={<SearchOutlined />}
            />
            <Button type="primary" onClick={handleManualScore} loading={manualLoading}>
              {t('scoreBtn')}
            </Button>
          </Space>
          {manualResult && !('error' in manualResult) && (
            <div style={{ marginTop: 16 }}>
              <Space align="center" style={{ marginBottom: 12 }}>
                <Text strong style={{ fontSize: 28, color: scoreColor(manualResult.combined_score) }}>
                  {manualResult.combined_score}/100
                </Text>
                {signalTag(manualResult.combined_signal)}
                <VolatilityBadge tag={manualResult.volatility_regime_tag} />
              </Space>
              <Row gutter={16} style={{ marginBottom: 12 }}>
                <Col xs={12} md={6}>
                  <Statistic
                    title="MC Prob Up"
                    value={`${(manualResult.engines?.monte_carlo?.prob_up as number | undefined)?.toFixed(0) ?? '—'}%`}
                    valueStyle={{ color: '#00d4aa' }}
                  />
                </Col>
                <Col xs={12} md={6}>
                  <Statistic
                    title="Expected"
                    value={`${(manualResult.engines?.monte_carlo?.expected_change as number | undefined)?.toFixed(1) ?? '—'}%`}
                  />
                </Col>
                <Col xs={12} md={6}>
                  <Statistic
                    title="Best Case"
                    value={`+${(manualResult.engines?.monte_carlo?.best_case as number | undefined)?.toFixed(1) ?? '—'}%`}
                    valueStyle={{ color: '#00d4aa' }}
                  />
                </Col>
                <Col xs={12} md={6}>
                  <Statistic
                    title="Worst Case"
                    value={`${(manualResult.engines?.monte_carlo?.worst_case as number | undefined)?.toFixed(1) ?? '—'}%`}
                    valueStyle={{ color: '#ff4757' }}
                  />
                </Col>
              </Row>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
                  gap: 6,
                }}
              >
                {ENGINE_KEYS.map(({ key, tKey, icon }) => {
                  const eng = manualResult.engines?.[key];
                  if (!eng) return null;
                  return <EngineCell key={key} name={key} tKey={tKey} icon={icon} engine={eng} />;
                })}
              </div>
            </div>
          )}
          {manualResult && 'error' in manualResult && (
            <Alert type="error" message={manualResult.error} style={{ marginTop: 8 }} />
          )}
        </Card>

        {/* Danger Alerts */}
        <div style={{ marginTop: 24 }}>
          <Space style={{ marginBottom: 12 }}>
            <WarningOutlined style={{ color: '#ff4757', fontSize: 16 }} />
            <Title level={5} style={{ margin: 0 }}>{t('danger.title')}</Title>
            <Text type="secondary" style={{ fontSize: 12 }}>{t('danger.subtitle')}</Text>
          </Space>

          {alertsLoading ? (
            <Spin />
          ) : alerts.length === 0 ? (
            <Card><Text type="secondary">{t('danger.noPositions')}</Text></Card>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {alerts.map((alert) => (
                <Card
                  key={alert.position_id}
                  size="small"
                  style={{ borderInlineStart: `3px solid ${alertLevelColor(alert.alert_level)}` }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space>
                      {alertIcon(alert.alert_level)}
                      <Text strong style={{ color: '#ff6b00', fontSize: 14 }}>{alert.ticker}</Text>
                      <Tag>{alert.direction?.toUpperCase()}</Tag>
                      <Text type="secondary" style={{ fontSize: 12 }}>{alert.primary_reason}</Text>
                    </Space>
                    <Space>
                      <Text strong style={{ color: alertLevelColor(alert.alert_level), fontSize: 18 }}>
                        {alert.combined_score}
                      </Text>
                      <Tag color={alert.alert_level === 'red' ? 'error' : alert.alert_level === 'yellow' ? 'warning' : 'success'}>
                        {t(`danger.${alert.alert_level}`)}
                      </Tag>
                    </Space>
                  </div>
                  {alert.engines && Object.keys(alert.engines).length > 0 && (
                    <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--border)' }}>
                      {ENGINE_KEYS.map(({ key, icon }) => {
                        const eng = alert.engines?.[key];
                        if (!eng) return null;
                        return (
                          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                            <span style={{ fontSize: 12 }}>{icon}</span>
                            <Progress percent={eng.score} size="small" strokeColor={scoreColor(eng.score)} style={{ flex: 1 }} showInfo={false} />
                            <Text style={{ fontSize: 10, color: scoreColor(eng.score), fontWeight: 600, width: 24, textAlign: 'right' }}>
                              {eng.score}
                            </Text>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Detail Drawer */}
      <PickDetailDrawer
        pick={drawerPick}
        open={drawerPick !== null}
        onClose={() => setDrawerPick(null)}
      />
    </>
  );
}

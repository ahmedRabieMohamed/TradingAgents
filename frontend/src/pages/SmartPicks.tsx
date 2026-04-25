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
import { getSmartPicks, getDangerAlerts, getEngineScore } from '../services/api';

const { Title, Text } = Typography;

const ENGINE_KEYS = [
  { key: 'monte_carlo', icon: '🎲' },
  { key: 'momentum', icon: '🚀' },
  { key: 'volume', icon: '📊' },
  { key: 'support_resistance', icon: '🎯' },
  { key: 'mean_reversion', icon: '🔄' },
  { key: 'bollinger', icon: '💥' },
  { key: 'correlation', icon: '🔗' },
];

function scoreColor(score: number): string {
  if (score >= 65) return '#00d4aa';
  if (score >= 45) return '#ffd43b';
  return '#ff4757';
}

function signalColor(signal: string): string {
  if (signal.includes('BUY')) return 'success';
  if (signal.includes('SELL')) return 'error';
  return 'warning';
}

function alertLevelColor(level: string) {
  if (level === 'red') return '#ff4757';
  if (level === 'yellow') return '#ffd43b';
  return '#00d4aa';
}

function alertLevelIcon(level: string) {
  if (level === 'red') return <WarningOutlined style={{ color: '#ff4757' }} />;
  if (level === 'yellow') return <ExclamationCircleOutlined style={{ color: '#ffd43b' }} />;
  return <CheckCircleOutlined style={{ color: '#00d4aa' }} />;
}

export default function SmartPicks() {
  const { t } = useTranslation(['engines', 'common']);
  const navigate = useNavigate();

  const [picks, setPicks] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Manual score
  const [manualTicker, setManualTicker] = useState('');
  const [manualMarket, setManualMarket] = useState('egypt');
  const [manualResult, setManualResult] = useState<any>(null);
  const [manualLoading, setManualLoading] = useState(false);

  async function fetchPicks() {
    setLoading(true);
    setError(null);
    try {
      const data = await getSmartPicks('egypt', 10);
      setPicks(data.picks || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load smart picks');
    } finally {
      setLoading(false);
    }
  }

  async function fetchAlerts() {
    setAlertsLoading(true);
    try {
      const data = await getDangerAlerts();
      setAlerts(data.alerts || []);
    } catch {
      // Silent — alerts are secondary
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
    } catch (err: any) {
      setManualResult({ error: err.message || 'Failed to score' });
    } finally {
      setManualLoading(false);
    }
  }

  useEffect(() => {
    fetchPicks();
    fetchAlerts();
  }, []);

  const columns = [
    {
      title: '#',
      dataIndex: 'rank',
      key: 'rank',
      width: 50,
      render: (v: number) => <Text strong style={{ color: '#ff6b00' }}>#{v}</Text>,
    },
    {
      title: t('ticker'),
      dataIndex: 'ticker',
      key: 'ticker',
      render: (v: string) => <Text strong style={{ color: '#ff6b00' }}>{v}</Text>,
    },
    {
      title: t('company'),
      dataIndex: 'company_name',
      key: 'company_name',
      render: (v: string) => <Text type="secondary">{v}</Text>,
    },
    {
      title: t('score'),
      dataIndex: 'combined_score',
      key: 'combined_score',
      render: (v: number) => (
        <Text strong style={{ color: scoreColor(v), fontSize: 16 }}>{v}</Text>
      ),
    },
    {
      title: t('mcProb'),
      dataIndex: 'mc_probability',
      key: 'mc_probability',
      render: (v: number | null) => v != null ? (
        <Text style={{ color: v > 55 ? '#00d4aa' : v < 45 ? '#ff4757' : '#ffd43b' }}>
          {v.toFixed(0)}%
        </Text>
      ) : '—',
    },
    {
      title: t('momentum'),
      dataIndex: 'momentum_score',
      key: 'momentum_score',
      render: (v: number | null) => v != null ? (
        <Text style={{ color: scoreColor(v) }}>{v}</Text>
      ) : '—',
    },
    {
      title: t('signal'),
      dataIndex: 'signal',
      key: 'signal',
      render: (v: string) => <Tag color={signalColor(v)}>{v}</Tag>,
    },
    {
      title: '',
      key: 'action',
      render: (_: unknown, record: any) => (
        <Button
          size="small"
          type="primary"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/analysis?ticker=${record.ticker}&market=${record.market_id}`);
          }}
        >
          {t('analyze')}
        </Button>
      ),
    },
  ];

  return (
    <>
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 1100 }}>

        {/* Header */}
        <Space style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <div>
            <Title level={4} style={{ margin: 0 }}>{t('title')}</Title>
            <Text type="secondary" style={{ fontSize: 12 }}>{t('subtitle')}</Text>
          </div>
          <Button icon={<ReloadOutlined />} onClick={fetchPicks} loading={loading}>
            {t('refresh')}
          </Button>
        </Space>

        {/* Smart Picks Table */}
        {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

        {loading ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Spin size="large" tip={t('loading')} />
          </div>
        ) : picks.length === 0 ? (
          <Empty description={t('noData')} style={{ padding: 40 }} />
        ) : (
          <Table
            dataSource={picks}
            columns={columns}
            rowKey="ticker"
            size="middle"
            pagination={false}
            scroll={{ x: true }}
            expandable={{
              expandedRowRender: (record) => (
                <div style={{ padding: '8px 0' }}>
                  <Text strong style={{ fontSize: 13, marginBottom: 12, display: 'block' }}>
                    {t('engineBreakdown')}
                  </Text>
                  {ENGINE_KEYS.map(({ key, icon }) => {
                    const eng = record.engines?.[key];
                    if (!eng) return null;
                    const score = eng.score ?? 50;
                    return (
                      <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                        <span style={{ width: 20 }}>{icon}</span>
                        <Text style={{ width: 130, fontSize: 12 }}>{t(`engines.${key === 'monte_carlo' ? 'monteCarlo' : key === 'support_resistance' ? 'supportResistance' : key === 'mean_reversion' ? 'meanReversion' : key}`)}</Text>
                        <Progress
                          percent={score}
                          size="small"
                          strokeColor={scoreColor(score)}
                          style={{ flex: 1, margin: 0 }}
                          format={() => <span style={{ color: scoreColor(score), fontWeight: 700 }}>{score}</span>}
                        />
                        <Tag color={eng.verdict === 'BULLISH' ? 'success' : eng.verdict === 'BEARISH' ? 'error' : 'warning'} style={{ margin: 0, fontSize: 10 }}>
                          {t(`verdicts.${eng.verdict}`)}
                        </Tag>
                      </div>
                    );
                  })}
                  {record.engines?.monte_carlo && !record.engines.monte_carlo.error && (
                    <Card size="small" style={{ marginTop: 12 }}>
                      <Row gutter={16}>
                        <Col span={6}><Statistic title={t('mc.probUp')} value={`${record.engines.monte_carlo.prob_up?.toFixed(0)}%`} valueStyle={{ color: '#00d4aa' }} /></Col>
                        <Col span={6}><Statistic title={t('mc.expected')} value={`${record.engines.monte_carlo.expected_change > 0 ? '+' : ''}${record.engines.monte_carlo.expected_change?.toFixed(1)}%`} /></Col>
                        <Col span={6}><Statistic title={t('mc.bestCase')} value={`+${record.engines.monte_carlo.best_case?.toFixed(1)}%`} valueStyle={{ color: '#00d4aa' }} /></Col>
                        <Col span={6}><Statistic title={t('mc.worstCase')} value={`${record.engines.monte_carlo.worst_case?.toFixed(1)}%`} valueStyle={{ color: '#ff4757' }} /></Col>
                      </Row>
                      <Text type="secondary" style={{ fontSize: 10, marginTop: 8, display: 'block' }}>{t('mc.simulations')}</Text>
                    </Card>
                  )}
                </div>
              ),
            }}
          />
        )}

        {/* Score Any Stock */}
        <Card size="small" style={{ marginTop: 24 }}>
          <Text strong>{t('scoreAny')}</Text>
          <Space style={{ marginTop: 8, width: '100%' }} wrap>
            <Select value={manualMarket} onChange={setManualMarket} style={{ width: 120 }}
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
          {manualResult && !manualResult.error && (
            <div style={{ marginTop: 12 }}>
              <Space>
                <Text strong style={{ fontSize: 20, color: scoreColor(manualResult.combined_score) }}>
                  {manualResult.combined_score}/100
                </Text>
                <Tag color={signalColor(manualResult.combined_signal)}>{manualResult.combined_signal}</Tag>
              </Space>
              <div style={{ marginTop: 8 }}>
                {ENGINE_KEYS.map(({ key, icon }) => {
                  const eng = manualResult.engines?.[key];
                  if (!eng) return null;
                  return (
                    <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span>{icon}</span>
                      <Progress percent={eng.score} size="small" strokeColor={scoreColor(eng.score)} style={{ flex: 1 }} format={() => eng.score} />
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          {manualResult?.error && <Alert type="error" message={manualResult.error} style={{ marginTop: 8 }} />}
        </Card>

        {/* Danger Alerts */}
        <div style={{ marginTop: 24 }}>
          <Space style={{ marginBottom: 12 }}>
            <ThunderboltOutlined style={{ color: '#ff4757' }} />
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
                  style={{
                    borderInlineStart: `3px solid ${alertLevelColor(alert.alert_level)}`,
                  }}
                >
                  <Space style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Space>
                      {alertLevelIcon(alert.alert_level)}
                      <Text strong style={{ color: '#ff6b00' }}>{alert.ticker}</Text>
                      <Tag>{alert.direction?.toUpperCase()}</Tag>
                      <Text type="secondary" style={{ fontSize: 12 }}>{alert.primary_reason}</Text>
                    </Space>
                    <Space>
                      <Text strong style={{ color: alertLevelColor(alert.alert_level), fontSize: 16 }}>
                        {alert.combined_score}
                      </Text>
                      <Tag color={alert.alert_level === 'red' ? 'error' : alert.alert_level === 'yellow' ? 'warning' : 'success'}>
                        {t(`danger.${alert.alert_level}`)}
                      </Tag>
                    </Space>
                  </Space>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

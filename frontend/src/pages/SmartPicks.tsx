import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table, Button, Tag, Typography, Space, Spin, Alert, Card,
  Progress, Input, Select, Statistic, Row, Col, Empty, Tooltip,
  Descriptions,
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
  { key: 'monte_carlo', tKey: 'monteCarlo', icon: '🎲' },
  { key: 'momentum', tKey: 'momentum', icon: '🚀' },
  { key: 'volume', tKey: 'volume', icon: '📊' },
  { key: 'support_resistance', tKey: 'supportResistance', icon: '🎯' },
  { key: 'mean_reversion', tKey: 'meanReversion', icon: '🔄' },
  { key: 'bollinger', tKey: 'bollinger', icon: '💥' },
  { key: 'correlation', tKey: 'correlation', icon: '🔗' },
];

function scoreColor(score: number): string {
  if (score >= 65) return '#00d4aa';
  if (score >= 45) return '#ffd43b';
  return '#ff4757';
}

function signalTag(signal: string) {
  const color = signal.includes('BUY') ? 'success' : signal.includes('SELL') ? 'error' : 'warning';
  return <Tag color={color}>{signal}</Tag>;
}

function pctText(val: number | null | undefined, prefix = '') {
  if (val == null) return <Text type="secondary">—</Text>;
  const color = val > 0 ? '#00d4aa' : val < 0 ? '#ff4757' : undefined;
  return <Text style={{ color, fontWeight: 600 }}>{prefix}{val > 0 ? '+' : ''}{val.toFixed(1)}%</Text>;
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

export default function SmartPicks() {
  const { t } = useTranslation(['engines', 'common']);
  const navigate = useNavigate();

  const [picks, setPicks] = useState<any[]>([]);
  const [totalScored, setTotalScored] = useState(0);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [computedAt, setComputedAt] = useState<string | null>(null);

  // Manual score
  const [manualTicker, setManualTicker] = useState('');
  const [manualMarket, setManualMarket] = useState('egypt');
  const [manualResult, setManualResult] = useState<any>(null);
  const [manualLoading, setManualLoading] = useState(false);

  async function fetchPicks() {
    setLoading(true);
    setError(null);
    try {
      const data = await getSmartPicks('egypt', 50);
      setPicks(data.picks || []);
      setTotalScored(data.total_scored || 0);
      setComputedAt(data.computed_at || null);
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
    } catch { /* silent */ } finally {
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

  useEffect(() => { fetchPicks(); fetchAlerts(); }, []);

  const columns: any[] = [
    {
      title: '#',
      dataIndex: 'rank',
      key: 'rank',
      width: 45,
      fixed: 'left' as const,
      render: (v: number) => <Text strong style={{ color: '#ff6b00' }}>#{v}</Text>,
    },
    {
      title: t('ticker'),
      dataIndex: 'ticker',
      key: 'ticker',
      width: 70,
      fixed: 'left' as const,
      render: (v: string) => <Text strong style={{ color: '#ff6b00' }}>{v}</Text>,
    },
    {
      title: t('company'),
      dataIndex: 'company_name',
      key: 'company_name',
      width: 160,
      ellipsis: true,
      render: (v: string, r: any) => (
        <div>
          <Text ellipsis style={{ fontSize: 12 }}>{v}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 10 }}>{r.sector}</Text>
        </div>
      ),
    },
    {
      title: t('score'),
      dataIndex: 'combined_score',
      key: 'combined_score',
      width: 65,
      sorter: (a: any, b: any) => a.combined_score - b.combined_score,
      defaultSortOrder: 'descend' as const,
      render: (v: number) => (
        <Text strong style={{ color: scoreColor(v), fontSize: 16 }}>{v}</Text>
      ),
    },
    {
      title: t('signal'),
      dataIndex: 'signal',
      key: 'signal',
      width: 100,
      filters: [
        { text: 'Strong Buy', value: 'STRONG BUY' },
        { text: 'Buy', value: 'BUY' },
        { text: 'Hold', value: 'HOLD' },
        { text: 'Sell', value: 'SELL' },
      ],
      onFilter: (value: any, record: any) => record.signal === value,
      render: (v: string) => signalTag(v),
    },
    {
      title: <Tooltip title="Monte Carlo Probability Up">{t('mcProb')}</Tooltip>,
      dataIndex: 'mc_probability',
      key: 'mc_probability',
      width: 70,
      sorter: (a: any, b: any) => (a.mc_probability ?? 0) - (b.mc_probability ?? 0),
      render: (v: number | null) => v != null ? (
        <Text style={{ color: scoreColor(v), fontWeight: 600 }}>{v.toFixed(0)}%</Text>
      ) : '—',
    },
    {
      title: <Tooltip title="Expected 7-day change (Monte Carlo)">Expected</Tooltip>,
      dataIndex: 'mc_expected',
      key: 'mc_expected',
      width: 80,
      render: (v: number | null) => pctText(v),
    },
    {
      title: <Tooltip title="5-day price change">5d Change</Tooltip>,
      dataIndex: 'momentum_roc_5d',
      key: 'momentum_roc_5d',
      width: 80,
      sorter: (a: any, b: any) => (a.momentum_roc_5d ?? 0) - (b.momentum_roc_5d ?? 0),
      render: (v: number | null) => pctText(v),
    },
    {
      title: <Tooltip title="20-day price change">20d Change</Tooltip>,
      dataIndex: 'momentum_roc_20d',
      key: 'momentum_roc_20d',
      width: 80,
      render: (v: number | null) => pctText(v),
    },
    {
      title: <Tooltip title="Volume vs 20-day average">Vol Ratio</Tooltip>,
      dataIndex: 'volume_ratio',
      key: 'volume_ratio',
      width: 75,
      render: (v: number | null, r: any) => v != null ? (
        <Tooltip title={r.volume_is_real ? 'Real move (confirmed)' : 'Low volume (unconfirmed)'}>
          <Text style={{ color: v > 1.5 ? '#00d4aa' : 'var(--text2)' }}>
            {v.toFixed(1)}x {r.volume_is_real ? '✓' : ''}
          </Text>
        </Tooltip>
      ) : '—',
    },
    {
      title: <Tooltip title="Support / Resistance">S/R</Tooltip>,
      key: 'sr',
      width: 100,
      render: (_: unknown, r: any) => r.sr_support != null ? (
        <Tooltip title={`Support: ${r.sr_support} | Resistance: ${r.sr_resistance} | R:R ${r.sr_risk_reward}`}>
          <Text style={{ fontSize: 10 }}>
            <span style={{ color: '#00d4aa' }}>S:{r.sr_support?.toFixed(0)}</span>
            {' / '}
            <span style={{ color: '#ff4757' }}>R:{r.sr_resistance?.toFixed(0)}</span>
          </Text>
        </Tooltip>
      ) : '—',
    },
    {
      title: <Tooltip title="Bollinger Band status">BB</Tooltip>,
      dataIndex: 'bb_band_width',
      key: 'bb',
      width: 75,
      render: (v: string | null) => v ? (
        <Tag color={v === 'expanding' ? 'green' : v === 'squeeze' ? 'orange' : 'default'} style={{ fontSize: 10 }}>
          {v === 'expanding' ? '💥 Breakout' : v === 'squeeze' ? '⏳ Squeeze' : 'Normal'}
        </Tag>
      ) : '—',
    },
    {
      title: <Tooltip title="Bullish engines out of 7">Engines</Tooltip>,
      key: 'engines_agree',
      width: 70,
      render: (_: unknown, r: any) => (
        <Text style={{ color: r.bullish_engines >= 4 ? '#00d4aa' : r.bullish_engines >= 2 ? '#ffd43b' : '#ff4757' }}>
          {r.bullish_engines}/{r.total_engines}
        </Text>
      ),
    },
    {
      title: '',
      key: 'action',
      width: 80,
      fixed: 'right' as const,
      render: (_: unknown, record: any) => (
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

  const expandedRowRender = (record: any) => (
    <div style={{ padding: '8px 0' }}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        {/* Monte Carlo Card */}
        <Col span={8}>
          <Card size="small" title={<span>🎲 Monte Carlo (10K simulations)</span>}>
            <Row gutter={8}>
              <Col span={12}><Statistic title={t('mc.probUp')} value={`${record.mc_probability?.toFixed(0) ?? '—'}%`} valueStyle={{ color: '#00d4aa', fontSize: 18 }} /></Col>
              <Col span={12}><Statistic title={t('mc.expected')} value={`${record.mc_expected > 0 ? '+' : ''}${record.mc_expected?.toFixed(1) ?? '—'}%`} valueStyle={{ fontSize: 18 }} /></Col>
            </Row>
            <Row gutter={8} style={{ marginTop: 8 }}>
              <Col span={12}><Statistic title={t('mc.bestCase')} value={`+${record.mc_best_case?.toFixed(1) ?? '—'}%`} valueStyle={{ color: '#00d4aa', fontSize: 14 }} /></Col>
              <Col span={12}><Statistic title={t('mc.worstCase')} value={`${record.mc_worst_case?.toFixed(1) ?? '—'}%`} valueStyle={{ color: '#ff4757', fontSize: 14 }} /></Col>
            </Row>
          </Card>
        </Col>

        {/* Price Levels Card */}
        <Col span={8}>
          <Card size="small" title={<span>🎯 Price Levels</span>}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Current">{record.sr_current?.toFixed(2) ?? '—'}</Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#00d4aa' }}>Support</span>}>{record.sr_support?.toFixed(2) ?? '—'}</Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#ff4757' }}>Resistance</span>}>{record.sr_resistance?.toFixed(2) ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="Risk/Reward">{record.sr_risk_reward?.toFixed(1) ?? '—'}x</Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#00d4aa' }}>Upside</span>}>{pctText(record.sr_upside_pct, '↑ ')}</Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#ff4757' }}>Downside</span>}>{pctText(record.sr_downside_pct ? -record.sr_downside_pct : null, '↓ ')}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* Quick Stats Card */}
        <Col span={8}>
          <Card size="small" title={<span>📊 Quick Stats</span>}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Momentum Trend">{record.momentum_trend ?? '—'}/100</Descriptions.Item>
              <Descriptions.Item label="Mean Rev Distance">{pctText(record.mr_distance_pct)}</Descriptions.Item>
              <Descriptions.Item label="Oversold">{record.mr_is_oversold ? <Tag color="green">YES — Bounce likely</Tag> : 'No'}</Descriptions.Item>
              <Descriptions.Item label="Overbought">{record.mr_is_overbought ? <Tag color="red">YES — Pullback risk</Tag> : 'No'}</Descriptions.Item>
              <Descriptions.Item label="Bollinger">{record.bb_band_width === 'squeeze' ? <Tag color="orange">Squeeze — Big move soon</Tag> : record.bb_band_width === 'expanding' ? <Tag color="green">Breakout in progress</Tag> : 'Normal'}</Descriptions.Item>
              <Descriptions.Item label="Sector">{record.corr_sector ?? '—'} ({record.corr_peers_bullish ?? 0}/{record.corr_peers_total ?? 0} peers bullish)</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      {/* 7 Engine Bars */}
      <Text strong style={{ fontSize: 13, marginBottom: 8, display: 'block' }}>
        {t('engineBreakdown')} — {record.bullish_engines}/{record.total_engines} engines bullish
      </Text>
      {ENGINE_KEYS.map(({ key, tKey, icon }) => {
        const eng = record.engines?.[key];
        if (!eng) return null;
        const score = eng.score ?? 50;
        return (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ width: 20 }}>{icon}</span>
            <Text style={{ width: 140, fontSize: 12 }}>{t(`engines.${tKey}`)}</Text>
            <Progress
              percent={score}
              size="small"
              strokeColor={scoreColor(score)}
              style={{ flex: 1, margin: 0 }}
              format={() => <span style={{ color: scoreColor(score), fontWeight: 700 }}>{score}</span>}
            />
            <Tag
              color={eng.verdict === 'BULLISH' ? 'success' : eng.verdict === 'BEARISH' ? 'error' : 'warning'}
              style={{ margin: 0, fontSize: 10, width: 65, textAlign: 'center' }}
            >
              {t(`verdicts.${eng.verdict}`)}
            </Tag>
          </div>
        );
      })}
    </div>
  );

  return (
    <>
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 1400 }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div>
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
            <div style={{ marginTop: 4, fontSize: 11, color: 'var(--text3)' }}>
              Scoring all EGX stocks with 7 engines...
            </div>
          </div>
        ) : picks.length === 0 ? (
          <Empty description={t('noData')} style={{ padding: 60 }} />
        ) : (
          <Table
            dataSource={picks}
            columns={columns}
            rowKey="ticker"
            size="small"
            scroll={{ x: 1300 }}
            pagination={{ pageSize: 25, showTotal: (total) => `${total} stocks` }}
            expandable={{ expandedRowRender }}
          />
        )}

        {/* Score Any Stock */}
        <Card size="small" style={{ marginTop: 24 }}>
          <Space style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text strong><SearchOutlined /> {t('scoreAny')}</Text>
          </Space>
          <Space style={{ marginTop: 10, width: '100%' }} wrap>
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
            <div style={{ marginTop: 16 }}>
              <Space align="center" style={{ marginBottom: 12 }}>
                <Text strong style={{ fontSize: 28, color: scoreColor(manualResult.combined_score) }}>
                  {manualResult.combined_score}/100
                </Text>
                {signalTag(manualResult.combined_signal)}
              </Space>
              <Row gutter={16} style={{ marginBottom: 12 }}>
                <Col span={6}><Statistic title="MC Prob Up" value={`${manualResult.engines?.monte_carlo?.prob_up?.toFixed(0) ?? '—'}%`} valueStyle={{ color: '#00d4aa' }} /></Col>
                <Col span={6}><Statistic title="Expected" value={`${manualResult.engines?.monte_carlo?.expected_change?.toFixed(1) ?? '—'}%`} /></Col>
                <Col span={6}><Statistic title="Best Case" value={`+${manualResult.engines?.monte_carlo?.best_case?.toFixed(1) ?? '—'}%`} valueStyle={{ color: '#00d4aa' }} /></Col>
                <Col span={6}><Statistic title="Worst Case" value={`${manualResult.engines?.monte_carlo?.worst_case?.toFixed(1) ?? '—'}%`} valueStyle={{ color: '#ff4757' }} /></Col>
              </Row>
              {ENGINE_KEYS.map(({ key, tKey, icon }) => {
                const eng = manualResult.engines?.[key];
                if (!eng) return null;
                return (
                  <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span>{icon}</span>
                    <Text style={{ width: 130, fontSize: 12 }}>{t(`engines.${tKey}`)}</Text>
                    <Progress percent={eng.score} size="small" strokeColor={scoreColor(eng.score)} style={{ flex: 1 }} format={() => eng.score} />
                    <Tag color={eng.verdict === 'BULLISH' ? 'success' : eng.verdict === 'BEARISH' ? 'error' : 'warning'} style={{ fontSize: 10 }}>
                      {t(`verdicts.${eng.verdict}`)}
                    </Tag>
                  </div>
                );
              })}
            </div>
          )}
          {manualResult?.error && <Alert type="error" message={manualResult.error} style={{ marginTop: 8 }} />}
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
                  {/* Mini engine bars for each alert */}
                  {alert.engines && Object.keys(alert.engines).length > 0 && (
                    <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--border)' }}>
                      {ENGINE_KEYS.map(({ key, icon }) => {
                        const eng = alert.engines?.[key];
                        if (!eng) return null;
                        return (
                          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                            <span style={{ fontSize: 12 }}>{icon}</span>
                            <Progress percent={eng.score} size="small" strokeColor={scoreColor(eng.score)} style={{ flex: 1 }} showInfo={false} />
                            <Text style={{ fontSize: 10, color: scoreColor(eng.score), fontWeight: 600, width: 24, textAlign: 'right' }}>{eng.score}</Text>
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
    </>
  );
}

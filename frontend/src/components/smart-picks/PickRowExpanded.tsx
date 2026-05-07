import { Card, Col, Descriptions, Row, Statistic, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import EngineCell from './EngineCell';
import type { SmartPick } from '../../types';

const { Text } = Typography;

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

function pctText(val: number | null | undefined, prefix = '') {
  if (val == null) return <Text type="secondary">—</Text>;
  const color = val > 0 ? '#00d4aa' : val < 0 ? '#ff4757' : undefined;
  return (
    <Text style={{ color, fontWeight: 600 }}>
      {prefix}
      {val > 0 ? '+' : ''}
      {val.toFixed(1)}%
    </Text>
  );
}

interface PickRowExpandedProps {
  record: SmartPick;
}

export default function PickRowExpanded({ record }: PickRowExpandedProps) {
  const { t } = useTranslation('engines');

  const r = record as unknown as Record<string, number | string | null | undefined>;
  return (
    <div style={{ padding: '8px 0' }}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        {/* Monte Carlo Card */}
        <Col xs={24} md={8}>
          <Card size="small" title={<span>🎲 Monte Carlo (10K simulations)</span>}>
            <Row gutter={8}>
              <Col span={12}>
                <Statistic
                  title={t('mc.probUp')}
                  value={`${(r.mc_probability as number | undefined)?.toFixed(0) ?? '—'}%`}
                  valueStyle={{ color: '#00d4aa', fontSize: 18 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title={t('mc.expected')}
                  value={`${
                    (r.mc_expected as number | undefined) != null && (r.mc_expected as number) > 0 ? '+' : ''
                  }${(r.mc_expected as number | undefined)?.toFixed(1) ?? '—'}%`}
                  valueStyle={{ fontSize: 18 }}
                />
              </Col>
            </Row>
            <Row gutter={8} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Statistic
                  title={t('mc.bestCase')}
                  value={`+${(r.mc_best_case as number | undefined)?.toFixed(1) ?? '—'}%`}
                  valueStyle={{ color: '#00d4aa', fontSize: 14 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title={t('mc.worstCase')}
                  value={`${(r.mc_worst_case as number | undefined)?.toFixed(1) ?? '—'}%`}
                  valueStyle={{ color: '#ff4757', fontSize: 14 }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* Price Levels Card */}
        <Col xs={24} md={8}>
          <Card size="small" title={<span>🎯 Price Levels</span>}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Current">{(r.sr_current as number | undefined)?.toFixed(2) ?? '—'}</Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#00d4aa' }}>Support</span>}>
                {(r.sr_support as number | undefined)?.toFixed(2) ?? '—'}
              </Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#ff4757' }}>Resistance</span>}>
                {(r.sr_resistance as number | undefined)?.toFixed(2) ?? '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Risk/Reward">{(r.sr_risk_reward as number | undefined)?.toFixed(1) ?? '—'}x</Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#00d4aa' }}>Upside</span>}>
                {pctText(r.sr_upside_pct as number | undefined, '↑ ')}
              </Descriptions.Item>
              <Descriptions.Item label={<span style={{ color: '#ff4757' }}>Downside</span>}>
                {pctText(
                  (r.sr_downside_pct as number | undefined) != null ? -(r.sr_downside_pct as number) : null,
                  '↓ ',
                )}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* Quick Stats Card */}
        <Col xs={24} md={8}>
          <Card size="small" title={<span>📊 Quick Stats</span>}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Momentum 5d">{pctText(r.momentum_roc_5d as number | undefined)}</Descriptions.Item>
              <Descriptions.Item label="Momentum 20d">{pctText(r.momentum_roc_20d as number | undefined)}</Descriptions.Item>
              <Descriptions.Item label="Mean-rev distance">{pctText(r.mr_distance_pct as number | undefined)}</Descriptions.Item>
              <Descriptions.Item label="Volume ratio">
                {(r.volume_ratio as number | undefined) != null ? `${(r.volume_ratio as number).toFixed(1)}x` : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Bollinger">
                {r.bb_band_width === 'squeeze' ? (
                  <Tag color="orange">Squeeze — Big move soon</Tag>
                ) : r.bb_band_width === 'expanding' ? (
                  <Tag color="green">Breakout in progress</Tag>
                ) : (
                  'Normal'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Sector">
                {(r.corr_sector as string | undefined) ?? '—'} ({(r.corr_peers_bullish as number | undefined) ?? 0}/
                {(r.corr_peers_total as number | undefined) ?? 0} peers bullish)
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      {/* Engine breakdown (educational chips — hover any chip for explanation) */}
      <Text strong style={{ fontSize: 13, marginBottom: 8, display: 'block' }}>
        {t('engineBreakdown')} — {record.bullish_engines}/{record.total_engines} engines bullish
      </Text>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: 6,
          marginTop: 4,
        }}
      >
        {ENGINE_KEYS.map(({ key, tKey, icon }) => {
          const eng = record.engines?.[key];
          if (!eng) return null;
          return <EngineCell key={key} name={key} tKey={tKey} icon={icon} engine={eng} />;
        })}
      </div>
    </div>
  );
}

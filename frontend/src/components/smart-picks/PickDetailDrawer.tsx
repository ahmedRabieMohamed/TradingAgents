import { Drawer, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import EngineCell from './EngineCell';
import VolatilityBadge from './VolatilityBadge';
import type { SmartPick } from '../../types';

const { Text, Title } = Typography;

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

interface PickDetailDrawerProps {
  pick: SmartPick | null;
  open: boolean;
  onClose: () => void;
}

/**
 * Per-pick detail drawer. Phase 3 (US1) ships a skeleton: ticker header,
 * combined-score chip, regime badge, full engine list. Phase 7 (US5) adds
 * the score-breakdown panel with weight-contribution bars.
 */
export default function PickDetailDrawer({ pick, open, onClose }: PickDetailDrawerProps) {
  const { t } = useTranslation(['engines', 'common']);

  return (
    <Drawer
      open={open}
      onClose={onClose}
      width={520}
      title={
        pick && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Text strong style={{ color: '#ff6b00', fontSize: 18 }}>{pick.ticker}</Text>
            <Text type="secondary" style={{ fontSize: 12 }}>{pick.company_name}</Text>
            <VolatilityBadge tag={pick.volatility_regime_tag} />
          </div>
        )
      }
    >
      {pick && (
        <>
          {/* Score header */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 16 }}>
            <Text strong style={{ fontSize: 36, color: scoreColor(pick.combined_score) }}>
              {pick.combined_score}
            </Text>
            <Text type="secondary" style={{ fontSize: 13 }}>/ 100</Text>
            <Tag
              color={pick.signal.includes('BUY') ? 'success' : pick.signal.includes('SELL') ? 'error' : 'warning'}
              style={{ fontSize: 13, padding: '2px 10px' }}
            >
              {pick.signal}
            </Tag>
            {pick.combined_score_raw !== pick.combined_score && (
              <Text type="secondary" style={{ fontSize: 11, marginInlineStart: 'auto' }}>
                raw {pick.combined_score_raw} → {pick.combined_score}
              </Text>
            )}
          </div>

          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 16 }}>
            {pick.bullish_engines}/{pick.total_engines} engines bullish · {pick.sector}
          </Text>

          {/* Engines list */}
          <Title level={5} style={{ marginTop: 0, marginBottom: 8 }}>
            {t('engineBreakdown')}
          </Title>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {ENGINE_KEYS.map(({ key, tKey, icon }) => {
              const eng = pick.engines?.[key];
              if (!eng) return null;
              return <EngineCell key={key} name={key} tKey={tKey} icon={icon} engine={eng} />;
            })}
          </div>
        </>
      )}
    </Drawer>
  );
}

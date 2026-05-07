import { Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import EngineEducationPopover from './EngineEducationPopover';
import type { EngineResult } from '../../types';

const { Text } = Typography;

function scoreColor(score: number): string {
  if (score >= 65) return '#00d4aa';
  if (score >= 45) return '#ffd43b';
  return '#ff4757';
}

interface EngineCellProps {
  /** Backend engine key — must match a key in `frontend/src/locales/{en,ar}/engines.json` */
  name: string;
  /** Legacy translation alias used by the existing `engines.{tKey}` strings (for the engine label fallback). */
  tKey: string;
  icon: string;
  engine: EngineResult;
}

/**
 * Renders one engine's row inside the Pick expand-row: icon, label, score
 * chip, signal tag. The whole row is wrapped in EngineEducationPopover so a
 * hover/click explains what the engine does and why it matters.
 */
export default function EngineCell({ name, tKey, icon, engine }: EngineCellProps) {
  const { t } = useTranslation('engines');
  const label = t(`${name}.label`, { defaultValue: t(`engines.${tKey}`, { defaultValue: name }) });
  const dataMissing = engine.data_sufficient === false || engine.score == null;
  const score = engine.score ?? 50;
  const verdict = (engine as { verdict?: string }).verdict;
  const signal = engine.signal ?? verdict ?? 'NEUTRAL';

  return (
    <EngineEducationPopover engineName={name}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '4px 8px',
          background: 'var(--surface2)',
          borderRadius: 4,
          cursor: 'help',
        }}
        aria-label={`${label} engine score`}
      >
        <span style={{ width: 18, fontSize: 14 }}>{icon}</span>
        <Text style={{ fontSize: 11, flex: 1 }}>{label}</Text>
        {dataMissing ? (
          <Text type="secondary" style={{ fontSize: 10 }}>—</Text>
        ) : (
          <>
            <Text strong style={{ color: scoreColor(score), fontSize: 13, width: 28, textAlign: 'right' }}>
              {score}
            </Text>
            <Tag
              color={signal.includes('BUY') ? 'success' : signal.includes('SELL') ? 'error' : 'warning'}
              style={{ margin: 0, fontSize: 9, padding: '0 4px' }}
            >
              {signal}
            </Tag>
          </>
        )}
      </div>
    </EngineEducationPopover>
  );
}

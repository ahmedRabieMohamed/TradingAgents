import type { CSSProperties } from 'react';
import { useAnalysisStore } from '../../stores/analysisStore';
import StatsBar from './StatsBar';
import PipelineStageRow from './PipelineStage';
import MessageLog from './MessageLog';

const STAGE_ICONS: Record<string, string> = {
  'Market Analyst': '\uD83D\uDCC8',
  'News Analyst': '\uD83D\uDCF0',
  'Social Media Analyst': '\uD83D\uDCAC',
  'Fundamentals Analyst': '\uD83D\uDCCA',
  'Bull vs Bear Debate': '\u2696\uFE0F',
  'Trader': '\uD83D\uDCB9',
  'Risk Assessment': '\uD83D\uDEE1\uFE0F',
  'Portfolio Manager': '\uD83C\uDFAF',
};

const containerStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 16,
};

const stagesContainer: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 6,
};

const sectionLabel: CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: 'var(--text2)',
  marginBottom: 4,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const errorBox: CSSProperties = {
  padding: 16,
  background: 'rgba(239, 68, 68, 0.1)',
  border: '1px solid rgba(239, 68, 68, 0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#ef4444',
  fontSize: 13,
};

export default function AnalysisProgress() {
  const stages = useAnalysisStore((s) => s.stages);
  const messages = useAnalysisStore((s) => s.messages);
  const stats = useAnalysisStore((s) => s.stats);
  const error = useAnalysisStore((s) => s.error);
  const status = useAnalysisStore((s) => s.status);

  return (
    <div style={containerStyle}>
      {/* Stats */}
      <StatsBar stats={stats} />

      {/* Pipeline */}
      <div>
        <div style={sectionLabel}>Pipeline</div>
        <div style={stagesContainer}>
          {stages.map((stage) => (
            <PipelineStageRow
              key={stage.name}
              name={stage.name}
              description={stage.description}
              status={stage.status}
              icon={STAGE_ICONS[stage.name] || '\u2699\uFE0F'}
            />
          ))}
        </div>
      </div>

      {/* Messages */}
      <div>
        <div style={sectionLabel}>Agent Messages</div>
        <MessageLog messages={messages} />
      </div>

      {/* Error */}
      {status === 'failed' && error && (
        <div style={errorBox}>Analysis failed: {error}</div>
      )}
    </div>
  );
}

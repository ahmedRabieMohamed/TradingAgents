import { CSSProperties } from 'react';
import type { AnalysisSession } from '../../types';

interface CompareModalProps {
  sessions: [AnalysisSession, AnalysisSession];
  onClose: () => void;
}

const overlayStyle: CSSProperties = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0,0,0,0.6)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
  padding: 24,
};

const modalStyle: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  width: '100%',
  maxWidth: 900,
  maxHeight: '85vh',
  overflow: 'auto',
  padding: 24,
};

const headerStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 20,
};

const titleStyle: CSSProperties = {
  fontSize: 16,
  fontWeight: 600,
  color: 'var(--text)',
};

const closeBtnStyle: CSSProperties = {
  background: 'none',
  border: 'none',
  color: 'var(--text3)',
  fontSize: 20,
  cursor: 'pointer',
  padding: 4,
};

const columnsStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 20,
};

const columnStyle: CSSProperties = {
  background: 'var(--surface2)',
  borderRadius: 'var(--radius-md)',
  padding: 16,
  border: '1px solid var(--border)',
};

const tickerStyle: CSSProperties = {
  fontSize: 18,
  fontWeight: 700,
  color: 'var(--text)',
  marginBottom: 4,
};

const subtitleStyle: CSSProperties = {
  fontSize: 12,
  color: 'var(--text3)',
  marginBottom: 16,
};

const fieldRow: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  padding: '6px 0',
  borderBottom: '1px solid var(--border)',
  fontSize: 13,
};

const fieldLabel: CSSProperties = {
  color: 'var(--text3)',
  fontWeight: 500,
};

const sectionTitle: CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: 'var(--text2)',
  marginTop: 16,
  marginBottom: 8,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const reportPreview: CSSProperties = {
  fontSize: 12,
  color: 'var(--text2)',
  lineHeight: 1.6,
  maxHeight: 200,
  overflow: 'auto',
  padding: 10,
  background: 'var(--bg)',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  whiteSpace: 'pre-wrap',
};

function recColor(rec: string | null): string {
  if (rec === 'BUY') return '#10b981';
  if (rec === 'SELL') return '#ef4444';
  if (rec === 'HOLD') return '#eab308';
  return 'var(--text3)';
}

function SessionColumn({ session }: { session: AnalysisSession }) {
  const conf = session.confidence !== null ? `${Math.round(session.confidence)}%` : '--';

  // Get agent report summaries (first 300 chars of each)
  const reports = (session.reports || [])
    .sort((a, b) => a.sequence - b.sequence)
    .slice(0, 4);

  return (
    <div style={columnStyle}>
      <div style={tickerStyle}>{session.ticker}</div>
      <div style={subtitleStyle}>{session.stock_name} - {session.market_id.toUpperCase()}</div>

      <div style={fieldRow}>
        <span style={fieldLabel}>Recommendation</span>
        <span style={{ fontWeight: 600, color: recColor(session.recommendation) }}>
          {session.recommendation || '--'}
        </span>
      </div>
      <div style={fieldRow}>
        <span style={fieldLabel}>Confidence</span>
        <span style={{ fontWeight: 600, color: 'var(--text)' }}>{conf}</span>
      </div>
      <div style={fieldRow}>
        <span style={fieldLabel}>Horizon</span>
        <span style={{ color: 'var(--text)' }}>{session.trade_horizon}</span>
      </div>
      <div style={fieldRow}>
        <span style={fieldLabel}>Date</span>
        <span style={{ color: 'var(--text)' }}>{session.analysis_date}</span>
      </div>
      <div style={fieldRow}>
        <span style={fieldLabel}>Status</span>
        <span style={{ color: 'var(--text)' }}>{session.status}</span>
      </div>

      {session.simulation && (
        <div style={fieldRow}>
          <span style={fieldLabel}>Return</span>
          <span style={{
            fontWeight: 600,
            color: session.simulation.return_pct >= 0 ? '#10b981' : '#ef4444',
          }}>
            {session.simulation.return_pct >= 0 ? '+' : ''}
            {session.simulation.return_pct.toFixed(2)}%
          </span>
        </div>
      )}

      {reports.length > 0 && (
        <>
          <div style={sectionTitle}>Agent Reports</div>
          {reports.map((r, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--accent)', marginBottom: 4 }}>
                {r.agent_name}
              </div>
              <div style={reportPreview}>
                {r.content.slice(0, 400)}{r.content.length > 400 ? '...' : ''}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default function CompareModal({ sessions, onClose }: CompareModalProps) {
  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <span style={titleStyle}>Compare Analyses</span>
          <button style={closeBtnStyle} onClick={onClose}>&times;</button>
        </div>
        <div style={columnsStyle}>
          <SessionColumn session={sessions[0]} />
          <SessionColumn session={sessions[1]} />
        </div>
      </div>
    </div>
  );
}

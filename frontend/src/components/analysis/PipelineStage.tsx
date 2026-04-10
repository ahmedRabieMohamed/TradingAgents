import type { CSSProperties } from 'react';

interface PipelineStageProps {
  name: string;
  description: string;
  status: 'waiting' | 'active' | 'done';
  icon: string;
}

const rowBase: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  padding: '10px 14px',
  borderRadius: 'var(--radius-sm)',
  transition: 'all 0.2s ease',
};

function rowStyle(status: 'waiting' | 'active' | 'done'): CSSProperties {
  if (status === 'active') {
    return {
      ...rowBase,
      border: '1.5px solid var(--accent)',
      background: 'rgba(99, 102, 241, 0.06)',
      opacity: 1,
    };
  }
  if (status === 'done') {
    return {
      ...rowBase,
      border: '1.5px solid var(--green)',
      background: 'rgba(34, 197, 94, 0.06)',
      opacity: 1,
    };
  }
  return {
    ...rowBase,
    border: '1px solid var(--border)',
    background: 'var(--surface)',
    opacity: 0.5,
  };
}

function iconContainerStyle(status: 'waiting' | 'active' | 'done'): CSSProperties {
  const bg =
    status === 'active'
      ? 'rgba(99, 102, 241, 0.15)'
      : status === 'done'
        ? 'rgba(34, 197, 94, 0.15)'
        : 'var(--surface2)';
  return {
    width: 36,
    height: 36,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 16,
    flexShrink: 0,
    background: bg,
  };
}

const nameStyle: CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text)',
};

const descStyle: CSSProperties = {
  fontSize: 11,
  color: 'var(--text3)',
  marginTop: 2,
};

const statusTextBase: CSSProperties = {
  fontSize: 11,
  fontWeight: 600,
  marginLeft: 'auto',
  flexShrink: 0,
  display: 'flex',
  alignItems: 'center',
  gap: 6,
};

const spinner: CSSProperties = {
  width: 14,
  height: 14,
  border: '2px solid rgba(99, 102, 241, 0.3)',
  borderTopColor: 'var(--accent)',
  borderRadius: '50%',
  animation: 'spin 0.8s linear infinite',
};

export default function PipelineStage({ name, description, status, icon }: PipelineStageProps) {
  return (
    <>
      {/* Inject spinner keyframes once */}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={rowStyle(status)}>
        <div style={iconContainerStyle(status)}>
          {status === 'done' ? (
            <span style={{ color: 'var(--green)' }}>&#10003;</span>
          ) : (
            <span style={{ color: status === 'active' ? 'var(--accent)' : 'var(--text3)' }}>
              {icon}
            </span>
          )}
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={nameStyle}>{name}</div>
          <div style={descStyle}>{description}</div>
        </div>

        <div
          style={{
            ...statusTextBase,
            color:
              status === 'done'
                ? 'var(--green)'
                : status === 'active'
                  ? 'var(--accent)'
                  : 'var(--text3)',
          }}
        >
          {status === 'active' && <div style={spinner} />}
          {status === 'waiting' && 'Waiting'}
          {status === 'active' && 'Running'}
          {status === 'done' && 'Complete'}
        </div>
      </div>
    </>
  );
}

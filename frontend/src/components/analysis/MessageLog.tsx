import { useEffect, useRef } from 'react';
import type { CSSProperties } from 'react';

interface Message {
  timestamp: string;
  agentName: string;
  content: string;
}

interface MessageLogProps {
  messages: Message[];
}

const containerStyle: CSSProperties = {
  maxHeight: 200,
  overflowY: 'auto',
  background: 'var(--bg)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: 10,
  fontFamily: '"SF Mono", "Fira Code", "Cascadia Code", monospace',
  fontSize: 12,
  lineHeight: 1.6,
};

const lineStyle: CSSProperties = {
  display: 'flex',
  gap: 8,
  padding: '2px 0',
  borderBottom: '1px solid rgba(255,255,255,0.04)',
};

const timestampStyle: CSSProperties = {
  color: 'var(--text3)',
  flexShrink: 0,
  fontSize: 11,
};

const agentStyle: CSSProperties = {
  color: 'var(--accent)',
  fontWeight: 600,
  flexShrink: 0,
};

const contentStyle: CSSProperties = {
  color: 'var(--text2)',
  wordBreak: 'break-word',
};

const emptyStyle: CSSProperties = {
  color: 'var(--text3)',
  fontStyle: 'italic',
  textAlign: 'center',
  padding: 20,
  fontSize: 12,
};

function formatTime(ts: string): string {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString('en-US', { hour12: false });
  } catch {
    return ts;
  }
}

export default function MessageLog({ messages }: MessageLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  if (messages.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={emptyStyle}>Waiting for agent messages...</div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {messages.map((msg, i) => (
        <div key={i} style={lineStyle}>
          <span style={timestampStyle}>{formatTime(msg.timestamp)}</span>
          <span style={agentStyle}>[{msg.agentName}]</span>
          <span style={contentStyle}>{msg.content}</span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

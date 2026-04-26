import { useState, useMemo } from 'react';
import type { CSSProperties } from 'react';
import { marked } from 'marked';

// Configure marked for GFM tables and breaks
marked.setOptions({
  gfm: true,
  breaks: false,
});

interface ReportSectionProps {
  title: string;
  icon: string;
  content: string;
  defaultOpen?: boolean;
}

const headerStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '14px 18px',
  background: 'var(--surface2)',
  borderRadius: 'var(--radius-sm)',
  cursor: 'pointer',
  userSelect: 'none',
  transition: 'background 0.15s',
};

const titleStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text)',
};

const bodyStyle: CSSProperties = {
  padding: '16px 18px',
  background: 'var(--surface)',
  borderRadius: '0 0 var(--radius-sm) var(--radius-sm)',
  borderTop: '1px solid var(--border)',
};

const containerStyle: CSSProperties = {
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  overflow: 'hidden',
  boxShadow: 'var(--shadow-sm)',
};

export default function ReportSection({ title, icon, content, defaultOpen = false }: ReportSectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  const [hovered, setHovered] = useState(false);

  const html = useMemo(() => {
    try {
      return marked.parse(content) as string;
    } catch {
      return content;
    }
  }, [content]);

  return (
    <div style={containerStyle}>
      <div
        style={{
          ...headerStyle,
          ...(hovered ? { background: 'rgba(59, 130, 246, 0.08)' } : {}),
          ...(open ? { borderRadius: 'var(--radius-sm) var(--radius-sm) 0 0' } : {}),
        }}
        onClick={() => setOpen(!open)}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <span style={titleStyle}>
          <span>{icon}</span>
          {title}
        </span>
        <span
          style={{
            fontSize: 12,
            color: 'var(--text3)',
            transition: 'transform 0.2s',
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
            display: 'inline-block',
          }}
        >
          &#9660;
        </span>
      </div>
      {open && (
        <div style={bodyStyle}>
          <div
            className="markdown-body"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        </div>
      )}
    </div>
  );
}

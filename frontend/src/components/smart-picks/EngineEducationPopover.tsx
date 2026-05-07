import { Popover, Tag, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';

const { Text, Paragraph } = Typography;

interface EngineEducationPopoverProps {
  /** Backend engine key — also the i18n key (`engines.<engineName>.*`). */
  engineName: string;
  children: ReactNode;
}

/**
 * Wraps an engine score chip; on hover (desktop) or click (touch) shows a
 * popover with what the engine measures, score-range interpretation, and
 * why it matters. Reads from i18n namespace `engines` so the active locale
 * (EN or AR) drives the content.
 */
export default function EngineEducationPopover({ engineName, children }: EngineEducationPopoverProps) {
  const { t } = useTranslation('engines');

  const FALLBACK_MISSING = '__missing__';
  const label = t(`${engineName}.label`, { defaultValue: FALLBACK_MISSING });
  const category = t(`${engineName}.category`, { defaultValue: FALLBACK_MISSING });
  const measures = t(`${engineName}.measures`, { defaultValue: FALLBACK_MISSING });
  const scoreRange = t(`${engineName}.scoreRange`, { defaultValue: FALLBACK_MISSING });
  const whyMatters = t(`${engineName}.whyMatters`, { defaultValue: FALLBACK_MISSING });

  // If the i18n catalog is missing this engine, render a graceful placeholder
  // (FR-014 / contract `engine-reference.md` — "no description available").
  const hasContent = measures !== FALLBACK_MISSING;

  const title = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <Text strong style={{ fontSize: 14 }}>{label === FALLBACK_MISSING ? engineName : label}</Text>
      {category !== FALLBACK_MISSING && (
        <Tag color="blue" style={{ margin: 0, fontSize: 10 }}>{category}</Tag>
      )}
    </div>
  );

  const content = hasContent ? (
    <div style={{ maxWidth: 320 }}>
      <div style={{ marginBottom: 8 }}>
        <Text type="secondary" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {t('education.measures', { defaultValue: 'What it measures' })}
        </Text>
        <Paragraph style={{ margin: '2px 0 0', fontSize: 12 }}>{measures}</Paragraph>
      </div>
      <div style={{ marginBottom: 8 }}>
        <Text type="secondary" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {t('education.scoreRange', { defaultValue: 'Score range' })}
        </Text>
        <Paragraph style={{ margin: '2px 0 0', fontSize: 12 }}>{scoreRange}</Paragraph>
      </div>
      <div>
        <Text type="secondary" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {t('education.whyMatters', { defaultValue: 'Why it matters' })}
        </Text>
        <Paragraph style={{ margin: '2px 0 0', fontSize: 12 }}>{whyMatters}</Paragraph>
      </div>
    </div>
  ) : (
    <div style={{ maxWidth: 280 }}>
      <Text type="secondary" style={{ fontSize: 12 }}>
        {t('education.missing', { defaultValue: 'No description available for this engine.' })}
      </Text>
    </div>
  );

  return (
    <Popover content={content} title={title} placement="top" trigger={['hover', 'click']} mouseEnterDelay={0.15}>
      {children}
    </Popover>
  );
}

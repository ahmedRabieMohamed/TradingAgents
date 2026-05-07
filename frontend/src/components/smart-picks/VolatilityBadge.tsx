import { Tag, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';
import type { VolatilityRegimeTag } from '../../types';

interface VolatilityBadgeProps {
  tag?: VolatilityRegimeTag;
}

const TAG_COLORS: Record<VolatilityRegimeTag, string> = {
  calm: 'default',
  normal: 'default',
  elevated: 'orange',
  extreme: 'red',
};

const TAG_GLYPH: Record<VolatilityRegimeTag, string> = {
  calm: '·',
  normal: '·',
  elevated: '!',
  extreme: '!!',
};

export default function VolatilityBadge({ tag }: VolatilityBadgeProps) {
  const { t } = useTranslation('engines');
  if (!tag) return null;
  const label = t(`regime.${tag}`, { defaultValue: tag });
  const tooltip = t(`regime.${tag}_tooltip`, { defaultValue: '' });
  return (
    <Tooltip title={tooltip || undefined}>
      <Tag color={TAG_COLORS[tag]} style={{ margin: 0, fontSize: 10 }}>
        {TAG_GLYPH[tag]} {label}
      </Tag>
    </Tooltip>
  );
}

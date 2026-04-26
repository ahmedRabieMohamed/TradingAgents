import { Layout, Typography, Space, Tag, Button } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { useMarketStore } from '../../stores/marketStore';
import { useLocaleStore } from '../../stores/localeStore';

const { Header } = Layout;
const { Title } = Typography;

interface TopbarProps {
  title: string;
}

export default function Topbar({ title }: TopbarProps) {
  const marketLabel = useMarketStore((s) => s.marketLabel);
  const { locale, setLocale } = useLocaleStore();

  return (
    <Header
      style={{
        height: 'var(--topbar-height)',
        position: 'sticky',
        top: 0,
        background: 'var(--surface)',
        borderBottom: '1px solid var(--border)',
        boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        zIndex: 50,
        lineHeight: 'normal',
      }}
    >
      <Title level={4} style={{ margin: 0, fontSize: 16, color: 'var(--text)' }}>
        {title}
      </Title>
      <Space size={10}>
        <Tag color="blue">{marketLabel}</Tag>
        <Tag color="purple">v0.1.0</Tag>
        <Button
          type="text"
          size="small"
          icon={<GlobalOutlined />}
          onClick={() => setLocale(locale === 'en' ? 'ar' : 'en')}
          style={{ color: 'var(--text2)', fontSize: 13 }}
        >
          {locale === 'en' ? 'العربية' : 'English'}
        </Button>
      </Space>
    </Header>
  );
}

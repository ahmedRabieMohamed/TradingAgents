import { Routes, Route } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import enUS from 'antd/locale/en_US'
import arEG from 'antd/locale/ar_EG'
import { useLocaleStore } from './stores/localeStore'
import appTheme from './theme'
import Sidebar from './components/layout/Sidebar'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import NewAnalysis from './pages/NewAnalysis'
import History from './pages/History'
import Performance from './pages/Performance'
import Portfolio from './pages/Portfolio'
import Watchlist from './pages/Watchlist'

export default function App() {
  const { locale, direction } = useLocaleStore()
  const antLocale = locale === 'ar' ? arEG : enUS

  return (
    <ConfigProvider theme={appTheme} locale={antLocale} direction={direction}>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar />
        <main
          style={{
            flex: 1,
            marginInlineStart: 'var(--sidebar-width)',
            minHeight: '100vh',
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<NewAnalysis />} />
            <Route path="/history" element={<History />} />
            <Route path="/performance" element={<Performance />} />
            <Route path="/watchlist" element={<Watchlist />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </ConfigProvider>
  )
}

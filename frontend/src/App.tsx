import { Routes, Route, useLocation } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import { AnimatePresence } from 'motion/react'
import enUS from 'antd/locale/en_US'
import arEG from 'antd/locale/ar_EG'
import { useLocaleStore } from './stores/localeStore'
import { PageTransition } from './motion'
import appTheme from './theme'
import Sidebar from './components/layout/Sidebar'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import NewAnalysis from './pages/NewAnalysis'
import History from './pages/History'
import Performance from './pages/Performance'
import Portfolio from './pages/Portfolio'
import Watchlist from './pages/Watchlist'
import SmartPicks from './pages/SmartPicks'

function AnimatedRoutes() {
  const location = useLocation()
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<PageTransition><Dashboard /></PageTransition>} />
        <Route path="/analysis" element={<PageTransition><NewAnalysis /></PageTransition>} />
        <Route path="/history" element={<PageTransition><History /></PageTransition>} />
        <Route path="/performance" element={<PageTransition><Performance /></PageTransition>} />
        <Route path="/watchlist" element={<PageTransition><Watchlist /></PageTransition>} />
        <Route path="/smart-picks" element={<PageTransition><SmartPicks /></PageTransition>} />
        <Route path="/portfolio" element={<PageTransition><Portfolio /></PageTransition>} />
        <Route path="/settings" element={<PageTransition><Settings /></PageTransition>} />
      </Routes>
    </AnimatePresence>
  )
}

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
            minWidth: 0,
            overflowX: 'auto',
            marginInlineStart: 'var(--sidebar-width)',
            minHeight: '100vh',
          }}
        >
          <AnimatedRoutes />
        </main>
      </div>
    </ConfigProvider>
  )
}

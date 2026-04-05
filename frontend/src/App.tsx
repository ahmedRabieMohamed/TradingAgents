import { Routes, Route } from 'react-router-dom'
import { CSSProperties } from 'react'
import Sidebar from './components/layout/Sidebar'
import Settings from './pages/Settings'
import NewAnalysis from './pages/NewAnalysis'
import History from './pages/History'
import Performance from './pages/Performance'
import Portfolio from './pages/Portfolio'

const layoutStyle: CSSProperties = {
  display: 'flex',
  minHeight: '100vh',
}

const mainStyle: CSSProperties = {
  flex: 1,
  marginLeft: 'var(--sidebar-width)',
  minHeight: '100vh',
}

export default function App() {
  return (
    <div style={layoutStyle}>
      <Sidebar />
      <main style={mainStyle}>
        <Routes>
          <Route path="/" element={<NewAnalysis />} />
          <Route path="/history" element={<History />} />
          <Route path="/performance" element={<Performance />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}

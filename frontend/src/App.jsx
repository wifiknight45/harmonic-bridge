import { NavLink, Route, Routes } from 'react-router-dom'
import { Disc3, Home, Sparkles, RefreshCw } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Sync from './pages/Sync'
import Recommendations from './pages/Recommendations'

const nav = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/sync', label: 'Sync Library', icon: RefreshCw },
  { to: '/recommendations', label: 'Generate', icon: Sparkles },
]

export default function App() {
  return (
    <div className="min-h-screen bg-ink bg-mesh">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-ink/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-spotify/80 to-apple/80 shadow-neon">
              <Disc3 className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="font-display text-lg font-bold tracking-tight">harmonic-bridge</p>
              <p className="text-xs text-white/50">sync your library · generate playlists that slap</p>
            </div>
          </div>
          <nav className="flex items-center gap-1 rounded-2xl border border-white/10 bg-white/5 p-1">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition ${
                    isActive
                      ? 'bg-white/15 text-white shadow-glass'
                      : 'text-white/60 hover:bg-white/5 hover:text-white'
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/sync" element={<Sync />} />
          <Route path="/recommendations" element={<Recommendations />} />
        </Routes>
      </main>

      <footer className="mx-auto max-w-6xl px-4 pb-10 pt-2 text-center text-xs text-white/40">
        Secrets stay on the backend · this Pages site is the vibe layer ·{' '}
        <a
          className="text-spotify hover:underline"
          href="https://github.com/wifiknight45/harmonic-bridge"
          target="_blank"
          rel="noreferrer"
        >
          GitHub
        </a>
      </footer>
    </div>
  )
}

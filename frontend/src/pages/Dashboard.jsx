import { Link } from 'react-router-dom'
import { RefreshCw, Sparkles, Waves } from 'lucide-react'
import AccountStatus from '../components/AccountStatus'
import TasteProfile from '../components/TasteProfile'

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <section className="glass relative overflow-hidden p-8 md:p-10">
        <div className="pointer-events-none absolute -right-10 -top-10 h-56 w-56 rounded-full bg-spotify/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-16 left-1/3 h-56 w-56 rounded-full bg-apple/20 blur-3xl" />
        <p className="chip mb-4 w-fit border-spotify/30 text-spotify">
          <Waves className="h-3.5 w-3.5" /> GitHub Pages music product
        </p>
        <h1 className="max-w-2xl font-display text-3xl font-bold tracking-tight md:text-4xl">
          Sync your library. Generate playlists that actually slap.
        </h1>
        <p className="mt-3 max-w-xl text-white/60">
          harmonic-bridge bridges Spotify and Apple Music in the browser — match tracks by ISRC,
          fuzzy-fill the gaps, then shape a Camelot-aware harmonic flow. Demo mode is unlocked so
          you can feel the magic before wiring credentials.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/sync" className="btn-primary">
            <RefreshCw className="h-4 w-4" /> Sync my library
          </Link>
          <Link to="/recommendations" className="btn-ghost">
            <Sparkles className="h-4 w-4" /> Generate a playlist
          </Link>
        </div>
      </section>

      <AccountStatus />

      <div className="grid gap-6 lg:grid-cols-2">
        <TasteProfile />
        <section className="glass flex flex-col justify-between gap-4 p-6">
          <div>
            <h2 className="text-xl font-bold">How it flows</h2>
            <ol className="mt-4 space-y-3 text-sm text-white/70">
              <li className="flex gap-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-spotify/20 text-xs font-bold text-spotify">
                  1
                </span>
                Connect Spotify & Apple Music (or stay in demo).
              </li>
              <li className="flex gap-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-glow/20 text-xs font-bold text-glow">
                  2
                </span>
                Sync a playlist — ISRC exact match, then Title+Artist fuzzy.
              </li>
              <li className="flex gap-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-apple/20 text-xs font-bold text-apple">
                  3
                </span>
                Generate a Ramp Up / Peak / Chill Down mix and vibe.
              </li>
            </ol>
          </div>
          <p className="text-xs text-white/40">
            OAuth tokens & Apple .p8 keys never ship to Pages — only your hosted backend holds secrets.
          </p>
        </section>
      </div>
    </div>
  )
}

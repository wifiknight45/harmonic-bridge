import { useQuery } from '@tanstack/react-query'
import { Loader2, Radar } from 'lucide-react'
import { api } from '../lib/api'

const LABELS = [
  { key: 'danceability', label: 'Dance' },
  { key: 'energy', label: 'Energy' },
  { key: 'valence', label: 'Vibe' },
  { key: 'tempo', label: 'Tempo' },
  { key: 'acousticness', label: 'Acoustic' },
]

function RadarChart({ profile }) {
  const cx = 120
  const cy = 120
  const r = 90
  const n = LABELS.length

  const point = (i, value) => {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / n
    const rr = r * Math.min(Math.max(value, 0), 1)
    return [cx + rr * Math.cos(angle), cy + rr * Math.sin(angle)]
  }

  const polygon = LABELS.map((l, i) => point(i, profile[l.key] ?? 0).join(',')).join(' ')
  const grid = [0.25, 0.5, 0.75, 1].map((scale) =>
    LABELS.map((_, i) => point(i, scale).join(',')).join(' '),
  )

  return (
    <svg viewBox="0 0 240 240" className="mx-auto h-56 w-56">
      {grid.map((g, idx) => (
        <polygon
          key={idx}
          points={g}
          fill="none"
          stroke="rgba(255,255,255,0.12)"
          strokeWidth="1"
        />
      ))}
      {LABELS.map((l, i) => {
        const [x, y] = point(i, 1)
        return (
          <g key={l.key}>
            <line x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,0.12)" />
            <text
              x={x * 1.08 - cx * 0.08}
              y={y * 1.08 - cy * 0.08 + 4}
              textAnchor="middle"
              className="fill-white/60 text-[10px]"
            >
              {l.label}
            </text>
          </g>
        )
      })}
      <polygon
        points={polygon}
        fill="rgba(29,185,84,0.35)"
        stroke="#1DB954"
        strokeWidth="2"
      />
    </svg>
  )
}

export default function TasteProfile() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['taste'],
    queryFn: () => api.taste('spotify', 'demo-chill-vibes'),
  })

  return (
    <section className="glass space-y-4 p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold">Taste profile</h2>
          <p className="text-sm text-white/55">Your library&apos;s sonic fingerprint.</p>
        </div>
        <Radar className="h-5 w-5 text-apple" />
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-white/50">
          <Loader2 className="h-4 w-4 animate-spin" /> Reading the room…
        </div>
      )}
      {isError && (
        <p className="text-sm text-white/50">Connect the API to load your taste radar.</p>
      )}
      {data && (
        <>
          <RadarChart profile={data.taste_profile} />
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
            {LABELS.map((l) => (
              <div key={l.key} className="rounded-xl bg-black/25 px-3 py-2 text-center">
                <p className="text-[10px] uppercase tracking-wide text-white/40">{l.label}</p>
                <p className="text-sm font-semibold text-spotify">
                  {Math.round((data.taste_profile[l.key] || 0) * 100)}
                </p>
              </div>
            ))}
          </div>
          <p className="text-xs text-white/40">
            Based on {data.track_count} tracks
            {data.demo_mode ? ' · demo library' : ''}.
          </p>
        </>
      )}
    </section>
  )
}

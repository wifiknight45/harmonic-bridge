import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Activity, Loader2, Play } from 'lucide-react'
import { api } from '../lib/api'

export default function HarmonicFlow() {
  const { data: flowsData } = useQuery({
    queryKey: ['flows'],
    queryFn: api.listFlows,
  })
  const [curve, setCurve] = useState('peak_energy')

  const mixMut = useMutation({
    mutationFn: () =>
      api.recommendMix({
        seed_platform: 'spotify',
        playlist_id: 'demo-chill-vibes',
        catalog_platform: 'apple',
        curve,
        top_k: 10,
      }),
  })

  const flows = flowsData?.flows || [
    { id: 'ramp_up', name: 'Ramp Up', description: 'Ease in, finish hot.' },
    { id: 'peak_energy', name: 'Peak Energy', description: 'Hit the drop.' },
    { id: 'chill_down', name: 'Chill Down', description: 'Soft landing.' },
  ]

  const tracks = mixMut.data?.tracks || []
  const maxEnergy = Math.max(...tracks.map((t) => t.energy || 0), 0.01)

  return (
    <section className="glass space-y-5 p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold">Harmonic Flow</h2>
          <p className="text-sm text-white/55">
            Camelot-aware sequencing so your playlist transitions feel DJ-smooth.
          </p>
        </div>
        <Activity className="h-5 w-5 text-spotify" />
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {flows.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setCurve(f.id)}
            className={`rounded-2xl border p-4 text-left transition ${
              curve === f.id
                ? 'border-spotify/60 bg-spotify/10 shadow-neon'
                : 'border-white/10 bg-white/5 hover:bg-white/10'
            }`}
          >
            <div className="mt-1 font-semibold">{f.name}</div>
            <p className="mt-1 text-xs text-white/50">{f.description}</p>
          </button>
        ))}
      </div>

      <button
        type="button"
        className="btn-primary"
        disabled={mixMut.isPending}
        onClick={() => mixMut.mutate()}
      >
        {mixMut.isPending ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Play className="h-4 w-4" />
        )}
        Generate playlist
      </button>

      {mixMut.data && (
        <div className="space-y-4">
          <p className="text-sm text-spotify">{mixMut.data.message}</p>
          <div className="flex h-24 items-end gap-1.5 rounded-xl border border-white/10 bg-black/25 p-3">
            {tracks.map((t) => (
              <div
                key={t.id}
                title={`${t.title} · energy ${(t.energy * 100).toFixed(0)}%`}
                className="flex-1 rounded-t-md bg-gradient-to-t from-glow to-spotify transition-all"
                style={{ height: `${Math.max(12, (t.energy / maxEnergy) * 100)}%` }}
              />
            ))}
          </div>
          <ol className="space-y-2">
            {tracks.map((t, i) => (
              <li
                key={t.id}
                className="flex items-center justify-between gap-3 rounded-xl border border-white/5 bg-white/[0.03] px-3 py-2 text-sm"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 text-center text-xs text-white/40">{i + 1}</span>
                  <div>
                    <p className="font-medium">{t.title}</p>
                    <p className="text-xs text-white/45">{t.artist}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-white/50">
                  {t.camelot && <span className="chip">{t.camelot}</span>}
                  <span>{Math.round(t.tempo)} BPM</span>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}

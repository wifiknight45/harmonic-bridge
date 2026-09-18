import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Link2, Music2, Loader2, Info } from 'lucide-react'
import { api, isDemoOffline } from '../lib/api'

function PlatformCard({ name, colorClass, status, onConnect, connecting, demo, offline }) {
  const connected = status?.connected
  return (
    <div className="glass flex flex-1 flex-col gap-4 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${colorClass}`}>
            <Music2 className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold">{name}</h3>
            <p className="text-xs text-white/50">
              {connected ? (demo || status?.demo ? 'Demo library unlocked' : 'Connected') : 'Not connected'}
            </p>
          </div>
        </div>
        {connected ? (
          <span className="chip text-spotify">
            <CheckCircle2 className="h-3.5 w-3.5" /> Ready
          </span>
        ) : (
          <span className="chip">Offline</span>
        )}
      </div>
      <p className="text-sm text-white/65">{status?.message || 'Connect to sync your library.'}</p>
      <button
        type="button"
        className={name.includes('Spotify') ? 'btn-primary' : 'btn-apple'}
        onClick={onConnect}
        disabled={connecting}
      >
        {connecting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Link2 className="h-4 w-4" />}
        {connected
          ? offline || demo
            ? 'Demo unlocked'
            : 'Reconnect'
          : offline || demo
            ? `Unlock demo ${name}`
            : `Connect ${name}`}
      </button>
    </div>
  )
}

export default function AccountStatus() {
  const qc = useQueryClient()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['authStatus'],
    queryFn: api.authStatus,
  })

  const spotifyMut = useMutation({
    mutationFn: async () => {
      const start = await api.spotifyAuth()
      if (start.demo || !start.authorize_url) {
        return api.connectSpotifyDemo()
      }
      window.location.href = start.authorize_url
      return start
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['authStatus'] }),
  })

  const appleMut = useMutation({
    mutationFn: api.connectAppleDemo,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['authStatus'] }),
  })

  if (isLoading) {
    return (
      <div className="glass flex items-center gap-3 p-6 text-white/60">
        <Loader2 className="h-5 w-5 animate-spin" /> Checking your accounts…
      </div>
    )
  }

  if (isError && !isDemoOffline()) {
    return (
      <div className="glass space-y-3 border-white/15 p-6">
        <p className="font-semibold text-white/80">Could not load account status</p>
        <p className="text-sm text-white/55">
          Retrying will use local demo data. Optional:{' '}
          <code className="text-spotify">VITE_API_URL</code> for live sync.
        </p>
      </div>
    )
  }

  const offline = isDemoOffline() || data?.offline_demo

  return (
    <section className="space-y-4">
      {offline && (
        <div className="flex flex-wrap items-start gap-3 rounded-2xl border border-glow/25 bg-glow/5 px-4 py-3 text-sm text-white/70">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-glow" />
          <div className="min-w-0 flex-1 space-y-1">
            <p className="font-medium text-glow">Demo mode (no API)</p>
            <p className="text-xs text-white/50">
              Unlock demo unlocks a local mock library (not live Spotify/Apple OAuth). Sync and
              generate use browser mock data. Live OAuth needs a free-hosted backend and{' '}
              <code className="text-spotify">VITE_API_URL</code> later — the UI stays usable now.
            </p>
          </div>
          <span className="chip border-glow/40 text-glow">Offline demo</span>
        </div>
      )}
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold">Your accounts</h2>
          <p className="text-sm text-white/55">
            Unlock demo libraries — then sync and generate with mock data.
          </p>
        </div>
        {data?.demo_mode && !offline && (
          <span className="chip border-glow/40 text-glow">Demo mode · no keys required</span>
        )}
      </div>
      <div className="flex flex-col gap-4 md:flex-row">
        <PlatformCard
          name="Spotify"
          colorClass="bg-spotify"
          status={data?.spotify}
          demo={data?.demo_mode}
          offline={offline}
          connecting={spotifyMut.isPending}
          onConnect={() => spotifyMut.mutate()}
        />
        <PlatformCard
          name="Apple Music"
          colorClass="bg-apple"
          status={data?.apple}
          demo={data?.demo_mode}
          offline={offline}
          connecting={appleMut.isPending}
          onConnect={() => appleMut.mutate()}
        />
      </div>
    </section>
  )
}

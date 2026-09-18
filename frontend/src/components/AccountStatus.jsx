import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Link2, Music2, Loader2 } from 'lucide-react'
import { api } from '../lib/api'

function PlatformCard({ name, colorClass, status, onConnect, connecting, demo }) {
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
        {connected ? 'Reconnect' : `Connect ${name}`}
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

  if (isError) {
    return (
      <div className="glass space-y-3 border-apple/30 p-6">
        <p className="font-semibold text-apple">Backend not reachable</p>
        <p className="text-sm text-white/60">
          Set <code className="text-spotify">VITE_API_URL</code> to your hosted API, or run the backend locally.
          Demo UI still works once the API is up — no secrets needed on Pages.
        </p>
      </div>
    )
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold">Your accounts</h2>
          <p className="text-sm text-white/55">Connect once — then sync & generate anytime.</p>
        </div>
        {data?.demo_mode && (
          <span className="chip border-glow/40 text-glow">Demo mode · no keys required</span>
        )}
      </div>
      <div className="flex flex-col gap-4 md:flex-row">
        <PlatformCard
          name="Spotify"
          colorClass="bg-spotify"
          status={data?.spotify}
          demo={data?.demo_mode}
          connecting={spotifyMut.isPending}
          onConnect={() => spotifyMut.mutate()}
        />
        <PlatformCard
          name="Apple Music"
          colorClass="bg-apple"
          status={data?.apple}
          demo={data?.demo_mode}
          connecting={appleMut.isPending}
          onConnect={() => appleMut.mutate()}
        />
      </div>
    </section>
  )
}

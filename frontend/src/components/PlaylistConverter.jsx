import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { ArrowRightLeft, Loader2, Sparkles } from 'lucide-react'
import { api } from '../lib/api'

export default function PlaylistConverter() {
  const { data: playlistsData } = useQuery({
    queryKey: ['playlists'],
    queryFn: () => api.listPlaylists('all'),
  })

  const playlists = playlistsData?.playlists || []
  const [source, setSource] = useState('spotify')
  const [target, setTarget] = useState('apple')
  const [playlistId, setPlaylistId] = useState('demo-chill-vibes')

  const filtered = useMemo(
    () => playlists.filter((p) => p.platform === source),
    [playlists, source],
  )

  const syncMut = useMutation({
    mutationFn: () =>
      api.syncPlaylist({
        source_platform: source,
        target_platform: target,
        playlist_id: playlistId,
        playlist_name: `harmonic · ${playlistId}`,
        create_on_target: true,
      }),
  })

  const summary = syncMut.data?.summary
  const matchRate = summary ? Math.round((summary.match_rate || 0) * 100) : 0

  return (
    <section className="glass space-y-5 p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold">Sync your library</h2>
          <p className="text-sm text-white/55">
            Bridge playlists across Spotify ↔ Apple Music with ISRC + fuzzy matching.
          </p>
        </div>
        <ArrowRightLeft className="h-5 w-5 text-glow" />
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <label className="space-y-1 text-xs text-white/50">
          From
          <select
            className="w-full rounded-xl border border-white/10 bg-panel px-3 py-2.5 text-sm text-white"
            value={source}
            onChange={(e) => {
              setSource(e.target.value)
              setTarget(e.target.value === 'spotify' ? 'apple' : 'spotify')
            }}
          >
            <option value="spotify">Spotify</option>
            <option value="apple">Apple Music</option>
          </select>
        </label>
        <label className="space-y-1 text-xs text-white/50">
          To
          <select
            className="w-full rounded-xl border border-white/10 bg-panel px-3 py-2.5 text-sm text-white"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
          >
            <option value="apple">Apple Music</option>
            <option value="spotify">Spotify</option>
          </select>
        </label>
        <label className="space-y-1 text-xs text-white/50">
          Playlist
          <select
            className="w-full rounded-xl border border-white/10 bg-panel px-3 py-2.5 text-sm text-white"
            value={playlistId}
            onChange={(e) => setPlaylistId(e.target.value)}
          >
            {(filtered.length ? filtered : [{ id: 'demo-chill-vibes', name: 'Chill Vibes' }]).map(
              (p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ),
            )}
          </select>
        </label>
      </div>

      <button
        type="button"
        className="btn-primary w-full sm:w-auto"
        disabled={syncMut.isPending || source === target}
        onClick={() => syncMut.mutate()}
      >
        {syncMut.isPending ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Sparkles className="h-4 w-4" />
        )}
        Sync playlist
      </button>

      {syncMut.data && (
        <div className="space-y-4 rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="text-sm font-medium text-spotify">{syncMut.data.message}</p>
          <div>
            <div className="mb-1 flex justify-between text-xs text-white/50">
              <span>Match progress</span>
              <span>
                {summary?.matched}/{summary?.total} · {matchRate}%
              </span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-spotify to-glow transition-all duration-700"
                style={{ width: `${matchRate}%` }}
              />
            </div>
            <div className="mt-2 flex flex-wrap gap-2 text-xs">
              <span className="chip">ISRC {summary?.isrc_matches ?? 0}</span>
              <span className="chip">Fuzzy {summary?.fuzzy_matches ?? 0}</span>
              <span className="chip">Missed {summary?.unmatched ?? 0}</span>
            </div>
          </div>
          {syncMut.data.target_playlist && (
            <p className="text-sm text-white/70">
              Created on {target}:{' '}
              <span className="font-semibold text-white">
                {syncMut.data.target_playlist.name}
              </span>
            </p>
          )}
          <ul className="max-h-48 space-y-1 overflow-y-auto text-xs text-white/60">
            {syncMut.data.matches?.slice(0, 12).map((m, i) => (
              <li key={`${m.source_title}-${i}`} className="flex justify-between gap-2">
                <span>
                  {m.source_title}{' '}
                  <span className="text-white/35">· {m.source_artist}</span>
                </span>
                <span className={m.matched ? 'text-spotify' : 'text-apple'}>
                  {m.matched ? m.method : 'miss'}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}

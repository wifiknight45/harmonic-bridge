import { useState } from 'react'
import {
  Brain,
  CloudMoon,
  Disc3,
  Filter,
  Loader2,
  Shuffle,
  Sparkles,
  Users,
} from 'lucide-react'
import { api } from '../lib/api'

const TABS = [
  { id: 'taste-twin', label: 'Taste twin', icon: Users },
  { id: 'mood-mix', label: 'Mood to mix', icon: CloudMoon },
  { id: 'gap-fill', label: 'Gap filler', icon: Shuffle },
  { id: 'dj-coach', label: 'DJ coach', icon: Disc3 },
  { id: 'lyric-safe', label: 'Lyric-safe', icon: Filter },
  { id: 'weekly-drop', label: 'Weekly drop', icon: Sparkles },
]

function ResultPanel({ title, children }) {
  return (
    <div className="glass mt-4 space-y-3 p-4">
      <h3 className="text-sm font-semibold text-white/80">{title}</h3>
      {children}
    </div>
  )
}

function TrackList({ tracks }) {
  if (!tracks?.length) return null
  return (
    <ul className="divide-y divide-white/5 rounded-xl border border-white/10">
      {tracks.slice(0, 12).map((t, i) => (
        <li
          key={t.id || `${t.title}-${i}`}
          className="flex items-center justify-between gap-3 px-3 py-2 text-sm"
        >
          <div>
            <p className="font-medium">{t.title}</p>
            <p className="text-xs text-white/50">{t.artist}</p>
          </div>
          <div className="flex flex-wrap justify-end gap-2 text-xs text-white/45">
            {t.camelot && <span className="chip">{t.camelot}</span>}
            {typeof t.energy === 'number' && <span>E {t.energy.toFixed(2)}</span>}
            {typeof t.similarity === 'number' && <span>sim {t.similarity.toFixed(2)}</span>}
            {typeof t.confidence === 'number' && (
              <span>{(t.confidence * 100).toFixed(0)}%</span>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}

export default function AIStudio() {
  const [tab, setTab] = useState('taste-twin')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const [mood, setMood] = useState('chill sunday drive')
  const [gapTitle, setGapTitle] = useState('Stay')
  const [gapArtist, setGapArtist] = useState('The Kid LAROI')
  const [lyricPolicy, setLyricPolicy] = useState('family')

  async function run(action) {
    setLoading(true)
    setError(null)
    try {
      setResult(await action())
    } catch (e) {
      setError(e.message || 'Request failed')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <div className="mb-2 flex items-center gap-2">
          <Brain className="h-6 w-6 text-spotify" />
          <h1 className="text-2xl font-bold md:text-3xl">AI Studio</h1>
        </div>
        <p className="mt-1 text-white/55">
          Six free local features: taste twin, mood mix, gap filler, DJ coach, lyric-safe, and
          weekly drop.
        </p>
        <p className="mt-2 text-xs text-spotify">Runs fully free — no AI API keys needed.</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => {
              setTab(id)
              setResult(null)
              setError(null)
            }}
            className={`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition ${
              tab === id
                ? 'bg-white/15 text-white shadow-glass'
                : 'border border-white/10 bg-white/5 text-white/60 hover:bg-white/10 hover:text-white'
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      <div className="glass space-y-4 p-6">
        {tab === 'taste-twin' && (
          <>
            <h2 className="font-semibold">Taste twin</h2>
            <p className="text-sm text-white/55">
              Compact library embedding and cross-platform playlist seeds for people like you.
            </p>
            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() => run(() => api.tasteTwin({ top_k: 3 }))}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Users className="h-4 w-4" />}
              Find my twins
            </button>
            {result?.seeds && (
              <ResultPanel title={result.message}>
                <ul className="space-y-2">
                  {result.seeds.map((s) => (
                    <li key={s.id} className="rounded-xl border border-white/10 bg-white/5 p-3">
                      <div className="flex justify-between gap-2">
                        <p className="font-medium">{s.label}</p>
                        <span className="chip">{s.platform}</span>
                      </div>
                      <p className="text-sm text-white/70">{s.playlist_name}</p>
                      <p className="mt-1 text-xs text-white/45">{s.blurb}</p>
                      <p className="mt-1 text-xs text-spotify">similarity {s.similarity}</p>
                    </li>
                  ))}
                </ul>
              </ResultPanel>
            )}
          </>
        )}

        {tab === 'mood-mix' && (
          <>
            <h2 className="font-semibold">Mood to mix</h2>
            <p className="text-sm text-white/55">
              Natural-language mood to energy/valence/tempo curve, then Camelot-aware playlist.
            </p>
            <input
              className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm"
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              placeholder="e.g. hype workout party"
            />
            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() => run(() => api.moodMix({ mood, top_k: 10 }))}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <CloudMoon className="h-4 w-4" />
              )}
              Build mix
            </button>
            {result?.tracks && (
              <ResultPanel title={`${result.message} (${result.curve})`}>
                <p className="text-xs text-white/45">
                  targets E {result.targets?.energy} / V {result.targets?.valence} /{' '}
                  {result.targets?.tempo} BPM
                </p>
                <TrackList tracks={result.tracks} />
              </ResultPanel>
            )}
          </>
        )}

        {tab === 'gap-fill' && (
          <>
            <h2 className="font-semibold">Gap filler</h2>
            <p className="text-sm text-white/55">
              On ISRC/fuzzy miss, suggest alternate recordings with confidence (local heuristic).
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                className="rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm"
                value={gapTitle}
                onChange={(e) => setGapTitle(e.target.value)}
                placeholder="Title"
              />
              <input
                className="rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm"
                value={gapArtist}
                onChange={(e) => setGapArtist(e.target.value)}
                placeholder="Artist"
              />
            </div>
            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() =>
                run(() => api.gapFill({ title: gapTitle, artist: gapArtist, top_k: 3 }))
              }
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Shuffle className="h-4 w-4" />
              )}
              Suggest alternates
            </button>
            {result?.alternates && (
              <ResultPanel title={result.message}>
                <TrackList tracks={result.alternates} />
              </ResultPanel>
            )}
          </>
        )}

        {tab === 'dj-coach' && (
          <>
            <h2 className="font-semibold">DJ coach</h2>
            <p className="text-sm text-white/55">
              Critique key clashes, energy cliffs, vocal stacking — plus reorder proposals.
            </p>
            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() =>
                run(() => api.djCoach({ propose_reorder: true, curve: 'peak_energy' }))
              }
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Disc3 className="h-4 w-4" />}
              Critique demo mix
            </button>
            {result && (
              <ResultPanel title={result.message}>
                <p className="text-lg font-bold text-spotify">Score {result.score}/100</p>
                <ul className="space-y-2 text-sm">
                  {(result.issues || []).map((issue, i) => (
                    <li key={i} className="rounded-lg border border-white/10 bg-white/5 p-2">
                      <span className="chip">{issue.type}</span>{' '}
                      <span className="text-white/70">{issue.detail}</span>
                    </li>
                  ))}
                </ul>
                {result.reorder_proposal?.order && (
                  <div className="mt-3">
                    <p className="mb-2 text-xs text-white/50">Proposed reorder</p>
                    <TrackList tracks={result.reorder_proposal.order} />
                  </div>
                )}
              </ResultPanel>
            )}
          </>
        )}

        {tab === 'lyric-safe' && (
          <>
            <h2 className="font-semibold">Lyric-safe filter</h2>
            <p className="text-sm text-white/55">
              Optional family/focus policy before sync (metadata heuristic classifier).
            </p>
            <select
              className="rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm"
              value={lyricPolicy}
              onChange={(e) => setLyricPolicy(e.target.value)}
            >
              <option value="family">Family</option>
              <option value="focus">Focus</option>
              <option value="off">Off (tag only)</option>
            </select>
            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() => run(() => api.lyricSafe({ policy: lyricPolicy }))}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Filter className="h-4 w-4" />
              )}
              Apply policy
            </button>
            {result?.summary && (
              <ResultPanel title={result.message}>
                <p className="text-sm text-white/70">
                  kept {result.summary.allowed}/{result.summary.total} · blocked{' '}
                  {result.summary.blocked}
                </p>
                {result.blocked?.length > 0 && (
                  <div>
                    <p className="mb-1 text-xs text-white/45">Blocked</p>
                    <TrackList tracks={result.blocked} />
                  </div>
                )}
              </ResultPanel>
            )}
          </>
        )}

        {tab === 'weekly-drop' && (
          <>
            <h2 className="font-semibold">Weekly drop</h2>
            <p className="text-sm text-white/55">
              Digest of mismatches fixed, one fresh playlist, short why-blurb. Hook via cron /
              GitHub Actions on GET/POST /api/v1/ai/weekly-drop.
            </p>
            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() => run(() => api.weeklyDrop({}))}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              Generate weekly drop
            </button>
            {result?.fresh_playlist && (
              <ResultPanel title={result.why_blurb || result.message}>
                <p className="text-xs text-white/45">{result.cron_hint}</p>
                <p className="text-sm font-medium">{result.fresh_playlist.name}</p>
                <p className="text-xs text-white/50">
                  {result.mismatches_fixed?.length || 0} mismatches fixed
                </p>
                <TrackList tracks={result.fresh_playlist.tracks} />
              </ResultPanel>
            )}
          </>
        )}

        {error && <p className="text-sm text-apple">{error}</p>}
      </div>
    </div>
  )
}

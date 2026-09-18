/**
 * In-browser demo store for GitHub Pages when no API is configured or reachable.
 * Shapes mirror backend demo_data + endpoint responses.
 */

import demoData from './demoData.js'

const STORAGE_KEY = 'hb-demo-auth'

const {
  playlists: DEMO_PLAYLISTS,
  syncSpotifyToApple: SYNC_SPOTIFY_TO_APPLE,
  syncAppleToSpotify: SYNC_APPLE_TO_SPOTIFY,
  tasteProfile: TASTE_PROFILE,
  energyCurve: ENERGY_CURVE,
  camelotDistribution: CAMELOT_DISTRIBUTION,
  topArtists: TOP_ARTISTS,
  mixTracks: MIX_TRACKS,
  flows: FLOWS,
  curveLabels: CURVE_LABELS,
} = demoData

function loadAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    /* ignore */
  }
  return { spotify: false, apple: false }
}

function saveAuth(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    /* ignore */
  }
}

let authState = loadAuth()

function delay(ms = 280) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function authStatus() {
  return {
    spotify: {
      configured: false,
      demo: true,
      connected: Boolean(authState.spotify),
      label: 'Spotify',
      authorize_url: null,
      message: authState.spotify
        ? 'Demo Spotify library unlocked — ready to sync.'
        : 'Connect to unlock the demo Spotify library (no keys needed).',
    },
    apple: {
      configured: false,
      demo: true,
      connected: Boolean(authState.apple),
      label: 'Apple Music',
      message: authState.apple
        ? 'Apple Music demo unlocked — generate something dope.'
        : 'Connect to unlock the demo Apple Music catalog.',
    },
    demo_mode: true,
    offline_demo: true,
  }
}

function connectSpotify() {
  authState = { ...authState, spotify: true }
  saveAuth(authState)
  return {
    connected: true,
    demo: true,
    display_name: 'Demo Listener',
    session_token: 'demo-spotify-offline',
    message: "You're in — demo Spotify library ready to sync.",
  }
}

function connectApple() {
  authState = { ...authState, apple: true }
  saveAuth(authState)
  return {
    connected: true,
    demo: true,
    display_name: 'Demo Apple Fan',
    session_token: 'demo-apple-offline',
    message: "Apple Music demo unlocked — let's generate something dope.",
  }
}

function spotifyAuthStart() {
  return {
    demo: true,
    authorize_url: null,
    message: 'Offline demo — use Connect to unlock the local Spotify library.',
  }
}

function listPlaylists(platform = 'all') {
  const playlists =
    platform === 'all'
      ? DEMO_PLAYLISTS
      : DEMO_PLAYLISTS.filter((p) => p.platform === platform)
  return { playlists, demo_mode: true, offline_demo: true }
}

function syncPlaylist(body = {}) {
  const source = body.source_platform || 'spotify'
  const target = body.target_platform || 'apple'
  const playlistId = body.playlist_id || 'demo-chill-vibes'
  const playlistName = body.playlist_name || `harmonic · ${playlistId}`

  if (source === target) {
    return {
      job_id: 'demo-offline',
      source_platform: source,
      target_platform: target,
      playlist_id: playlistId,
      summary: {
        total: 0,
        matched: 0,
        unmatched: 0,
        match_rate: 0,
        isrc_matches: 0,
        fuzzy_matches: 0,
      },
      matches: [],
      message: 'Pick two different platforms to sync your library across.',
    }
  }

  const pack = source === 'spotify' ? SYNC_SPOTIFY_TO_APPLE : SYNC_APPLE_TO_SPOTIFY
  const matchedIds = pack.matches.filter((m) => m.matched).map((m) => m.target_id)
  const rate = pack.summary.match_rate
  const vibe =
    rate >= 0.8
      ? 'Library synced — that was smooth.'
      : rate >= 0.5
        ? 'Most tracks landed. A few need a manual nudge.'
        : 'Partial sync — try another playlist or tighten titles.'

  return {
    job_id: `demo-${Date.now().toString(36)}`,
    source_platform: source,
    target_platform: target,
    playlist_id: playlistId,
    target_playlist:
      body.create_on_target !== false
        ? {
            demo: true,
            id: `demo-sync-${Date.now().toString(36)}`,
            name: playlistName,
            track_ids: matchedIds,
            message: `Demo ${target} playlist with ${matchedIds.length} matched tracks.`,
          }
        : null,
    summary: pack.summary,
    matches: pack.matches,
    message: vibe,
  }
}

function recommendMix(body = {}) {
  const curve = body.curve || 'peak_energy'
  const tracks = MIX_TRACKS[curve] || MIX_TRACKS.peak_energy
  const topK = Math.min(Math.max(body.top_k || 10, 1), tracks.length)
  return {
    curve,
    seed_profile: TASTE_PROFILE,
    tracks: tracks.slice(0, topK),
    message: `Playlist generated · ${CURVE_LABELS[curve] || curve}. Hit play and feel the flow.`,
  }
}

function listFlows() {
  return { flows: FLOWS }
}

function taste() {
  return {
    taste_profile: TASTE_PROFILE,
    track_count: ENERGY_CURVE.length,
    energy_curve: ENERGY_CURVE,
    camelot_distribution: CAMELOT_DISTRIBUTION,
    top_artists: TOP_ARTISTS,
    demo_mode: true,
    offline_demo: true,
  }
}

function overview() {
  return {
    app: 'harmonic-bridge',
    demo_mode: true,
    offline_demo: true,
    spotify_configured: false,
    apple_configured: false,
    tagline: 'Sync your library. Generate playlists that actually slap.',
  }
}

/**
 * Route a request path to a local demo response (no network).
 */

function demoTasteTwin() {
  return {
    taste_embedding: {
      dims: ['danceability', 'energy', 'valence', 'tempo', 'acousticness'],
      profile: { danceability: 0.62, energy: 0.71, valence: 0.58, tempo: 0.6, acousticness: 0.18 },
      embedding: [0.45, 0.52, 0.42, 0.44, 0.13],
      track_count: 8,
      norm: 1.0,
    },
    seeds: [
      {
        id: 'twin-night-drive',
        label: 'Night Drive Twin',
        platform: 'apple',
        playlist_name: 'Midnight Highway',
        blurb: 'High energy, mid-tempo neon — people like you queue this for late rides.',
        similarity: 0.91,
      },
      {
        id: 'twin-sunday-soft',
        label: 'Sunday Soft Twin',
        platform: 'spotify',
        playlist_name: 'Soft Focus Sundays',
        blurb: 'Lower energy, warmer valence — your chill twin lives here.',
        similarity: 0.84,
      },
    ],
    message: 'People like you start here — cross-platform playlist seeds from your taste twin.',
    demo_mode: true,
  }
}

function demoMoodMix(body = {}) {
  const mood = body.mood || 'chill'
  return {
    mood,
    targets: { energy: 0.35, valence: 0.55, tempo: 90 },
    curve: 'chill_down',
    curve_points: [
      { index: 0, energy: 0.95, valence: 0.55, tempo: 90 },
      { index: 1, energy: 0.6, valence: 0.55, tempo: 90 },
      { index: 2, energy: 0.25, valence: 0.55, tempo: 90 },
    ],
    matched_keywords: ['chill'],
    tracks: (MIX_TRACKS.chill_down || MIX_TRACKS.peak_energy || []).slice(0, body.top_k || 8),
    blurb: 'Soft landing — cool the room, keep the groove.',
    message: 'Mood mix ready — soft landing.',
    demo_mode: true,
  }
}

function demoGapFill(body = {}) {
  return {
    query: { title: body.title || 'Stay', artist: body.artist || 'The Kid LAROI', isrc: body.isrc || null },
    alternates: [
      {
        id: 'am-4',
        title: 'Stay',
        artist: 'The Kid LAROI',
        album: 'F*CK LOVE 3: OVER YOU',
        isrc: null,
        platform: 'apple',
        confidence: 0.86,
        reason: 'title~0.95; artist~0.80',
      },
    ],
    provider: 'HeuristicAlternateProvider',
    message: 'Found 1 alternate recording(s) for gap fill.',
    demo_mode: true,
  }
}

function demoDjCoach() {
  const tracks = (MIX_TRACKS.peak_energy || []).slice(0, 6)
  return {
    score: 78,
    issue_count: 2,
    issues: [
      {
        type: 'energy_cliff',
        severity: 'warn',
        from_index: 0,
        to_index: 1,
        from_track: tracks[0]?.title || 'A',
        to_track: tracks[1]?.title || 'B',
        energy_delta: 0.32,
        detail: 'Energy drop between adjacent tracks.',
      },
      {
        type: 'key_clash',
        severity: 'warn',
        from_index: 2,
        to_index: 3,
        from_track: tracks[2]?.title || 'C',
        to_track: tracks[3]?.title || 'D',
        from_camelot: '8B',
        to_camelot: '3A',
        detail: 'Camelot jump outside compatible neighbors.',
      },
    ],
    reorder_proposal: {
      curve: 'peak_energy',
      order: tracks,
      note: 'Reordered for Camelot-compatible transitions.',
    },
    message: 'DJ coach score 78/100 — 1 key clash(es), 1 energy cliff(s).',
    demo_mode: true,
  }
}

function demoLyricSafe(body = {}) {
  const policy = body.policy || 'family'
  const rows = [
    { id: '1', title: 'Stay', artist: 'Artist', album: 'F*CK LOVE 3', explicit: true, family_ok: false },
    { id: '2', title: 'Heat Waves', artist: 'Glass Animals', album: 'Dreamland', explicit: false, family_ok: true },
  ]
  const blocked = policy === 'off' ? [] : rows.filter((r) => !r.family_ok)
  const allowed = policy === 'off' ? rows : rows.filter((r) => r.family_ok)
  return {
    policy,
    allowed,
    blocked,
    summary: { total: rows.length, allowed: allowed.length, blocked: blocked.length },
    message: `Lyric-safe (${policy}): kept ${allowed.length}/${rows.length} tracks.`,
    demo_mode: true,
    classifier: 'metadata_heuristic',
  }
}

function demoWeeklyDrop() {
  const tracks = (MIX_TRACKS.peak_energy || []).slice(0, 8)
  return {
    week_label: 'Week of demo',
    generated_at: new Date().toISOString(),
    mismatches_fixed: [
      {
        source_title: 'Stay',
        source_artist: 'The Kid LAROI & Justin Bieber',
        target_title: 'Stay',
        target_artist: 'The Kid LAROI',
        method: 'fuzzy',
        score: 0.86,
        note: 'Artist credit trimmed on Apple; fuzzy bridge closed the gap.',
      },
    ],
    fresh_playlist: {
      name: 'Weekly Drop · demo',
      mood: 'feel good sunday drive',
      curve: 'peak_energy',
      tracks,
      blurb: 'Bright peak energy — smile-friendly Camelot flow.',
    },
    why_blurb: 'Your taste twin leaned balanced; we closed 1 sync gap and dropped a fresh playlist.',
    taste_twin_seed: null,
    cron_hint: 'Hook GET/POST /api/v1/ai/weekly-drop from cron or GitHub Actions weekly.',
    message: 'Weekly drop ready.',
    demo_mode: true,
  }
}


export async function handleDemoRequest(path, options = {}) {
  await delay()
  const method = (options.method || 'GET').toUpperCase()
  let body = {}
  if (options.body) {
    try {
      body = typeof options.body === 'string' ? JSON.parse(options.body) : options.body
    } catch {
      body = {}
    }
  }

  const url = new URL(path, 'https://demo.local')
  const pathname = url.pathname
  const platform = url.searchParams.get('platform') || 'all'

  if (pathname === '/api/v1/analytics/overview') return overview()
  if (pathname === '/api/v1/auth/status') return authStatus()
  if (pathname === '/api/v1/auth/spotify' && method === 'GET') return spotifyAuthStart()
  if (pathname === '/api/v1/auth/spotify/demo-connect' && method === 'POST') {
    return connectSpotify()
  }
  if (pathname === '/api/v1/auth/apple/demo-connect' && method === 'POST') {
    return connectApple()
  }
  if (pathname === '/api/v1/playlists') return listPlaylists(platform)
  if (pathname === '/api/v1/playlists/sync' && method === 'POST') return syncPlaylist(body)
  if (pathname === '/api/v1/recommend/mix' && method === 'POST') return recommendMix(body)
  if (pathname === '/api/v1/recommend/flows') return listFlows()
  if (pathname === '/api/v1/analytics/taste') return taste()


  if (pathname === '/api/v1/ai/taste-twin' && method === 'POST') return demoTasteTwin()
  if (pathname === '/api/v1/ai/mood-mix' && method === 'POST') return demoMoodMix(body)
  if (pathname === '/api/v1/ai/gap-fill' && method === 'POST') return demoGapFill(body)
  if (pathname === '/api/v1/ai/dj-coach' && method === 'POST') return demoDjCoach()
  if (pathname === '/api/v1/ai/lyric-safe' && method === 'POST') return demoLyricSafe(body)
  if (pathname === '/api/v1/ai/weekly-drop' && (method === 'POST' || method === 'GET')) {
    return demoWeeklyDrop()
  }
  if (pathname === '/api/v1/ai/features') {
    return {
      features: [
        { id: 'taste-twin', name: 'Taste twin', path: '/api/v1/ai/taste-twin' },
        { id: 'mood-mix', name: 'Mood to mix', path: '/api/v1/ai/mood-mix' },
        { id: 'gap-fill', name: 'Gap filler', path: '/api/v1/ai/gap-fill' },
        { id: 'dj-coach', name: 'DJ coach', path: '/api/v1/ai/dj-coach' },
        { id: 'lyric-safe', name: 'Lyric-safe filter', path: '/api/v1/ai/lyric-safe' },
        { id: 'weekly-drop', name: 'Weekly drop', path: '/api/v1/ai/weekly-drop' },
      ],
      demo_mode: true,
      runs_fully_free: true,
      note: 'Runs fully free - no AI API keys needed.',
    }
  }

  throw new Error(`Demo store has no handler for ${method} ${pathname}`)
}

export const demoStore = {
  authStatus,
  connectSpotify,
  connectApple,
  listPlaylists,
  syncPlaylist,
  recommendMix,
  listFlows,
  taste,
  overview,
  isConnected: () => authState,
}

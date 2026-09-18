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

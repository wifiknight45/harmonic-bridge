/**
 * API client. VITE_API_URL points the static GitHub Pages site at a hosted backend.
 * OAuth secrets and Apple .p8 keys live ONLY on the backend — never in Pages.
 *
 * When VITE_API_URL is unset or the fetch fails, requests fall back to the
 * in-browser demo store so connect / sync / generate stay usable offline.
 */

import { handleDemoRequest } from './demoStore'

const RAW_BASE = import.meta.env.VITE_API_URL || ''
export const API_BASE = RAW_BASE.replace(/\/$/, '')

/** True when serving responses from the local demo store (no live API). */
let offlineDemoActive = !API_BASE

export function isDemoOffline() {
  return offlineDemoActive
}

async function request(path, options = {}) {
  if (!API_BASE) {
    offlineDemoActive = true
    return handleDemoRequest(path, options)
  }

  try {
    const url = `${API_BASE}${path}`
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(text || `Request failed (${res.status})`)
    }
    offlineDemoActive = false
    return res.json()
  } catch {
    offlineDemoActive = true
    return handleDemoRequest(path, options)
  }
}

export const api = {
  overview: () => request('/api/v1/analytics/overview'),
  authStatus: () => request('/api/v1/auth/status'),
  connectSpotifyDemo: () =>
    request('/api/v1/auth/spotify/demo-connect', { method: 'POST' }),
  connectAppleDemo: () =>
    request('/api/v1/auth/apple/demo-connect', { method: 'POST' }),
  spotifyAuth: () => request('/api/v1/auth/spotify'),
  listPlaylists: (platform = 'all') =>
    request(`/api/v1/playlists?platform=${platform}`),
  syncPlaylist: (body) =>
    request('/api/v1/playlists/sync', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  recommendMix: (body) =>
    request('/api/v1/recommend/mix', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  listFlows: () => request('/api/v1/recommend/flows'),
  taste: (platform = 'spotify', playlistId = 'demo-chill-vibes') =>
    request(
      `/api/v1/analytics/taste?platform=${platform}&playlist_id=${encodeURIComponent(playlistId)}`,
    ),
  tasteTwin: (body = {}) =>
    request('/api/v1/ai/taste-twin', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  moodMix: (body) =>
    request('/api/v1/ai/mood-mix', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  gapFill: (body) =>
    request('/api/v1/ai/gap-fill', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  djCoach: (body = {}) =>
    request('/api/v1/ai/dj-coach', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  lyricSafe: (body = {}) =>
    request('/api/v1/ai/lyric-safe', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  weeklyDrop: (body = {}) =>
    request('/api/v1/ai/weekly-drop', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  weeklyDropGet: (weekLabel) =>
    request(
      weekLabel
        ? `/api/v1/ai/weekly-drop?week_label=${encodeURIComponent(weekLabel)}`
        : '/api/v1/ai/weekly-drop',
    ),
  aiFeatures: () => request('/api/v1/ai/features'),
}

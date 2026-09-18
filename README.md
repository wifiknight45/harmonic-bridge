# harmonic-bridge

[![Status](https://img.shields.io/badge/status-under%20development-orange.svg)](https://github.com/wifiknight45/harmonic-bridge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Spotify](https://img.shields.io/badge/Spotify-1DB954?logo=spotify&logoColor=white)](https://developer.spotify.com/)
[![Apple Music](https://img.shields.io/badge/Apple%20Music-FA243C?logo=applemusic&logoColor=white)](https://developer.apple.com/musickit/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222?logo=github&logoColor=white)](https://wifiknight45.github.io/harmonic-bridge/)
[![API](https://img.shields.io/badge/API-Render-46E3B7?logo=render&logoColor=white)](https://harmonic-bridge-api.onrender.com)
[![Changelog](https://img.shields.io/badge/changelog-Keep%20a%20Changelog-blue.svg)](./CHANGELOG.md)
[![GitHub stars](https://img.shields.io/github/stars/wifiknight45/harmonic-bridge?style=social)](https://github.com/wifiknight45/harmonic-bridge/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/wifiknight45/harmonic-bridge)](https://github.com/wifiknight45/harmonic-bridge/issues)
[![Last commit](https://img.shields.io/github/last-commit/wifiknight45/harmonic-bridge)](https://github.com/wifiknight45/harmonic-bridge/commits/main)

> **Currently under development** — GitHub Pages UI + Render API are live; real Spotify OAuth still being wired. Expect rapid changes.

**Sync your library. Generate playlists that slap.**

Live site (GitHub Pages): **[https://wifiknight45.github.io/harmonic-bridge/](https://wifiknight45.github.io/harmonic-bridge/)**

Hosted API (Render, HTTPS): **[https://harmonic-bridge-api.onrender.com](https://harmonic-bridge-api.onrender.com)** · [health](https://harmonic-bridge-api.onrender.com/health) · [docs](https://harmonic-bridge-api.onrender.com/docs)

harmonic-bridge is a consumer music product in the browser: connect Spotify & Apple Music, sync playlists across platforms with ISRC + fuzzy matching, then generate Camelot-aware harmonic-flow mixes (Ramp Up / Peak Energy / Chill Down).

> Demo mode ships on by default — explore the full sync + generate experience before you wire real credentials.


## Docs

- **[Changelog](./CHANGELOG.md)** — features, commits, PRs, and release notes
- [Pull requests](https://github.com/wifiknight45/harmonic-bridge/pulls)
- [Commits](https://github.com/wifiknight45/harmonic-bridge/commits/main)

---

## Product flow

1. **Connect** Spotify and/or Apple Music (or stay in demo)
2. **Sync your library** — source → target playlist conversion with live match progress
3. **Generate** — cosine-similarity recommendations sequenced on the Camelot wheel

The Pages site is the vibe layer. **OAuth secrets, Spotify client secrets, and Apple Music `.p8` keys live only on the backend** — never in the static frontend.

---

## Repo layout

```
harmonic-bridge/
├── frontend/          # Vite React 18 + Tailwind + React Query (GitHub Pages)
├── backend/           # FastAPI + SQLAlchemy async + matching + recommender
├── docker-compose.yml # Postgres + backend
├── CHANGELOG.md       # Release notes and history
└── .github/workflows/ # Pages deploy
```

---

## GitHub Pages setup

1. Push to `main` (workflow builds `frontend/` and deploys).
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Optional: set repository variable `VITE_API_URL` to your hosted FastAPI base URL
   (currently `https://harmonic-bridge-api.onrender.com`) so the live site can call the backend.
4. Site URL: `https://wifiknight45.github.io/harmonic-bridge/`

Vite is configured with `base: '/harmonic-bridge/'` so assets resolve under the repo path.

Without `VITE_API_URL`, the UI still loads; connect/sync/generate need a reachable API
(local proxy in dev, or a hosted backend for Pages).

---

## Quick start (local)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

OpenAPI docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
cp .env.example .env   # leave VITE_API_URL empty to use Vite proxy → :8000
npm install
npm run dev
```

App: http://localhost:5173/harmonic-bridge/

### Docker (Postgres + backend)

```bash
docker compose up --build
```

Backend on `:8000`, Postgres on `:5432`. Demo mode activates when Spotify/Apple env vars are empty.

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./harmonic_bridge.db` or Postgres async URL |
| `SECRET_KEY` | JWT signing for session tokens |
| `CORS_ORIGINS` | Comma-separated origins (include Pages origin) |
| `SPOTIPY_CLIENT_ID` / `SPOTIPY_CLIENT_SECRET` / `SPOTIPY_REDIRECT_URI` | Spotify OAuth |
| `APPLE_DEVELOPER_KEY_ID` / `APPLE_TEAM_ID` / `APPLE_PRIVATE_KEY_PATH` | MusicKit ES256 developer token |
| `APPLE_MUSIC_USER_TOKEN` | Optional user token for library playlist writes |
| `DEMO_MODE` | `auto` (default) / `true` / `false` |

### Frontend (`frontend/.env`)

| Variable | Purpose |
|----------|---------|
| `VITE_API_URL` | Hosted API base (no trailing slash). Empty = same-origin / Vite proxy |

**Do not put Spotify secrets or Apple `.p8` keys in frontend env or Pages.**

---

## API highlights

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/auth/status` | Connection + demo status |
| GET | `/api/v1/auth/spotify` | OAuth URL (or demo) |
| POST | `/api/v1/auth/spotify/demo-connect` | One-click demo connect |
| POST | `/api/v1/playlists/sync` | Cross-platform sync |
| POST | `/api/v1/recommend/mix` | Harmonic-flow recommendations |
| GET | `/api/v1/analytics/taste` | Taste radar features |

### Matching

1. Exact **ISRC** match
2. Else normalized Title + Artist **rapidfuzz** ratio **> 0.85**

### Recommender

Feature vector: `[danceability, energy, valence, tempo_normalized, acousticness]` → cosine similarity, then Camelot + BPM energy-curve sort.

---

## Tests

```bash
cd backend
pytest tests/ -q
```

---

## Changelog

See **[CHANGELOG.md](./CHANGELOG.md)** for release history, features, and notes.

## License

MIT — build something that goes hard.

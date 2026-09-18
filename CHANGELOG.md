# Changelog

All notable changes to harmonic-bridge are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Client-side offline demo mode for GitHub Pages when `VITE_API_URL` is unset or the API is unreachable (`frontend/src/lib/demoStore.js`)
- API client falls back to in-browser mock responses for auth, playlists, sync, recommend, and taste
- Calm "Demo mode (no API)" banner in AccountStatus instead of a hard backend-unreachable dead-end

### Planned
- Hosted FastAPI backend with OAuth for Spotify and Apple Music
- Wire `VITE_API_URL` on GitHub Pages to a production API
- Persist user sessions and library sync history

### Fixed
- Pages deploy workflow no longer requires `package-lock.json` for npm cache
- Enabled GitHub Pages (build_type: workflow) so `actions/deploy-pages` can publish

## [0.1.0] - 2026-09-18

Initial public scaffold and GitHub Pages frontend.

### Added
- Vite React 18 frontend with Tailwind CSS and React Query
- GitHub Pages deploy workflow (`.github/workflows/deploy-pages.yml`) building `frontend/` on push to `main`
- Static demo-mode UI shell: Dashboard, Sync Library, Generate (Harmonic Flow)
- Account connect cards (Spotify / Apple Music) with demo-connect paths
- Playlist converter UI with ISRC + fuzzy match progress display
- Taste profile radar and Camelot-aware mix curve selectors (Ramp Up / Peak Energy / Chill Down)
- FastAPI backend: auth, playlists sync, recommend, analytics endpoints
- Matching engine (exact ISRC, then Title+Artist rapidfuzz)
- Harmonic-flow recommender (cosine similarity + Camelot/BPM energy curves)
- Demo data / Spotify / Apple Music service layers
- Docker Compose for Postgres + backend
- Alembic initial migration and backend tests for matching/recommender
- Project `.gitignore` excluding secrets, `node_modules`, `.venv`, and build artifacts
- `CHANGELOG.md` linked from README (Docs + Changelog section)

### Documentation
- Polished README with badges, Pages setup, env vars, and API highlights
- This changelog

### Notes
- Live site: https://wifiknight45.github.io/harmonic-bridge/
- Vite `base` and React Router `basename` are `/harmonic-bridge/`
- OAuth secrets and Apple Music `.p8` keys must stay on the backend only
- Without `VITE_API_URL` (or if the API is down), Pages runs fully in client-side demo mode — connect/sync/generate use local mock data
- Workflow uses `npm ci || npm install` so builds succeed even if `package-lock.json` is absent

### Commits / PRs (selected)
- `feat: add Pages frontend and deploy workflow`
- `feat: add frontend pages and API client`
- `feat: add frontend UI components`
- `feat: add backend source` (foundation, endpoints, matching, recommender, platform services)
- `docs: polish README with Pages setup, Docs, and Changelog section`
- `docs: add CHANGELOG, gitignore, and docker-compose`
- `fix: make Pages workflow succeed without package-lock cache`
- No open PRs at initial release; work landed directly on `main`

[Unreleased]: https://github.com/wifiknight45/harmonic-bridge/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/wifiknight45/harmonic-bridge/releases/tag/v0.1.0

# Changelog

All notable changes to harmonic-bridge are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Hosted FastAPI backend with OAuth for Spotify and Apple Music
- Wire `VITE_API_URL` on GitHub Pages to a production API
- Persist user sessions and library sync history

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
- Demo data services so the product works without API keys
- Docker Compose for Postgres + backend
- Alembic initial migration and backend tests for matching/recommender
- Project `.gitignore` excluding secrets, `node_modules`, `.venv`, and build artifacts

### Documentation
- Polished README with badges, Pages setup, env vars, and API highlights
- This changelog

### Notes
- Live site target: https://wifiknight45.github.io/harmonic-bridge/
- Vite `base` and React Router `basename` are `/harmonic-bridge/`
- OAuth secrets and Apple Music `.p8` keys must stay on the backend only
- Without `VITE_API_URL`, the Pages UI loads as a static shell; sync/generate need a reachable API
- Workflow uses `npm ci || npm install` so builds succeed even if `package-lock.json` is absent

### Commits (selected)
- `feat: add Pages frontend and deploy workflow`
- `feat: add frontend pages and API client`
- `feat: add frontend UI components`
- `feat: add backend source`
- `docs: polish README and add docker-compose and gitignore`
- `docs: add CHANGELOG and link from README`

[Unreleased]: https://github.com/wifiknight45/harmonic-bridge/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/wifiknight45/harmonic-bridge/releases/tag/v0.1.0

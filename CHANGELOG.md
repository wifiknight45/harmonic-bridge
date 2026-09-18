# Changelog

All notable changes to **harmonic-bridge** are documented in this file.

Format inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not yet follow strict SemVer tags; entries are dated and commit-linked until `v0.1.0`.

Site: https://wifiknight45.github.io/harmonic-bridge/

---

## [Unreleased]

### Planned
- Complete FastAPI backend push (`auth`, playlist sync, recommend/mix, analytics)
- Wire live Spotify / Apple Music OAuth (demo mode ships first)
- Enable GitHub Pages source = GitHub Actions (if not already)
- Hosted API URL via repo variable `VITE_API_URL`

### Notes
- Product goal: browser site to sync libraries and generate harmonic playlists
- Static Pages frontend; OAuth secrets stay on the backend only
- Public docs stay emoji-free by preference

---

## [0.0.2] - 2026-09-18

### Added
- GitHub Pages frontend scaffold (Vite + React 18, `base: /harmonic-bridge/`)
- Deploy workflow: `.github/workflows/deploy-pages.yml`
- Dashboard pages: Sync, Recommendations
- UI: Account status, playlist converter, harmonic flow controls, taste profile
- Frontend API client + Tailwind dark glass styling (Spotify / Apple Music accents)

### Commits
- [`055ebd2`](https://github.com/wifiknight45/harmonic-bridge/commit/055ebd23a1a8a9bfb9e23d25e8ee0c9780e6597b) — feat: add Pages frontend and deploy workflow
- [`db03890`](https://github.com/wifiknight45/harmonic-bridge/commit/db038907219e8773639c18e1786a69dcc45f8aff) — feat: add frontend pages and API client
- [`93a1931`](https://github.com/wifiknight45/harmonic-bridge/commit/93a193107424d0aebe27bc9263add4c3254c3f19) — feat: add frontend UI components
- [`1c7072e`](https://github.com/wifiknight45/harmonic-bridge/commit/1c7072ebf6b9eb77373a2ea504e5fc361d5a6b3e) — chore: add frontend package-lock.json
- [`a3cc615`](https://github.com/wifiknight45/harmonic-bridge/commit/a3cc615af3ebec06da7c11b9e48fcc20a197990f) — chore: remove stub package-lock so npm install can resolve deps

### Pull requests
- None yet (changes landed directly on `main`)

---

## [0.0.1] - 2026-09-18

### Added
- Public repository created
- README with shields.io badges and under-development status

### Changed
- Removed construction emoji from README (status text retained)

### Commits
- [`a56e14d`](https://github.com/wifiknight45/harmonic-bridge/commit/a56e14d7f2fe5e3b3039bb7416ad3c6edb8d9b42) — Initial commit
- [`288993a`](https://github.com/wifiknight45/harmonic-bridge/commit/288993a6b068a12f69828605a55fcfcfa8acdfd4) — docs: add shields.io badges to README
- [`221ffbb`](https://github.com/wifiknight45/harmonic-bridge/commit/221ffbbec08d198aa2d8f9d70acd791b9af13a1f) — docs: mark repo as currently under development
- [`ec91fbf`](https://github.com/wifiknight45/harmonic-bridge/commit/ec91fbf6bf8e722e0539d048e155b639ae17949f) — docs: remove construction emoji from README

### Pull requests
- None

---

## Maintenance

When merging a PR or cutting a release:
1. Move items from **Unreleased** into a new dated section
2. Link the PR (`#N`) and key commits
3. Note user-facing features vs internal chores separately

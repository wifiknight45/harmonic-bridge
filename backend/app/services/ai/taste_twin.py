"""Taste twin: compact library embedding + cross-platform playlist seeds.

Free local implementation (numpy / scikit-learn). No paid LLM keys.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.services.demo_data import as_audio_tracks, demo_spotify_tracks
from app.services.recommender import FEATURE_KEYS, AudioTrack, taste_profile

# Demo "people like you" personas
_DEMO_TWINS: List[Dict[str, Any]] = [
    {
        "id": "twin-night-drive",
        "label": "Night Drive Twin",
        "platform": "apple",
        "playlist_name": "Midnight Highway",
        "blurb": "High energy, mid-tempo neon — people like you queue this for late rides.",
        "vector": [0.58, 0.78, 0.42, 0.72, 0.08],
    },
    {
        "id": "twin-sunday-soft",
        "label": "Sunday Soft Twin",
        "platform": "spotify",
        "playlist_name": "Soft Focus Sundays",
        "blurb": "Lower energy, warmer valence — your chill twin lives here.",
        "vector": [0.62, 0.45, 0.68, 0.48, 0.35],
    },
    {
        "id": "twin-peak-party",
        "label": "Peak Party Twin",
        "platform": "apple",
        "playlist_name": "Floor Fillers Crossfade",
        "blurb": "Dance-forward, bright valence — cross-platform party seeds.",
        "vector": [0.78, 0.88, 0.75, 0.65, 0.05],
    },
    {
        "id": "twin-indie-glow",
        "label": "Indie Glow Twin",
        "platform": "spotify",
        "playlist_name": "Glow Indie Bridge",
        "blurb": "Balanced energy with acoustic lift — indie-leaning listeners like you.",
        "vector": [0.55, 0.58, 0.55, 0.55, 0.42],
    },
]


def build_taste_embedding(tracks: Sequence[AudioTrack]) -> Dict[str, Any]:
    """Mean feature profile + L2-normalized twin embedding."""
    profile = taste_profile(tracks)
    raw = np.array([profile[k] for k in FEATURE_KEYS], dtype=np.float64)
    norm = float(np.linalg.norm(raw)) or 1.0
    embedding = (raw / norm).tolist()
    return {
        "dims": list(FEATURE_KEYS),
        "profile": profile,
        "embedding": embedding,
        "track_count": len(tracks),
        "norm": norm,
    }


def suggest_playlist_seeds(
    tracks: Optional[Sequence[AudioTrack]] = None,
    top_k: int = 3,
    target_platform: Optional[str] = None,
) -> Dict[str, Any]:
    """Cross-platform playlist seeds for 'people like you' (demo twin personas)."""
    if not tracks:
        tracks = as_audio_tracks(demo_spotify_tracks())

    emb = build_taste_embedding(tracks)
    query = np.array(emb["embedding"], dtype=np.float64).reshape(1, -1)

    candidates = _DEMO_TWINS
    if target_platform:
        filtered = [t for t in candidates if t["platform"] == target_platform]
        if filtered:
            candidates = filtered

    matrix = np.array([t["vector"] for t in candidates], dtype=np.float64)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    sims = cosine_similarity(query, matrix / norms)[0]

    ranked = sorted(zip(candidates, sims), key=lambda x: float(x[1]), reverse=True)[
        : max(1, top_k)
    ]

    seeds = [
        {
            "id": twin["id"],
            "label": twin["label"],
            "platform": twin["platform"],
            "playlist_name": twin["playlist_name"],
            "blurb": twin["blurb"],
            "similarity": round(float(sim), 4),
        }
        for twin, sim in ranked
    ]

    return {
        "taste_embedding": emb,
        "seeds": seeds,
        "message": "People like you start here — cross-platform playlist seeds from your taste twin.",
        "demo_mode": True,
    }

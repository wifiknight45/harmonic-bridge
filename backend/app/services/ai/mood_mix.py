"""Mood to mix: NL mood -> energy/valence/tempo curve -> Camelot-aware playlist.

Free keyword heuristics + local recommender. No paid LLM keys.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.services.demo_data import as_audio_tracks, demo_apple_tracks
from app.services.recommender import AudioTrack, FlowCurve, harmonic_flow_sort, recommend_similar

_MOOD_LEXICON: List[Tuple[Tuple[str, ...], Dict[str, float], FlowCurve, str]] = [
    (
        ("hype", "pump", "workout", "party", "fire", "club", "dance"),
        {"energy": 0.88, "valence": 0.72, "tempo": 128.0},
        FlowCurve.RAMP_UP,
        "High-energy ramp — build to the floor.",
    ),
    (
        ("chill", "calm", "relax", "lofi", "sleep", "wind down", "soft"),
        {"energy": 0.35, "valence": 0.55, "tempo": 90.0},
        FlowCurve.CHILL_DOWN,
        "Soft landing — cool the room, keep the groove.",
    ),
    (
        ("sad", "melancholy", "heartbreak", "blue", "lonely", "rain"),
        {"energy": 0.40, "valence": 0.22, "tempo": 95.0},
        FlowCurve.CHILL_DOWN,
        "Low valence glide — space to feel it.",
    ),
    (
        ("focus", "study", "deep work", "concentrate", "flow state"),
        {"energy": 0.45, "valence": 0.48, "tempo": 105.0},
        FlowCurve.PEAK_ENERGY,
        "Steady focus curve — peak mid-set without spikes.",
    ),
    (
        ("happy", "sunny", "feel good", "upbeat", "joy", "summer"),
        {"energy": 0.70, "valence": 0.85, "tempo": 118.0},
        FlowCurve.PEAK_ENERGY,
        "Bright peak energy — smile-friendly Camelot flow.",
    ),
    (
        ("night", "drive", "neon", "after dark", "late"),
        {"energy": 0.75, "valence": 0.40, "tempo": 120.0},
        FlowCurve.RAMP_UP,
        "Night drive ramp — tension then lift.",
    ),
]

_DEFAULT = (
    {"energy": 0.60, "valence": 0.55, "tempo": 115.0},
    FlowCurve.PEAK_ENERGY,
    "Balanced peak energy — Camelot-aware default mix.",
)


def parse_mood(mood: str) -> Dict[str, Any]:
    """Map NL mood string to target audio curve parameters."""
    text = (mood or "").strip().lower()
    if not text:
        targets, curve, blurb = _DEFAULT
        return {
            "mood": mood or "",
            "targets": dict(targets),
            "curve": curve.value,
            "blurb": blurb,
            "matched_keywords": [],
        }

    best: Optional[Tuple[int, Dict[str, float], FlowCurve, str, List[str]]] = None
    for keywords, targets, curve, blurb in _MOOD_LEXICON:
        hits = [kw for kw in keywords if kw in text or re.search(rf"\b{re.escape(kw)}\b", text)]
        if hits and (best is None or len(hits) > best[0]):
            best = (len(hits), targets, curve, blurb, hits)

    if best is None:
        targets, curve, blurb = _DEFAULT
        return {
            "mood": mood,
            "targets": dict(targets),
            "curve": curve.value,
            "blurb": blurb,
            "matched_keywords": [],
        }

    _, targets, curve, blurb, hits = best
    return {
        "mood": mood,
        "targets": dict(targets),
        "curve": curve.value,
        "blurb": blurb,
        "matched_keywords": hits,
    }


def _synthetic_seed(targets: Dict[str, float]) -> AudioTrack:
    return AudioTrack(
        id="mood-seed",
        title="Mood Seed",
        artist="harmonic-bridge",
        danceability=0.55,
        energy=float(targets.get("energy", 0.6)),
        valence=float(targets.get("valence", 0.55)),
        tempo=float(targets.get("tempo", 115.0)),
        acousticness=0.2,
        key=0,
        mode=1,
    )


def mood_to_mix(
    mood: str,
    catalog: Optional[Sequence[AudioTrack]] = None,
    top_k: int = 12,
) -> Dict[str, Any]:
    """NL mood -> targets -> Camelot-aware playlist (local heuristics)."""
    parsed = parse_mood(mood)
    if not catalog:
        catalog = as_audio_tracks(demo_apple_tracks())

    seed = _synthetic_seed(parsed["targets"])
    similar = recommend_similar(seed, catalog, top_k=top_k)
    picks = [t for t, _ in similar]
    scored = {t.id: float(s) for t, s in similar}
    curve = FlowCurve(parsed["curve"])
    flowed = harmonic_flow_sort(picks, curve=curve)

    n = max(len(flowed), 1)
    valence_t = float(parsed["targets"]["valence"])
    tempo_t = float(parsed["targets"]["tempo"])
    curve_points: List[Dict[str, Any]] = []
    for i in range(len(flowed)):
        t = i / max(n - 1, 1)
        if curve == FlowCurve.RAMP_UP:
            e = 0.25 + 0.7 * t
        elif curve == FlowCurve.CHILL_DOWN:
            e = 0.95 - 0.7 * t
        else:
            e = 0.35 + 0.6 * math.sin(math.pi * t)
        curve_points.append(
            {
                "index": i,
                "energy": round(e, 3),
                "valence": round(valence_t, 3),
                "tempo": round(tempo_t, 1),
            }
        )

    tracks = [
        {
            "id": t.id,
            "title": t.title,
            "artist": t.artist,
            "similarity": round(scored.get(t.id, 0.0), 4),
            "camelot": t.camelot() if hasattr(t, "camelot") else None,
            "energy": t.energy,
            "tempo": t.tempo,
            "valence": t.valence,
            "danceability": t.danceability,
            "acousticness": t.acousticness,
        }
        for t in flowed
    ]

    return {
        "mood": parsed["mood"],
        "targets": {
            "energy": float(parsed["targets"]["energy"]),
            "valence": valence_t,
            "tempo": tempo_t,
        },
        "curve": parsed["curve"],
        "curve_points": curve_points,
        "matched_keywords": parsed["matched_keywords"],
        "tracks": tracks,
        "blurb": parsed["blurb"],
        "message": f"Mood mix ready — {parsed['blurb']}",
        "demo_mode": True,
    }

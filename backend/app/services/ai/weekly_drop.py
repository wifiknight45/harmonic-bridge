"""Weekly drop: digest of mismatches fixed, one fresh playlist, short why-blurb.

Free local assembly of other AI Studio heuristics. Designed for cron/routine hooks.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from app.services.ai.mood_mix import mood_to_mix
from app.services.ai.taste_twin import suggest_playlist_seeds
from app.services.demo_data import as_audio_tracks, demo_apple_tracks, demo_spotify_tracks
from app.services.recommender import AudioTrack


def _demo_mismatches_fixed() -> List[Dict[str, Any]]:
    return [
        {
            "source_title": "Stay",
            "source_artist": "The Kid LAROI & Justin Bieber",
            "target_title": "Stay",
            "target_artist": "The Kid LAROI",
            "method": "fuzzy",
            "score": 0.86,
            "note": "Artist credit trimmed on Apple; fuzzy bridge closed the gap.",
        },
        {
            "source_title": "Levitating",
            "source_artist": "Dua Lipa",
            "target_title": "Levitating (feat. DaBaby)",
            "target_artist": "Dua Lipa",
            "method": "isrc",
            "score": 1.0,
            "note": "ISRC hit after catalog refresh.",
        },
        {
            "source_title": "Save Your Tears",
            "source_artist": "The Weeknd",
            "target_title": "Save Your Tears",
            "target_artist": "The Weeknd",
            "method": "gap_filler",
            "score": 0.78,
            "note": "Gap filler suggested the standard edit after an earlier miss.",
        },
    ]


def build_weekly_digest(
    seed_tracks: Optional[Sequence[AudioTrack]] = None,
    week_label: Optional[str] = None,
) -> Dict[str, Any]:
    """Build weekly digest — hook from cron: GET/POST /api/v1/ai/weekly-drop."""
    now = datetime.now(timezone.utc)
    label = week_label or now.strftime("Week of %Y-%m-%d")

    if not seed_tracks:
        seed_tracks = as_audio_tracks(demo_spotify_tracks())

    mismatches = _demo_mismatches_fixed()
    twin = suggest_playlist_seeds(seed_tracks, top_k=1)
    top_seed = twin["seeds"][0] if twin["seeds"] else None

    mood = "feel good sunday drive"
    if top_seed:
        label_l = top_seed.get("label", "").lower()
        if "party" in label_l:
            mood = "hype party fire"
        elif "soft" in label_l:
            mood = "chill soft focus"
        elif "night" in label_l:
            mood = "night drive neon"

    mix = mood_to_mix(mood, catalog=as_audio_tracks(demo_apple_tracks()), top_k=8)

    why = (
        f"Your taste twin leaned {top_seed['label'] if top_seed else 'balanced'}; "
        f"we closed {len(mismatches)} sync gaps and dropped a Camelot-aware "
        f"'{mix['curve']}' playlist ({mood})."
    )

    return {
        "week_label": label,
        "generated_at": now.isoformat(),
        "mismatches_fixed": mismatches,
        "fresh_playlist": {
            "name": f"Weekly Drop · {label}",
            "mood": mood,
            "curve": mix["curve"],
            "tracks": mix["tracks"],
            "blurb": mix["blurb"],
        },
        "why_blurb": why,
        "taste_twin_seed": top_seed,
        "cron_hint": (
            "Hook this endpoint from cron or GitHub Actions: "
            "GET/POST /api/v1/ai/weekly-drop on a weekly schedule."
        ),
        "message": f"Weekly drop ready — {why}",
        "demo_mode": True,
    }

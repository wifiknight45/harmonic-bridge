"""AI Studio services for harmonic-bridge.

Runs fully free — no AI API keys needed. All features use local heuristics,
numpy/scikit-learn, and demo fixtures so offline / Pages demo mode works.
"""

from app.services.ai.dj_coach import critique_mix
from app.services.ai.gap_filler import suggest_alternates
from app.services.ai.lyric_safe import filter_lyric_safe
from app.services.ai.mood_mix import mood_to_mix
from app.services.ai.taste_twin import build_taste_embedding, suggest_playlist_seeds
from app.services.ai.weekly_drop import build_weekly_digest

__all__ = [
    "build_taste_embedding",
    "suggest_playlist_seeds",
    "mood_to_mix",
    "suggest_alternates",
    "critique_mix",
    "filter_lyric_safe",
    "build_weekly_digest",
]

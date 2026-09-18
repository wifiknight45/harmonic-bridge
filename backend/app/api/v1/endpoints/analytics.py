"""Taste profile / audio feature analytics for the radar chart."""

from collections import Counter
from typing import Optional

from fastapi import APIRouter, Query

from app.core.config import get_settings
from app.schemas.api import AnalyticsResponse
from app.services.apple_music_service import get_apple_music_service
from app.services.recommender import taste_profile
from app.services.spotify_service import get_spotify_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/taste", response_model=AnalyticsResponse)
async def taste_analytics(
    platform: str = Query(default="spotify"),
    playlist_id: Optional[str] = Query(default="demo-chill-vibes"),
    spotify_access_token: Optional[str] = None,
):
    settings = get_settings()
    spotify = get_spotify_service()
    apple = get_apple_music_service()

    if platform == "apple":
        rows = apple.catalog_tracks()
        tracks = apple.to_audio_tracks(rows)
    else:
        rows = spotify.playlist_tracks(
            playlist_id or "demo-chill-vibes", access_token=spotify_access_token
        )
        tracks = spotify.to_audio_tracks(rows)

    profile = taste_profile(tracks)
    energy_curve = [round(t.energy, 3) for t in tracks]

    camelot_counts: Counter[str] = Counter()
    for t in tracks:
        code = t.camelot()
        if code:
            camelot_counts[code] += 1

    artist_counts: Counter[str] = Counter(t.artist for t in tracks)
    top_artists = [
        {"artist": name, "count": count}
        for name, count in artist_counts.most_common(8)
    ]

    return AnalyticsResponse(
        taste_profile=profile,
        track_count=len(tracks),
        energy_curve=energy_curve,
        camelot_distribution=dict(camelot_counts),
        top_artists=top_artists,
        demo_mode=settings.use_demo_mode,
    )


@router.get("/overview")
async def overview():
    settings = get_settings()
    return {
        "app": settings.app_name,
        "demo_mode": settings.use_demo_mode,
        "spotify_configured": settings.spotify_configured,
        "apple_configured": settings.apple_configured,
        "tagline": "Sync your library. Generate playlists that actually slap.",
    }

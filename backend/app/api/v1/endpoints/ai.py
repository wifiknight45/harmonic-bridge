"""AI Studio endpoints — free local heuristics; no paid AI API keys required."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter

from app.schemas.api import (
    DjCoachRequest,
    DjCoachResponse,
    GapFillRequest,
    GapFillResponse,
    LyricSafeRequest,
    LyricSafeResponse,
    MoodMixRequest,
    MoodMixResponse,
    TasteTwinRequest,
    TasteTwinResponse,
    WeeklyDropRequest,
    WeeklyDropResponse,
)
from app.services.ai.dj_coach import critique_mix
from app.services.ai.gap_filler import suggest_alternates
from app.services.ai.lyric_safe import filter_lyric_safe
from app.services.ai.mood_mix import mood_to_mix
from app.services.ai.taste_twin import suggest_playlist_seeds
from app.services.ai.weekly_drop import build_weekly_digest
from app.services.apple_music_service import get_apple_music_service
from app.services.demo_data import demo_spotify_tracks
from app.services.recommender import AudioTrack, FlowCurve
from app.services.spotify_service import get_spotify_service

router = APIRouter(prefix='/ai', tags=['ai'])


def _load_seed_tracks(
    platform: str,
    playlist_id: str | None,
    spotify_token: str | None = None,
) -> List[AudioTrack]:
    spotify = get_spotify_service()
    apple = get_apple_music_service()
    pid = playlist_id or "demo-chill-vibes"
    if platform == "spotify":
        rows = spotify.playlist_tracks(pid, access_token=spotify_token)
        return spotify.to_audio_tracks(rows)
    rows = apple.catalog_tracks()
    return apple.to_audio_tracks(rows)


def _load_catalog(platform: str) -> List[AudioTrack]:
    spotify = get_spotify_service()
    apple = get_apple_music_service()
    if platform == "apple":
        return apple.to_audio_tracks(apple.catalog_tracks())
    return spotify.to_audio_tracks(spotify.playlist_tracks("demo-workout-fire"))


@router.post("/taste-twin", response_model=TasteTwinResponse)
async def taste_twin(body: TasteTwinRequest):
    tracks = _load_seed_tracks(body.seed_platform, body.playlist_id, body.spotify_access_token)
    result = suggest_playlist_seeds(
        tracks,
        top_k=body.top_k,
        target_platform=body.target_platform,
    )
    return TasteTwinResponse(**result)


@router.post("/mood-mix", response_model=MoodMixResponse)
async def mood_mix_endpoint(body: MoodMixRequest):
    catalog = _load_catalog(body.catalog_platform)
    result = mood_to_mix(body.mood, catalog=catalog, top_k=body.top_k)
    return MoodMixResponse(**result)


@router.post("/gap-fill", response_model=GapFillResponse)
async def gap_fill(body: GapFillRequest):
    result = suggest_alternates(
        title=body.title,
        artist=body.artist,
        isrc=body.isrc,
        top_k=body.top_k,
    )
    return GapFillResponse(**result)


@router.post("/dj-coach", response_model=DjCoachResponse)
async def dj_coach(body: DjCoachRequest):
    if body.tracks:
        tracks = [
            AudioTrack(
                id=t.id or f"t-{i}",
                title=t.title,
                artist=t.artist,
                energy=t.energy,
                tempo=t.tempo,
                danceability=t.danceability,
                valence=t.valence,
                acousticness=t.acousticness,
                key=t.key,
                mode=t.mode,
            )
            for i, t in enumerate(body.tracks)
        ]
    else:
        tracks = _load_seed_tracks(body.seed_platform, body.playlist_id or "demo-sunday-drive")

    result = critique_mix(
        tracks,
        propose_reorder=body.propose_reorder,
        curve=FlowCurve(body.curve),
    )
    return DjCoachResponse(**result)


@router.post("/lyric-safe", response_model=LyricSafeResponse)
async def lyric_safe(body: LyricSafeRequest):
    if body.tracks:
        rows = [t.model_dump() for t in body.tracks]
    else:
        rows = demo_spotify_tracks()
    result = filter_lyric_safe(rows, policy=body.policy)
    return LyricSafeResponse(**result)


@router.post("/weekly-drop", response_model=WeeklyDropResponse)
async def weekly_drop(body: WeeklyDropRequest):
    tracks = _load_seed_tracks(body.seed_platform, body.playlist_id)
    result = build_weekly_digest(seed_tracks=tracks, week_label=body.week_label)
    return WeeklyDropResponse(**result)


@router.get("/weekly-drop", response_model=WeeklyDropResponse)
async def weekly_drop_get(week_label: str | None = None):
    """Cron-friendly GET variant for weekly digest."""
    result = build_weekly_digest(week_label=week_label)
    return WeeklyDropResponse(**result)


@router.get("/features")
async def list_ai_features():
    return {
        "features": [
            {"id": "taste-twin", "name": "Taste twin", "path": "/api/v1/ai/taste-twin"},
            {"id": "mood-mix", "name": "Mood to mix", "path": "/api/v1/ai/mood-mix"},
            {"id": "gap-fill", "name": "Gap filler", "path": "/api/v1/ai/gap-fill"},
            {"id": "dj-coach", "name": "DJ coach", "path": "/api/v1/ai/dj-coach"},
            {"id": "lyric-safe", "name": "Lyric-safe filter", "path": "/api/v1/ai/lyric-safe"},
            {"id": "weekly-drop", "name": "Weekly drop", "path": "/api/v1/ai/weekly-drop"},
        ],
        "demo_mode": True,
        "runs_fully_free": True,
        "note": "Runs fully free - no AI API keys needed. Local heuristics + numpy/scikit-learn only.",
    }

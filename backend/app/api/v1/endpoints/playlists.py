"""Playlist listing + cross-platform sync."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

from app.schemas.api import MatchDetail, SyncRequest, SyncResponse
from app.services.apple_music_service import get_apple_music_service
from app.services.matching_engine import match_playlist, match_summary
from app.services.spotify_service import get_spotify_service

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("")
async def list_playlists(platform: str = Query(default="all")):
    spotify = get_spotify_service()
    apple = get_apple_music_service()
    items: List[Dict[str, Any]] = []
    if platform in ("all", "spotify"):
        items.extend(spotify.list_playlists())
    if platform in ("all", "apple"):
        items.extend(apple.list_playlists())
    return {"playlists": items, "demo_mode": spotify.demo or apple.demo}


@router.get("/{playlist_id}/tracks")
async def playlist_tracks(
    playlist_id: str,
    platform: str = Query(default="spotify"),
    spotify_access_token: Optional[str] = None,
):
    spotify = get_spotify_service()
    apple = get_apple_music_service()
    if platform == "apple":
        tracks = apple.catalog_tracks()
    else:
        tracks = spotify.playlist_tracks(playlist_id, access_token=spotify_access_token)
    return {"playlist_id": playlist_id, "platform": platform, "tracks": tracks}


@router.post("/sync", response_model=SyncResponse)
async def sync_playlist(body: SyncRequest):
    """
    Sync a playlist from source → target.
    Matches by ISRC first, then Title+Artist fuzzy (>0.85).
    In demo mode, returns a full match report + simulated target playlist.
    """
    if body.source_platform == body.target_platform:
        return SyncResponse(
            source_platform=body.source_platform,
            target_platform=body.target_platform,
            playlist_id=body.playlist_id,
            summary={"total": 0, "matched": 0, "unmatched": 0, "match_rate": 0.0},
            matches=[],
            message="Pick two different platforms to sync your library across.",
        )

    spotify = get_spotify_service()
    apple = get_apple_music_service()

    if body.source_platform == "spotify":
        source_rows = spotify.playlist_tracks(
            body.playlist_id, access_token=body.spotify_access_token
        )
        source_refs = spotify.to_track_refs(source_rows)
    else:
        source_rows = apple.catalog_tracks()
        source_refs = apple.to_track_refs(source_rows)

    if body.target_platform == "apple":
        target_rows = apple.catalog_tracks()
        target_refs = apple.to_track_refs(target_rows)
    else:
        # Use Spotify demo/catalog as searchable target set
        target_rows = spotify.playlist_tracks("demo-chill-vibes")
        target_refs = spotify.to_track_refs(target_rows)

    results = match_playlist(source_refs, target_refs)
    summary = match_summary(results)

    details = [
        MatchDetail(
            source_title=r.source.title,
            source_artist=r.source.artist,
            source_isrc=r.source.isrc,
            matched=r.matched,
            method=r.method,
            score=round(r.score, 3),
            target_id=r.target.id if r.target else None,
            target_title=r.target.title if r.target else None,
            target_artist=r.target.artist if r.target else None,
        )
        for r in results
    ]

    matched_ids = [r.target.id for r in results if r.matched and r.target]
    target_playlist: Optional[Dict[str, Any]] = None
    playlist_name = body.playlist_name or f"Synced · {body.playlist_id}"

    if body.create_on_target and matched_ids:
        if body.target_platform == "apple":
            target_playlist = await apple.create_playlist(
                user_token=body.apple_user_token or "demo",
                name=playlist_name,
                track_ids=matched_ids,
                description="Synced with harmonic-bridge — seamless library magic.",
            )
        else:
            target_playlist = {
                "demo": True,
                "id": f"sp-sync-{uuid.uuid4().hex[:8]}",
                "name": playlist_name,
                "track_ids": matched_ids,
                "message": f"Demo Spotify playlist with {len(matched_ids)} matched tracks.",
            }

    rate = summary["match_rate"]
    vibe = (
        "Library synced — that was smooth."
        if rate >= 0.8
        else "Most tracks landed. A few need a manual nudge."
        if rate >= 0.5
        else "Partial sync — try another playlist or tighten titles."
    )

    return SyncResponse(
        job_id=uuid.uuid4().hex,
        source_platform=body.source_platform,
        target_platform=body.target_platform,
        playlist_id=body.playlist_id,
        target_playlist=target_playlist,
        summary=summary,
        matches=details,
        message=vibe,
    )

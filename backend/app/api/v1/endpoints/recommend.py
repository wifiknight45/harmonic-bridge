"""Cross-platform mix recommendations + harmonic flow."""

from fastapi import APIRouter

from app.schemas.api import MixRequest, MixResponse
from app.services.apple_music_service import get_apple_music_service
from app.services.recommender import FlowCurve, mix_recommendations
from app.services.spotify_service import get_spotify_service

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.post("/mix", response_model=MixResponse)
async def recommend_mix(body: MixRequest):
    spotify = get_spotify_service()
    apple = get_apple_music_service()

    playlist_id = body.playlist_id or "demo-chill-vibes"

    if body.seed_platform == "spotify":
        seed_rows = spotify.playlist_tracks(
            playlist_id, access_token=body.spotify_access_token
        )
        seeds = spotify.to_audio_tracks(seed_rows)
    else:
        seed_rows = apple.catalog_tracks()
        seeds = apple.to_audio_tracks(seed_rows)

    if body.catalog_platform == "apple":
        catalog_rows = apple.catalog_tracks()
        catalog = apple.to_audio_tracks(catalog_rows)
    else:
        catalog_rows = spotify.playlist_tracks("demo-workout-fire")
        catalog = spotify.to_audio_tracks(catalog_rows)

    curve = FlowCurve(body.curve)
    result = mix_recommendations(seeds, catalog, top_k=body.top_k, curve=curve)

    curve_labels = {
        "ramp_up": "Ramp Up — start chill, finish on fire",
        "peak_energy": "Peak Energy — climb to the drop, then coast",
        "chill_down": "Chill Down — cool the room, keep the groove",
    }

    return MixResponse(
        curve=result["curve"],
        seed_profile=result["seed_profile"],
        tracks=result["tracks"],
        message=f"Playlist generated · {curve_labels.get(body.curve, body.curve)}. Hit play and feel the flow.",
    )


@router.get("/flows")
async def list_flows():
    return {
        "flows": [
            {
                "id": "ramp_up",
                "name": "Ramp Up",
                "description": "Ease in, then lift the energy track by track.",
            },
            {
                "id": "peak_energy",
                "name": "Peak Energy",
                "description": "Build to a mid-set peak, then ride it out.",
            },
            {
                "id": "chill_down",
                "name": "Chill Down",
                "description": "Soft landing — perfect for the drive home.",
            },
        ]
    }

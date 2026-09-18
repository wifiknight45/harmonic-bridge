"""Auth status + OAuth kickoff for Spotify / Apple Music."""

from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.api import AuthStatusResponse
from app.services.apple_music_service import get_apple_music_service
from app.services.spotify_service import get_spotify_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status():
    settings = get_settings()
    spotify = get_spotify_service()
    apple = get_apple_music_service()

    sp_info = spotify.auth_url()
    am_info = apple.auth_status()

    return AuthStatusResponse(
        spotify={
            "configured": spotify.configured,
            "demo": spotify.demo,
            "connected": spotify.demo or spotify.configured,
            "label": "Spotify",
            "authorize_url": sp_info.get("authorize_url"),
            "message": sp_info.get("message")
            or ("Ready to sync your Spotify library" if spotify.configured else "Demo Spotify library unlocked"),
        },
        apple={
            "configured": apple.configured,
            "demo": apple.demo,
            "connected": am_info.get("connected", False),
            "label": "Apple Music",
            "message": am_info.get("message"),
        },
        demo_mode=settings.use_demo_mode,
    )


@router.get("/spotify")
async def spotify_auth_start(state: str = Query(default="harmonic")):
    """Return authorize URL (or demo payload). Frontend opens the URL."""
    spotify = get_spotify_service()
    return spotify.auth_url(state=state)


@router.get("/spotify/callback")
async def spotify_callback(code: str = Query(...), state: Optional[str] = None):
    spotify = get_spotify_service()
    result = spotify.exchange_code(code)
    session = create_access_token(
        subject=result.get("external_id") or "spotify-user",
        extra={
            "platform": "spotify",
            "access_token": result.get("access_token"),
            "display_name": result.get("display_name"),
            "demo": result.get("demo", False),
        },
    )
    settings = get_settings()
    frontend = settings.cors_origin_list[0] if settings.cors_origin_list else None
    if frontend and not result.get("demo"):
        sep = "&" if "?" in frontend else "?"
        return RedirectResponse(f"{frontend}{sep}spotify_session={session}")
    return {"session_token": session, **{k: v for k, v in result.items() if k != "access_token"}}


@router.post("/spotify/demo-connect")
async def spotify_demo_connect():
    """One-click demo connect for the Pages experience."""
    session = create_access_token(
        subject="demo-spotify",
        extra={
            "platform": "spotify",
            "access_token": "demo-spotify-token",
            "display_name": "Demo Listener",
            "demo": True,
        },
    )
    return {
        "connected": True,
        "demo": True,
        "display_name": "Demo Listener",
        "session_token": session,
        "message": "You're in — demo Spotify library ready to sync.",
    }


@router.get("/apple")
async def apple_auth():
    apple = get_apple_music_service()
    return apple.auth_status()


@router.post("/apple/demo-connect")
async def apple_demo_connect():
    session = create_access_token(
        subject="demo-apple",
        extra={
            "platform": "apple",
            "display_name": "Demo Apple Fan",
            "demo": True,
        },
    )
    return {
        "connected": True,
        "demo": True,
        "display_name": "Demo Apple Fan",
        "session_token": session,
        "message": "Apple Music demo unlocked — let's generate something dope.",
    }

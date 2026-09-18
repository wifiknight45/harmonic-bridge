"""Multi-platform ISRC sync execute endpoint (distinct from playlist sync)."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.sync_engine import run_sync_pipeline

router = APIRouter(prefix="/sync", tags=["sync-engine"])


class TrackPayload(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    isrc: Optional[str] = None


class IsrcSyncRequest(BaseModel):
    target_platform: str = Field(
        ...,
        description="Target catalog: spotify or apple_music",
        examples=["spotify"],
    )
    target_credentials: Dict[str, Any] = Field(
        ...,
        description=(
            "Platform credentials for the target. Pass tokens from your session; "
            "do not hard-code secrets in clients or docs."
        ),
        examples=[{"access_token": "<spotify_access_token>"}],
    )
    tracks: List[TrackPayload]


@router.post("/execute")
async def execute_sync(request: IsrcSyncRequest, background_tasks: BackgroundTasks):
    tracks_dict = [t.model_dump() for t in request.tracks]
    background_tasks.add_task(
        run_sync_pipeline,
        source_tracks=tracks_dict,
        target_platform=request.target_platform,
        target_credentials=request.target_credentials,
    )
    return {
        "status": "processing",
        "message": (
            f"Initiated cross-platform sync for {len(tracks_dict)} tracks "
            f"to {request.target_platform}"
        ),
    }

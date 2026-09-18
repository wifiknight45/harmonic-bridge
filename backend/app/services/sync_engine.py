import logging
from typing import List, Dict, Any
from app.services.adapters import SpotifyAdapter, AppleMusicAdapter

logger = logging.getLogger(__name__)

async def run_sync_pipeline(
    source_tracks: List[Dict[str, Any]], 
    target_platform: str, 
    target_credentials: Dict[str, Any]
) -> Dict[str, Any]:
    matched_tracks = []
    unmatched_tracks = []

    if target_platform == "spotify":
        adapter = SpotifyAdapter(access_token=target_credentials["access_token"])
    elif target_platform == "apple_music":
        adapter = AppleMusicAdapter(
            developer_jwt=target_credentials["developer_jwt"],
            user_token=target_credentials["user_token"],
            storefront=target_credentials.get("storefront", "us")
        )
    else:
        raise ValueError(f"Unsupported target platform: {target_platform}")

    for track in source_tracks:
        isrc = track.get("isrc")
        match = await adapter.search_by_isrc(isrc) if isrc else None
        if match:
            matched_tracks.append(match)
        else:
            unmatched_tracks.append(track)

    logger.info(f"Sync complete: {len(matched_tracks)} matched, {len(unmatched_tracks)} unmatched.")
    return {
        "matched": matched_tracks,
        "unmatched": unmatched_tracks,
        "success_rate": len(matched_tracks) / max(len(source_tracks), 1)
    }

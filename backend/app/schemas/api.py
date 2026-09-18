from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AuthStatusResponse(BaseModel):
    spotify: Dict[str, Any]
    apple: Dict[str, Any]
    demo_mode: bool


class SyncRequest(BaseModel):
    source_platform: Literal["spotify", "apple"]
    target_platform: Literal["spotify", "apple"]
    playlist_id: str
    playlist_name: Optional[str] = None
    create_on_target: bool = True
    spotify_access_token: Optional[str] = None
    apple_user_token: Optional[str] = None


class MatchDetail(BaseModel):
    source_title: str
    source_artist: str
    source_isrc: Optional[str] = None
    matched: bool
    method: str
    score: float
    target_id: Optional[str] = None
    target_title: Optional[str] = None
    target_artist: Optional[str] = None


class SyncResponse(BaseModel):
    job_id: Optional[str] = None
    source_platform: str
    target_platform: str
    playlist_id: str
    target_playlist: Optional[Dict[str, Any]] = None
    summary: Dict[str, Any]
    matches: List[MatchDetail]
    message: str


class MixRequest(BaseModel):
    seed_platform: Literal["spotify", "apple"] = "spotify"
    playlist_id: Optional[str] = None
    catalog_platform: Literal["spotify", "apple"] = "apple"
    curve: Literal["ramp_up", "peak_energy", "chill_down"] = "peak_energy"
    top_k: int = Field(default=12, ge=1, le=50)
    spotify_access_token: Optional[str] = None


class MixResponse(BaseModel):
    curve: str
    seed_profile: Dict[str, float]
    tracks: List[Dict[str, Any]]
    message: str


class AnalyticsResponse(BaseModel):
    taste_profile: Dict[str, float]
    track_count: int
    energy_curve: List[float]
    camelot_distribution: Dict[str, int]
    top_artists: List[Dict[str, Any]]
    demo_mode: bool

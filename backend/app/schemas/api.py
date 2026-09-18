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


# --- AI Studio schemas (free local heuristics; no AI API keys) ---


class TasteTwinRequest(BaseModel):
    playlist_id: Optional[str] = "demo-chill-vibes"
    seed_platform: Literal["spotify", "apple"] = "spotify"
    target_platform: Optional[Literal["spotify", "apple"]] = None
    top_k: int = Field(default=3, ge=1, le=10)
    spotify_access_token: Optional[str] = None


class TasteTwinResponse(BaseModel):
    taste_embedding: Dict[str, Any]
    seeds: List[Dict[str, Any]]
    message: str
    demo_mode: bool = True


class MoodMixRequest(BaseModel):
    mood: str = Field(..., min_length=1, max_length=240)
    top_k: int = Field(default=12, ge=1, le=50)
    catalog_platform: Literal["spotify", "apple"] = "apple"


class MoodMixResponse(BaseModel):
    mood: str
    targets: Dict[str, float]
    curve: str
    curve_points: List[Dict[str, Any]]
    matched_keywords: List[str]
    tracks: List[Dict[str, Any]]
    blurb: str
    message: str
    demo_mode: bool = True


class GapFillRequest(BaseModel):
    title: str
    artist: str
    isrc: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)


class GapFillResponse(BaseModel):
    query: Dict[str, Any]
    alternates: List[Dict[str, Any]]
    provider: str
    message: str
    demo_mode: bool = True


class MixTrackInput(BaseModel):
    id: Optional[str] = None
    title: str
    artist: str
    energy: float = 0.5
    tempo: float = 120.0
    danceability: float = 0.5
    valence: float = 0.5
    acousticness: float = 0.2
    key: Optional[int] = None
    mode: Optional[int] = None


class DjCoachRequest(BaseModel):
    tracks: Optional[List[MixTrackInput]] = None
    playlist_id: Optional[str] = None
    propose_reorder: bool = True
    curve: Literal["ramp_up", "peak_energy", "chill_down"] = "peak_energy"
    seed_platform: Literal["spotify", "apple"] = "apple"


class DjCoachResponse(BaseModel):
    score: float
    issue_count: int
    issues: List[Dict[str, Any]]
    reorder_proposal: Optional[Dict[str, Any]] = None
    message: str
    demo_mode: bool = True


class LyricSafeTrackInput(BaseModel):
    id: Optional[str] = None
    title: str
    artist: str
    album: Optional[str] = None
    explicit: Optional[bool] = None


class LyricSafeRequest(BaseModel):
    tracks: Optional[List[LyricSafeTrackInput]] = None
    policy: Literal["family", "focus", "off"] = "family"
    playlist_id: Optional[str] = None


class LyricSafeResponse(BaseModel):
    policy: str
    allowed: List[Dict[str, Any]]
    blocked: List[Dict[str, Any]]
    summary: Dict[str, Any]
    message: str
    demo_mode: bool = True
    classifier: str = "metadata_heuristic"


class WeeklyDropRequest(BaseModel):
    week_label: Optional[str] = None
    playlist_id: Optional[str] = "demo-chill-vibes"
    seed_platform: Literal["spotify", "apple"] = "spotify"


class WeeklyDropResponse(BaseModel):
    week_label: str
    generated_at: str
    mismatches_fixed: List[Dict[str, Any]]
    fresh_playlist: Dict[str, Any]
    why_blurb: str
    taste_twin_seed: Optional[Dict[str, Any]] = None
    cron_hint: str
    message: str
    demo_mode: bool = True

"""TrackNode + HarmonicEngine adapter over the existing Camelot helpers.

Wraps ``app.services.recommender`` pitch-class -> Camelot mapping and
neighbor rules so discovery playlists can reuse the same harmonic graph
without depending on AudioTrack / sklearn feature vectors.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.services.recommender import AudioTrack, _camelot_neighbors


class TrackNode(BaseModel):
    """Lightweight track identity for discovery / playlist sequencing."""

    title: str
    artist: str
    isrc: Optional[str] = None
    energy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    key: Optional[int] = Field(default=None, ge=0, le=11)
    mode: Optional[int] = Field(default=None, ge=0, le=1)
    camelot: Optional[str] = None

    def resolve_camelot(self) -> Optional[str]:
        """Prefer an explicit Camelot code; otherwise derive from key/mode."""
        if self.camelot:
            return self.camelot.upper()
        if self.key is None or self.mode is None:
            return None
        return AudioTrack(
            id="_",
            title=self.title,
            artist=self.artist,
            key=self.key,
            mode=self.mode,
        ).camelot()


class HarmonicEngine:
    """Camelot-neighbor compatibility checks.

    Two tracks are compatible when their Camelot codes share a wheel
    neighbor relationship: same code, relative major/minor (same number,
    flip A/B), or +/- 1 number with the same letter. If either track lacks
    Camelot information, they are treated as compatible (neutral fallback)
    so sequencing can still proceed.
    """

    @staticmethod
    def is_harmonically_compatible(a: TrackNode, b: TrackNode) -> bool:
        cam_a = a.resolve_camelot()
        cam_b = b.resolve_camelot()
        if not cam_a or not cam_b:
            return True
        return cam_b in _camelot_neighbors(cam_a)

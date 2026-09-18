"""ISRC-first track matching with Title+Artist fuzzy fallback."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from rapidfuzz import fuzz


MATCH_THRESHOLD = 0.85


@dataclass
class TrackRef:
    """Normalized track identity used across platforms."""

    id: str
    title: str
    artist: str
    platform: str
    isrc: Optional[str] = None
    album: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def normalized_title(self) -> str:
        return _normalize(self.title)

    def normalized_artist(self) -> str:
        return _normalize(self.artist)


@dataclass
class MatchResult:
    source: TrackRef
    target: Optional[TrackRef]
    method: str  # isrc | fuzzy | none
    score: float
    matched: bool


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\(.*?\)|\[.*?\]", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\b(feat|ft|featuring|with)\b.*$", "", text).strip()
    return text


def fuzzy_score(a: TrackRef, b: TrackRef) -> float:
    """Combined title+artist rapidfuzz ratio in [0, 1]."""
    title_score = fuzz.ratio(a.normalized_title(), b.normalized_title()) / 100.0
    artist_score = fuzz.ratio(a.normalized_artist(), b.normalized_artist()) / 100.0
    return 0.6 * title_score + 0.4 * artist_score


def match_track(
    source: TrackRef,
    candidates: Sequence[TrackRef],
    threshold: float = MATCH_THRESHOLD,
) -> MatchResult:
    """Match a source track against candidates: ISRC exact, then fuzzy."""
    if source.isrc:
        isrc_upper = source.isrc.strip().upper()
        for cand in candidates:
            if cand.isrc and cand.isrc.strip().upper() == isrc_upper:
                return MatchResult(
                    source=source,
                    target=cand,
                    method="isrc",
                    score=1.0,
                    matched=True,
                )

    best: Optional[TrackRef] = None
    best_score = 0.0
    for cand in candidates:
        score = fuzzy_score(source, cand)
        if score > best_score:
            best_score = score
            best = cand

    if best is not None and best_score >= threshold:
        return MatchResult(
            source=source,
            target=best,
            method="fuzzy",
            score=best_score,
            matched=True,
        )

    return MatchResult(
        source=source,
        target=None,
        method="none",
        score=best_score,
        matched=False,
    )


def match_playlist(
    source_tracks: Sequence[TrackRef],
    target_catalog: Sequence[TrackRef],
    threshold: float = MATCH_THRESHOLD,
) -> List[MatchResult]:
    """Match every source track against a target-platform catalog."""
    return [match_track(t, target_catalog, threshold) for t in source_tracks]


def match_summary(results: Sequence[MatchResult]) -> Dict[str, Any]:
    matched = sum(1 for r in results if r.matched)
    isrc = sum(1 for r in results if r.method == "isrc")
    fuzzy = sum(1 for r in results if r.method == "fuzzy")
    return {
        "total": len(results),
        "matched": matched,
        "unmatched": len(results) - matched,
        "isrc_matches": isrc,
        "fuzzy_matches": fuzzy,
        "match_rate": (matched / len(results)) if results else 0.0,
    }

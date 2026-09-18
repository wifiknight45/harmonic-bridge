"""Gap filler: on ISRC/fuzzy miss, suggest alternate recordings with confidence.

Free local rapidfuzz heuristics. Pluggable provider interface for future free
local models — never requires paid LLM API keys.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, Sequence

from rapidfuzz import fuzz

from app.services.demo_data import demo_apple_tracks, demo_spotify_tracks
from app.services.matching_engine import TrackRef, _normalize as normalize_text


class AlternateProvider(Protocol):
    """Pluggable provider for alternate recording suggestions."""

    def suggest(
        self,
        query: TrackRef,
        catalog: Sequence[TrackRef],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        ...


class HeuristicAlternateProvider:
    """Title/artist fuzzy + album/version cues. No LLM key needed."""

    VERSION_BONUS = ("live", "acoustic", "remix", "radio edit", "deluxe", "remaster")

    def suggest(
        self,
        query: TrackRef,
        catalog: Sequence[TrackRef],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        q_title = normalize_text(query.title)
        q_artist = normalize_text(query.artist)
        scored: List[Dict[str, Any]] = []

        for cand in catalog:
            if cand.id == query.id:
                continue
            if query.isrc and cand.isrc and query.isrc == cand.isrc:
                continue

            title_score = fuzz.token_set_ratio(q_title, normalize_text(cand.title)) / 100.0
            artist_score = fuzz.token_set_ratio(q_artist, normalize_text(cand.artist)) / 100.0
            combined = 0.65 * title_score + 0.35 * artist_score

            album = (cand.album or "").lower()
            title_l = cand.title.lower()
            version_note = None
            for token in self.VERSION_BONUS:
                if token in album or token in title_l:
                    combined = min(1.0, combined + 0.05)
                    version_note = token
                    break

            if combined < 0.45:
                continue

            scored.append(
                {
                    "id": cand.id,
                    "title": cand.title,
                    "artist": cand.artist,
                    "album": cand.album,
                    "isrc": cand.isrc,
                    "platform": cand.platform,
                    "confidence": round(combined, 4),
                    "reason": _reason(title_score, artist_score, version_note),
                }
            )

        scored.sort(key=lambda x: x["confidence"], reverse=True)
        return scored[:top_k]


def _reason(title_score: float, artist_score: float, version_note: Optional[str]) -> str:
    parts = [f"title~{title_score:.2f}", f"artist~{artist_score:.2f}"]
    if version_note:
        parts.append(f"version:{version_note}")
    return "; ".join(parts)


def _default_provider() -> AlternateProvider:
    """Always use free local heuristics (no paid LLM / API keys)."""
    return HeuristicAlternateProvider()


def suggest_alternates(
    title: str,
    artist: str,
    isrc: Optional[str] = None,
    catalog: Optional[Sequence[TrackRef]] = None,
    top_k: int = 3,
    provider: Optional[AlternateProvider] = None,
) -> Dict[str, Any]:
    """Suggest alternate recordings when ISRC/fuzzy matching misses."""
    query = TrackRef(
        id="gap-query",
        title=title,
        artist=artist,
        platform="query",
        isrc=isrc,
    )

    if catalog is None:
        rows = demo_apple_tracks() + demo_spotify_tracks()
        catalog = [
            TrackRef(
                id=r["id"],
                title=r["title"],
                artist=r["artist"],
                platform="apple" if str(r["id"]).startswith("am") else "spotify",
                isrc=r.get("isrc"),
                album=r.get("album"),
            )
            for r in rows
        ]

    prov = provider or _default_provider()
    alts = prov.suggest(query, catalog, top_k=top_k)

    return {
        "query": {"title": title, "artist": artist, "isrc": isrc},
        "alternates": alts,
        "provider": type(prov).__name__,
        "message": (
            f"Found {len(alts)} alternate recording(s) for gap fill."
            if alts
            else "No strong alternate recordings — try a different title spelling."
        ),
        "demo_mode": True,
    }

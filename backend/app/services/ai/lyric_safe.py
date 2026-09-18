"""Lyric-safe filter: optional family/focus policy before sync.

Metadata/heuristic classifier only (title/artist/album). Free — no lyric API
or paid LLM keys.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional, Sequence

PolicyName = Literal["family", "focus", "off"]

_EXPLICIT_MARKERS = (
    r"\bexplicit\b",
    r"f\*ck",
    r"\bfuck\b",
    r"\bshit\b",
    r"\bbitch\b",
    r"\bass\b",
    r"\bnigga\b",
    r"\bnigger\b",
    r"\bdamn\b",
)

_FOCUS_NOISE = ("party", "club", "remix", "feat.", "ft.", "radio edit")
_FAMILY_SAFE_HINTS = ("kids", "lullaby", "family", "clean")


def _blob(title: str, artist: str, album: Optional[str] = None) -> str:
    return " ".join([title or "", artist or "", album or ""]).lower()


def classify_track(
    title: str,
    artist: str,
    album: Optional[str] = None,
    explicit_flag: Optional[bool] = None,
) -> Dict[str, Any]:
    """Heuristic lyric-safety classifier from metadata only."""
    blob = _blob(title, artist, album)
    reasons: List[str] = []
    explicit = False

    if explicit_flag is True:
        explicit = True
        reasons.append("explicit_flag")

    for marker in _EXPLICIT_MARKERS:
        if re.search(marker, blob, re.I):
            explicit = True
            reasons.append(f"marker:{marker}")
            break

    if album and re.search(r"f\*ck|fuck", album, re.I):
        explicit = True
        if "album_title" not in reasons:
            reasons.append("album_title")

    focus_noisy = any(tok in blob for tok in _FOCUS_NOISE)
    family_hint = any(tok in blob for tok in _FAMILY_SAFE_HINTS)

    if explicit:
        family_ok = False
        label = "explicit"
    elif family_hint:
        family_ok = True
        label = "family_friendly"
    else:
        family_ok = True
        label = "clean_unknown"

    focus_ok = (not focus_noisy) and (not explicit)

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "label": label,
        "explicit": explicit,
        "family_ok": family_ok,
        "focus_ok": focus_ok,
        "reasons": reasons,
        "confidence": 0.9 if reasons or family_hint else 0.55,
    }


def filter_lyric_safe(
    tracks: Sequence[Dict[str, Any]],
    policy: PolicyName = "family",
) -> Dict[str, Any]:
    """Apply family or focus policy before sync. policy=off tags only."""
    classified = []
    for t in tracks:
        c = classify_track(
            title=str(t.get("title", "")),
            artist=str(t.get("artist", "")),
            album=t.get("album"),
            explicit_flag=t.get("explicit"),
        )
        c["id"] = t.get("id")
        classified.append(c)

    if policy == "off":
        allowed, blocked = classified, []
    elif policy == "focus":
        allowed = [c for c in classified if c["focus_ok"]]
        blocked = [c for c in classified if not c["focus_ok"]]
    else:
        allowed = [c for c in classified if c["family_ok"]]
        blocked = [c for c in classified if not c["family_ok"]]

    return {
        "policy": policy,
        "allowed": allowed,
        "blocked": blocked,
        "summary": {
            "total": len(classified),
            "allowed": len(allowed),
            "blocked": len(blocked),
        },
        "message": (
            f"Lyric-safe ({policy}): kept {len(allowed)}/{len(classified)} tracks."
            if policy != "off"
            else f"Lyric-safe off: tagged {len(classified)} tracks, none blocked."
        ),
        "demo_mode": True,
        "classifier": "metadata_heuristic",
    }

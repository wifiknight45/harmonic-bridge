"""DJ coach: critique mix for key clashes, energy cliffs, vocal stacking + reorder.

Free local Camelot / energy heuristics. No paid AI APIs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from app.services.demo_data import as_audio_tracks, demo_apple_tracks
from app.services.recommender import AudioTrack, FlowCurve, harmonic_flow_sort

ENERGY_CLIFF_THRESHOLD = 0.28
VOCAL_STACK_WINDOW = 3


def _camelot_neighbors(code: str) -> set[str]:
    if len(code) < 2:
        return {code}
    num = int(code[:-1])
    letter = code[-1]
    other = "A" if letter == "B" else "B"
    return {
        code,
        f"{num}{other}",
        f"{(num % 12) + 1}{letter}",
        f"{((num - 2) % 12) + 1}{letter}",
    }


def _vocal_score(track: AudioTrack) -> float:
    """Heuristic vocal prominence proxy (inverse acousticness + energy/dance)."""
    return max(
        0.0,
        min(
            1.0,
            (1.0 - track.acousticness) * 0.6
            + track.energy * 0.25
            + track.danceability * 0.15,
        ),
    )


def critique_mix(
    tracks: Optional[Sequence[AudioTrack]] = None,
    propose_reorder: bool = True,
    curve: FlowCurve = FlowCurve.PEAK_ENERGY,
) -> Dict[str, Any]:
    """Critique a mix; optionally propose a Camelot/energy reorder."""
    if not tracks:
        tracks = as_audio_tracks(demo_apple_tracks())[:8]

    track_list = list(tracks)
    issues: List[Dict[str, Any]] = []

    for i in range(1, len(track_list)):
        prev, curr = track_list[i - 1], track_list[i]
        prev_c, curr_c = prev.camelot(), curr.camelot()
        if prev_c and curr_c:
            neighbors = _camelot_neighbors(prev_c)
            if curr_c not in neighbors:
                issues.append(
                    {
                        "type": "key_clash",
                        "severity": "warn",
                        "from_index": i - 1,
                        "to_index": i,
                        "from_track": prev.title,
                        "to_track": curr.title,
                        "from_camelot": prev_c,
                        "to_camelot": curr_c,
                        "detail": f"Camelot jump {prev_c} -> {curr_c} is outside compatible neighbors.",
                    }
                )

    for i in range(1, len(track_list)):
        prev, curr = track_list[i - 1], track_list[i]
        delta = abs(curr.energy - prev.energy)
        if delta >= ENERGY_CLIFF_THRESHOLD:
            direction = "drop" if curr.energy < prev.energy else "spike"
            issues.append(
                {
                    "type": "energy_cliff",
                    "severity": "warn" if delta < 0.4 else "error",
                    "from_index": i - 1,
                    "to_index": i,
                    "from_track": prev.title,
                    "to_track": curr.title,
                    "energy_delta": round(delta, 3),
                    "detail": (
                        f"Energy {direction} of {delta:.2f} between tracks "
                        f"({prev.energy:.2f} -> {curr.energy:.2f})."
                    ),
                }
            )

    vocals = [_vocal_score(t) for t in track_list]
    run_start = 0
    while run_start < len(vocals):
        if vocals[run_start] < 0.72:
            run_start += 1
            continue
        run_end = run_start
        while run_end < len(vocals) and vocals[run_end] >= 0.72:
            run_end += 1
        run_len = run_end - run_start
        if run_len >= VOCAL_STACK_WINDOW:
            titles = [track_list[j].title for j in range(run_start, run_end)]
            issues.append(
                {
                    "type": "vocal_stacking",
                    "severity": "info",
                    "from_index": run_start,
                    "to_index": run_end - 1,
                    "tracks": titles,
                    "detail": (
                        f"{run_len} consecutive vocal-heavy tracks may fatigue the floor: "
                        f"{', '.join(titles)}."
                    ),
                }
            )
        run_start = run_end

    score = max(
        0.0,
        100.0
        - 12.0 * len([i for i in issues if i["severity"] == "error"])
        - 6.0 * len([i for i in issues if i["severity"] == "warn"])
        - 2.0 * len([i for i in issues if i["severity"] == "info"]),
    )

    reorder_proposal = None
    if propose_reorder and len(track_list) > 1:
        reordered = harmonic_flow_sort(track_list, curve=curve)
        reorder_proposal = {
            "curve": curve.value,
            "order": [
                {
                    "id": t.id,
                    "title": t.title,
                    "artist": t.artist,
                    "camelot": t.camelot(),
                    "energy": t.energy,
                    "tempo": t.tempo,
                }
                for t in reordered
            ],
            "note": "Reordered for Camelot-compatible transitions along the selected energy curve.",
        }

    clash_n = sum(1 for i in issues if i["type"] == "key_clash")
    cliff_n = sum(1 for i in issues if i["type"] == "energy_cliff")
    stack_n = sum(1 for i in issues if i["type"] == "vocal_stacking")
    summary_bits = []
    if clash_n:
        summary_bits.append(f"{clash_n} key clash(es)")
    if cliff_n:
        summary_bits.append(f"{cliff_n} energy cliff(s)")
    if stack_n:
        summary_bits.append(f"{stack_n} vocal stack(s)")
    if not summary_bits:
        summary_bits.append("clean transitions")

    return {
        "score": round(score, 1),
        "issue_count": len(issues),
        "issues": issues,
        "reorder_proposal": reorder_proposal,
        "message": f"DJ coach score {score:.0f}/100 — {', '.join(summary_bits)}.",
        "demo_mode": True,
    }

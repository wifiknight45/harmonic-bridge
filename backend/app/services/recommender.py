"""Audio-feature recommender + Camelot wheel harmonic flow sorter."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


FEATURE_KEYS = ("danceability", "energy", "valence", "tempo", "acousticness")
TEMPO_MAX = 200.0  # for normalization


class FlowCurve(str, Enum):
    RAMP_UP = "ramp_up"
    PEAK_ENERGY = "peak_energy"
    CHILL_DOWN = "chill_down"


_PITCH_TO_CAMELOT_MAJOR = {
    0: "8B", 1: "3B", 2: "10B", 3: "5B", 4: "12B", 5: "7B",
    6: "2B", 7: "9B", 8: "4B", 9: "11B", 10: "6B", 11: "1B",
}
_PITCH_TO_CAMELOT_MINOR = {
    0: "5A", 1: "12A", 2: "7A", 3: "2A", 4: "9A", 5: "4A",
    6: "11A", 7: "6A", 8: "1A", 9: "8A", 10: "3A", 11: "10A",
}


@dataclass
class AudioTrack:
    id: str
    title: str
    artist: str
    danceability: float = 0.5
    energy: float = 0.5
    valence: float = 0.5
    tempo: float = 120.0
    acousticness: float = 0.2
    key: Optional[int] = None
    mode: Optional[int] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def feature_vector(self) -> np.ndarray:
        tempo_n = min(max(self.tempo, 0.0), TEMPO_MAX) / TEMPO_MAX
        return np.array(
            [
                float(self.danceability),
                float(self.energy),
                float(self.valence),
                tempo_n,
                float(self.acousticness),
            ],
            dtype=np.float64,
        )

    def camelot(self) -> Optional[str]:
        if self.key is None or self.mode is None:
            return None
        if self.key < 0 or self.key > 11:
            return None
        table = _PITCH_TO_CAMELOT_MAJOR if self.mode == 1 else _PITCH_TO_CAMELOT_MINOR
        return table.get(self.key)


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


def build_matrix(tracks: Sequence[AudioTrack]) -> np.ndarray:
    if not tracks:
        return np.zeros((0, len(FEATURE_KEYS)))
    return np.vstack([t.feature_vector() for t in tracks])


def recommend_similar(
    seed: AudioTrack | Sequence[AudioTrack],
    catalog: Sequence[AudioTrack],
    top_k: int = 20,
    exclude_ids: Optional[set[str]] = None,
) -> List[Tuple[AudioTrack, float]]:
    if not catalog:
        return []

    exclude_ids = exclude_ids or set()
    if isinstance(seed, AudioTrack):
        seed_vec = seed.feature_vector().reshape(1, -1)
        exclude_ids = exclude_ids | {seed.id}
    else:
        seeds = list(seed)
        if not seeds:
            return []
        seed_vec = build_matrix(seeds).mean(axis=0, keepdims=True)
        exclude_ids = exclude_ids | {s.id for s in seeds}

    matrix = build_matrix(catalog)
    sims = cosine_similarity(seed_vec, matrix)[0]

    scored: List[Tuple[AudioTrack, float]] = []
    for track, sim in zip(catalog, sims):
        if track.id in exclude_ids:
            continue
        scored.append((track, float(sim)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def _energy_target_curve(n: int, curve: FlowCurve) -> np.ndarray:
    if n <= 0:
        return np.array([])
    x = np.linspace(0.0, 1.0, n)
    if curve == FlowCurve.RAMP_UP:
        return 0.25 + 0.7 * x
    if curve == FlowCurve.CHILL_DOWN:
        return 0.95 - 0.7 * x
    return 0.35 + 0.6 * np.sin(np.pi * x)


def harmonic_flow_sort(
    tracks: Sequence[AudioTrack],
    curve: FlowCurve = FlowCurve.PEAK_ENERGY,
) -> List[AudioTrack]:
    if len(tracks) <= 1:
        return list(tracks)

    remaining = list(tracks)
    targets = _energy_target_curve(len(tracks), curve)
    first_idx = int(np.argmin([abs(t.energy - targets[0]) for t in remaining]))
    ordered = [remaining.pop(first_idx)]

    for i in range(1, len(tracks)):
        target_energy = targets[i]
        prev = ordered[-1]
        prev_cam = prev.camelot()
        neighbors = _camelot_neighbors(prev_cam) if prev_cam else set()

        def score(t: AudioTrack) -> float:
            energy_pen = abs(t.energy - target_energy)
            bpm_pen = abs(t.tempo - prev.tempo) / TEMPO_MAX
            cam = t.camelot()
            if prev_cam and cam:
                harm_bonus = 0.0 if cam in neighbors else 0.35
            else:
                harm_bonus = 0.15
            return energy_pen + 0.4 * bpm_pen + harm_bonus

        best_i = int(np.argmin([score(t) for t in remaining]))
        ordered.append(remaining.pop(best_i))

    return ordered


def taste_profile(tracks: Sequence[AudioTrack]) -> Dict[str, float]:
    if not tracks:
        return {k: 0.0 for k in FEATURE_KEYS}
    mat = build_matrix(tracks)
    means = mat.mean(axis=0)
    return {k: float(means[i]) for i, k in enumerate(FEATURE_KEYS)}


def mix_recommendations(
    seed_tracks: Sequence[AudioTrack],
    catalog: Sequence[AudioTrack],
    top_k: int = 25,
    curve: FlowCurve = FlowCurve.PEAK_ENERGY,
) -> Dict[str, Any]:
    similar = recommend_similar(seed_tracks, catalog, top_k=top_k)
    picks = [t for t, _ in similar]
    scored = {t.id: s for t, s in similar}
    flowed = harmonic_flow_sort(picks, curve=curve)
    return {
        "curve": curve.value,
        "seed_profile": taste_profile(seed_tracks),
        "tracks": [
            {
                "id": t.id,
                "title": t.title,
                "artist": t.artist,
                "similarity": scored.get(t.id, 0.0),
                "camelot": t.camelot(),
                "energy": t.energy,
                "tempo": t.tempo,
                "danceability": t.danceability,
                "valence": t.valence,
                "acousticness": t.acousticness,
                "key": t.key,
                "mode": t.mode,
                **t.extras,
            }
            for t in flowed
        ],
    }

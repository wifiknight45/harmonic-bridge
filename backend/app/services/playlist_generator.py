"""
playlist_generator.py
Playlist generation and novel music discovery engine for harmonic-bridge.
"""

from __future__ import annotations

from typing import List, Set

from pydantic import BaseModel, Field

from app.services.harmonic_core import HarmonicEngine, TrackNode


class SeedParams(BaseModel):
    seed_tracks: List[TrackNode]
    target_size: int = Field(default=20, ge=1)
    min_energy: float = Field(default=0.0, ge=0.0, le=1.0)
    max_energy: float = Field(default=1.0, ge=0.0, le=1.0)


class DiscoveryPlaylistEngine:
    """
    Generates tailored discovery playlists by filtering out known library tracks
    and sequencing candidate tracks for smooth transitions.
    """

    def __init__(self, user_library_ids: Set[str]):
        # Combined set of track identifiers (ISRCs / normalized titles) the user already owns
        self.user_library = user_library_ids

    def filter_novel_candidates(self, raw_recommendations: List[TrackNode]) -> List[TrackNode]:
        """
        Removes any candidate track that exists in the user's cross-platform library.
        """
        novel_tracks: List[TrackNode] = []
        for track in raw_recommendations:
            track_identifier = track.isrc or f"{track.artist.lower()}:{track.title.lower()}"
            if track_identifier not in self.user_library:
                novel_tracks.append(track)
        return novel_tracks

    def sequence_playlist_flow(self, candidate_tracks: List[TrackNode]) -> List[TrackNode]:
        """
        Orders candidate tracks so each song transitions harmonically
        into the next when possible.
        """
        if not candidate_tracks:
            return []

        remaining = list(candidate_tracks)
        playlist = [remaining.pop(0)]

        while remaining:
            current_track = playlist[-1]
            next_idx = None

            # Look for the first harmonically compatible track in candidates
            for idx, candidate in enumerate(remaining):
                if HarmonicEngine.is_harmonically_compatible(current_track, candidate):
                    next_idx = idx
                    break

            # Fallback to the next available track if no harmonic match is found
            if next_idx is None:
                next_idx = 0

            playlist.append(remaining.pop(next_idx))

        return playlist

    def generate_discovery_set(
        self, raw_recommendations: List[TrackNode], params: SeedParams
    ) -> List[TrackNode]:
        """
        Full pipeline: Filters for novelty, trims to target size, and sequences flow.
        """
        novel = self.filter_novel_candidates(raw_recommendations)
        energy_filtered = [
            t
            for t in novel
            if t.energy is None or params.min_energy <= t.energy <= params.max_energy
        ]
        trimmed = energy_filtered[: params.target_size]
        return self.sequence_playlist_flow(trimmed)

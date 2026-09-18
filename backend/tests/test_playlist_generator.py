"""Unit tests for discovery playlist novelty filter and harmonic sequencing."""

from app.services.harmonic_core import HarmonicEngine, TrackNode
from app.services.playlist_generator import DiscoveryPlaylistEngine, SeedParams


def _node(title, artist, *, isrc=None, energy=None, key=None, mode=None, camelot=None):
    return TrackNode(
        title=title,
        artist=artist,
        isrc=isrc,
        energy=energy,
        key=key,
        mode=mode,
        camelot=camelot,
    )


def test_filter_novel_candidates_drops_known_isrc_and_title_artist():
    library = {"USRC123", "known artist:known song"}
    engine = DiscoveryPlaylistEngine(library)
    raw = [
        _node("Known Song", "Known Artist"),  # title:artist hit
        _node("Fresh Track", "New Band", isrc="USRC999"),
        _node("Owned Hit", "Someone", isrc="USRC123"),  # isrc hit
        _node("Another Fresh", "Other Band"),
    ]
    novel = engine.filter_novel_candidates(raw)
    titles = [t.title for t in novel]
    assert titles == ["Fresh Track", "Another Fresh"]


def test_sequence_playlist_flow_prefers_harmonic_neighbor():
    # 8B neighbors include 8A, 9B, 7B (and 8B itself)
    a = _node("A", "Art", camelot="8B")
    incompatible = _node("Far", "Art", camelot="2A")  # not a neighbor of 8B
    compatible = _node("Near", "Art", camelot="9B")
    engine = DiscoveryPlaylistEngine(set())
    ordered = engine.sequence_playlist_flow([a, incompatible, compatible])
    assert [t.title for t in ordered] == ["A", "Near", "Far"]


def test_sequence_playlist_flow_falls_back_when_no_match():
    # No Camelot neighbors among candidates -> always take index 0
    a = _node("A", "Art", camelot="8B")
    b = _node("B", "Art", camelot="2A")
    c = _node("C", "Art", camelot="5A")
    engine = DiscoveryPlaylistEngine(set())
    ordered = engine.sequence_playlist_flow([a, b, c])
    assert [t.title for t in ordered] == ["A", "B", "C"]


def test_generate_discovery_set_trims_and_filters_energy():
    library = {"SKIP1"}
    engine = DiscoveryPlaylistEngine(library)
    raw = [
        _node("Skip Me", "X", isrc="SKIP1", energy=0.5, camelot="8B"),
        _node("Low", "X", energy=0.1, camelot="8B"),
        _node("Mid", "X", energy=0.5, camelot="9B"),
        _node("High", "X", energy=0.9, camelot="7B"),
        _node("Extra", "X", energy=0.6, camelot="8A"),
    ]
    params = SeedParams(seed_tracks=[raw[2]], target_size=2, min_energy=0.4, max_energy=0.95)
    result = engine.generate_discovery_set(raw, params)
    assert len(result) == 2
    assert all(t.title != "Skip Me" for t in result)
    assert all(t.title != "Low" for t in result)
    assert all(t.energy is None or 0.4 <= t.energy <= 0.95 for t in result)


def test_empty_candidates_return_empty_playlist():
    engine = DiscoveryPlaylistEngine(set())
    assert engine.sequence_playlist_flow([]) == []
    params = SeedParams(seed_tracks=[], target_size=5)
    assert engine.generate_discovery_set([], params) == []


def test_harmonic_engine_compatible_neighbors_and_neutral_missing():
    a = _node("A", "Art", camelot="8B")
    assert HarmonicEngine.is_harmonically_compatible(a, _node("B", "Art", camelot="9B"))
    assert HarmonicEngine.is_harmonically_compatible(a, _node("C", "Art", camelot="8A"))
    assert not HarmonicEngine.is_harmonically_compatible(a, _node("D", "Art", camelot="2A"))
    # Missing Camelot => neutral compatible
    assert HarmonicEngine.is_harmonically_compatible(a, _node("E", "Art"))

"""Unit tests for the six free local AI Studio features."""

from app.services.ai.dj_coach import critique_mix
from app.services.ai.gap_filler import HeuristicAlternateProvider, suggest_alternates
from app.services.ai.lyric_safe import classify_track, filter_lyric_safe
from app.services.ai.mood_mix import mood_to_mix, parse_mood
from app.services.ai.taste_twin import build_taste_embedding, suggest_playlist_seeds
from app.services.ai.weekly_drop import build_weekly_digest
from app.services.demo_data import as_audio_tracks, demo_spotify_tracks
from app.services.matching_engine import TrackRef
from app.services.recommender import AudioTrack, FlowCurve


def _track(i, energy=0.5, key=0, mode=1, acousticness=0.2, title=None):
    return AudioTrack(
        id=str(i),
        title=title or f"Track {i}",
        artist="Artist",
        danceability=0.5,
        energy=energy,
        valence=0.5,
        tempo=120.0,
        acousticness=acousticness,
        key=key,
        mode=mode,
    )


def test_taste_embedding_dims():
    tracks = as_audio_tracks(demo_spotify_tracks())
    emb = build_taste_embedding(tracks)
    assert emb["dims"] == ["danceability", "energy", "valence", "tempo", "acousticness"]
    assert emb["track_count"] == len(tracks)
    assert len(emb["embedding"]) == 5
    assert abs(sum(x * x for x in emb["embedding"]) ** 0.5 - 1.0) < 1e-6


def test_taste_twin_seeds_ranked():
    result = suggest_playlist_seeds(as_audio_tracks(demo_spotify_tracks()), top_k=2)
    assert len(result["seeds"]) == 2
    assert result["seeds"][0]["similarity"] >= result["seeds"][1]["similarity"]
    assert "taste_embedding" in result


def test_parse_mood_hype():
    parsed = parse_mood("hype workout party")
    assert parsed["targets"]["energy"] >= 0.8
    assert parsed["curve"] == "ramp_up"
    assert "hype" in parsed["matched_keywords"] or "workout" in parsed["matched_keywords"]


def test_mood_to_mix_returns_tracks():
    result = mood_to_mix("chill evening wind down", top_k=5)
    assert result["curve"] == "chill_down"
    assert len(result["tracks"]) == 5
    assert "camelot" in result["tracks"][0]
    assert len(result["curve_points"]) == 5


def test_gap_filler_finds_alternates():
    result = suggest_alternates(title="Stay", artist="The Kid LAROI", top_k=3)
    assert result["provider"] == "HeuristicAlternateProvider"
    assert len(result["alternates"]) >= 1
    assert result["alternates"][0]["confidence"] >= 0.45


def test_heuristic_provider_skips_exact_isrc():
    query = TrackRef(
        id="q",
        title="Blinding Lights",
        artist="The Weeknd",
        platform="q",
        isrc="USUG11904206",
    )
    catalog = [
        TrackRef(
            id="a",
            title="Blinding Lights",
            artist="The Weeknd",
            platform="apple",
            isrc="USUG11904206",
        ),
        TrackRef(
            id="b",
            title="Blinding Lights Live",
            artist="The Weeknd",
            platform="apple",
            isrc="OTHER",
        ),
    ]
    alts = HeuristicAlternateProvider().suggest(query, catalog, top_k=3)
    ids = {a["id"] for a in alts}
    assert "a" not in ids
    assert "b" in ids


def test_dj_coach_detects_energy_cliff():
    tracks = [_track(0, energy=0.9, key=0), _track(1, energy=0.2, key=0)]
    result = critique_mix(tracks, propose_reorder=False)
    types = {i["type"] for i in result["issues"]}
    assert "energy_cliff" in types
    assert result["score"] < 100


def test_dj_coach_reorder_proposal():
    tracks = [_track(i, energy=0.3 + i * 0.15, key=i % 12) for i in range(5)]
    result = critique_mix(tracks, propose_reorder=True, curve=FlowCurve.RAMP_UP)
    assert result["reorder_proposal"] is not None
    assert len(result["reorder_proposal"]["order"]) == 5


def test_lyric_safe_blocks_explicit_album():
    tracks = [
        {"id": "1", "title": "Stay", "artist": "Artist", "album": "F*CK LOVE 3"},
        {"id": "2", "title": "Heat Waves", "artist": "Glass Animals", "album": "Dreamland"},
    ]
    result = filter_lyric_safe(tracks, policy="family")
    assert result["summary"]["blocked"] >= 1
    blocked_ids = {t["id"] for t in result["blocked"]}
    assert "1" in blocked_ids
    assert "2" not in blocked_ids


def test_classify_track_explicit_flag():
    c = classify_track("Song", "Artist", explicit_flag=True)
    assert c["explicit"] is True
    assert c["family_ok"] is False


def test_lyric_safe_focus_policy():
    tracks = [
        {"title": "Club Remix Party", "artist": "DJ X", "album": "Hits"},
        {"title": "Quiet Study", "artist": "Calm", "album": "Focus"},
    ]
    result = filter_lyric_safe(tracks, policy="focus")
    assert result["summary"]["allowed"] >= 1
    assert result["summary"]["blocked"] >= 1


def test_weekly_digest_shape():
    digest = build_weekly_digest(week_label="Week of test")
    assert digest["week_label"] == "Week of test"
    assert len(digest["mismatches_fixed"]) >= 1
    assert "tracks" in digest["fresh_playlist"]
    assert digest["why_blurb"]
    assert "cron" in digest["cron_hint"].lower()

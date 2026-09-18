from app.services.recommender import (
    AudioTrack,
    FlowCurve,
    harmonic_flow_sort,
    mix_recommendations,
    recommend_similar,
    taste_profile,
)


def _track(i, energy, tempo=120.0, key=0, mode=1):
    return AudioTrack(
        id=str(i),
        title=f"Track {i}",
        artist="Artist",
        danceability=0.5,
        energy=energy,
        valence=0.5,
        tempo=tempo,
        acousticness=0.2,
        key=key,
        mode=mode,
    )


def test_cosine_recommender_ranks_similar():
    seed = _track(0, 0.9, tempo=170)
    catalog = [_track(1, 0.85, tempo=168), _track(2, 0.1, tempo=70), _track(3, 0.8, tempo=165)]
    results = recommend_similar(seed, catalog, top_k=2)
    assert len(results) == 2
    assert results[0][0].id in {"1", "3"}
    assert results[0][1] >= results[1][1]


def test_harmonic_flow_ramp_up_increases_energy():
    tracks = [_track(i, e) for i, e in enumerate([0.9, 0.2, 0.5, 0.7, 0.35])]
    ordered = harmonic_flow_sort(tracks, curve=FlowCurve.RAMP_UP)
    energies = [t.energy for t in ordered]
    assert energies[0] <= energies[-1]


def test_taste_profile_keys():
    tracks = [_track(1, 0.5), _track(2, 0.7)]
    profile = taste_profile(tracks)
    assert set(profile.keys()) == {"danceability", "energy", "valence", "tempo", "acousticness"}
    assert 0.5 <= profile["energy"] <= 0.7


def test_mix_recommendations_returns_flowed_tracks():
    seeds = [_track(0, 0.7, key=0, mode=1)]
    catalog = [_track(i, 0.4 + i * 0.1, key=i % 12, mode=1) for i in range(1, 8)]
    result = mix_recommendations(seeds, catalog, top_k=5, curve=FlowCurve.PEAK_ENERGY)
    assert result["curve"] == "peak_energy"
    assert len(result["tracks"]) == 5
    assert "seed_profile" in result

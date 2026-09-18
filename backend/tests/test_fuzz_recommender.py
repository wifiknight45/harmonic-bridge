"""Hypothesis fuzz tests for recommender feature vectors / Camelot / cosine."""

from __future__ import annotations

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.services.recommender import (
    FEATURE_KEYS,
    TEMPO_MAX,
    AudioTrack,
    FlowCurve,
    build_matrix,
    harmonic_flow_sort,
    mix_recommendations,
    recommend_similar,
    taste_profile,
    _camelot_neighbors,
)


SETTINGS = settings(
    max_examples=60,
    deadline=800,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)

feat = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
tempo_st = st.floats(min_value=0.0, max_value=300.0, allow_nan=False, allow_infinity=False)
key_st = st.one_of(st.none(), st.integers(min_value=-2, max_value=14))
mode_st = st.one_of(st.none(), st.integers(min_value=-1, max_value=2))


@st.composite
def audio_track(draw, tid: str | None = None):
    i = draw(st.integers(min_value=0, max_value=10_000))
    return AudioTrack(
        id=tid if tid is not None else f"t{i}-{draw(st.integers(0, 9999))}",
        title=draw(st.text(max_size=20)),
        artist=draw(st.text(max_size=20)),
        danceability=draw(feat),
        energy=draw(feat),
        valence=draw(feat),
        tempo=draw(tempo_st),
        acousticness=draw(feat),
        key=draw(key_st),
        mode=draw(mode_st),
    )


@SETTINGS
@given(track=audio_track())
def test_feature_vector_shape_and_bounds(track: AudioTrack):
    vec = track.feature_vector()
    assert vec.shape == (len(FEATURE_KEYS),)
    assert all(0.0 <= float(x) <= 1.0 for x in vec)
    # tempo normalized by TEMPO_MAX with clamp
    expected_tempo = min(max(track.tempo, 0.0), TEMPO_MAX) / TEMPO_MAX
    assert abs(float(vec[3]) - expected_tempo) < 1e-9


@SETTINGS
@given(track=audio_track())
def test_camelot_none_or_valid_code(track: AudioTrack):
    code = track.camelot()
    if code is None:
        return
    assert len(code) >= 2
    assert code[-1] in ("A", "B")
    num = int(code[:-1])
    assert 1 <= num <= 12


@SETTINGS
@given(num=st.integers(1, 12), letter=st.sampled_from(["A", "B"]))
def test_camelot_neighbors_include_self(num: int, letter: str):
    code = f"{num}{letter}"
    neighbors = _camelot_neighbors(code)
    assert code in neighbors
    assert len(neighbors) == 4
    for n in neighbors:
        assert n[-1] in ("A", "B")
        assert 1 <= int(n[:-1]) <= 12


@SETTINGS
@given(tracks=st.lists(audio_track(), min_size=0, max_size=12))
def test_build_matrix_and_taste_profile(tracks):
    # Ensure unique ids for downstream APIs
    uniq = []
    seen = set()
    for i, t in enumerate(tracks):
        tid = f"u{i}"
        if tid in seen:
            continue
        seen.add(tid)
        uniq.append(
            AudioTrack(
                id=tid,
                title=t.title,
                artist=t.artist,
                danceability=t.danceability,
                energy=t.energy,
                valence=t.valence,
                tempo=t.tempo,
                acousticness=t.acousticness,
                key=t.key,
                mode=t.mode,
            )
        )
    mat = build_matrix(uniq)
    assert mat.shape == (len(uniq), len(FEATURE_KEYS))
    profile = taste_profile(uniq)
    assert set(profile.keys()) == set(FEATURE_KEYS)
    for v in profile.values():
        assert isinstance(v, float)


@SETTINGS
@given(
    seed=audio_track(),
    catalog=st.lists(audio_track(), min_size=0, max_size=15),
    top_k=st.integers(min_value=1, max_value=10),
)
def test_recommend_similar_invariants(seed, catalog, top_k):
    # Deduplicate catalog ids
    fixed = []
    seen = {seed.id}
    for i, t in enumerate(catalog):
        tid = f"c{i}"
        if tid in seen:
            continue
        seen.add(tid)
        fixed.append(
            AudioTrack(
                id=tid,
                title=t.title,
                artist=t.artist,
                danceability=t.danceability,
                energy=t.energy,
                valence=t.valence,
                tempo=t.tempo,
                acousticness=t.acousticness,
                key=t.key,
                mode=t.mode,
            )
        )
    results = recommend_similar(seed, fixed, top_k=top_k)
    assert len(results) <= min(top_k, len(fixed))
    assert all(t.id != seed.id for t, _ in results)
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)
    for _, s in results:
        assert -1.01 <= s <= 1.01  # cosine bound with float slack


@SETTINGS
@given(
    tracks=st.lists(audio_track(), min_size=0, max_size=10),
    curve=st.sampled_from(list(FlowCurve)),
)
def test_harmonic_flow_sort_permutation(tracks, curve):
    fixed = []
    for i, t in enumerate(tracks):
        fixed.append(
            AudioTrack(
                id=f"f{i}",
                title=t.title,
                artist=t.artist,
                danceability=t.danceability,
                energy=t.energy,
                valence=t.valence,
                tempo=t.tempo,
                acousticness=t.acousticness,
                key=t.key,
                mode=t.mode,
            )
        )
    ordered = harmonic_flow_sort(fixed, curve=curve)
    assert len(ordered) == len(fixed)
    assert {t.id for t in ordered} == {t.id for t in fixed}


@SETTINGS
@given(
    n_seeds=st.integers(1, 4),
    n_catalog=st.integers(0, 12),
    top_k=st.integers(1, 8),
    curve=st.sampled_from(list(FlowCurve)),
    data=st.data(),
)
def test_mix_recommendations_structure(n_seeds, n_catalog, top_k, curve, data):
    seeds = [
        data.draw(audio_track(tid=f"seed{i}"))
        for i in range(n_seeds)
    ]
    catalog = [
        data.draw(audio_track(tid=f"cat{i}"))
        for i in range(n_catalog)
    ]
    result = mix_recommendations(seeds, catalog, top_k=top_k, curve=curve)
    assert result["curve"] == curve.value
    assert set(result["seed_profile"].keys()) == set(FEATURE_KEYS)
    assert len(result["tracks"]) <= min(top_k, n_catalog)
    ids = [t["id"] for t in result["tracks"]]
    assert len(ids) == len(set(ids))
    seed_ids = {s.id for s in seeds}
    assert seed_ids.isdisjoint(ids)

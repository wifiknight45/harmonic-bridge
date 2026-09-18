"""Hypothesis fuzz tests for matching_engine normalize / ISRC / fuzzy match."""

from __future__ import annotations

import string

import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

from app.services.matching_engine import (
    MATCH_THRESHOLD,
    TrackRef,
    fuzzy_score,
    match_playlist,
    match_summary,
    match_track,
    _normalize,
)


# Keep fuzz runtime bounded (~60s total across this module)
SETTINGS = settings(
    max_examples=80,
    deadline=500,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)

printable = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "Z"),
        whitelist_characters=" []()-_&'/.",
    ),
    min_size=0,
    max_size=40,
)

isrc_chars = string.ascii_uppercase + string.digits
isrc_st = st.text(alphabet=isrc_chars, min_size=12, max_size=12)


@SETTINGS
@given(text=printable)
def test_normalize_returns_ascii_lowercase_or_empty(text: str):
    out = _normalize(text)
    assert isinstance(out, str)
    assert out == out.lower()
    assert "  " not in out
    # ASCII-only after NFKD strip
    out.encode("ascii")


@SETTINGS
@given(text=printable)
def test_normalize_idempotent(text: str):
    once = _normalize(text)
    assert _normalize(once) == once


@SETTINGS
@given(
    title=printable,
    artist=printable,
    isrc=st.one_of(st.none(), isrc_st, st.text(max_size=20)),
)
def test_match_track_empty_candidates_never_matches(title: str, artist: str, isrc):
    src = TrackRef(id="s", title=title, artist=artist, platform="spotify", isrc=isrc)
    result = match_track(src, [])
    assert result.matched is False
    assert result.method == "none"
    assert result.target is None
    assert 0.0 <= result.score <= 1.0


@SETTINGS
@given(code=isrc_st, title=printable, artist=printable)
def test_isrc_exact_always_wins(code: str, title: str, artist: str):
    src = TrackRef(id="s", title=title, artist=artist, platform="spotify", isrc=code)
    # Different title/artist but same ISRC (case/whitespace variants)
    cand = TrackRef(
        id="t",
        title="totally different",
        artist="nobody",
        platform="apple",
        isrc=f"  {code.lower()}  ",
    )
    distractor = TrackRef(
        id="d",
        title=title,
        artist=artist,
        platform="apple",
        isrc="ZZZZ99999999",
    )
    result = match_track(src, [distractor, cand])
    assert result.matched is True
    assert result.method == "isrc"
    assert result.score == 1.0
    assert result.target is not None and result.target.id == "t"


@SETTINGS
@given(
    title=st.text(alphabet=string.ascii_letters + " ", min_size=3, max_size=25),
    artist=st.text(alphabet=string.ascii_letters + " ", min_size=2, max_size=20),
)
def test_identical_tracks_fuzzy_score_high(title: str, artist: str):
    assume(_normalize(title) and _normalize(artist))
    a = TrackRef(id="1", title=title, artist=artist, platform="spotify")
    b = TrackRef(id="2", title=title, artist=artist, platform="apple")
    score = fuzzy_score(a, b)
    assert score == pytest.approx(1.0)
    result = match_track(a, [b])
    assert result.matched is True
    assert result.method == "fuzzy"
    assert result.score >= MATCH_THRESHOLD


@SETTINGS
@given(
    titles=st.lists(printable, min_size=1, max_size=8),
    artists=st.lists(printable, min_size=1, max_size=8),
)
def test_match_summary_invariants(titles, artists):
    n = min(len(titles), len(artists))
    sources = [
        TrackRef(id=f"s{i}", title=titles[i], artist=artists[i], platform="spotify")
        for i in range(n)
    ]
    catalog = [
        TrackRef(id=f"c{i}", title=titles[i], artist=artists[i], platform="apple")
        for i in range(n)
    ]
    results = match_playlist(sources, catalog)
    summary = match_summary(results)
    assert summary["total"] == n
    assert summary["matched"] + summary["unmatched"] == n
    assert summary["isrc_matches"] + summary["fuzzy_matches"] == summary["matched"]
    assert 0.0 <= summary["match_rate"] <= 1.0


@SETTINGS
@given(
    a_title=printable,
    a_artist=printable,
    b_title=printable,
    b_artist=printable,
)
def test_fuzzy_score_bounded(a_title, a_artist, b_title, b_artist):
    a = TrackRef(id="a", title=a_title, artist=a_artist, platform="spotify")
    b = TrackRef(id="b", title=b_title, artist=b_artist, platform="apple")
    score = fuzzy_score(a, b)
    assert 0.0 <= score <= 1.0

from app.services.matching_engine import TrackRef, match_playlist, match_summary, match_track


def test_isrc_exact_match():
    src = TrackRef(id="1", title="X", artist="Y", platform="spotify", isrc="USUG11904206")
    cand = [
        TrackRef(id="a", title="Other", artist="Z", platform="apple", isrc="USUG11904206"),
        TrackRef(id="b", title="X", artist="Y", platform="apple", isrc="OTHER"),
    ]
    result = match_track(src, cand)
    assert result.matched
    assert result.method == "isrc"
    assert result.target and result.target.id == "a"


def test_fuzzy_title_artist():
    src = TrackRef(id="1", title="Stay", artist="The Kid LAROI & Justin Bieber", platform="spotify")
    cand = [
        TrackRef(id="a", title="Stay", artist="The Kid LAROI", platform="apple"),
    ]
    result = match_track(src, cand)
    assert result.matched
    assert result.method == "fuzzy"
    assert result.score >= 0.85


def test_no_match_below_threshold():
    src = TrackRef(id="1", title="Completely Different Song", artist="Nobody", platform="spotify")
    cand = [TrackRef(id="a", title="Blinding Lights", artist="The Weeknd", platform="apple")]
    result = match_track(src, cand)
    assert not result.matched
    assert result.method == "none"


def test_playlist_summary():
    sources = [
        TrackRef(id="1", title="Blinding Lights", artist="The Weeknd", platform="spotify", isrc="USUG11904206"),
        TrackRef(id="2", title="Unknown Jam", artist="Mystery", platform="spotify"),
    ]
    catalog = [
        TrackRef(id="a", title="Blinding Lights", artist="The Weeknd", platform="apple", isrc="USUG11904206"),
    ]
    results = match_playlist(sources, catalog)
    summary = match_summary(results)
    assert summary["total"] == 2
    assert summary["matched"] == 1
    assert summary["isrc_matches"] == 1

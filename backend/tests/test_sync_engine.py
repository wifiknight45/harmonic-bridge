"""Unit tests for multi-platform ISRC sync engine (mocked adapters, no HTTP)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.services.sync_engine import run_sync_pipeline


@pytest.mark.asyncio
async def test_run_sync_pipeline_spotify_matches_by_isrc():
    source_tracks = [
        {"title": "Blinding Lights", "artist": "The Weeknd", "isrc": "USUG11904206"},
        {"title": "No ISRC Song", "artist": "Someone", "isrc": None},
        {"title": "Missing Everywhere", "artist": "Nobody", "isrc": "XXNOMATCH0001"},
    ]

    async def fake_search(self, isrc: str) -> Optional[Dict[str, Any]]:
        if isrc == "USUG11904206":
            return {
                "platform": "spotify",
                "uri": "spotify:track:abc",
                "title": "Blinding Lights",
                "artist": "The Weeknd",
                "isrc": isrc,
            }
        return None

    with patch(
        "app.services.sync_engine.SpotifyAdapter.search_by_isrc",
        new=fake_search,
    ):
        result = await run_sync_pipeline(
            source_tracks=source_tracks,
            target_platform="spotify",
            target_credentials={"access_token": "test-token"},
        )

    assert len(result["matched"]) == 1
    assert result["matched"][0]["uri"] == "spotify:track:abc"
    assert len(result["unmatched"]) == 2
    assert result["success_rate"] == pytest.approx(1 / 3)


@pytest.mark.asyncio
async def test_run_sync_pipeline_apple_music_uses_credentials():
    source_tracks = [
        {"title": "Stay", "artist": "The Kid LAROI", "isrc": "USSM12100501"},
    ]

    mock_search = AsyncMock(
        return_value={
            "platform": "apple_music",
            "id": "123",
            "title": "Stay",
            "artist": "The Kid LAROI",
            "isrc": "USSM12100501",
        }
    )

    with patch("app.services.sync_engine.AppleMusicAdapter") as MockApple:
        instance = MockApple.return_value
        instance.search_by_isrc = mock_search
        result = await run_sync_pipeline(
            source_tracks=source_tracks,
            target_platform="apple_music",
            target_credentials={
                "developer_jwt": "dev-jwt",
                "user_token": "user-token",
                "storefront": "gb",
            },
        )

    MockApple.assert_called_once_with(
        developer_jwt="dev-jwt",
        user_token="user-token",
        storefront="gb",
    )
    mock_search.assert_awaited_once_with("USSM12100501")
    assert len(result["matched"]) == 1
    assert result["unmatched"] == []
    assert result["success_rate"] == 1.0


@pytest.mark.asyncio
async def test_run_sync_pipeline_unsupported_platform():
    with pytest.raises(ValueError, match="Unsupported target platform"):
        await run_sync_pipeline(
            source_tracks=[],
            target_platform="tidal",
            target_credentials={},
        )


@pytest.mark.asyncio
async def test_run_sync_pipeline_empty_sources():
    with patch(
        "app.services.sync_engine.SpotifyAdapter.search_by_isrc",
        new=AsyncMock(return_value=None),
    ):
        result = await run_sync_pipeline(
            source_tracks=[],
            target_platform="spotify",
            target_credentials={"access_token": "x"},
        )
    assert result["matched"] == []
    assert result["unmatched"] == []
    assert result["success_rate"] == 0.0


def test_sync_execute_endpoint_accepts_payload():
    from app.main import create_app

    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/sync/execute",
            json={
                "target_platform": "spotify",
                "target_credentials": {"access_token": "test-token"},
                "tracks": [
                    {
                        "title": "Blinding Lights",
                        "artist": "The Weeknd",
                        "isrc": "USUG11904206",
                    }
                ],
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "processing"
    assert "1 tracks" in body["message"]
    assert "spotify" in body["message"]


def test_playlist_sync_route_still_present():
    from app.main import create_app

    app = create_app()
    paths = set(app.openapi()["paths"])
    assert "/api/v1/playlists/sync" in paths
    assert "/api/v1/sync/execute" in paths

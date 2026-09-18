"""Apple Music MusicKit client with real ES256 developer tokens."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import jwt

from app.core.config import Settings, get_settings
from app.services.demo_data import DEMO_PLAYLISTS, demo_apple_tracks
from app.services.matching_engine import TrackRef
from app.services.recommender import AudioTrack

MUSIC_KIT_BASE = "https://api.music.apple.com/v1"
# Apple allows developer tokens up to 6 months (~180 days)
MAX_TOKEN_SECONDS = 180 * 24 * 60 * 60


class AppleMusicService:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._cached_token: Optional[str] = None
        self._cached_exp: float = 0.0

    @property
    def configured(self) -> bool:
        return self.settings.apple_configured

    @property
    def demo(self) -> bool:
        return self.settings.use_demo_mode or not self.configured

    def generate_developer_token(self, lifetime_seconds: int = MAX_TOKEN_SECONDS) -> str:
        """
        Create an ES256 (ECDSA P-256) MusicKit developer token.
        Lifetime is capped at 180 days per Apple docs.
        """
        if not self.configured:
            raise RuntimeError("Apple Music credentials are not configured")

        lifetime_seconds = min(lifetime_seconds, MAX_TOKEN_SECONDS)
        key_path = Path(self.settings.apple_private_key_path)
        private_key = key_path.read_text(encoding="utf-8")

        now = int(time.time())
        headers = {
            "alg": "ES256",
            "kid": self.settings.apple_developer_key_id,
        }
        payload = {
            "iss": self.settings.apple_team_id,
            "iat": now,
            "exp": now + lifetime_seconds,
        }
        token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
        # PyJWT may return str already
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        self._cached_token = token
        self._cached_exp = now + lifetime_seconds - 60
        return token

    def get_developer_token(self) -> str:
        if self._cached_token and time.time() < self._cached_exp:
            return self._cached_token
        return self.generate_developer_token()

    def auth_status(self) -> Dict[str, Any]:
        if self.demo:
            return {
                "demo": True,
                "connected": True,
                "message": "Demo mode — Apple Music is simulated. Drop in your .p8 + Team ID to go live.",
            }
        try:
            token = self.get_developer_token()
            return {
                "demo": False,
                "connected": True,
                "developer_token_ready": bool(token),
                "message": "Developer token ready. Pass a MusicKit user token for library writes.",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "demo": False,
                "connected": False,
                "error": str(exc),
            }

    def _headers(self, user_token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.get_developer_token()}",
            "Content-Type": "application/json",
        }
        if user_token:
            headers["Music-User-Token"] = user_token
        return headers

    async def search_by_isrc(
        self, isrc_code: str, storefront: str = "us"
    ) -> Optional[Dict[str, Any]]:
        """Look up a song by ISRC via MusicKit catalog."""
        if self.demo:
            for t in demo_apple_tracks():
                if t.get("isrc") and t["isrc"].upper() == isrc_code.upper():
                    return t
            return None

        url = f"{MUSIC_KIT_BASE}/catalog/{storefront}/songs"
        params = {"filter[isrc]": isrc_code}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers(), params=params)
            resp.raise_for_status()
            data = resp.json().get("data") or []
            if not data:
                return None
            song = data[0]
            attrs = song.get("attributes") or {}
            return {
                "id": song.get("id"),
                "title": attrs.get("name"),
                "artist": attrs.get("artistName"),
                "album": attrs.get("albumName"),
                "isrc": isrc_code,
                "duration_ms": attrs.get("durationInMillis"),
            }

    async def search_catalog(
        self, term: str, storefront: str = "us", limit: int = 10
    ) -> List[Dict[str, Any]]:
        if self.demo:
            term_l = term.lower()
            return [
                t
                for t in demo_apple_tracks()
                if term_l in t["title"].lower() or term_l in t["artist"].lower()
            ][:limit]

        url = f"{MUSIC_KIT_BASE}/catalog/{storefront}/search"
        params = {"term": term, "types": "songs", "limit": limit}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers(), params=params)
            resp.raise_for_status()
            songs = (
                resp.json().get("results", {}).get("songs", {}).get("data") or []
            )
            out: List[Dict[str, Any]] = []
            for song in songs:
                attrs = song.get("attributes") or {}
                out.append(
                    {
                        "id": song.get("id"),
                        "title": attrs.get("name"),
                        "artist": attrs.get("artistName"),
                        "album": attrs.get("albumName"),
                        "isrc": attrs.get("isrc"),
                        "duration_ms": attrs.get("durationInMillis"),
                    }
                )
            return out

    async def create_playlist(
        self,
        user_token: str,
        name: str,
        track_ids: List[str],
        description: str = "Made with harmonic-bridge",
    ) -> Dict[str, Any]:
        """Create a library playlist and add songs (requires Music-User-Token)."""
        if self.demo:
            return {
                "demo": True,
                "id": "demo-am-playlist",
                "name": name,
                "track_ids": track_ids,
                "message": f"Demo playlist '{name}' with {len(track_ids)} tracks ready to vibe.",
            }

        payload = {
            "attributes": {"name": name, "description": description},
            "relationships": {
                "tracks": {
                    "data": [{"id": tid, "type": "songs"} for tid in track_ids]
                }
            },
        }
        url = f"{MUSIC_KIT_BASE}/me/library/playlists"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url, headers=self._headers(user_token=user_token), json=payload
            )
            resp.raise_for_status()
            data = resp.json().get("data") or [{}]
            playlist = data[0]
            return {
                "demo": False,
                "id": playlist.get("id"),
                "name": name,
                "track_ids": track_ids,
            }

    def list_playlists(self) -> List[Dict[str, Any]]:
        if self.demo:
            return [p for p in DEMO_PLAYLISTS if p["platform"] == "apple"]
        # Without user token we only expose demo/catalog helpers
        return [p for p in DEMO_PLAYLISTS if p["platform"] == "apple"]

    def catalog_tracks(self) -> List[Dict[str, Any]]:
        return demo_apple_tracks() if self.demo else demo_apple_tracks()

    def to_track_refs(self, rows: List[Dict[str, Any]]) -> List[TrackRef]:
        return [
            TrackRef(
                id=r["id"],
                title=r["title"],
                artist=r["artist"],
                platform="apple",
                isrc=r.get("isrc"),
                album=r.get("album"),
            )
            for r in rows
        ]

    def to_audio_tracks(self, rows: List[Dict[str, Any]]) -> List[AudioTrack]:
        return [
            AudioTrack(
                id=r["id"],
                title=r["title"],
                artist=r["artist"],
                danceability=float(r.get("danceability") or 0.5),
                energy=float(r.get("energy") or 0.5),
                valence=float(r.get("valence") or 0.5),
                tempo=float(r.get("tempo") or 120.0),
                acousticness=float(r.get("acousticness") or 0.2),
                key=r.get("key"),
                mode=r.get("mode"),
                extras={"platform": "apple", "isrc": r.get("isrc")},
            )
            for r in rows
        ]


def get_apple_music_service() -> AppleMusicService:
    return AppleMusicService()

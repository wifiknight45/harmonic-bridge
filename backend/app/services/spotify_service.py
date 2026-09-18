"""Spotify Web API wrapper via spotipy, with demo fallback."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.config import Settings, get_settings
from app.services.demo_data import DEMO_PLAYLISTS, demo_spotify_tracks
from app.services.matching_engine import TrackRef
from app.services.recommender import AudioTrack


class SpotifyService:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._client = None
        self._oauth = None

    @property
    def configured(self) -> bool:
        return self.settings.spotify_configured

    @property
    def demo(self) -> bool:
        return self.settings.use_demo_mode or not self.configured

    def _ensure_oauth(self):
        if self._oauth is not None:
            return self._oauth
        if not self.configured:
            return None
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth

        self._oauth = SpotifyOAuth(
            client_id=self.settings.spotipy_client_id,
            client_secret=self.settings.spotipy_client_secret,
            redirect_uri=self.settings.spotipy_redirect_uri,
            scope=" ".join(
                [
                    "user-read-email",
                    "playlist-read-private",
                    "playlist-modify-public",
                    "playlist-modify-private",
                    "user-library-read",
                ]
            ),
            cache_path=None,
            open_browser=False,
        )
        return self._oauth

    def auth_url(self, state: str = "harmonic") -> Dict[str, Any]:
        if self.demo:
            return {
                "demo": True,
                "authorize_url": None,
                "message": "Demo mode — connect is simulated. Add Spotify credentials to go live.",
            }
        oauth = self._ensure_oauth()
        assert oauth is not None
        return {"demo": False, "authorize_url": oauth.get_authorize_url(state=state)}

    def exchange_code(self, code: str) -> Dict[str, Any]:
        if self.demo:
            return {
                "demo": True,
                "access_token": "demo-spotify-token",
                "refresh_token": None,
                "display_name": "Demo Spotify Listener",
            }
        oauth = self._ensure_oauth()
        assert oauth is not None
        token_info = oauth.get_access_token(code, as_dict=True, check_cache=False)
        client = self._client_from_token(token_info["access_token"])
        me = client.current_user()
        return {
            "demo": False,
            "access_token": token_info.get("access_token"),
            "refresh_token": token_info.get("refresh_token"),
            "display_name": me.get("display_name") or me.get("id"),
            "external_id": me.get("id"),
        }

    def _client_from_token(self, access_token: str):
        import spotipy

        return spotipy.Spotify(auth=access_token)

    def list_playlists(self, access_token: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.demo or not access_token:
            return [p for p in DEMO_PLAYLISTS if p["platform"] == "spotify"]
        client = self._client_from_token(access_token)
        results = client.current_user_playlists(limit=50)
        items = []
        for pl in results.get("items", []):
            items.append(
                {
                    "id": pl["id"],
                    "name": pl["name"],
                    "platform": "spotify",
                    "track_count": pl.get("tracks", {}).get("total", 0),
                    "description": pl.get("description") or "",
                }
            )
        return items

    def playlist_tracks(
        self, playlist_id: str, access_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if self.demo or not access_token:
            return demo_spotify_tracks()
        client = self._client_from_token(access_token)
        results = client.playlist_items(playlist_id, additional_types=("track",))
        tracks: List[Dict[str, Any]] = []
        for item in results.get("items", []):
            t = item.get("track") or {}
            if not t or t.get("is_local"):
                continue
            external = t.get("external_ids") or {}
            artists = ", ".join(a["name"] for a in t.get("artists", []))
            tracks.append(
                {
                    "id": t["id"],
                    "title": t.get("name", ""),
                    "artist": artists,
                    "album": (t.get("album") or {}).get("name"),
                    "isrc": external.get("isrc"),
                    "duration_ms": t.get("duration_ms"),
                }
            )
        # Enrich with audio features in batches
        ids = [t["id"] for t in tracks if t.get("id")]
        features_by_id: Dict[str, Dict[str, Any]] = {}
        for i in range(0, len(ids), 100):
            batch = ids[i : i + 100]
            feats = client.audio_features(batch) or []
            for f in feats:
                if f and f.get("id"):
                    features_by_id[f["id"]] = f
        for t in tracks:
            f = features_by_id.get(t["id"], {})
            t.update(
                {
                    "danceability": f.get("danceability"),
                    "energy": f.get("energy"),
                    "valence": f.get("valence"),
                    "tempo": f.get("tempo"),
                    "acousticness": f.get("acousticness"),
                    "key": f.get("key"),
                    "mode": f.get("mode"),
                }
            )
        return tracks

    def audio_features(
        self, track_ids: List[str], access_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if self.demo or not access_token:
            by_id = {t["id"]: t for t in demo_spotify_tracks()}
            return [by_id[i] for i in track_ids if i in by_id]
        client = self._client_from_token(access_token)
        feats = client.audio_features(track_ids) or []
        return [f for f in feats if f]

    def to_track_refs(self, rows: List[Dict[str, Any]]) -> List[TrackRef]:
        return [
            TrackRef(
                id=r["id"],
                title=r["title"],
                artist=r["artist"],
                platform="spotify",
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
                extras={"platform": "spotify", "isrc": r.get("isrc")},
            )
            for r in rows
        ]


def get_spotify_service() -> SpotifyService:
    return SpotifyService()

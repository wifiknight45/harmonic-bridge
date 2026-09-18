import httpx
from typing import Optional, Dict, Any, List

class BaseMusicAdapter:
    async def search_by_isrc(self, isrc: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

class SpotifyAdapter(BaseMusicAdapter):
    def __init__(self, access_token: str):
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def search_by_isrc(self, isrc: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://api.spotify.com/v1/search",
                headers=self.headers,
                params={"q": f"isrc:{isrc}", "type": "track", "limit": 1}
            )
            if res.status_code == 200:
                tracks = res.json().get("tracks", {}).get("items", [])
                if tracks:
                    return {
                        "platform": "spotify",
                        "uri": tracks[0]["uri"],
                        "title": tracks[0]["name"],
                        "artist": tracks[0]["artists"][0]["name"],
                        "isrc": isrc
                    }
            return None

class LastFMAdapter:
    def __init__(self, api_key: str, session_key: Optional[str] = None):
        self.api_key = api_key
        self.session_key = session_key
        self.base_url = "https://ws.audioscrobbler.com/2.0/"

    async def get_recent_scrobbles(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        params = {
            "method": "user.getrecenttracks",
            "user": username,
            "api_key": self.api_key,
            "format": "json",
            "limit": limit
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(self.base_url, params=params)
            if res.status_code == 200:
                return res.json().get("recenttracks", {}).get("track", [])
            return []

class AppleMusicAdapter(BaseMusicAdapter):
    def __init__(self, developer_jwt: str, user_token: str, storefront: str = "us"):
        self.headers = {
            "Authorization": f"Bearer {developer_jwt}",
            "Music-User-Token": user_token
        }
        self.storefront = storefront

    async def search_by_isrc(self, isrc: str) -> Optional[Dict[str, Any]]:
        url = f"https://api.music.apple.com/v1/catalog/{self.storefront}/songs"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers, params={"filter[isrc]": isrc})
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data:
                    song = data[0]
                    return {
                        "platform": "apple_music",
                        "id": song["id"],
                        "title": song["attributes"]["name"],
                        "artist": song["attributes"]["artistName"],
                        "isrc": isrc
                    }
            return None

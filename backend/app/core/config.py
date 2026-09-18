"""Application settings loaded from environment / .env."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "harmonic-bridge"
    debug: bool = True
    secret_key: str = "dev-secret-change-me"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = "sqlite+aiosqlite:///./harmonic_bridge.db"

    spotipy_client_id: str = ""
    spotipy_client_secret: str = ""
    spotipy_redirect_uri: str = "http://localhost:8000/api/v1/auth/spotify/callback"

    apple_developer_key_id: str = ""
    apple_team_id: str = ""
    apple_private_key_path: str = "./AuthKey.p8"
    apple_music_user_token: str = ""

    demo_mode: str = "auto"  # auto | true | false

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _keep_string(cls, v: object) -> object:
        return v

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def spotify_configured(self) -> bool:
        return bool(self.spotipy_client_id and self.spotipy_client_secret)

    @property
    def apple_configured(self) -> bool:
        return bool(
            self.apple_developer_key_id
            and self.apple_team_id
            and self.apple_private_key_path
        )

    @property
    def use_demo_mode(self) -> bool:
        if self.demo_mode.lower() == "true":
            return True
        if self.demo_mode.lower() == "false":
            return False
        # auto
        return not (self.spotify_configured or self.apple_configured)


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""harmonic-bridge FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="harmonic-bridge",
        description=(
            "Sync your music library across Spotify & Apple Music, "
            "then generate dope harmonic-flow playlists in the browser."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list + [
            "https://wifiknight45.github.io",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "app": settings.app_name,
            "demo_mode": settings.use_demo_mode,
        }

    @app.get("/")
    async def root():
        return {
            "name": "harmonic-bridge",
            "docs": "/docs",
            "pages": "https://wifiknight45.github.io/harmonic-bridge/",
            "message": "Sync your library. Generate playlists that slap.",
        }

    return app


app = create_app()

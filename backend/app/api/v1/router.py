from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, playlists, recommend, sync_engine

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(playlists.router)
api_router.include_router(recommend.router)
api_router.include_router(analytics.router)
api_router.include_router(sync_engine.router)

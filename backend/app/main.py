"""harmonic-bridge FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

    @app.get("/", response_class=HTMLResponse)
    async def root():
        pages = "https://wifiknight45.github.io/harmonic-bridge/"
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>harmonic-bridge API</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{
      margin: 0; min-height: 100vh; display: grid; place-items: center;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
      background: #0b0f14; color: #e8eef7;
    }}
    .card {{
      width: min(520px, 92vw); padding: 2rem; border-radius: 1.25rem;
      background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
      box-shadow: 0 20px 60px rgba(0,0,0,0.45);
    }}
    h1 {{ margin: 0 0 0.35rem; font-size: 1.6rem; }}
    p {{ margin: 0.4rem 0; color: rgba(232,238,247,0.7); line-height: 1.45; }}
    .ok {{ color: #1DB954; font-weight: 600; }}
    a.btn {{
      display: inline-block; margin-top: 1.1rem; margin-right: 0.6rem;
      padding: 0.7rem 1.1rem; border-radius: 999px; text-decoration: none;
      font-weight: 600; background: #1DB954; color: #04110a;
    }}
    a.ghost {{
      display: inline-block; margin-top: 1.1rem;
      padding: 0.7rem 1.1rem; border-radius: 999px; text-decoration: none;
      font-weight: 600; border: 1px solid rgba(255,255,255,0.2); color: #e8eef7;
    }}
    code {{ font-size: 0.85rem; color: #9ae6b4; }}
  </style>
</head>
<body>
  <main class="card">
    <p class="ok">API online</p>
    <h1>harmonic-bridge</h1>
    <p>This Render URL is the <strong>backend API</strong> (HTTPS). The full app UI lives on GitHub Pages.</p>
    <p>Demo mode is on — open the site to sync libraries and generate playlists now.</p>
    <p><code>/health</code> · <code>/docs</code> · demo playlists ready</p>
    <a class="btn" href="{pages}">Open the app</a>
    <a class="ghost" href="/docs">API docs</a>
  </main>
</body>
</html>"""


    return app


app = create_app()

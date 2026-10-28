"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag_hive import __version__, api
from rag_hive.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI app with its middleware and routers.

    Args:
        settings: Configuration to use. Defaults to `get_settings()`.

    Returns:
        The configured application.
    """
    settings = settings or get_settings()
    app = FastAPI(
        title="RAG Hive",
        version=__version__,
        docs_url=f"{api.API_PREFIX}/docs",
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=f"{api.API_PREFIX}/docs/oauth2-redirect",
        openapi_url=f"{api.API_PREFIX}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.include_router(api.router)
    return app


app = create_app()

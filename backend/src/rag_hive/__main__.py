"""Dev entrypoint: `uv run python -m rag_hive` / `make dev-backend`.

Host, port and reload come from `Settings`, so nothing is hardcoded in the Makefile.
"""

import uvicorn

from rag_hive.config import get_settings


def main() -> None:
    """Serve the FastAPI app with uvicorn using the configured host, port and reload flag."""
    settings = get_settings()
    uvicorn.run(
        "rag_hive.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_reload,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()

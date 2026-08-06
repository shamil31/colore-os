"""Startup diagnostics and environment validation.

Diagnostic only: nothing here changes application behaviour. It exists so
that a container running the wrong code, or missing configuration, is
obvious in the first lines of the log instead of surfacing later as a 404
or a 503.
"""

import logging
import os
import subprocess
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger("colore.startup")

REQUIRED_ENV_VARS = (
    "OPENAI_API_KEY",
    "POSTGRES_HOST",
    "POSTGRES_DB",
    "ALTEGIO_BASE_URL",
)

BACKEND_DIR = Path(__file__).resolve().parents[2]
STATIC_INDEX = BACKEND_DIR / "app" / "static" / "index.html"


def _value(name: str) -> str:
    """Read a setting, falling back to the raw environment."""
    return str(getattr(settings, name, "") or os.getenv(name, "")).strip()


def _git_commit() -> str:
    """Commit baked in at build time, or resolved live outside the container."""
    baked = os.getenv("GIT_COMMIT", "").strip()
    if baked:
        return baked
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(BACKEND_DIR),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
    except Exception:
        return "unknown"


def _ensure_logging() -> None:
    """uvicorn does not attach a root handler, so INFO records would be dropped."""
    if not logger.handlers and not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_runtime_info() -> None:
    _ensure_logging()
    logger.info("--- Coloré OS runtime ---")
    logger.info("  version:        %s", settings.VERSION)
    logger.info("  git commit:     %s", _git_commit())
    logger.info("  build context:  %s", os.getenv("BUILD_CONTEXT", "unknown"))
    logger.info("  app directory:  %s", BACKEND_DIR)
    # Never log the key itself.
    logger.info("  OPENAI_API_KEY: %s", "YES" if _value("OPENAI_API_KEY") else "NO")
    logger.info("  OPENAI_MODEL:   %s", settings.OPENAI_MODEL)


def validate_environment() -> None:
    """Stop with a readable message when required configuration is absent."""
    _ensure_logging()
    missing = [name for name in REQUIRED_ENV_VARS if not _value(name)]
    if not missing:
        return

    logger.error("Coloré OS cannot start: required configuration is missing.")
    for name in missing:
        logger.error("  missing: %s", name)
    logger.error(
        "Set these in the env file used by this deployment "
        "(/opt/colore-os/docker/.env for the container, "
        "backend/.env when running uvicorn directly), then start again."
    )
    # Raising here would be re-raised through Starlette's lifespan and printed
    # as a traceback. Exit immediately so the operator sees only the message.
    for handler in logger.handlers:
        handler.flush()
    os._exit(1)


def verify_ui(app) -> None:
    """Confirm /docs and the /ui mount are actually served by this build."""
    _ensure_logging()
    paths = {getattr(route, "path", "") for route in app.routes}

    if app.docs_url and app.docs_url in paths:
        logger.info("  docs:           %s available", app.docs_url)
    else:
        logger.error("  docs:           %s is NOT registered", app.docs_url or "/docs")

    if "/ui" not in paths:
        logger.error(
            "  ui:             /ui is NOT mounted. This build does not serve the "
            "conversation UI. Check that app.mount(\"/ui\", ...) is present in "
            "app/main.py in the image that was actually built."
        )
        return

    if not STATIC_INDEX.is_file():
        logger.error(
            "  ui:             /ui is mounted but %s is missing. The build context "
            "did not include app/static/ — check .dockerignore and the compose "
            "build context (expected /root/colore-os/backend).",
            STATIC_INDEX,
        )
        return

    logger.info("  ui:             /ui/ available")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.ai import router as ai_router
from app.api.booking import router as booking_router
from app.api.clients import router as clients_router
from app.api.conversations import router as conversations_router
from app.core.config import settings
from app.core.startup import log_runtime_info, validate_environment, verify_ui
from app.db.database import test_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_runtime_info()
    verify_ui(app)
    validate_environment()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
    }


@app.get("/db")
def database_status():
    return {
        "postgres": test_connection()
    }


app.include_router(clients_router)
app.include_router(conversations_router)
app.include_router(ai_router)
app.include_router(booking_router)

# Serves app/static/index.html at /ui/ from the same origin as the API,
# so the browser does not block the UI's requests with CORS.
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")
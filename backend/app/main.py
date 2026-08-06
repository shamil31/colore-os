from fastapi import FastAPI

from app.api.ai import router as ai_router
from app.api.clients import router as clients_router
from app.api.conversations import router as conversations_router
from app.core.config import settings
from app.db.database import test_connection

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
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
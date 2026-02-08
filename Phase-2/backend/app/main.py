from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.tasks import router as tasks_router
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.database.connection import engine
from app.models import user, task  # Import models for Alembic
from app.config import settings
import os

def create_app():
    app = FastAPI(
        title="Todo API",
        description="API for Todo application",
        version="1.0.0"
    )

    # Configure CORS
    # Determine allowed origins; in development, fall back to permissive CORS
    allowed_origins = settings.get_allowed_origins()
    if not allowed_origins and settings.ENVIRONMENT == "development":
        allowed_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, prefix="", tags=["health"])
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
    app.include_router(tasks_router, prefix="/api/v1", tags=["tasks"])

    return app

app = create_app()

@app.on_event("startup")
async def startup_event():
    # Create database tables
    from sqlmodel import SQLModel
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.workouts import router as workout_router
from app.core.config import get_settings, setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    logger.info("Starting F3RVA Workout Service")
    yield
    # Shutdown
    logger.info("Shutting down F3RVA Workout Service")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="API for managing information related to F3RVA workouts",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(
        workout_router,
        prefix="/api/v1",
        tags=["workouts"]
    )

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "F3RVA Workout Service API",
            "version": "0.1.0",
            "docs": "/docs"
        }

    return app


# Create application instance
app = create_app()

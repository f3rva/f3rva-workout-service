"""API endpoints for workout operations."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import DatabaseConfig, DatabaseConnection
from app.models.workout import WorkoutRequest, WorkoutResponse
from app.services.workout_service import WorkoutService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_workout_service() -> WorkoutService:
    """Dependency to get workout service instance."""
    db_config = DatabaseConfig.from_env()
    db_connection = DatabaseConnection(db_config)
    return WorkoutService(db_connection)


@router.get("/health", response_model=dict)
async def health_check(
    workout_service: WorkoutService = Depends(get_workout_service),
) -> dict:
    """Health check endpoint."""
    try:
        db_healthy = await workout_service.health_check()

        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "service": "f3rva-workout-service",
            "database": "connected" if db_healthy else "disconnected",
        }
    except Exception as e:
        logger.exception("Health check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from e


@router.get("/workouts/{year}/{month}/{day}/{url_slug}", response_model=WorkoutResponse)
async def get_workout(
    year: int,
    month: int,
    day: int,
    url_slug: str,
    workout_service: WorkoutService = Depends(get_workout_service)
) -> WorkoutResponse:
    """Get workout data by date and URL slug.
    
    Args:
        year: Year of the workout (2000-9999)
        month: Month of the workout (1-12)
        day: Day of the workout (1-31)
        url_slug: URL slug identifier
        
    Returns:
        WorkoutResponse with workout data
    """
    # Validate date parameters
    if not (2000 <= year <= 9999):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be between 2000 and 9999"
        )

    if not (1 <= month <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12"
        )

    if not (1 <= day <= 31):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Day must be between 1 and 31"
        )

    try:
        # Create date object
        workout_date = date(year, month, day)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {e}"
        )

    try:
        # Retrieve workout data
        workout = await workout_service.get_workout_by_date_and_slug(
            workout_date, url_slug
        )

        if workout is None:
            return WorkoutResponse(
                success=False,
                message=f"No workout found for {workout_date} with slug '{url_slug}'",
                data=None
            )

        return WorkoutResponse(
            success=True,
            message="Workout data retrieved successfully",
            data=workout
        )

    except Exception as e:
        logger.error(f"Error retrieving workout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/workouts/search", response_model=WorkoutResponse)
async def search_workout(
    request: WorkoutRequest,
    workout_service: WorkoutService = Depends(get_workout_service)
) -> WorkoutResponse:
    """Search for workout data using request body.
    
    Alternative endpoint that accepts workout parameters in request body.
    
    Args:
        request: WorkoutRequest with search parameters
        
    Returns:
        WorkoutResponse with workout data
    """
    try:
        # Create date object
        workout_date = date(request.year, request.month, request.day)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {e}"
        )

    try:
        # Retrieve workout data
        workout = await workout_service.get_workout_by_date_and_slug(
            workout_date, request.url_slug
        )

        if workout is None:
            return WorkoutResponse(
                success=False,
                message=f"No workout found for {workout_date} with slug '{request.url_slug}'",
                data=None
            )

        return WorkoutResponse(
            success=True,
            message="Workout data retrieved successfully",
            data=workout
        )

    except Exception as e:
        logger.error(f"Error retrieving workout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

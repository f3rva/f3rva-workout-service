"""Integration tests for the workout API endpoints."""

from datetime import date
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestWorkoutAPI:
    """Integration tests for workout API."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "F3RVA Workout Service API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"

    @patch("app.services.workout_service.WorkoutService.health_check")
    def test_health_check_healthy(self, mock_health_check, client):
        """Test health check endpoint when healthy."""
        mock_health_check.return_value = True

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "f3rva-workout-service"
        assert data["database"] == "connected"

    @patch("app.services.workout_service.WorkoutService.health_check")
    def test_health_check_unhealthy(self, mock_health_check, client):
        """Test health check endpoint when unhealthy."""
        mock_health_check.return_value = False

        response = client.get("/api/v1/health")

        assert response.status_code == 200  # Still returns 200 but with unhealthy status
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"

    @patch("app.services.workout_service.WorkoutService.health_check")
    def test_health_check_exception(self, mock_health_check, client):
        """Test health check endpoint with exception."""
        mock_health_check.side_effect = Exception("Database error")

        response = client.get("/api/v1/health")

        assert response.status_code == 503
        data = response.json()
        assert data["detail"] == "Service unavailable"

    @patch("app.services.workout_service.WorkoutService.get_workout_by_date_and_slug")
    def test_get_workout_success(self, mock_get_workout, client):
        """Test successful workout retrieval."""
        from app.models.workout import AOSModel, PAXModel, QICModel, WorkoutModel

        # Mock workout data
        mock_workout = WorkoutModel(
            workout_date=date(2024, 1, 15),
            qic=QICModel(name="Ripken", f3_name="Cal Ripken Jr."),
            pax=[PAXModel(name="Donatello"), PAXModel(name="Leonardo")],
            aos=[AOSModel(name="Warm-Up"), AOSModel(name="The Thang")],
            url_slug="test-workout"
        )
        mock_get_workout.return_value = mock_workout

        response = client.get("/api/v1/workouts/2024/1/15/test-workout")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Workout data retrieved successfully"
        assert data["data"] is not None
        assert data["data"]["workout_date"] == "2024-01-15"
        assert data["data"]["qic"]["name"] == "Ripken"
        assert len(data["data"]["pax"]) == 2
        assert len(data["data"]["aos"]) == 2

    @patch("app.services.workout_service.WorkoutService.get_workout_by_date_and_slug")
    def test_get_workout_not_found(self, mock_get_workout, client):
        """Test workout not found."""
        mock_get_workout.return_value = None

        response = client.get("/api/v1/workouts/2024/1/15/nonexistent-workout")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No workout found" in data["message"]
        assert data["data"] is None

    def test_get_workout_invalid_year(self, client):
        """Test invalid year parameter."""
        response = client.get("/api/v1/workouts/1999/1/15/test-workout")

        assert response.status_code == 400
        data = response.json()
        assert "Year must be between 2000 and 9999" in data["detail"]

    def test_get_workout_invalid_month(self, client):
        """Test invalid month parameter."""
        response = client.get("/api/v1/workouts/2024/13/15/test-workout")

        assert response.status_code == 400
        data = response.json()
        assert "Month must be between 1 and 12" in data["detail"]

    def test_get_workout_invalid_day(self, client):
        """Test invalid day parameter."""
        response = client.get("/api/v1/workouts/2024/1/32/test-workout")

        assert response.status_code == 400
        data = response.json()
        assert "Day must be between 1 and 31" in data["detail"]

    def test_get_workout_invalid_date(self, client):
        """Test invalid date combination."""
        response = client.get("/api/v1/workouts/2024/2/30/test-workout")  # Feb 30th doesn't exist

        assert response.status_code == 400
        data = response.json()
        assert "Invalid date" in data["detail"]

    @patch("app.services.workout_service.WorkoutService.get_workout_by_date_and_slug")
    def test_get_workout_server_error(self, mock_get_workout, client):
        """Test server error during workout retrieval."""
        mock_get_workout.side_effect = Exception("Database connection failed")

        response = client.get("/api/v1/workouts/2024/1/15/test-workout")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Internal server error"

    @patch("app.services.workout_service.WorkoutService.get_workout_by_date_and_slug")
    def test_search_workout_success(self, mock_get_workout, client):
        """Test successful workout search using POST endpoint."""
        from app.models.workout import QICModel, WorkoutModel

        # Mock workout data
        mock_workout = WorkoutModel(
            workout_date=date(2024, 1, 15),
            qic=QICModel(name="Ripken"),
            pax=[],
            aos=[],
            url_slug="test-workout"
        )
        mock_get_workout.return_value = mock_workout

        request_data = {
            "year": 2024,
            "month": 1,
            "day": 15,
            "url_slug": "test-workout"
        }

        response = client.post("/api/v1/workouts/search", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is not None

    def test_search_workout_invalid_request(self, client):
        """Test invalid search workout request."""
        request_data = {
            "year": 1999,  # Invalid year
            "month": 1,
            "day": 15,
            "url_slug": "test-workout"
        }

        response = client.post("/api/v1/workouts/search", json=request_data)

        assert response.status_code == 422  # Pydantic validation error

    def test_search_workout_invalid_date(self, client):
        """Test search workout with invalid date."""
        request_data = {
            "year": 2024,
            "month": 2,
            "day": 30,  # Feb 30th doesn't exist
            "url_slug": "test-workout"
        }

        response = client.post("/api/v1/workouts/search", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid date" in data["detail"]

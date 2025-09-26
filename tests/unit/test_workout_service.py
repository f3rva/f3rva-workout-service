"""Unit tests for workout service."""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.core.database import DatabaseConnection
from app.models.workout import AOSModel, PAXModel, WorkoutModel
from app.services.workout_service import WorkoutService


class TestWorkoutService:
    """Test cases for WorkoutService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = MagicMock(spec=DatabaseConnection)
        self.service = WorkoutService(self.mock_db)

    @pytest.mark.asyncio
    async def test_get_workout_by_date_and_slug_success(self):
        """Test successful workout retrieval."""
        # Mock database responses
        workout_data = {
            "workout_date": date(2024, 1, 15),
            "url_slug": "test-workout",
            "qic_name": "Ripken",
            "qic_f3_name": "Cal Ripken Jr."
        }

        pax_data = [
            {"pax_name": "Donatello", "f3_name": "Donatello TMNT"},
            {"pax_name": "Leonardo", "f3_name": None}
        ]

        aos_data = [
            {"aos_name": "Warm-Up", "description": "Getting loose"},
            {"aos_name": "The Thang", "description": "Main event"}
        ]

        self.mock_db.execute_single.return_value = workout_data
        self.mock_db.execute_query.side_effect = [pax_data, aos_data]

        # Execute the method
        result = await self.service.get_workout_by_date_and_slug(
            date(2024, 1, 15), "test-workout"
        )

        # Verify results
        assert result is not None
        assert isinstance(result, WorkoutModel)
        assert result.workout_date == date(2024, 1, 15)
        assert result.url_slug == "test-workout"
        assert result.qic.name == "Ripken"
        assert result.qic.f3_name == "Cal Ripken Jr."
        assert len(result.pax) == 2
        assert result.pax[0].name == "Donatello"
        assert result.pax[0].f3_name == "Donatello TMNT"
        assert result.pax[1].name == "Leonardo"
        assert result.pax[1].f3_name is None
        assert len(result.aos) == 2
        assert result.aos[0].name == "Warm-Up"
        assert result.aos[1].name == "The Thang"

    @pytest.mark.asyncio
    async def test_get_workout_by_date_and_slug_not_found(self):
        """Test workout not found scenario."""
        self.mock_db.execute_single.return_value = None

        result = await self.service.get_workout_by_date_and_slug(
            date(2024, 1, 15), "nonexistent-workout"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_workout_by_date_and_slug_database_error(self):
        """Test database error handling."""
        self.mock_db.execute_single.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception) as exc_info:
            await self.service.get_workout_by_date_and_slug(
                date(2024, 1, 15), "test-workout"
            )

        assert "Database connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_pax_for_workout(self):
        """Test getting PAX for workout."""
        pax_data = [
            {"pax_name": "Ripken", "f3_name": "Cal Ripken Jr."},
            {"pax_name": "YHC", "f3_name": None}
        ]

        self.mock_db.execute_query.return_value = pax_data

        result = await self.service._get_pax_for_workout(
            date(2024, 1, 15), "test-workout"
        )

        assert len(result) == 2
        assert isinstance(result[0], PAXModel)
        assert result[0].name == "Ripken"
        assert result[0].f3_name == "Cal Ripken Jr."
        assert result[1].name == "YHC"
        assert result[1].f3_name is None

    @pytest.mark.asyncio
    async def test_get_aos_for_workout(self):
        """Test getting AOS for workout."""
        aos_data = [
            {"aos_name": "Warm-Up", "description": "Getting ready"},
            {"aos_name": "Cool Down", "description": None}
        ]

        self.mock_db.execute_query.return_value = aos_data

        result = await self.service._get_aos_for_workout(
            date(2024, 1, 15), "test-workout"
        )

        assert len(result) == 2
        assert isinstance(result[0], AOSModel)
        assert result[0].name == "Warm-Up"
        assert result[0].description == "Getting ready"
        assert result[1].name == "Cool Down"
        assert result[1].description is None

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        self.mock_db.execute_single.return_value = {"status": 1}

        result = await self.service.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure."""
        self.mock_db.execute_single.side_effect = Exception("Connection failed")

        result = await self.service.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_invalid_response(self):
        """Test health check with invalid database response."""
        self.mock_db.execute_single.return_value = {"status": 0}

        result = await self.service.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_no_response(self):
        """Test health check with no database response."""
        self.mock_db.execute_single.return_value = None

        result = await self.service.health_check()

        assert result is False

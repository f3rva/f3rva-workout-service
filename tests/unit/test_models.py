"""Unit tests for workout models."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.models.workout import (
    AOSModel,
    PAXModel,
    QICModel,
    WorkoutModel,
    WorkoutRequest,
    WorkoutResponse,
)


class TestAOSModel:
    """Test cases for AOSModel."""

    def test_aos_model_creation(self):
        """Test creating AOS model with valid data."""
        aos = AOSModel(name="The Thang", description="Main workout activity")

        assert aos.name == "The Thang"
        assert aos.description == "Main workout activity"

    def test_aos_model_without_description(self):
        """Test creating AOS model without description."""
        aos = AOSModel(name="Warm-Up")

        assert aos.name == "Warm-Up"
        assert aos.description is None

    def test_aos_model_invalid_data(self):
        """Test AOS model validation with invalid data."""
        with pytest.raises(ValidationError):
            AOSModel()  # Missing required name field


class TestPAXModel:
    """Test cases for PAXModel."""

    def test_pax_model_creation(self):
        """Test creating PAX model with valid data."""
        pax = PAXModel(name="Ripken", f3_name="Cal Ripken Jr.")

        assert pax.name == "Ripken"
        assert pax.f3_name == "Cal Ripken Jr."

    def test_pax_model_without_f3_name(self):
        """Test creating PAX model without F3 name."""
        pax = PAXModel(name="YHC")

        assert pax.name == "YHC"
        assert pax.f3_name is None


class TestQICModel:
    """Test cases for QICModel."""

    def test_qic_model_creation(self):
        """Test creating QIC model with valid data."""
        qic = QICModel(name="Ripken", f3_name="Cal Ripken Jr.")

        assert qic.name == "Ripken"
        assert qic.f3_name == "Cal Ripken Jr."

    def test_qic_model_without_f3_name(self):
        """Test creating QIC model without F3 name."""
        qic = QICModel(name="YHC")

        assert qic.name == "YHC"
        assert qic.f3_name is None


class TestWorkoutModel:
    """Test cases for WorkoutModel."""

    def test_workout_model_creation(self):
        """Test creating workout model with valid data."""
        qic = QICModel(name="Ripken")
        pax = [PAXModel(name="Donatello"), PAXModel(name="Leonardo")]
        aos = [AOSModel(name="Warm-Up"), AOSModel(name="The Thang")]

        workout = WorkoutModel(
            workout_date=date(2024, 1, 15),
            qic=qic,
            pax=pax,
            aos=aos,
            url_slug="ripken-beatdown-2024-01-15"
        )

        assert workout.workout_date == date(2024, 1, 15)
        assert workout.qic.name == "Ripken"
        assert len(workout.pax) == 2
        assert len(workout.aos) == 2
        assert workout.url_slug == "ripken-beatdown-2024-01-15"

    def test_workout_model_empty_lists(self):
        """Test creating workout model with empty PAX and AOS lists."""
        qic = QICModel(name="Ripken")

        workout = WorkoutModel(
            workout_date=date(2024, 1, 15),
            qic=qic,
            pax=[],
            aos=[],
            url_slug="solo-workout"
        )

        assert len(workout.pax) == 0
        assert len(workout.aos) == 0


class TestWorkoutRequest:
    """Test cases for WorkoutRequest."""

    def test_workout_request_creation(self):
        """Test creating workout request with valid data."""
        request = WorkoutRequest(
            year=2024,
            month=1,
            day=15,
            url_slug="test-workout"
        )

        assert request.year == 2024
        assert request.month == 1
        assert request.day == 15
        assert request.url_slug == "test-workout"

    def test_workout_request_validation(self):
        """Test workout request validation."""
        # Test invalid year
        with pytest.raises(ValidationError):
            WorkoutRequest(year=1999, month=1, day=1, url_slug="test")

        with pytest.raises(ValidationError):
            WorkoutRequest(year=10000, month=1, day=1, url_slug="test")

        # Test invalid month
        with pytest.raises(ValidationError):
            WorkoutRequest(year=2024, month=0, day=1, url_slug="test")

        with pytest.raises(ValidationError):
            WorkoutRequest(year=2024, month=13, day=1, url_slug="test")

        # Test invalid day
        with pytest.raises(ValidationError):
            WorkoutRequest(year=2024, month=1, day=0, url_slug="test")

        with pytest.raises(ValidationError):
            WorkoutRequest(year=2024, month=1, day=32, url_slug="test")


class TestWorkoutResponse:
    """Test cases for WorkoutResponse."""

    def test_workout_response_success(self):
        """Test creating successful workout response."""
        qic = QICModel(name="Ripken")
        workout = WorkoutModel(
            workout_date=date(2024, 1, 15),
            qic=qic,
            pax=[],
            aos=[],
            url_slug="test-workout"
        )

        response = WorkoutResponse(
            success=True,
            message="Workout found successfully",
            data=workout
        )

        assert response.success is True
        assert response.message == "Workout found successfully"
        assert response.data is not None
        assert response.data.workout_date == date(2024, 1, 15)

    def test_workout_response_failure(self):
        """Test creating failure workout response."""
        response = WorkoutResponse(
            success=False,
            message="Workout not found",
            data=None
        )

        assert response.success is False
        assert response.message == "Workout not found"
        assert response.data is None

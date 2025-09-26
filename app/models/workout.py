"""Data models for the workout service."""

from datetime import date

from pydantic import BaseModel, Field


class AOSModel(BaseModel):
    """Area of Service model."""

    name: str = Field(..., description="Name of the AOS")
    description: str | None = Field(None, description="Description of the AOS")


class PAXModel(BaseModel):
    """PAX (participant) model."""

    name: str = Field(..., description="PAX name/handle")
    f3_name: str | None = Field(None, description="Official F3 name")


class QICModel(BaseModel):
    """Q in Charge model."""

    name: str = Field(..., description="QIC name/handle")
    f3_name: str | None = Field(None, description="Official F3 name")


class WorkoutModel(BaseModel):
    """Complete workout model."""

    workout_date: date = Field(..., description="Date of the workout")
    qic: QICModel = Field(..., description="The QIC for this workout")
    pax: list[PAXModel] = Field(..., description="List of PAX who attended")
    aos: list[AOSModel] = Field(..., description="List of AOS covered in the workout")
    url_slug: str = Field(..., description="URL slug identifier for the workout")


class WorkoutRequest(BaseModel):
    """Request model for retrieving workout data."""

    year: int = Field(..., ge=2000, le=9999, description="Year of the workout")
    month: int = Field(..., ge=1, le=12, description="Month of the workout")
    day: int = Field(..., ge=1, le=31, description="Day of the workout")
    url_slug: str = Field(..., description="URL slug identifier")


class WorkoutResponse(BaseModel):
    """Response model for workout data."""

    success: bool = Field(..., description="Whether the request was successful")
    message: str | None = Field(None, description="Response message")
    data: WorkoutModel | None = Field(None, description="Workout data if found")

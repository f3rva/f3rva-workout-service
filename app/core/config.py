"""Application configuration."""

import logging
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    app_name: str = Field(default="F3RVA Workout Service", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Database settings (placeholders)
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=3306, description="Database port")
    db_username: str = Field(default="workout_user", description="Database username")
    db_password: str = Field(default="workout_password", description="Database password")
    db_name: str = Field(default="f3rva_workouts", description="Database name")

    # AWS/Lambda settings
    aws_region: str = Field(default="us-east-1", description="AWS region")
    lambda_timeout: int = Field(default=30, description="Lambda timeout in seconds")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


def setup_logging(level: str | None = None) -> None:
    """Set up application logging."""
    if level is None:
        level = get_settings().log_level

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("pymysql").setLevel(logging.WARNING)

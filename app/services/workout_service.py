"""Workout service for retrieving workout data."""

import logging
from datetime import date

from app.core.database import DatabaseConnection
from app.models.workout import AOSModel, PAXModel, QICModel, WorkoutModel

logger = logging.getLogger(__name__)


class WorkoutService:
    """Service for managing workout data operations."""

    def __init__(self, db_connection: DatabaseConnection) -> None:
        self.db = db_connection

    async def get_workout_by_date_and_slug(
        self, workout_date: date, url_slug: str
    ) -> WorkoutModel | None:
        """Retrieve workout data by date and URL slug.
        
        Args:
            workout_date: The date of the workout
            url_slug: URL slug identifier
            
        Returns:
            WorkoutModel if found, None otherwise
        """
        try:
            # SQL query to get workout data
            # This is a placeholder query - adjust based on your actual database schema
            workout_query = """
                SELECT 
                    w.workout_date,
                    w.url_slug,
                    w.qic_name,
                    w.qic_f3_name
                FROM workouts w
                WHERE w.workout_date = %(workout_date)s 
                AND w.url_slug = %(url_slug)s
                LIMIT 1
            """

            workout_data = self.db.execute_single(
                workout_query,
                {"workout_date": workout_date, "url_slug": url_slug}
            )

            if not workout_data:
                logger.info(f"No workout found for date {workout_date} and slug {url_slug}")
                return None

            # Get PAX for this workout
            pax_list = await self._get_pax_for_workout(workout_date, url_slug)

            # Get AOS for this workout
            aos_list = await self._get_aos_for_workout(workout_date, url_slug)

            # Create QIC model
            qic = QICModel(
                name=workout_data["qic_name"],
                f3_name=workout_data.get("qic_f3_name")
            )

            # Create workout model
            workout = WorkoutModel(
                workout_date=workout_data["workout_date"],
                qic=qic,
                pax=pax_list,
                aos=aos_list,
                url_slug=workout_data["url_slug"]
            )

            logger.info(f"Retrieved workout data for {workout_date} - {url_slug}")
            return workout

        except Exception as e:
            logger.error(f"Error retrieving workout data: {e}")
            raise

    async def _get_pax_for_workout(self, workout_date: date, url_slug: str) -> list[PAXModel]:
        """Get PAX list for a specific workout."""
        # Placeholder query - adjust based on your database schema
        pax_query = """
            SELECT 
                p.pax_name,
                p.f3_name
            FROM workout_pax wp
            JOIN pax p ON wp.pax_id = p.id
            JOIN workouts w ON wp.workout_id = w.id
            WHERE w.workout_date = %(workout_date)s 
            AND w.url_slug = %(url_slug)s
        """

        pax_data = self.db.execute_query(
            pax_query,
            {"workout_date": workout_date, "url_slug": url_slug}
        )

        return [
            PAXModel(name=row["pax_name"], f3_name=row.get("f3_name"))
            for row in pax_data
        ]

    async def _get_aos_for_workout(self, workout_date: date, url_slug: str) -> list[AOSModel]:
        """Get AOS list for a specific workout."""
        # Placeholder query - adjust based on your database schema
        aos_query = """
            SELECT 
                a.aos_name,
                a.description
            FROM workout_aos wa
            JOIN aos a ON wa.aos_id = a.id  
            JOIN workouts w ON wa.workout_id = w.id
            WHERE w.workout_date = %(workout_date)s
            AND w.url_slug = %(url_slug)s
        """

        aos_data = self.db.execute_query(
            aos_query,
            {"workout_date": workout_date, "url_slug": url_slug}
        )

        return [
            AOSModel(name=row["aos_name"], description=row.get("description"))
            for row in aos_data
        ]

    async def health_check(self) -> bool:
        """Perform a health check on the database connection."""
        try:
            result = self.db.execute_single("SELECT 1 as status")
            return result is not None and result.get("status") == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

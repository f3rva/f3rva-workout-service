"""Database configuration and connection utilities."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import pymysql
from pymysql.connections import Connection

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        charset: str = "utf8mb4",
        autocommit: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.charset = charset
        self.autocommit = autocommit

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create database config from environment variables.
        
        This is a placeholder - in production, these would come from
        environment variables or AWS Systems Manager Parameter Store.
        """
        # TODO: Replace with actual environment variable loading
        return cls(
            host="your-mysql-host.rds.amazonaws.com",
            port=3306,
            username="your-db-username",
            password="your-db-password",  # This should be from AWS Secrets Manager
            database="f3rva_workouts",
        )


class DatabaseConnection:
    """Database connection manager."""

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self._connection: Connection | None = None

    def connect(self) -> Connection:
        """Establish database connection."""
        try:
            self._connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                charset=self.config.charset,
                autocommit=self.config.autocommit,
                cursorclass=pymysql.cursors.DictCursor,
            )
            logger.info("Database connection established")
            return self._connection
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    @contextmanager
    def get_connection(self) -> Generator[Connection, None, None]:
        """Context manager for database connections."""
        connection = None
        try:
            connection = self.connect()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            self.disconnect()

    def execute_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchall()

    def execute_single(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Execute a SELECT query and return single result."""
        results = self.execute_query(query, params)
        return results[0] if results else None

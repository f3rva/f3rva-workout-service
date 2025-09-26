"""Unit tests for database configuration and connection."""

from unittest.mock import MagicMock, patch

import pymysql
import pytest

from app.core.database import DatabaseConfig, DatabaseConnection


class TestDatabaseConfig:
    """Test cases for DatabaseConfig."""

    def test_database_config_creation(self):
        """Test creating database configuration."""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            username="test_user",
            password="test_password",
            database="test_db"
        )

        assert config.host == "localhost"
        assert config.port == 3306
        assert config.username == "test_user"
        assert config.password == "test_password"
        assert config.database == "test_db"
        assert config.charset == "utf8mb4"
        assert config.autocommit is True

    def test_database_config_from_env(self):
        """Test creating database config from environment."""
        config = DatabaseConfig.from_env()

        # These are placeholder values from the implementation
        assert config.host == "your-mysql-host.rds.amazonaws.com"
        assert config.port == 3306
        assert config.username == "your-db-username"
        assert config.password == "your-db-password"
        assert config.database == "f3rva_workouts"


class TestDatabaseConnection:
    """Test cases for DatabaseConnection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = DatabaseConfig(
            host="localhost",
            port=3306,
            username="test_user",
            password="test_password",
            database="test_db"
        )
        self.db_connection = DatabaseConnection(self.config)

    @patch("app.core.database.pymysql.connect")
    def test_connect_success(self, mock_connect):
        """Test successful database connection."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        result = self.db_connection.connect()

        assert result == mock_connection
        mock_connect.assert_called_once_with(
            host="localhost",
            port=3306,
            user="test_user",
            password="test_password",
            database="test_db",
            charset="utf8mb4",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    @patch("app.core.database.pymysql.connect")
    def test_connect_failure(self, mock_connect):
        """Test database connection failure."""
        mock_connect.side_effect = Exception("Connection failed")

        with pytest.raises(Exception) as exc_info:
            self.db_connection.connect()

        assert "Connection failed" in str(exc_info.value)

    def test_disconnect(self):
        """Test database disconnection."""
        mock_connection = MagicMock()
        self.db_connection._connection = mock_connection

        self.db_connection.disconnect()

        mock_connection.close.assert_called_once()
        assert self.db_connection._connection is None

    def test_disconnect_no_connection(self):
        """Test disconnection when no connection exists."""
        self.db_connection._connection = None

        # Should not raise exception
        self.db_connection.disconnect()

    @patch.object(DatabaseConnection, "connect")
    @patch.object(DatabaseConnection, "disconnect")
    def test_get_connection_context_manager(self, mock_disconnect, mock_connect):
        """Test database connection context manager."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        with self.db_connection.get_connection() as conn:
            assert conn == mock_connection

        mock_connect.assert_called_once()
        mock_disconnect.assert_called_once()

    @patch.object(DatabaseConnection, "connect")
    @patch.object(DatabaseConnection, "disconnect")
    def test_get_connection_context_manager_exception(self, mock_disconnect, mock_connect):
        """Test database connection context manager with exception."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        with pytest.raises(ValueError):
            with self.db_connection.get_connection() as conn:
                raise ValueError("Test error")

        mock_connect.assert_called_once()
        mock_connection.rollback.assert_called_once()
        mock_disconnect.assert_called_once()

    @patch.object(DatabaseConnection, "get_connection")
    def test_execute_query(self, mock_get_connection):
        """Test executing query and returning results."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_connection

        expected_results = [{"id": 1, "name": "test"}]
        mock_cursor.fetchall.return_value = expected_results

        query = "SELECT * FROM test_table WHERE id = %(id)s"
        params = {"id": 1}

        result = self.db_connection.execute_query(query, params)

        assert result == expected_results
        mock_cursor.execute.assert_called_once_with(query, params)
        mock_cursor.fetchall.assert_called_once()

    @patch.object(DatabaseConnection, "execute_query")
    def test_execute_single(self, mock_execute_query):
        """Test executing query and returning single result."""
        mock_execute_query.return_value = [{"id": 1, "name": "test"}]

        result = self.db_connection.execute_single("SELECT * FROM test")

        assert result == {"id": 1, "name": "test"}

    @patch.object(DatabaseConnection, "execute_query")
    def test_execute_single_no_results(self, mock_execute_query):
        """Test executing query with no results."""
        mock_execute_query.return_value = []

        result = self.db_connection.execute_single("SELECT * FROM test")

        assert result is None

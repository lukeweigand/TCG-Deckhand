"""
Tests for database connection management.
"""
import pytest
import sqlite3
from pathlib import Path
import tempfile
import os

from src.db.connection import get_connection, get_connection_context, verify_connection
from src.db.schema import init_database


@pytest.fixture
def initialized_db():
    """Create and initialize a temporary database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_path = Path(path)
    
    # Initialize the database with schema
    init_database(db_path)
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


def test_get_connection_creates_connection(initialized_db):
    """Test that get_connection returns a valid connection."""
    conn = get_connection(initialized_db)
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_connection_has_foreign_keys_enabled(initialized_db):
    """Test that foreign keys are enabled on connections."""
    conn = get_connection(initialized_db)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys")
    result = cursor.fetchone()[0]
    conn.close()
    
    assert result == 1, "Foreign keys are not enabled"


def test_connection_uses_row_factory(initialized_db):
    """Test that connections return rows as dictionaries."""
    conn = get_connection(initialized_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    # sqlite3.Row allows both index and key access
    assert hasattr(row, 'keys'), "Row factory not set correctly"


def test_connection_context_manager(initialized_db):
    """Test the context manager for database connections."""
    with get_connection_context(initialized_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM cards")
        result = cursor.fetchone()
        assert result is not None
    
    # Connection should be closed after exiting context
    # Trying to use it should raise an error
    with pytest.raises(sqlite3.ProgrammingError):
        cursor.execute("SELECT 1")


def test_connection_context_commits_on_success(initialized_db):
    """Test that context manager commits changes on success."""
    # Insert a test card
    test_card_id = "test-card-123"
    
    with get_connection_context(initialized_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cards (id, name, card_type, rules_text) VALUES (?, ?, ?, ?)",
            (test_card_id, "Test Card", "Creature", "Does nothing")
        )
    
    # Verify the card was committed
    with get_connection_context(initialized_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cards WHERE id = ?", (test_card_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result["name"] == "Test Card"


def test_connection_context_rolls_back_on_error(initialized_db):
    """Test that context manager rolls back changes on error."""
    test_card_id = "test-card-456"
    
    try:
        with get_connection_context(initialized_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cards (id, name, card_type, rules_text) VALUES (?, ?, ?, ?)",
                (test_card_id, "Test Card", "Creature", "Does nothing")
            )
            # Force an error
            raise ValueError("Intentional error")
    except ValueError:
        pass  # Expected error
    
    # Verify the card was NOT committed
    with get_connection_context(initialized_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cards WHERE id = ?", (test_card_id,))
        result = cursor.fetchone()
        assert result is None, "Transaction should have been rolled back"


def test_verify_connection_returns_true_for_valid_db(initialized_db):
    """Test that verify_connection returns True for valid database."""
    assert verify_connection(initialized_db) is True


def test_verify_connection_returns_false_for_invalid_db():
    """Test that verify_connection returns False for non-existent database."""
    fake_path = Path("/nonexistent/path/to/database.db")
    assert verify_connection(fake_path) is False

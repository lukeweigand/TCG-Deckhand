"""
Tests for database schema and initialization.
"""
import pytest
import sqlite3
from pathlib import Path
import tempfile
import os

from src.db.schema import init_database, get_schema, get_schema_version, CURRENT_SCHEMA_VERSION


@pytest.fixture
def temp_db():
    """
    Create a temporary database for testing.
    
    This fixture:
    1. Creates a temporary database file
    2. Yields the path to tests
    3. Cleans up the file after the test
    
    This ensures each test gets a fresh, isolated database.
    """
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close the file descriptor
    db_path = Path(path)
    
    yield db_path
    
    # Cleanup: remove the temporary database
    if db_path.exists():
        db_path.unlink()


def test_database_initialization(temp_db):
    """Test that database initializes without errors."""
    init_database(temp_db)
    assert temp_db.exists()


def test_tables_created(temp_db):
    """Test that all expected tables are created."""
    init_database(temp_db)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Check that all expected tables exist
    expected_tables = ["cards", "decks", "deck_cards", "game_sessions"]
    for table in expected_tables:
        assert table in tables, f"Table '{table}' was not created"


def test_cards_table_structure(temp_db):
    """Test that the cards table has the correct columns."""
    init_database(temp_db)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Get column information
    cursor.execute("PRAGMA table_info(cards)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type
    
    conn.close()
    
    # Check that expected columns exist
    assert "id" in columns
    assert "name" in columns
    assert "card_type" in columns
    assert "stats" in columns
    assert "rules_text" in columns


def test_foreign_keys_enabled(temp_db):
    """Test that foreign key constraints are working."""
    init_database(temp_db)
    
    conn = sqlite3.connect(temp_db)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Try to insert a deck_card without a valid deck (should fail)
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO deck_cards (deck_id, card_id, quantity) VALUES (?, ?, ?)",
            ("nonexistent_deck", "nonexistent_card", 1)
        )
    
    conn.close()


def test_schema_is_valid_sql(temp_db):
    """Test that the schema SQL is valid and executes without errors."""
    conn = sqlite3.connect(temp_db)
    
    try:
        cursor = conn.cursor()
        cursor.executescript(get_schema())
        conn.commit()
        success = True
    except sqlite3.Error:
        success = False
    finally:
        conn.close()
    
    assert success, "Schema SQL contains syntax errors"


def test_schema_version_table_created(temp_db):
    """Test that schema_version table is created during initialization."""
    init_database(temp_db)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None, "schema_version table not created"


def test_initial_schema_version_is_set(temp_db):
    """Test that initial schema version is recorded as version 1."""
    init_database(temp_db)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT version, description FROM schema_version")
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == 1, "Initial version should be 1"
    assert "initial" in result[1].lower(), "Description should mention initial schema"


def test_get_schema_version_returns_current_version(temp_db):
    """Test that get_schema_version returns the correct version."""
    init_database(temp_db)
    
    version = get_schema_version(temp_db)
    assert version == CURRENT_SCHEMA_VERSION


def test_get_schema_version_returns_zero_for_nonexistent_db():
    """Test that get_schema_version returns 0 for non-existent database."""
    fake_path = Path("/nonexistent/database.db")
    version = get_schema_version(fake_path)
    assert version == 0

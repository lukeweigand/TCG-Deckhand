"""
Database connection management for TCG Deckhand.

This module provides utilities for:
- Creating database connections
- Managing connection lifecycle
- Context managers for safe connection handling
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .schema import DEFAULT_DB_PATH


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Args:
        db_path: Path to the database file. If None, uses default location.
        
    Returns:
        sqlite3.Connection: Active database connection
        
    Note:
        The caller is responsible for closing the connection.
        Consider using get_connection_context() for automatic cleanup.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    
    # Enable foreign key constraints (not enabled by default in SQLite)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Return rows as dictionaries instead of tuples (easier to work with)
    conn.row_factory = sqlite3.Row
    
    return conn


@contextmanager
def get_connection_context(db_path: Optional[Path] = None):
    """
    Context manager for database connections.
    
    Args:
        db_path: Path to the database file. If None, uses default location.
        
    Yields:
        sqlite3.Connection: Active database connection
        
    Usage:
        with get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cards")
            results = cursor.fetchall()
        # Connection automatically closed after the 'with' block
        
    This is the recommended way to work with the database because:
    - Automatically closes the connection
    - Handles exceptions gracefully
    - Commits on success, rolls back on error
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()  # Commit if everything succeeded
    except Exception:
        conn.rollback()  # Roll back if there was an error
        raise
    finally:
        conn.close()  # Always close the connection


def verify_connection(db_path: Optional[Path] = None) -> bool:
    """
    Verify that the database exists and is accessible.
    
    Args:
        db_path: Path to the database file. If None, uses default location.
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            # Try a simple query
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            return len(tables) > 0
    except sqlite3.Error:
        return False

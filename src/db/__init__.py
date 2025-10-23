"""
Database operations package for TCG Deckhand.

This package provides:
- schema: Database table definitions
- connection: Connection management utilities
"""

from .schema import init_database, get_schema, DEFAULT_DB_PATH
from .connection import get_connection, get_connection_context, verify_connection

__all__ = [
    "init_database",
    "get_schema",
    "DEFAULT_DB_PATH",
    "get_connection",
    "get_connection_context",
    "verify_connection",
]

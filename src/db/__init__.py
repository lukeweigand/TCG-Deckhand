"""
Database operations package for TCG Deckhand.

This package provides:
- schema: Database table definitions and version tracking
- connection: Connection management utilities
"""

from .schema import (
    init_database,
    get_schema,
    get_schema_version,
    DEFAULT_DB_PATH,
    CURRENT_SCHEMA_VERSION,
)
from .connection import get_connection, get_connection_context, verify_connection

__all__ = [
    "init_database",
    "get_schema",
    "get_schema_version",
    "DEFAULT_DB_PATH",
    "CURRENT_SCHEMA_VERSION",
    "get_connection",
    "get_connection_context",
    "verify_connection",
]

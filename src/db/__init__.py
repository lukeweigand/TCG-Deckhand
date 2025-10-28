"""
Database operations package for TCG Deckhand.

This package provides:
- schema: Database table definitions and version tracking
- connection: Connection management utilities
- card_operations: CRUD operations for cards
- deck_operations: CRUD operations for decks
"""

from .schema import (
    init_database,
    get_schema,
    get_schema_version,
    DEFAULT_DB_PATH,
    CURRENT_SCHEMA_VERSION,
)
from .connection import get_connection, get_connection_context, verify_connection
from .card_operations import (
    save_card,
    get_card_by_id,
    get_card_by_name,
    get_all_cards,
    get_cards_by_type,
    search_cards,
    delete_card,
    get_card_count,
)
from .deck_operations import (
    save_deck,
    get_deck_by_id,
    get_deck_by_name,
    get_all_decks,
    get_deck_card_count,
    delete_deck,
    search_decks,
    get_deck_count,
)

__all__ = [
    # Schema
    "init_database",
    "get_schema",
    "get_schema_version",
    "DEFAULT_DB_PATH",
    "CURRENT_SCHEMA_VERSION",
    # Connection
    "get_connection",
    "get_connection_context",
    "verify_connection",
    # Card operations
    "save_card",
    "get_card_by_id",
    "get_card_by_name",
    "get_all_cards",
    "get_cards_by_type",
    "search_cards",
    "delete_card",
    "get_card_count",
    # Deck operations
    "save_deck",
    "get_deck_by_id",
    "get_deck_by_name",
    "get_all_decks",
    "get_deck_card_count",
    "delete_deck",
    "search_decks",
    "get_deck_count",
]

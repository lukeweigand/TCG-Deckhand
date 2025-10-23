"""
SQLite database schema for TCG Deckhand.

This module defines the database structure for storing:
- Card definitions (user-created, TCG-agnostic)
- Deck configurations
- Game session history
"""

import sqlite3
from pathlib import Path
from typing import Optional

# Default database location
DEFAULT_DB_PATH = Path.home() / ".tcg_deckhand" / "deckhand.db"


def get_schema() -> str:
    """
    Returns the SQL schema for creating all database tables.
    
    This schema is TCG-agnostic and uses generic terminology:
    - Cards can be of any type (Creature, Spell, Resource, etc.)
    - Stats are stored as JSON for flexibility
    - Rules text is stored as plain text (future: parse into effects)
    """
    return """
    -- Card Definitions Table
    -- Stores user-defined cards in a generic, TCG-agnostic format
    CREATE TABLE IF NOT EXISTS cards (
        id TEXT PRIMARY KEY,              -- UUID for the card
        name TEXT NOT NULL,               -- Card name (e.g., "Lightning Bolt")
        card_type TEXT NOT NULL,          -- Generic type (e.g., "Creature", "Spell", "Resource")
        cost TEXT,                        -- Cost to play (JSON: {"mana": 2, "energy": 1})
        stats TEXT,                       -- Card stats (JSON: {"attack": 3, "defense": 2, "hp": 5})
        rules_text TEXT NOT NULL,         -- What the card does (plain text for now)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Decks Table
    -- Stores deck configurations (collection of cards)
    CREATE TABLE IF NOT EXISTS decks (
        id TEXT PRIMARY KEY,              -- UUID for the deck
        name TEXT NOT NULL,               -- Deck name (e.g., "Aggro Red")
        description TEXT,                 -- Optional deck notes
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Deck Cards Table
    -- Many-to-many relationship: decks contain multiple cards
    CREATE TABLE IF NOT EXISTS deck_cards (
        deck_id TEXT NOT NULL,            -- Foreign key to decks.id
        card_id TEXT NOT NULL,            -- Foreign key to cards.id
        quantity INTEGER NOT NULL DEFAULT 1,  -- How many copies in the deck
        PRIMARY KEY (deck_id, card_id),
        FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    );

    -- Game Sessions Table
    -- Stores completed game records for analysis
    CREATE TABLE IF NOT EXISTS game_sessions (
        id TEXT PRIMARY KEY,              -- UUID for the game session
        player_deck_id TEXT NOT NULL,     -- Which deck the player used
        ai_deck_id TEXT NOT NULL,         -- Which deck the AI used
        winner TEXT,                      -- "player", "ai", or "draw"
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,               -- When game ended
        total_turns INTEGER,              -- Number of turns played
        move_log TEXT NOT NULL,           -- Complete game history (JSON array)
        FOREIGN KEY (player_deck_id) REFERENCES decks(id),
        FOREIGN KEY (ai_deck_id) REFERENCES decks(id)
    );

    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
    CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(card_type);
    CREATE INDEX IF NOT EXISTS idx_game_sessions_player_deck ON game_sessions(player_deck_id);
    CREATE INDEX IF NOT EXISTS idx_game_sessions_winner ON game_sessions(winner);
    """


def init_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize the database by creating all tables.
    
    Args:
        db_path: Path to the database file. If None, uses default location.
        
    This function:
    1. Creates the database directory if it doesn't exist
    2. Connects to the SQLite database (creates file if needed)
    3. Executes the schema SQL to create all tables
    4. Commits changes and closes connection
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    
    # Create directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect and create tables
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(get_schema())
        conn.commit()
        print(f"✅ Database initialized successfully at: {db_path}")
    except sqlite3.Error as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Allow running this file directly to initialize the database
    init_database()

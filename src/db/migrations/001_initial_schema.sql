-- Migration 001: Initial Schema
-- Date: 2025-10-23
-- Description: Creates the initial database structure for TCG Deckhand
-- Tables: cards, decks, deck_cards, game_sessions, schema_version

BEGIN TRANSACTION;

-- Schema version tracking table
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL
);

-- Card Definitions Table
CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    card_type TEXT NOT NULL,
    cost TEXT,
    stats TEXT,
    rules_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decks Table
CREATE TABLE IF NOT EXISTS decks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deck Cards Table (many-to-many)
CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (deck_id, card_id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);

-- Game Sessions Table
CREATE TABLE IF NOT EXISTS game_sessions (
    id TEXT PRIMARY KEY,
    player_deck_id TEXT NOT NULL,
    ai_deck_id TEXT NOT NULL,
    winner TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_turns INTEGER,
    move_log TEXT NOT NULL,
    FOREIGN KEY (player_deck_id) REFERENCES decks(id),
    FOREIGN KEY (ai_deck_id) REFERENCES decks(id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(card_type);
CREATE INDEX IF NOT EXISTS idx_game_sessions_player_deck ON game_sessions(player_deck_id);
CREATE INDEX IF NOT EXISTS idx_game_sessions_winner ON game_sessions(winner);

-- Record this migration
INSERT OR IGNORE INTO schema_version (version, description)
VALUES (1, 'Initial schema - cards, decks, deck_cards, game_sessions');

COMMIT;

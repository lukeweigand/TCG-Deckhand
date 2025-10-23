# Database Design - TCG Deckhand

## Overview

TCG Deckhand uses **SQLite** as its local database. This choice provides:
- **Privacy:** All data stored locally on your machine (no cloud, no external servers)
- **Simplicity:** No separate database server to install or manage
- **Portability:** Single file database that moves with your application
- **Zero-config:** Works out of the box on Windows, macOS, and Linux

## Database Location

Default: `C:\Users\YourName\.tcg_deckhand\deckhand.db`

You can specify a custom location when initializing:
```powershell
py -m src.db.init_db --path C:/custom/path/game.db
```

## Schema Design

### TCG-Agnostic Philosophy

The database is designed to work with **any** trading card game. Instead of Pokémon-specific or Magic-specific tables, we use generic terminology:

- ❌ **Avoid:** `pokemon_cards` table with `evolution_stage` column
- ✅ **Use:** `cards` table with flexible `stats` JSON column

This means the same database structure can store cards from Pokémon, Magic: The Gathering, Yu-Gi-Oh, or even custom TCGs.

### Tables

#### `cards` - Card Definitions
Stores individual card data entered by the user.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | UUID primary key |
| `name` | TEXT | Card name (e.g., "Lightning Bolt") |
| `card_type` | TEXT | Generic type: "Creature", "Spell", "Resource", etc. |
| `cost` | TEXT | JSON object for play cost (e.g., `{"mana": 3}`) |
| `stats` | TEXT | JSON object for card stats (e.g., `{"attack": 5, "defense": 3}`) |
| `rules_text` | TEXT | What the card does (plain text) |
| `created_at` | TIMESTAMP | When card was added |
| `updated_at` | TIMESTAMP | Last modification time |

**Why JSON for `cost` and `stats`?**  
Different TCGs use different resource systems and stat types. JSON lets us store any structure without changing the database schema.

#### `decks` - Deck Configurations
Stores deck metadata (name, description).

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | UUID primary key |
| `name` | TEXT | Deck name (e.g., "Aggro Red") |
| `description` | TEXT | Optional notes about the deck |
| `created_at` | TIMESTAMP | When deck was created |
| `updated_at` | TIMESTAMP | Last modification time |

#### `deck_cards` - Deck Contents
Many-to-many relationship: links decks to cards with quantities.

| Column | Type | Description |
|--------|------|-------------|
| `deck_id` | TEXT | Foreign key to `decks.id` |
| `card_id` | TEXT | Foreign key to `cards.id` |
| `quantity` | INTEGER | How many copies in the deck |

**Primary Key:** `(deck_id, card_id)` - Each card appears once per deck

#### `game_sessions` - Game History
Stores completed game records for later analysis.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | UUID primary key |
| `player_deck_id` | TEXT | Which deck the player used |
| `ai_deck_id` | TEXT | Which deck the AI used |
| `winner` | TEXT | "player", "ai", or "draw" |
| `start_time` | TIMESTAMP | When game started |
| `end_time` | TIMESTAMP | When game ended |
| `total_turns` | INTEGER | Number of turns played |
| `move_log` | TEXT | Complete game history (JSON array) |

**Why store the full `move_log`?**  
This enables:
- Replaying games to see what happened
- Analyzing strategic decisions
- Debugging game engine issues
- Future analytics features

## Database Operations

### Connection Management

We use a **context manager** pattern for safe database access:

```python
from src.db import get_connection_context

# Recommended approach - auto-cleanup
with get_connection_context() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards")
    results = cursor.fetchall()
# Connection automatically closed and committed
```

**Why use context managers?**
- Automatically commits on success
- Automatically rolls back on error
- Always closes the connection (prevents resource leaks)
- Makes error handling cleaner

### Foreign Key Constraints

SQLite doesn't enable foreign key constraints by default. We enable them on every connection:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

This ensures:
- Can't add cards to non-existent decks
- Deleting a deck also deletes its card associations
- Data integrity is maintained

## Future Considerations

### Migration Strategy
Currently, schema changes require manual updates. Future improvements:
- Version tracking in database
- Automated migration scripts
- Backward compatibility checks

### Performance
For MVP scale (hundreds of cards, dozens of games), no optimization needed. If we grow:
- Additional indexes on frequently queried columns
- Separate read/write connections for concurrency
- Periodic VACUUM to reclaim space

### Data Export/Import
Future feature: Export decks and game history to JSON for:
- Sharing deck lists with friends
- Backing up game data
- Moving between devices

## Learning Resources

- **SQLite Documentation:** https://sqlite.org/docs.html
- **Python sqlite3 module:** https://docs.python.org/3/library/sqlite3.html
- **Database design principles:** https://www.sqlitetutorial.net/

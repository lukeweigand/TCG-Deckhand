# Database Migration Strategy

## Overview

As TCG Deckhand evolves, we'll need to change the database schema (add columns, new tables, modify structures). This document outlines our approach to making these changes safely without losing user data.

## Current State (MVP)

**Version:** 1.0 (Initial schema)  
**Approach:** Simple initialization script (`init_db.py`)  
**Limitation:** No automatic upgrades - schema changes require manual intervention

This is acceptable for MVP because:
- We're still in active development
- No public users yet
- We can manually recreate test databases

## Migration Philosophy

### Guiding Principles

1. **Never lose user data** - Migrations must preserve existing cards, decks, and game history
2. **Version tracking** - Know what schema version the database is on
3. **Rollback capability** - Be able to undo migrations if something goes wrong
4. **Idempotent** - Running the same migration twice should be safe
5. **Documented** - Every schema change has a clear reason and date

### When to Migrate

**Scenarios requiring migrations:**
- Adding new columns to existing tables
- Creating new tables for new features
- Changing column types or constraints
- Adding indexes for performance
- Renaming columns or tables

**Scenarios NOT requiring migrations:**
- Adding new Python code (models, logic)
- Changing business logic
- UI modifications

## MVP Migration Strategy (Manual)

For the MVP phase, we'll use a **manual, documented approach**:

### Version Tracking

Add a `schema_version` table to track the current database version:

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL
);

-- Initial version
INSERT INTO schema_version (version, description) 
VALUES (1, 'Initial schema - cards, decks, deck_cards, game_sessions');
```

### Migration File Structure

Store migrations in `src/db/migrations/` as numbered SQL files:

```
src/db/migrations/
├── 001_initial_schema.sql          # Current schema (already applied)
├── 002_add_card_rarity.sql         # Example: Future migration
├── 003_add_user_preferences.sql    # Example: Future migration
└── README.md                        # Migration log
```

### Migration File Format

Each migration file should:
1. Check current version
2. Apply changes
3. Update version number

**Example:** `002_add_card_rarity.sql`
```sql
-- Migration: Add rarity column to cards table
-- Date: 2025-11-15
-- Reason: Track card rarity for deck-building restrictions

-- Verify we're on version 1
BEGIN TRANSACTION;

-- Add the new column (default to 'common' for existing cards)
ALTER TABLE cards ADD COLUMN rarity TEXT DEFAULT 'common';

-- Update version
INSERT INTO schema_version (version, description)
VALUES (2, 'Added rarity column to cards table');

COMMIT;
```

### Manual Migration Process

When a schema change is needed:

1. **Create migration file** - `migrations/NNN_description.sql`
2. **Document the change** - Add entry to `migrations/README.md`
3. **Test on a copy** - Always test migration on a backup first
4. **Apply to dev database** - Run manually using SQLite CLI or Python
5. **Update schema.py** - Modify `get_schema()` to include changes
6. **Update tests** - Ensure tests reflect new schema

**Applying a migration (PowerShell):**
```powershell
# Option 1: Using SQLite CLI
sqlite3 C:\Users\Luke\.tcg_deckhand\deckhand.db < src\db\migrations\002_add_card_rarity.sql

# Option 2: Using Python
py -c "import sqlite3; conn = sqlite3.connect('C:/Users/Luke/.tcg_deckhand/deckhand.db'); conn.executescript(open('src/db/migrations/002_add_card_rarity.sql').read()); conn.close()"
```

## Post-MVP: Automated Migrations

Once we have real users, we'll implement an automated migration system:

### Recommended Approach: Alembic-style

**Tool options:**
- **Alembic** (if we add SQLAlchemy ORM later)
- **Yoyo Migrations** (lightweight, works with raw SQL)
- **Custom script** (full control, educational)

### Automated Migration Features

```python
# Future command
py -m src.db.migrate upgrade

# Would automatically:
# 1. Check current database version
# 2. Find unapplied migrations
# 3. Apply them in order
# 4. Update version tracking
# 5. Report success/failure
```

## Best Practices

### DO:
- ✅ **Backup before migrating** - Always have a copy of the database
- ✅ **Use transactions** - Wrap migrations in BEGIN/COMMIT
- ✅ **Test rollback** - Ensure you can undo changes
- ✅ **Add columns with defaults** - Don't break existing data
- ✅ **Version everything** - Track every schema change

### DON'T:
- ❌ **Delete columns directly** - SQLite doesn't support DROP COLUMN easily
- ❌ **Change column types** - Can corrupt data
- ❌ **Skip versions** - Migrations must be sequential
- ❌ **Modify old migrations** - Once applied, they're immutable

## Handling SQLite Limitations

SQLite has limited ALTER TABLE support. Workarounds:

### Renaming a Column (SQLite 3.25+)
```sql
ALTER TABLE cards RENAME COLUMN old_name TO new_name;
```

### Dropping a Column (Create New Table Method)
```sql
BEGIN TRANSACTION;

-- 1. Create new table without the column
CREATE TABLE cards_new (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    -- (excluded column not listed)
    card_type TEXT NOT NULL
);

-- 2. Copy data
INSERT INTO cards_new SELECT id, name, card_type FROM cards;

-- 3. Drop old table
DROP TABLE cards;

-- 4. Rename new table
ALTER TABLE cards_new RENAME TO cards;

-- 5. Recreate indexes
CREATE INDEX idx_cards_name ON cards(name);

COMMIT;
```

## Migration Log Template

Keep a human-readable log in `migrations/README.md`:

```markdown
# Migration History

## Version 1 (2025-10-23)
**File:** `001_initial_schema.sql`  
**Description:** Initial database schema  
**Tables Created:** cards, decks, deck_cards, game_sessions  
**Author:** Luke Weigand

## Version 2 (2025-11-15) [Example]
**File:** `002_add_card_rarity.sql`  
**Description:** Add rarity tracking for cards  
**Changes:**
- Added `rarity` column to `cards` table (TEXT, default 'common')
**Reason:** Enable deck-building restrictions by rarity  
**Author:** Luke Weigand
```

## Testing Migrations

Every migration should have tests:

```python
# tests/test_migrations.py

def test_migration_002_adds_rarity_column(temp_db):
    """Test that migration 002 successfully adds rarity column."""
    # 1. Set up database at version 1
    init_database(temp_db)
    
    # 2. Apply migration
    apply_migration(temp_db, "002_add_card_rarity.sql")
    
    # 3. Verify column exists
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(cards)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "rarity" in columns
    
    # 4. Verify version updated
    cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
    version = cursor.fetchone()[0]
    assert version == 2
```

## Emergency Procedures

### Corrupted Database
1. Stop the application
2. Restore from backup
3. Investigate what went wrong
4. Fix migration script
5. Re-apply

### User Reports Data Loss
1. Don't panic - data should still be in the file
2. Use SQLite recovery tools: `.recover` command
3. Export to SQL dump: `sqlite3 db.db .dump > backup.sql`
4. Investigate schema mismatch

### Rolling Back a Migration
```sql
-- Most migrations can't be automatically rolled back
-- Manual process:
-- 1. Restore from backup before migration
-- 2. OR manually undo changes (reverse the SQL)

-- Example rollback for "add column":
BEGIN TRANSACTION;

-- Create new table without the added column
CREATE TABLE cards_new AS 
SELECT id, name, card_type, cost, stats, rules_text, created_at, updated_at
FROM cards;

DROP TABLE cards;
ALTER TABLE cards_new RENAME TO cards;

-- Decrement version
DELETE FROM schema_version WHERE version = 2;

COMMIT;
```

## Future: Schema Version API

Eventually, expose version checking in code:

```python
from src.db import get_schema_version, CURRENT_SCHEMA_VERSION

def check_database_compatibility():
    """Check if database needs migration."""
    db_version = get_schema_version()
    
    if db_version < CURRENT_SCHEMA_VERSION:
        print(f"⚠️  Database needs migration (v{db_version} → v{CURRENT_SCHEMA_VERSION})")
        print("Run: py -m src.db.migrate upgrade")
        return False
    
    if db_version > CURRENT_SCHEMA_VERSION:
        print("❌ Database is newer than application!")
        print("Please update TCG Deckhand to the latest version.")
        return False
    
    return True
```

## Summary

**For MVP (Now):**
- Manual migrations via SQL files
- Version tracking table
- Documented process
- Test on backups first

**For Production (Later):**
- Automated migration tool
- Rollback capability
- Migration testing suite
- Version compatibility checks

**Key Takeaway:**  
Migrations are about **change management**, not just writing SQL. Plan changes carefully, test thoroughly, and always have backups.

## Resources

- **SQLite ALTER TABLE docs:** https://www.sqlite.org/lang_altertable.html
- **Alembic (for future):** https://alembic.sqlalchemy.org/
- **Yoyo Migrations:** https://ollycope.com/software/yoyo/
- **Database Versioning Best Practices:** https://www.liquibase.org/get-started/best-practices
